# Session 009 — 2026-05-31 — НАСТОЯЩАЯ причина «нет фото в баннерах»: блокировщик рекламы
← [session 008](./session_008_2026-05-31_banner-fix-polish.md)

## Session Intent
Добить проблему «фото в баннерах не видно». В s008 я думал, дело в background:url в карусели —
ОКАЗАЛОСЬ НЕ ТАК.

## Root cause (по скриншоту DevTools пользователя)
Network показал `/media/banners/*.jpg` → **(blocked:other), 0 B**. Это **блокировщик рекламы**
режет всё со словом «banner» в пути (и прячет элементы с «banner» в id/class). Категории в
`/media/categories/` не блокируются — поэтому «категории видно, баннеры нет». Файлы валидны,
по curl 200 — блок на стороне браузера. См. insight_2026-05-31_adblock-banner-path.

## Fix
- Banner.image upload_to 'banners/' → 'promo/' (миграция 0006_alter_banner_image).
- Перенёс существующие файлы media/banners/* → media/promo/* и обновил Banner.image пути в БД (2 шт).
- index.html: id bannerCarousel→promoCarousel, цикл banner→promo, alt/тексты.
- theme.css: .banner-slide(__cap)→.promo-slide(__cap).
- Имя модели Banner (Python/админка) не трогал — в HTML не попадает.

## What works now (with evidence)
- `check` → no issues; `test store` → 11/11 OK.
- HTML главной: `/media/promo/...`, promoCarousel, promo-slide; слова «banner» в HTML НЕТ (grep пусто).
- `/media/promo/podushki-3_ik3sHKi.jpg` → 200.

## Files changed
- `store/models.py` (upload_to), `store/migrations/0006_alter_banner_image.py` (НОВАЯ),
  `store/templates/store/index.html`, `store/static/store/theme.css`. + перенос медиа-файлов + правка путей в БД.

## Note / correction to s008
s008 предполагал причину в background:url — это было неверно (хотя переход на <img> сам по себе ок).
Истинная причина — ad-blocker на пути «banners». Запись исправлена этим session + insight.

## End state
Фото баннеров грузятся (нет слова «banner» в HTML). Осталось: пользователю Ctrl+Shift+R.
Старые осиротевшие файлы в media/banners/ (без суффикса) можно удалить вручную — не критично.

## Session Intent check
Достигнут — найдена и устранена истинная причина.
