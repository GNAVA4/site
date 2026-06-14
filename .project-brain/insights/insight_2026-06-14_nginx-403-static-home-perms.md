# Insight — nginx 403 на /static/ и /media/: права домашней папки приложения

_2026-06-14 (session 042)_

## Симптом
Сайт открывается, HTML рендерится, но БЕЗ стилей (и сайт, и админка «голые»), фото товаров — битые.
`STATIC_URL=/static/` корректный, ссылки в HTML правильные (хэшированные), файлы в `/opt/shop/staticfiles`
есть, nginx `location /static/ { alias /opt/shop/staticfiles/; }` корректен. Но `curl /static/...css` → **403**.

## Причина
`adduser --system --home /opt/shop shop` создаёт домашнюю папку с правами **750** (`drwxr-x---`).
nginx работает под `www-data` (не в группе `shop`) → не может ПРОЙТИ в `/opt/shop` → 403 на всё вложенное,
включая `staticfiles/` и `media/`. Это права на ПРОХОД (execute) у каталога, а не на сами файлы.

## Фикс
```
chmod 755 /opt/shop                          # сделать папку проходимой для остальных
chmod -R a+rX /opt/shop/staticfiles /opt/shop/media   # чтение статики/медиа всем (это публичные ассеты)
```
После: theme.css/admin css/media → 200. `.env` остаётся защищённым своими правами 600, даже если папка 755.
Новые файлы от `collectstatic` читаемы по умолчанию (umask 022 → 644/755), так что фикс разовый.

## Профилактика
Добавлено в `deploy/DEPLOY.md` §3: `sudo chmod 755 /opt/shop` сразу после создания пользователя/папки.
