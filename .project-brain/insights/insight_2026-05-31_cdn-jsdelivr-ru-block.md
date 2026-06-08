# INSIGHT: jsdelivr/Google Fonts тормозят в РФ → стили «не применяются»
_Filed: 2026-05-31 session 005_
_Category: tooling / frontend_

## The finding
В российских сетях `cdn.jsdelivr.net` и `fonts.googleapis.com` часто блокируются/висят, а
`cdnjs.cloudflare.com` (Cloudflare) работает. Render-blocking `<link>` на Bootstrap с jsdelivr,
который «висит», БЛОКИРУЕТ отрисовку всей страницы — и локальный theme.css визуально тоже не
применяется, хотя сам отдаётся корректно (200, text/css). Симптом: страница без стилей, но
иконки FontAwesome (с cdnjs) при этом видны.

## How we found it
Скриншот пользователя: сайт без вёрстки, но иконки есть. curl показал, что сервер отдаёт всё
правильно (theme.css 200 text/css, head корректный). Различие cdnjs(работает)/jsdelivr(нет).

## Evidence
FontAwesome (cdnjs) применился, Bootstrap (jsdelivr) — нет. Сервер отдаёт оба linked-тега и сам
CSS без ошибок. Значит дело в загрузке внешних CDN в браузере, не в Django.

## Action taken
- Bootstrap CSS+JS переведены с jsdelivr на cdnjs (Cloudflare) 5.3.3.
- Google Fonts грузятся НЕблокирующе: `<link rel=preload as=style onload="this.rel='stylesheet'">`
  + `<noscript>` фолбэк; в theme.css есть system-ui фолбэк шрифтов.

## Applies when
Любой проект с фронтендом для пользователей из РФ/СНГ на внешних CDN. Предпочитать cdnjs/Cloudflare;
критичную статику (Bootstrap) — лучше вообще локально (collectstatic) для прода и оффлайна.

## Does NOT apply when
Аудитория вне зон блокировок, или вся статика самохостится. Тогда выбор CDN не критичен.
