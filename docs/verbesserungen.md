# Verbesserungsvorschläge zum Product‑Backlog (karimi.me – Digitaler Garten)

## 1) Scope & Sequencing schärfen
- **Iteration 0/1 minimal halten:** Für I0/I1 nur *Gateway + Hello‑Page + TLS‑Automation* – keine Themes/Content‑Model‑Komplexität. So ist der Durchstich schneller validierbar.
- **E2 in zwei Builds splitten:** E2.01 (Hugo Minimal + RSS) vor E2.02 (Multi‑Output/Visibility‑Build). Dadurch bleibt die Pipeline zuerst simpel.
- **E4/E5 Abhängigkeiten markieren:** Kommentare (E5) hängen praktisch an *öffentlichen* Seiten; Authelia‑Setup kann parallel laufen, aber nicht zwingend vor E5‑Public.

## 2) Access‑Control & Build‑Strategie (Leak‑Sicherheit)
- **Explizite Content‑Filterung:** In Hugo kann man `where .Pages "Params.visibility" "public"` verwenden. In Kombination mit getrennten Builds reduziert das “vergessenes private Content im public Build”.
- **Build‑Flag statt Copy‑Tree:** Statt Content physisch zu kopieren (tmp dirs) kann ein Build‑Parameter (ENV `SITE_AUDIENCE`) genutzt werden, der in Templates/outputs filtert.
- **robots.txt & noindex:** Für `/g/` und `/private/` zusätzlich `X‑Robots‑Tag: noindex` im Nginx setzen, um versehentliche Indexierung zu verhindern.

## 3) Reverse‑Proxy‑Setup vereinfachen
- **DSM vs. Nginx Verantwortlichkeiten klar dokumentieren:** DSM bleibt TLS + Port‑Forward, Nginx übernimmt *alle* Pfad‑Regeln + Auth + Rate‑Limit. So gibt es nur eine “Logik‑Schicht”.
- **Health‑Endpoints definieren:** Nginx `/healthz` für Gateway, optional Authelia `/api/health` durchreichen.

## 4) Kommentar‑System (Remark42)
- **Pfad‑Routing Test‑Checkliste ergänzen:** Spezifisch 301/302‑Loops bei Sub‑Path, `REMARK_URL` + `X‑Forwarded‑Prefix` prüfen.
- **Provider‑Fallback klar beschreiben:** Wenn Email‑Auth allein nicht reicht, *genau ein* OAuth‑Provider als Fallback (z. B. GitHub) definieren.
- **Backups explizit:** Remark42 hat ein Backup‑Endpoint; in E7 Backups als Task erwähnen.

## 5) FreshRSS Sub‑Path Fallstricke
- **Cookie‑Path & Base‑URL prüfen:** `BASE_URL=https://karimi.me/reader` + `X‑Forwarded‑Prefix: /reader` als Fixpunkt in die Nginx‑Config.
- **CRON im Container testen:** Ein kurzer Smoke‑Test “letztes Update‑Timestamp ändert sich” hilft, Cron‑Updates zu verifizieren.

## 6) Content‑Modell & UX
- **Status‑Badges minimal:** Nur 3 Zustände (seedling/plant/tree) – als farbige Badges; nicht mehr.
- **Segment‑Landingpages:** Jede Segmentseite (Politik/Tech/Reise) als hand‑kuratierte MOC/Indexseite (nicht nur Blog‑Liste).
- **Dossier Timeline Sortierung festlegen:** Aufsteigend (chronologisch) oder absteigend *einheitlich*.

## 7) Sicherheit & Betrieb
- **Authelia‑Session & Cookie‑Domain:** `karimi.me` + `SameSite=Lax` dokumentieren, um SSO über Sub‑Pfad zu sichern.
- **Rate‑Limit getrennt für Login:** Authelia `/api/verify` und Remark42 `/auth` separate `limit_req`‑Zonen.
- **Minimal‑Logging:** Access‑Logs für `/comments/` und `/reader/` aktiv; so sieht man Fehler ohne Voll‑Debug.

## 8) Observability & Maintenance
- **Status‑Dashboard:** Ein kleines “Status”‑Markdown im Repo, in dem die Releases/Links gepflegt werden.
- **Update‑Policy:** Monatliches `docker compose pull` + `docker compose up -d` im Runbook ergänzen.

## 9) Dokumentation & Handoff
- **Quickstart + Troubleshooting:** Im Runbook je Feature 3–5 häufige Probleme (z. B. 404 bei Sub‑Path).
- **Entscheidungen festhalten:** Ein `DECISIONS.md` (ADR‑Light), damit spätere Änderungen nachvollziehbar bleiben.
