# TLS Automation (Iteration 1)

Dieses Setup automatisiert Let's Encrypt Zertifikate per DNS‑01 (IONOS) und deployt sie in DSM.

## Voraussetzungen

* Domain bei IONOS verwaltet.
* IONOS DNS API Zugangsdaten (`IONOS_PREFIX` + `IONOS_SECRET`).
* DSM Benutzer mit Berechtigung, Zertifikate zu verwalten.
* DSM Zugriffsdaten für den Deploy-Hook: `SYNO_HOSTNAME`, `SYNO_PORT`, `SYNO_SCHEME`, `SYNO_USERNAME`, `SYNO_PASSWORD`, `SYNO_CERTIFICATE`.

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
* `issue.sh`/`renew.sh` versuchen den Deploy-Schritt auch dann auszuführen, wenn acme.sh wegen "Domains not changed" einen Nicht-0-Code liefert, sofern bereits ein Zertifikat unter `certs/` vorhanden ist.


## Troubleshooting

* Wenn acme.sh nach `IONOS_PREFIX`/`IONOS_SECRET` fragt, sind die Variablen in `.env` falsch benannt.
* Wenn statt Let's Encrypt `ZeroSSL` verwendet wird, `ACME_SERVER=letsencrypt` in `.env` setzen (Default) oder im Skript übergeben lassen.

* Wenn Deploy auf `http://localhost:5000` geht, werden die Synology Variablen nicht erkannt. Nutze `SYNO_HOSTNAME`/`SYNO_PORT`/`SYNO_SCHEME` (nicht `SYNO_DSM_*`).
* Bei aktivem 2FA für DSM User `SYNO_DEVICE_ID` (und optional `SYNO_DEVICE_NAME`) setzen oder dedizierten Zertifikats-User ohne OTP nutzen.
