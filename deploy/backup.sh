#!/usr/bin/env bash
# Бэкап БД (pg_dump) + media. Запуск по cron. Хранит последние KEEP архивов каждого вида.
# Установка cron (ежедневно в 3:30):
#   sudo crontab -e
#   30 3 * * * /opt/shop/deploy/backup.sh >> /opt/shop/backups/backup.log 2>&1
set -euo pipefail

APP_DIR=/opt/shop
BACKUP_DIR="$APP_DIR/backups"
KEEP=14
TS=$(date +%Y%m%d_%H%M%S)

# Берём DATABASE_URL из .env приложения (pg_dump понимает URL-строку через libpq)
export "$(grep -E '^DATABASE_URL=' "$APP_DIR/.env")"

mkdir -p "$BACKUP_DIR"

# Дамп БД
pg_dump "$DATABASE_URL" | gzip > "$BACKUP_DIR/db_$TS.sql.gz"

# Архив загруженных файлов
tar -czf "$BACKUP_DIR/media_$TS.tar.gz" -C "$APP_DIR" media

# Ротация: оставить только KEEP последних
ls -1t "$BACKUP_DIR"/db_*.sql.gz    2>/dev/null | tail -n +$((KEEP + 1)) | xargs -r rm -f
ls -1t "$BACKUP_DIR"/media_*.tar.gz 2>/dev/null | tail -n +$((KEEP + 1)) | xargs -r rm -f

echo "[$(date)] backup ok: db_$TS.sql.gz, media_$TS.tar.gz"
