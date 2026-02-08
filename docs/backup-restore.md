# Backup & Restore

## Was wird gesichert?

- Authelia: `infra/authelia/db.sqlite3`, `infra/authelia/users_database.yml`
- Remark42 (public): `infra/remark42/`
- Remark42 (private): `infra/remark42-private/`
- FreshRSS: `infra/freshrss/`

## Backup erstellen

```bash
bash scripts/backup.sh
```

Erzeugt `backups/YYYY-MM-DD_HHMMSS.tar.gz`.

## Restore durchführen

```bash
bash scripts/restore.sh backups/<timestamp>.tar.gz
```

Das Script:
1. Stoppt betroffene Container (authelia, remark42, remark42-private, freshrss)
2. Entpackt das Backup (überschreibt bestehende Daten)
3. Startet die Container neu
4. Prüft `/healthz` Endpoint

## Restore-Drill Checkliste

- [ ] Backup-Datei vorhanden und lesbar?
- [ ] `bash scripts/restore.sh backups/<file>.tar.gz` erfolgreich?
- [ ] Healthcheck `/healthz` liefert 200?
- [ ] Authelia Login funktioniert?
- [ ] Remark42 Kommentare sichtbar?
- [ ] FreshRSS Feeds geladen?

## Admin-Navigation

Die Hauptnavigation zeigt zusätzliche Links (Privat, Friends, Family, Reader), wenn der Benutzer als Admin eingeloggt ist.

**Funktionsweise:**
- Ein `<script>` in `baseof.html` ruft `/api/admin-check` auf
- Nginx prüft via `auth_request` + Authelia `access_control` ob der Benutzer zur Gruppe `admins` gehört
- Bei 200 (Admin) werden die Links sichtbar, bei 401/403 bleiben sie versteckt
- Die Gruppe `admins` wird in `infra/authelia/users_database.yml` zugewiesen
- Die Authelia-Regel steht in `infra/authelia/configuration.yml`
