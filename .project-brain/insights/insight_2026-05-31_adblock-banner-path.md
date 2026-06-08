# INSIGHT: блокировщики рекламы режут пути/классы со словом «banner»
_Filed: 2026-05-31 session 009_
_Category: frontend / tooling_

## The finding
Фото баннеров не грузились у пользователя: в DevTools→Network статус **(blocked:other), 0 байт**.
Причина — **блокировщик рекламы** (uBlock/AdBlock) режет запросы, в URL которых есть «banner»/«ad»,
и косметическими фильтрами прячет элементы с такими словами в id/class. Файлы лежали в
`/media/banners/`, id карусели `bannerCarousel`, класс `.banner-slide` → всё блокировалось.
Категории (`/media/categories/`) грузились нормально — отсюда и разница «категории видно, баннеры нет».

## How we found it
Пользователь прислал скриншот Network: оба `/media/banners/*.jpg` → (blocked:other). Файлы при
этом валидны и по curl отдавались 200 (curl без блокировщика). Значит блок на стороне браузера.

## Evidence
curl: 200; браузер: blocked:other. После переноса в `/media/promo/` и переименования
id/классов (promoCarousel/.promo-slide) — слово «banner» исчезло из HTML, запросы не блокируются.

## Action taken
- Banner.image upload_to: 'banners/' → 'promo/' (миграция 0006); существующие файлы перенесены,
  пути в БД обновлены.
- index.html/theme.css: bannerCarousel→promoCarousel, .banner-slide→.promo-slide.
- Имя модели Banner (Python) оставлено — оно не попадает в HTML, не блокируется.

## Applies when
Любые пользовательские медиа/элементы, чьи URL или class/id содержат «banner», «ads», «advert»,
«popup», «sponsor» и т.п. Использовать нейтральные имена (promo, slide, hero, featured).

## Does NOT apply when
У пользователя нет блокировщика. Но закладываться на это нельзя — по умолчанию избегать таких слов.
