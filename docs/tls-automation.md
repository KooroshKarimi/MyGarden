# TLS Automation (Iteration 1)

Dieses Setup automatisiert Let's Encrypt Zertifikate per DNS‑01 (IONOS) und deployt sie in DSM.

## Voraussetzungen

* Domain bei IONOS verwaltet.
* IONOS DNS API Zugangsdaten (`IONOS_PREFIX` + `IONOS_SECRET`).
* DSM Benutzer mit Berechtigung, Zertifikate zu verwalten.

## Einrichtung

1. `.env` anlegen (siehe `.env.example`).
2. Ersteinrichtung ausführen:

```bash
EMAIL=you@example.com ./scripts/acme/issue.sh
```

3. Renewal (manuell oder per Cron):

```bash
./scripts/acme/renew.sh
```

## Hinweise

* Das Zertifikat wird via `synology_dsm` deploy-hook in DSM importiert.
* `ACME_SERVER` kann auf `letsencrypt` (default) oder `letsencrypt_test` gesetzt werden.


## Troubleshooting

* Wenn acme.sh nach `IONOS_PREFIX`/`IONOS_SECRET` fragt, sind die Variablen in `.env` falsch benannt.
* Wenn statt Let's Encrypt `ZeroSSL` verwendet wird, `ACME_SERVER=letsencrypt` in `.env` setzen (Default) oder im Skript übergeben lassen.
