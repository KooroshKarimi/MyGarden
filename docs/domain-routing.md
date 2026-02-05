# Domain Routing (karimi.me -> Gateway)

Ziel: `karimi.me` soll über DSM Reverse Proxy auf den Gateway-Container gehen.

## 1) Gateway starten (ohne ACME-Container)

```bash
./scripts/gateway/restart.sh
```

Das Skript startet nur den `gateway` Service und prüft `GET /` + `GET /healthz` auf HTTP 200.

## 2) DSM Reverse Proxy Regel

In DSM unter **Systemsteuerung -> Anmeldeportal -> Erweitert -> Reverse Proxy**:

* **Source**
  * Protokoll: `HTTPS`
  * Hostname: `karimi.me`
  * Port: `443`
* **Destination**
  * Protokoll: `HTTP`
  * Hostname/IP: `192.168.188.42`
  * Port: `1234`

(Optional: temporär `Host`/Ziel-IP an deine NAS-IP anpassen.)


## 2a) IONOS DNS automatisch per API setzen

Mit den Werten aus `.env` (`IONOS_PREFIX`, `IONOS_SECRET`) kannst du die Apex-Records automatisiert auf die IPs von `koorosh.synology.me` synchronisieren:

```bash
./scripts/domain/sync-ionos-dns.py
```

Das Skript:

* liest `DOMAIN` (default `karimi.me`) und `TARGET_HOSTNAME` (default `koorosh.synology.me`)
* resolved A/AAAA des Target-Hostnamens
* erstellt/aktualisiert die passenden Apex-Records in IONOS und entfernt veraltete Werte
* toleriert `RECORD_NOT_FOUND` beim Aufräumen veralteter Records (idempotenter Lauf)

## 3) DSM Zertifikat korrekt zuweisen (wichtig für SSL_ERROR_INTERNAL_ERROR_ALERT)

In DSM unter **Systemsteuerung -> Sicherheit -> Zertifikat -> Konfigurieren**:

* Das Let's Encrypt Zertifikat für `karimi.me` muss dem Reverse-Proxy/Virtual-Host für `karimi.me:443` zugewiesen sein.
* Wenn hier noch das Default-/abgelaufene Zertifikat hängt, kann es zu TLS-Handshake-Fehlern wie `SSL_ERROR_INTERNAL_ERROR_ALERT` kommen.

## 4) Domain Check

Nach dem Speichern prüfen:

```bash
curl -I https://karimi.me/
curl -I https://karimi.me/healthz
```

Erwartung: HTTP `200`.

## 5) TLS Diagnose bei Fehlern

```bash
./scripts/domain/diagnose-ssl.sh karimi.me
```

Das Skript zeigt den TLS-Handshake (`openssl s_client`) und Header-Checks (`curl -kI`) an.


## 6) IPv4/IPv6 DNS prüfen (sehr häufige Ursache)

Dein Screenshot zeigt, dass für `@` sowohl ein `A` als auch ein `AAAA` Record existiert.
Browser bevorzugen oft IPv6. Wenn dein IPv6-Pfad (Router/NAS/Reverse Proxy) nicht korrekt offen ist,
kommt es trotz funktionierendem IPv4 zu TLS-Fehlern.

Prüfe separat IPv4/IPv6:

```bash
./scripts/domain/check-dns-path.sh karimi.me
```

Wenn IPv4 funktioniert, aber IPv6 fehlschlägt:

* Bei IONOS den `AAAA` Record für `@` vorübergehend entfernen **oder**
* IPv6 vollständig für NAS/Router/DSM Reverse Proxy korrekt konfigurieren.

## 7) DNS Voraussetzung

Bei IONOS muss `karimi.me` auf deine öffentliche IP zeigen. Falls du intern testest, kann ein lokaler DNS Override nötig sein.
