# ADR 006 — Топология прод-развёртывания (Ubuntu VPS: nginx + gunicorn/systemd + нативный Postgres)

_Date: 2026-06-09 (session 037) · Status: active (артефакты готовы, не развёрнуто)_

## Контекст
После Партии 1 (код прод-готов, ADR 005) нужно развернуть на боевом сервере. Пользователь склоняется к
РФ-VPS (152-ФЗ: ПДн клиентов в заказах → дата-центр РФ). Рассматривал SpaceWeb Cloud Base
(2 CPU/2 ГБ/30 ГБ NVMe/Ubuntu LTS) и аналоги (Timeweb Cloud, VDSina, RuVDS). Хостинг финально ещё не заказан.

## Решение
Целевая топология на одном Ubuntu-VPS (всё в `/opt/shop`, пользователь `shop`):
- **nginx** — реверс-прокси на gunicorn (127.0.0.1:8000); сам отдаёт `/static/` (STATIC_ROOT) и
  `/media/` (MEDIA_ROOT); `client_max_body_size 20M` под загрузку фото.
- **gunicorn** под **systemd** (`shop.service`, 3 воркера, EnvironmentFile=/opt/shop/.env, Restart=always).
- **PostgreSQL — нативно (apt)**, НЕ в Docker. Причина: на 2 ГБ VPS нативный Postgres легче; Docker
  оставлен только для локальной разработки (паритет движка сохраняется — везде Postgres, ADR 005).
- **HTTPS** — Let's Encrypt (certbot --nginx), автопродление. Прод-`SECURE_*` уже включаются при DEBUG=False;
  nginx прокидывает `X-Forwarded-Proto` под `SECURE_PROXY_SSL_HEADER`.
- **Бэкапы** — `deploy/backup.sh` (pg_dump + tar media, ротация 14) по cron + опц. снапшоты провайдера.
- Артефакты в репо: `deploy/{gunicorn.service,nginx.conf,backup.sh,DEPLOY.md}`.

## Провенанс
Пользователь (s036/037): просил подготовить деплой-бандл заранее; подтвердил, что важна возможность и далее
менять сайт/данные. Выбор «нативный Postgres на проде, Docker только dev» — баланс простота/ресурсы для 2 ГБ.

## Последствия
- + Стандартная, надёжная схема; обновление = `git pull` + (опц.) migrate/collectstatic + `systemctl restart shop`.
- + Данные правятся через админку без деплоя; код — через git.
- − На сервере gunicorn НЕ запускается на Windows — это нормально (прод = Linux; локально runserver).
- Перенос данных на прод: dumpdata/loaddata (PYTHONUTF8=1 от cp1251) + scp media; для малого каталога —
  можно просто завести через админку. См. insight `dumpdata-cp1251-windows`, DEPLOY.md §7.
- Связано: [[adr_005_postgres-dev-parity]] (БД), DEPLOY.md (исполнение).
