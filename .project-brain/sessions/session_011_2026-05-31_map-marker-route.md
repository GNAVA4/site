# Session 011 — 2026-05-31 — точная метка на карте + кнопка маршрута
← [session 010](./session_010_2026-05-31_spacing-yandexmap.md)

## Session Intent
Текстовый поиск Яндекса показывал «окрестность» без точной метки. Нужны: точная метка по
координатам + кнопка «Проложить маршрут».

## Changes
| Изменение | Source |
|-----------|--------|
| SiteSettings.map_lat/map_lon (CharField, чтобы точка-разделитель не ломалась ru-локалью); миграция 0007 | [user] |
| Координаты сохранены: 55.616066 / 37.482762 | [user] |
| contacts.html: карта по ll=lon,lat&z=17 + pt=lon,lat,pm2rdm (точная метка); если координат нет — текстовый поиск | [user] |
| Кнопка «Проложить маршрут» → yandex.ru/maps/?rtext=~lat,lon&rtt=auto (от геолокации пользователя) | [user] |

## Gotcha
Яндекс map-widget ll/pt принимают порядок ДОЛГОТА,ШИРОТА (lon,lat); а /maps/?rtext — ШИРОТА,ДОЛГОТА (lat,lon).
Координаты в БД хранятся строками, чтобы ru-локаль не подставила запятую в URL.

## What works now (with evidence)
- `check` → no issues; `test store` → 11/11 OK.
- /contacts/: iframe ll=37.482762,55.616066&z=17&pt=...pm2rdm; кнопка rtext=~55.616066,37.482762&rtt=auto.

## Files changed
- `store/models.py` (+map_lat/map_lon), `store/admin.py` (поля в fieldset),
  `store/templates/store/contacts.html` (точная метка + кнопка маршрута),
  `store/migrations/0007_...py` (НОВАЯ). БД: координаты сохранены.

## Session Intent check
Достигнут.
