# Software‑Spezifikation & Umsetzungsplan

## Digitaler Garten auf `karimi.me` (Self‑Hosted, Docker‑Compose, Synology Reverse Proxy)

**Version:** 1.0  
**Datum:** 2026‑02‑02  
**Owner:** Koorosh Karimi  
**Betrieb:** Home‑Server (NAS), Self‑Hosted, ohne Social‑Network‑Abhängigkeit

---

## 1. Zielbild und Leitprinzipien

### 1.1 Vision

Du betreibst auf deiner eigenen Domain `karimi.me` eine Website im Stil eines **digitalen Gartens**: ein Wissensraum, der sich über Zeit entwickelt, offen vernetzt ist, aber nach außen **klar segmentiert und nicht chaotisch** wirkt.

Die Seite soll zwei Dinge gleichzeitig leisten:

1. **Publish (Garten)**  
   Du schreibst Inhalte (Politik, Tech, Reisen, privat) und veröffentlichst sie kontrolliert in unterschiedlichen Sichtbarkeiten:

   * privat
   * für definierte Nutzergruppen
   * öffentlich

2. **Consume (Leseraum)**  
   Du abonnierst Feeds anderer Seiten/“Gärten”/News und liest sie in **FreshRSS** – integriert unter derselben Domain (als Unterpfad).

### 1.2 Leitprinzipien

* **Self‑Hosted & unabhängig** (keine Plattform‑Lock‑ins).
* **Markdown‑First** als langfristig portables Format.
* **Sichtbarkeit pro Seite** (public / group / private) muss **technisch erzwungen** werden (nicht nur “versteckt”).
* **Iterativ & inkrementell**: Jede neue Fähigkeit wird so eingeführt, dass sie **End‑to‑End testbar** ist (Domain → Reverse Proxy → App → Funktion).
* **Minimalistisch**: so wenig bewegliche Teile wie möglich im MVP; Komplexität nur, wenn sie echten Nutzen bringt.

---

## 2. Systemkontext und feste Rahmenbedingungen

### 2.1 Hosting/Netzwerk

* NAS: Synology (DSM Reverse Proxy vorhanden)
* Container‑Orchestrierung: Docker über Docker‑Compose
* Domain/DNS: IONOS
* **Apex‑Domain**: `karimi.me` (keine Subdomain für den Garten)

### 2.2 Zertifikate (Option 2)

* TLS‑Zertifikate via Let's Encrypt
* **DNS‑01 Challenge** (keine Port‑80‑Abhängigkeit)
* Automatisierung via `acme.sh` + IONOS DNS API
* Deployment/Import ins DSM‑Zertifikatssystem (DSM benutzt das Zertifikat für den Reverse Proxy)

### 2.3 Reverse‑Proxy‑Topologie

* **DSM Reverse Proxy** ist die „Front Door“ und terminiert TLS.
* Dahinter: ein eigener Gateway‑Reverse‑Proxy Container (NGINX) für:

  * Routing nach Pfad (`/`, `/private/`, `/g/...`, `/reader/`, `/comments/`)
  * Auth‑Integration
  * Rate‑Limiting / Security Headers
  * klare, versionierbare Konfiguration im Repo (Infrastructure‑as‑Code)

---

## 3. Rollen, Benutzergruppen und Use Cases

### 3.1 Rollen

* **Owner (Admin)**: du; erstellt/ändert Inhalte; verwaltet Nutzergruppen; moderiert Kommentare.
* **Group‑User**: eingeloggte Nutzer (z. B. friends/family), sehen Group‑Content.
* **Public Visitor**: anonymer Besucher; sieht public Content; kann kommentieren (mit Human‑Verification).
* **Commenter**: kommentiert nach Verifikation; kann auch public sein.

### 3.2 Nutzergruppen

Mindestens:

* `owner`
* `friends`
* `family`

Erweiterbar (optional später):

* `work`
* `community`

### 3.3 Kern‑Use‑Cases

1. **Seite erstellen** (Notiz/Artikel/Dossier/Timeline/Reisebericht/Galerie)
2. **Sichtbarkeit pro Seite festlegen**: private / group(s) / public
3. **Dossier/Timeline fortlaufend aktualisieren** (z. B. politische Ereignisse)
4. **RSS Out**: Besucher abonnieren Updates (mind. public)
5. **RSS In**: Owner liest Feeds in FreshRSS unter `/reader/`
6. **Kommentare**: Besucher kommentiert – Bot‑/Spam‑Schutz verhindert Missbrauch
7. **Fotos einbetten** (in Reiseberichten oder “nur Fotos” Galerieposts)

---

## 4. Funktionale Anforderungen (MVP + Erweiterungen)

### 4.1 Inhaltsarten (Content Types)

**MVP muss unterstützen:**

* `note`: kurze Notiz
* `article`: ausformulierter Text
* `dossier`: Themenhub (z. B. “Iran”)
* `timeline-entry`: Eintrag innerhalb eines Dossiers
* `trip`: Reisebericht (Text + Bilder)
* `gallery`: primär Bilder (optional kurze Einleitung)

### 4.2 Sichtbarkeit pro Seite (zwingend)

Jede Seite hat eine Sichtbarkeit:

* `public` → öffentlich erreichbar, in Public‑Navigation sichtbar, Public‑RSS
* `group` → nur nach Login + Gruppenzugehörigkeit, nicht öffentlich indexierbar
* `private` → nur Owner, niemals öffentlich erreichbar

**Wichtig:** Sichtbarkeit muss **serverseitig** durchgesetzt werden und darf nicht vom Client abhängen.

### 4.3 “Reifegrad” / Status (Chaos‑Bremse)

Jede Seite hat zusätzlich einen Reifegrad (für “nicht chaotisch von außen”):

* `seedling` (Keimling) – unfertig/roh
* `plant` (Pflanze) – brauchbar, aber noch in Arbeit
* `tree` (Baum/Evergreen) – kuratiert/ausgereift

**Regel im Public‑Bereich (empfohlen):**

* Standard‑Listing zeigt nur `plant` + `tree`
* `seedling` bleibt privat oder wird nur in einem expliziten “Work in Progress” Bereich gezeigt

### 4.4 Segmentierung (Außenstruktur)

Die Website muss eine klare “Außenordnung” bieten, z. B.:

* Politik
* Technologie
* Reisen
* Notizen/Denken (optional)
* Projekte (optional)
* (Privat ist nicht öffentlich sichtbar)

**Maps of Content (MOCs)** / Indexseiten pro Segment sind Pflicht, damit Besucher nicht im Link‑Netz untergehen.

### 4.5 Dossiers & Timeline (fortlaufend ergänzbar)

Für Themen wie “Iran”:

* Eine Dossier‑Hub‑Seite als Überblick und Einstieg
* Viele Timeline‑Entries als einzelne Einträge (jeweils datiert)
* Timeline muss sortierbar sein (neu → alt, optional Filter nach Tags/Themensträngen)

**Timeline‑Entry Template** muss unterstützen:

* Fakten (“Was ist passiert?”)
* Quellenlinks
* Kontextlinks (auf andere Garten‑Seiten)
* Einschätzung getrennt von Fakten
* offene Fragen / TODO

### 4.6 Medien / Bilder

* Bilder werden gezielt pro Beitrag eingebettet (kein “alle Fotos hochladen” als Voll‑Gallery‑System).
* **Galerie‑Post** ist möglich (nur Fotos, wenig Text).
* Bilder sollen:

  * automatisch in sinnvolle Größen/Thumbnails generiert werden (Performance)
  * optional EXIF/GPS stripping (Privatsphäre)

### 4.7 RSS Out (dein Garten abonnierbar)

MVP:

* `public` Feed (global): neue/aktualisierte public Inhalte

Erweiterungen:

* Feed pro Segment (Politik/Tech/Reisen)
* Feed pro Dossier (Timeline‑Updates)
* “Evergreen‑Feed” nur für `tree` (für Leute, die nicht jeden Keimling wollen)

### 4.8 RSS In (FreshRSS)

* FreshRSS läuft unter Unterpfad: `karimi.me/reader/`
* Zugriff ist **private** (Owner)
* OPML Import/Export und Kategorien sind vorhanden (FreshRSS‑Standard)

### 4.9 Kommentare (öffentlich, aber bot‑/spam‑resistent)

* Kommentarfunktion auf Seiten
* **Human‑Verification:** Kommentare nur für verifizierte Nutzer
  MVP‑Ansatz: E‑Mail‑Login (Magic Link / Code) → “echte Menschen”-Hürde.
* Anti‑Spam:

  * Rate‑Limit pro IP / pro Endpoint im Gateway‑Proxy
  * Moderation (Owner kann löschen/blocken)
  * optional: “First comment needs approval” (wenn Tool unterstützt)

**Trennung public vs private/group Kommentare (Empfehlung):**

* Public‑Kommentare laufen auf einem eigenen Kommentar‑Space.
* Group/Private Kommentare laufen getrennt (damit nichts versehentlich öffentlich auftaucht).

---

## 5. Nichtfunktionale Anforderungen

### 5.1 Sicherheit

* TLS muss gültig sein, automatisches Renewal.
* Authentifizierung & Autorisierung über zentralen Auth‑Dienst.
* Strikte Trennung der Outputs, um Content‑Leaks zu verhindern.
* Rate‑Limiting für Kommentar‑ und Login‑Endpoints.
* Security Headers (CSP, HSTS optional, X‑Content‑Type‑Options etc.)
* Admin‑Zugänge (DSM / Deploy‑User) minimal berechtigen.

### 5.2 Datenschutz

* Keine externen Tracker.
* Kommentare: E‑Mail‑Adresse wird nur für Login/Verifikation genutzt und nicht öffentlich angezeigt.
* Bilder: EXIF/GPS optional entfernen.

### 5.3 Performance

* Public Bereich statisch und schnell.
* Bilder optimiert (responsive, lazy loading).
* Caching via Browser‑Cache Headers.

### 5.4 Wartbarkeit / Portabilität

* Alles versioniert im Repo (Compose, Nginx configs, Site‑Templates, Scripts).
* Secrets liegen in `.env` (nicht im Git).
* Markdown als Source of Truth.

### 5.5 Betrieb & Wiederherstellbarkeit

* Backup von:

  * Content‑Repo
  * FreshRSS Daten
  * Kommentar‑Daten
  * Auth‑Daten
  * Nginx/Authelia/Compose Config
* Restore‑Checkliste muss existieren und getestet sein.

---

## 6. Systemarchitektur (Komponenten & Schnittstellen)

### 6.1 Komponentenübersicht

* **DSM Reverse Proxy (TLS Termination)**
* **Gateway‑Proxy (Nginx in Compose)**  
  Routing, Auth‑Request, Rate‑Limit, Static Serving
* **Static Website Outputs**

  * `out/public`
  * `out/groups/<group>`
  * `out/private`
* **Site Builder (Hugo Container)**  
  Erzeugt die Outputs aus Markdown
* **Auth Service**: Authelia  
  Login, Sessions, Gruppen‑Policies
* **RSS Reader**: FreshRSS  
  läuft unter `/reader/`
* **Comments**: Remark42  
  unter `/comments/` (public) und `/comments-private/` (group/private)
* **Certificate Automation**: acme.sh (DNS‑01 IONOS + Deploy to DSM)

### 6.2 Request‑Flow

**Public:**  
`https://karimi.me/...` → DSM Reverse Proxy → Gateway Nginx → `out/public`

**Private:**  
`https://karimi.me/private/...` → DSM → Gateway Nginx → `auth_request` zu Authelia → (OK) → `out/private`

**Group:**  
`https://karimi.me/g/friends/...` → DSM → Gateway Nginx → Authelia → `out/groups/friends`

**Reader:**  
`https://karimi.me/reader/...` → DSM → Gateway Nginx → Authelia → FreshRSS (Subfolder‑Headers)

**Comments:**  
`https://karimi.me/comments/...` → DSM → Gateway → Remark42 public  
`https://karimi.me/comments-private/...` → DSM → Gateway → Authelia → Remark42 private

---

## 7. Content‑Datenmodell (Frontmatter)

### 7.1 Pflichtfelder pro Seite

```yaml
title: "..."
type: note | article | dossier | timeline-entry | trip | gallery
segment: politik | technik | reisen | ...
status: seedling | plant | tree
visibility: public | group | private
groups: ["friends", "family"] # nur wenn visibility=group
date: 2026-02-02              # Erstellungsdatum
lastmod: 2026-02-02           # Last updated (wichtig für Digital Garden)
tags: ["..."]
```

### 7.2 Timeline‑Spezifika (Empfehlung)

```yaml
dossier: iran
event_date: 2026-02-01
sources:
  - "..."
```

### 7.3 Safety‑Default

Wenn `visibility` fehlt → **private** (Fail‑Closed).

---

## 8. Verbesserungsvorschläge (Design‑ & Ops‑Upgrades)

Diese Punkte sind nicht alle MVP‑Pflicht, aber stark empfohlen:

### 8.1 Leak‑Prevention & Validierung

* Build‑Validierung: “public output enthält keine private/group Seiten”
* Link‑Check (broken links) im Build
* Content‑Linter: Frontmatter Schema Check

### 8.2 Suchfunktion (optional, später)

* Statische Suche (Pagefind/Lunr) im Public Bereich
* Separate Suche im Private Bereich (unter Auth)

### 8.3 Moderations‑Workflow Kommentare

* “First comment moderation” oder “new user throttle” (falls Tool unterstützt)
* Blocklists und Export/Backup der Kommentare

### 8.4 “Preview‑Modus”

* Lokaler Preview‑Host (nur LAN) z. B. `karimi.me:preview` oder eigener interner Port, um Inhalte zu prüfen, bevor sie “public build” werden.

### 8.5 Monitoring/Health

* `/healthz` Endpoints
* optional Uptime‑Monitoring (Uptime Kuma) intern

---

## 9. Umsetzungsplan: inkrementell & End‑to‑End testbar

### Grundregel für jede Iteration

**Done** heißt:

1. Feature läuft **über die echte Domain** `karimi.me` (oder mindestens über DSM Reverse Proxy im Netz)
2. Feature ist über definierte E2E‑Tests überprüft
3. Regression‑Smoke‑Tests laufen (mindestens `/healthz`, `/`, optional RSS, Auth, Reader, Comments)

### Standard‑Regression‑Pack (läuft nach jeder Iteration)

* `GET /healthz` → 200
* `GET /` → 200
* `GET /index.xml` → 200 (ab Iteration 3)
* `GET /private/` → 302/401 (ab Iteration 5)
* `GET /comments/` → 200 (ab Iteration 6)
* `GET /reader/` → 302/401 oder 200 (ab Iteration 7)

---

### Iteration 0 — Technologischer Durchstich: Domain → DSM → Container

**Ziel:** Der komplette Weg funktioniert, noch ohne Site Builder.

**Deliverables**

* Docker‑Compose: Gateway Nginx
* Static hello page im `out/public`
* DSM Reverse Proxy Route: `karimi.me` → Gateway Port

**E2E Tests**

* `https://karimi.me/` zeigt Hello
* `https://karimi.me/healthz` → 200

---

### Iteration 1 — TLS Automation: DNS‑01 + DSM Deploy

**Ziel:** HTTPS mit gültigem Zertifikat, ohne Zusatzkosten.

**Deliverables**

* acme.sh Container + IONOS DNS API Credentials
* Zertifikat für `karimi.me` wird automatisch erneuert
* DSM Reverse Proxy verwendet das Zertifikat

**E2E Tests**

* Browser: `https://karimi.me/` ohne Warnung
* Renewal‑Simulation dokumentiert (oder kurzfristiger Renewal‑Run)

---

### Iteration 2 — Static Site Pipeline: Markdown → Build → Live (Public)

**Ziel:** Der Garten kann aus Markdown gebaut werden.

**Deliverables**

* Hugo Projektstruktur
* Builder‑Script `build public` → `out/public`
* Nginx served `out/public`

**E2E Tests**

* Markdown ändern → Build → `https://karimi.me/` zeigt Änderung

---

### Iteration 3 — Außenstruktur & RSS Out

**Ziel:** Segmentierte, nicht-chaotische Navigation + RSS Feed.

**Deliverables**

* Segmente (Politik/Tech/Reisen)
* Indexseiten/MOCs
* Public RSS Feed (global)

**E2E Tests**

* `GET /politik/` etc. → 200
* `GET /index.xml` → 200, enthält public Einträge

---

### Iteration 4 — Dossier & Timeline

**Ziel:** Fortlaufende politische Chroniken.

**Deliverables**

* Content type `dossier` + `timeline-entry`
* Dossier Hub Seite, Timeline List

**E2E Tests**

* Neuer Timeline‑Entry (neue Datei) → Build → erscheint im Dossier
* Sortierung korrekt

---

### Iteration 5 — Auth & Sichtbarkeit pro Seite (public/group/private) + Leak‑sicheres Build

**Ziel:** Pro Seite Sichtbarkeit definieren; technisch geschützt.

**Deliverables**

* Authelia läuft unter `/auth/`
* Nginx `auth_request` für `/private/` und `/g/*`
* Build erzeugt getrennte Outputs:

  * public
  * groups/<group>
  * private

**E2E Tests**

* `GET /private/` ohne Login → Redirect/401
* Login → `/private/` sichtbar
* Group‑User → `/g/friends/` sichtbar, aber nicht `/g/family/` (wenn nicht in Gruppe)
* Leak‑Test: private Seiten sind nicht im public output erreichbar

---

### Iteration 6 — Kommentare Public + Anti‑Spam

**Ziel:** Kommentare auf öffentlichen Seiten, aber bot‑resistent.

**Deliverables**

* Remark42 public unter `/comments/`
* Email‑Login aktiv, anonymous aus
* Nginx Rate‑Limit für Kommentar‑Endpoints

**E2E Tests**

* Auf public Seite: Kommentarbox sichtbar
* Login per Email funktioniert
* Kommentar kann gepostet werden
* Rate‑Limit: durch schnelle Requests wird 429 ausgelöst

---

### Iteration 7 — FreshRSS unter `/reader/` (private)

**Ziel:** RSS In integriert.

**Deliverables**

* FreshRSS Container
* Nginx Proxy unter `/reader/`
* Auth Pflicht (Owner)

**E2E Tests**

* `GET /reader/` ohne Login → Redirect/401
* Nach Login: FreshRSS UI lädt korrekt (Assets/Links ok)
* Feed hinzufügen, Update läuft

---

### Iteration 8 — Kommentare Private/Group (separater Kommentar‑Space)

**Ziel:** Group/Private Seiten haben Kommentare ohne Public‑Leak.

**Deliverables**

* Remark42 private unter `/comments-private/` (Authelia geschützt)
* Templates binden je nach Audience den passenden Kommentar‑Endpoint ein

**E2E Tests**

* Group‑Seite: Kommentarbox zeigt private endpoint
* Kommentar ist nicht über public Kommentarspace sichtbar

---

### Iteration 9 — Medien‑UX (Reisen/Galerien) + Ops‑Hardening

**Ziel:** Reiseberichte/Galerien schön + Betrieb stabil.

**Deliverables**

* Bilder‑Pipeline (Thumbnails, optional EXIF strip)
* `smoke.sh` und `build.sh` final
* Backup‑Plan + Restore‑Drill dokumentiert

**E2E Tests**

* Reisebericht mit Bildern lädt schnell und responsive
* Restore‑Test: eine Seite + Kommentar‑DB oder Reader‑DB wird wiederhergestellt

---

## 10. End‑to‑End Teststrategie (konkret)

### 10.1 Automatisiert (Smoke)

Ein Script (z. B. `scripts/smoke.sh`) prüft HTTP‑Codes und erwartete Redirects/401.

### 10.2 Manuell (pro Feature)

* Auth: Login + Gruppenzugehörigkeit testen
* Kommentare: Login via Email, Posten, Moderation
* Reader: OPML Import, Feed update
* Timeline: neue Entry Datei, Build, Anzeige, RSS update

### 10.3 Security‑Regression

* Rate‑Limit: 429 bei Abuse
* Content Leak: private Seite darf nie in public erreichbar sein
* Robots: group/private noindex (empfohlen)

---

## 11. Abnahmekriterien (System‑Level)

Das System gilt als “Release‑fähig”, wenn:

1. `karimi.me` hat gültiges TLS, Renewal automatisiert
2. Public Content ist minimalistisch, segmentiert, RSS verfügbar
3. Pro Seite: public/group/private steuerbar und technisch enforced
4. FreshRSS unter `/reader/` läuft und ist privat
5. Kommentare funktionieren und sind bot‑/spam‑resistent (Human‑Verification + Rate‑Limit)
6. Dossiers/Timelines sind fortlaufend pflegbar
7. Backup/Restore ist dokumentiert und einmal getestet

---

Wenn du willst, kann ich dir als nächstes auch noch eine **“Developer‑Hand‑off‑Checkliste”** (kurz, operativ) schreiben, die ein Entwickler beim Setup Schritt für Schritt abarbeitet (DNS → acme → DSM → Compose → Build → Auth → Comments → Reader), inklusive “typische Fehlerbilder und wie man sie erkennt”.
