# INSIGHT: SQLite не умеет регистронезависимость/свёртку регистра для кириллицы
_Filed: 2026-06-02 session 026_
_Category: data / search / tooling_

## The finding
В SQLite оператор `LIKE` (→ Django `icontains`) и функция `lower()` (→ Django `Lower()`)
регистронезависимы и сворачивают регистр ТОЛЬКО для ASCII (A–Z). Для кириллицы:
- `'Матрас' LIKE '%матрас%'` → НЕ совпадает.
- `lower('Матрас')` → `'Матрас'` (без изменений).
Поэтому «привести всё к одному регистру средствами SQL» на SQLite для русского текста
не работает — это не про `icontains`, а про сам движок.

## How we found it
Проектируя поиск по товарам (кириллица). Проверка: `Levenshtein.distance('матрас','матрос')`
в Python (rapidfuzz) = 1, тогда как SQLite-фильтр регистр кириллицы игнорировать отказывался.

## Workaround / decision
Нормализуем регистр в **Python** (`str.lower()` — полный Unicode) и ищем на стороне Python
(см. ADR 003). Postgres этой проблемы лишён: `ILIKE` и `lower()` там Unicode-aware.

## Applies when
Любой текстовый поиск/сравнение по кириллице (или другому не-ASCII) на SQLite: фильтры,
уникальность без учёта регистра, сортировка. Не полагаться на `icontains`/`Lower` для свёртки.

## Does NOT apply when
БД — Postgres/MySQL с Unicode-collation, либо данные только латиница. Тогда `icontains`/`ILIKE` ок.
