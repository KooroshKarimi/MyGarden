# MyGarden

## Iteration 1: TLS Automation

Dieses Repo enthält die Basis für die TLS‑Automation per DNS‑01 (IONOS) und Deployment nach Synology DSM.

* Konfiguration: `.env` aus `.env.example` ableiten.
* Setup/Issue: `EMAIL=you@example.com ./scripts/acme/issue.sh`
* Renewal: `./scripts/acme/renew.sh`

Details: siehe [docs/tls-automation.md](docs/tls-automation.md).

## Iteration 2: Static Site Pipeline (Public)

Die Public‑Ausgabe wird mit Hugo aus `site/` nach `out/public` gebaut.

* Build lokal (Hugo installiert): `./scripts/build_public.sh`
* Build via Docker (falls Hugo nicht installiert ist): `./scripts/build_public.sh`

Die Example‑Navigation und ein Beispiel‑Beitrag liegen unter `site/content/`.
