# MyGarden

## Iteration 0: Domain-Durchstich (Gateway + Hello)

Lokaler Test des Gateway-Reverse-Proxys mit statischer Hello-Seite.

1. Gateway starten + prüfen: `./scripts/gateway/restart.sh`
2. Optionaler Smoke-Test: `./scripts/smoke.sh`
3. Browser: `http://localhost:1234/` (Hello-Seite) und `http://localhost:1234/healthz`
4. Für Domain-Zugriff `karimi.me`: siehe [docs/domain-routing.md](docs/domain-routing.md)

Nginx-Konfiguration liegt unter `infra/nginx/`, statische Ausgabe unter `out/public/`.

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
