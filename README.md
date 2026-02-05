# MyGarden

## Iteration 0: Domain-Durchstich (Gateway + Hello)

Lokaler Test des Gateway-Reverse-Proxys mit statischer Hello-Seite.

1. Gateway starten + prüfen: `./scripts/gateway/restart.sh`
2. Optionaler Smoke-Test: `./scripts/smoke.sh`
3. Browser: `http://localhost:1234/` (Hello-Seite) und `http://localhost:1234/healthz`
4. Für Domain-Zugriff `karimi.me`: siehe [docs/domain-routing.md](docs/domain-routing.md)

Nginx-Konfiguration liegt unter `infra/nginx/`, statische Ausgabe unter `out/public/`.

## Iteration 2: Static Site Pipeline (Markdown -> Hugo -> out/public)

1. Inhalt in `site/content/` pflegen
2. Build ausführen: `./scripts/build-public.sh`
3. Ergebnis prüfen: `http://localhost:1234/`
4. Bei Image-Fehlern kann Hugo-Image in `.env` überschrieben werden: `HUGO_IMAGE=klakegg/hugo:ext-alpine`


## Iteration 3: Außenstruktur + RSS Out

1. Segmente nutzen: `site/content/politik/`, `site/content/technik/`, `site/content/reisen/`
2. Build ausführen: `./scripts/build-public.sh`
3. Smoke-Test: `./scripts/smoke.sh`
4. Public prüfen: `/politik/`, `/technik/`, `/reisen/`, `/index.xml`


## Iteration 4: Dossier + Timeline

1. Dossier erstellen (z. B. `site/content/politik/dossier-iran.md`)
2. Timeline-Entries unter `site/content/politik/timeline/` mit `type: timeline-entry`, `dossier`, `event_date`
3. Build ausführen: `./scripts/build-public.sh`
4. Smoke-Test: `./scripts/smoke.sh`
5. Dossier prüfen: `/politik/dossier-iran/`

## Iteration 5 (Basis): getrennte Outputs + Leak-Check

1. Alle Ziel-Outputs bauen: `./scripts/build-all.sh`
2. Ergebnis prüfen:
   * Public: `out/public`
   * Group: `out/groups/friends`, `out/groups/family`
   * Private: `out/private`
3. Leak-Check: `./scripts/checks/leak-check.sh` (default auto-fix für stale/orphan Seiten)
4. Public-Artefakt-Check: `./scripts/checks/verify-public-tree.sh`
5. Strikter Leak-Check ohne Auto-Fix: `LEAK_CHECK_STRICT=1 ./scripts/checks/leak-check.sh`
   (Taxonomy/Utility-Seiten wie `/categories/` werden dabei nicht als Leak gewertet.)
6. Gateway-Routing prüfen (Public + Group + Private): `./scripts/smoke-all.sh`
   (prüft zusätzlich Marker im HTML, damit Link-Ziele nicht still auf die Startseite zurückfallen)
7. Builds bereinigen alte Dateien vorab automatisch (`rm -rf out/<audience>/*`), um Stale-Artefakte zu verhindern.

## Iteration 1: TLS Automation

TLS-Automation per DNS-01 (IONOS) und Deployment nach Synology DSM.

* Konfiguration: `.env` aus `.env.example` ableiten (`IONOS_PREFIX`/`IONOS_SECRET` und `SYNO_HOSTNAME` etc. setzen).
* Setup/Issue: `EMAIL=you@example.com ./scripts/acme/issue.sh`
* Renewal: `./scripts/acme/renew.sh`

Details: siehe [docs/tls-automation.md](docs/tls-automation.md).

Hinweis: Falls du noch alte `.env`-Namen (`SYNO_DSM_HOSTNAME`/`SYNO_DSM_PORT`) nutzt, mappen die Skripte diese automatisch. Empfohlen ist trotzdem die Umstellung auf `SYNO_HOSTNAME`/`SYNO_PORT`.

## NAS Checks ohne ripgrep

Wenn auf der Synology kein `rg` vorhanden ist:

```bash
./scripts/checks/nas-verify.sh
```

TLS/DNS Schnellcheck: `./scripts/domain/check-dns-path.sh karimi.me synology.karimi.me`

DNS per API synchronisieren (A/AAAA von `karimi.me` anhand `koorosh.synology.me`): `./scripts/domain/sync-ionos-dns.py`

Bei IPv6-Problemen: `INCLUDE_AAAA=false ./scripts/domain/sync-ionos-dns.py` (entfernt Apex-AAAA).

Go-Live (DNS sync + gateway + TLS checks + optional cert deploy): `EMAIL=you@example.com ./scripts/domain/go-live.sh`

Hinweis DSM Deploy: Bei `Unable to find certificate ... $SYNO_Create is not set` in `.env` `SYNO_CREATE=1` setzen.

DNS-Propagation (Cloud resolvers): `EXPECT_IPV4_ONLY=true ./scripts/domain/check-propagation.sh karimi.me`


**Fail-Closed Hinweis:** Fehlt `visibility`, wird eine Seite als `private` behandelt und nicht in `out/public`/Group-Outputs übernommen.

Struktur-Fallback: `_index.md` für Sections wird im gefilterten Build automatisch mitgenommen, wenn darunter öffentliche Seiten enthalten sind (damit `/politik/` etc. nicht 404 laufen).


Hinweis Iteration 5 Basis: `/private/` und `/g/<group>/` sind jetzt geroutet und mit `X-Robots-Tag: noindex` markiert. Auth folgt in der nächsten Iteration.

Hinweis Gateway: Public/Group/Private nutzen strikt statische Pfadauflösung mit Trailing-Slash-Normalisierung (`$clean_uri` + `try_files $clean_uri $clean_uri/ $clean_uri/index.html =404`), damit Pretty-URLs robust funktionieren und defekte Links nicht still zur Startseite zurückfallen.

Explizite MOC-Routen (`/politik/`, `/technik/`, `/reisen/`, `/politik/dossier-iran/`) sind im Gateway als Pretty-URL-Guards hinterlegt.
