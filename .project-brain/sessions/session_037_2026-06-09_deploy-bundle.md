# Session 037 — 2026-06-09 — деплой-бандл (nginx/gunicorn/systemd/backup/DEPLOY.md) + ADR 006
← [session 036](./session_036_2026-06-08_sqlite-to-pg-data.md)

## Session Intent
Пользователь выбирает РФ-VPS (смотрел SpaceWeb Cloud Base 2CPU/2ГБ/30ГБ + аналоги). Просил заранее
заготовить деплой-бандл «под типовой Ubuntu-VPS», подтвердить возможность дальнейших правок сайта/данных,
и обновить архитектуру/память.

## Changes (новые файлы, код приложения НЕ менялся)
| Файл | Назначение |
|------|-----------|
| `deploy/gunicorn.service` | systemd-юнит (gunicorn 127.0.0.1:8000, 3 воркера, EnvironmentFile=.env, Restart=always) |
| `deploy/nginx.conf` | реверс-прокси на gunicorn + отдача /static/ и /media/; client_max_body_size 20M; X-Forwarded-Proto |
| `deploy/backup.sh` | pg_dump + tar media, ротация (KEEP=14), для cron |
| `deploy/DEPLOY.md` | пошаговая установка на Ubuntu LTS + раздел «обновление сайта в будущем» |
| `decisions/adr_006_prod-deployment-topology.md` | ADR топологии прода |

## Решение (ADR 006)
Топология прода: 1 Ubuntu-VPS, всё в /opt/shop (юзер shop). nginx → gunicorn(systemd) → Django;
**PostgreSQL нативно (apt), НЕ Docker** (Docker — только dev); HTTPS Let's Encrypt; бэкап-скрипт+cron.
Рекомендация хостинга: РФ-VPS (152-ФЗ) — Timeweb Cloud / VDSina / RuVDS / SpaceWeb, ~2CPU/2-4ГБ/Ubuntu LTS.

## Возможность дальнейших правок (ответ пользователю — да)
- КОД (новые страницы/логика/стили): локально → git push → на сервере `git pull` + (опц.) pip/migrate/
  collectstatic + `systemctl restart shop`. Описано в DEPLOY.md §«Обновление».
- ДАННЫЕ (товары/категории/контент/контакты, удалить/добавить): через админку /admin/ без деплоя.

## Статус
Артефакты готовы и лежат в репо. НЕ развёрнуто — ждёт заказа VPS. После заказа пользователь присылает:
провайдер/ОС, IP, домен (+A-запись), вариант A (я даю команды) или B (SSH-доступ мне). Опц.: реквизиты ИП
для /privacy/, SMTP.

## Evidence / проверка
Конфиги статические (не исполнялись локально — это серверные артефакты под Linux). Проверка — при
реальном деплое (`nginx -t`, `systemctl status shop`, открытие домена). Зафиксировать как pending до деплоя.

## Session Intent check
Достигнут: бандл готов, возможность правок подтверждена и задокументирована, память/архитектура обновлены.
