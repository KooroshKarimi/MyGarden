# MyGarden

## Iteration 1: TLS Automation

Dieses Repo enthält die Basis für die TLS‑Automation per DNS‑01 (IONOS) und Deployment nach Synology DSM.

* Konfiguration: `.env` aus `.env.example` ableiten (`IONOS_PREFIX`/`IONOS_SECRET` und `SYNO_HOSTNAME` etc. setzen).
* Setup/Issue: `EMAIL=you@example.com ./scripts/acme/issue.sh`
* Renewal: `./scripts/acme/renew.sh`

Details: siehe [docs/tls-automation.md](docs/tls-automation.md).


Hinweis: Falls du noch alte `.env`-Namen (`SYNO_DSM_HOSTNAME`/`SYNO_DSM_PORT`) nutzt, mappen die Skripte diese automatisch. Empfohlen ist trotzdem die Umstellung auf `SYNO_HOSTNAME`/`SYNO_PORT`.
