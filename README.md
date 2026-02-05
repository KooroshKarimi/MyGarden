# MyGarden

## Iteration 1: TLS Automation

Dieses Repo enthält die Basis für die TLS‑Automation per DNS‑01 (IONOS) und Deployment nach Synology DSM.

* Konfiguration: `.env` aus `.env.example` ableiten (`IONOS_PREFIX`/`IONOS_SECRET` setzen).
* Setup/Issue: `EMAIL=you@example.com ./scripts/acme/issue.sh`
* Renewal: `./scripts/acme/renew.sh`

Details: siehe [docs/tls-automation.md](docs/tls-automation.md).
