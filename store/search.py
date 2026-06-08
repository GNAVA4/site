"""Поиск по товарам — на стороне Python, а НЕ в SQL. Осознанное решение (session 026).

Почему не ORM/SQL:
- SQLite `LIKE`/`icontains` и `lower()` регистронезависимы только для латиницы — кириллица
  «Матрас»≠«матрас». `str.lower()` в Python — полный Unicode, поэтому регистр нормализуем здесь.
- Нужны опечатки/близкие суффиксы («матрос»→«матрас», «матрасы»→«матрас») — это расстояние
  Левенштейна (считаем через rapidfuzz, C-реализация с ранним отсечением), которого в SQLite нет.

Масштаб: O(товаров × слов) в памяти — нормально для сотен товаров этого магазина. Когда проект
переедет на Postgres (см. OPEN.md, прод-подготовка) — масштабируемый путь: pg_trgm (нечёткость
с GIN-индексом) + SearchVector со стеммингом русского для морфологии. Тогда этот модуль заменится.

Алгоритм:
1. Запрос и поля товара нормализуем (.lower()) и режем на слова.
2. Слово запроса совпало с полем, если оно ПОДСТРОКА поля ИЛИ близко по Левенштейну к какому-то
   слову поля. Точная подстрока ценится выше нечёткого совпадения.
3. Вес поля: название > категория > описание.
4. Результат — товары, где совпали ВСЕ слова запроса (AND), по убыванию релевантности.
   Если таких нет — отдаём «похожие» (совпало хотя бы одно слово, OR), чтобы не было пустой страницы.
"""

import re

from rapidfuzz.distance import Levenshtein

from .models import Product

# ── Настройки релевантности (tunable magic values; задокументировано в DATA.md) ──
FIELD_WEIGHTS = {'title': 3, 'category': 2, 'description': 1}
EXACT_BONUS = 2        # точная подстрока ценится вдвое выше нечёткого совпадения
MIN_TOKEN_LEN = 2      # запросы/слова короче — игнорируем (1 буква = шум)
MAX_TOKENS = 8         # защита от слишком длинного запроса
MIN_FUZZY_LEN = 4      # фуззи только для слов от 4 букв (короче — слишком много ложных)

# Порог «умеренный» (выбор пользователя, session 026): ≤1 правка для слов 4–6 букв, ≤2 для 7+.
_FUZZY_LONG_LEN = 7

_WORD_RE = re.compile(r'\w+', re.UNICODE)


def _norm(text):
    return (text or '').lower()


def _words(text):
    return _WORD_RE.findall(_norm(text))


def _max_dist(token):
    """Допустимое расстояние Левенштейна для слова данной длины (0 = фуззи выключено)."""
    n = len(token)
    if n < MIN_FUZZY_LEN:
        return 0
    return 1 if n < _FUZZY_LONG_LEN else 2


def _token_field_score(token, field_text, field_words):
    """Вклад одного слова запроса по одному полю товара:
    EXACT_BONUS — точная подстрока, 1 — нечёткое совпадение, 0 — нет."""
    if token in field_text:
        return EXACT_BONUS
    max_dist = _max_dist(token)
    if max_dist:
        for w in field_words:
            # score_cutoff: rapidfuzz прекращает счёт, как только расстояние превысит порог.
            if Levenshtein.distance(token, w, score_cutoff=max_dist) <= max_dist:
                return 1
    return 0


def _score_product(tokens, fields):
    """fields: {имя_поля: (нормализованный_текст, [слова])}.
    Возвращает (суммарный_балл, сколько_слов_запроса_совпало)."""
    total = 0
    matched = 0
    for token in tokens:
        best = 0
        for name, weight in FIELD_WEIGHTS.items():
            text, words = fields[name]
            s = _token_field_score(token, text, words)
            if s:
                best = max(best, weight * s)
        if best:
            matched += 1
            total += best
    return total, matched


def search_products(query):
    """Главная точка входа. Возвращает (results, suggestions):
    - results     — совпали ВСЕ слова запроса (по релевантности);
    - suggestions — «может подойдёт» (совпало хотя бы одно слово), НЕпусто только если results пуст.
    """
    tokens = [t for t in _words(query) if len(t) >= MIN_TOKEN_LEN][:MAX_TOKENS]
    if not tokens:
        return [], []

    products = (
        Product.objects.filter(is_active=True)
        .select_related('category')
        .prefetch_related('sizes')
    )

    scored = []  # (score, matched, -is_hit, -views, -pk, product) — для сортировки по релевантности
    for p in products:
        fields = {
            'title': (_norm(p.title), _words(p.title)),
            'category': (_norm(p.category.name), _words(p.category.name)),
            'description': (_norm(p.description), _words(p.description)),
        }
        score, matched = _score_product(tokens, fields)
        if matched:
            scored.append((score, matched, p))

    scored.sort(key=lambda x: (-x[0], -int(x[2].is_hit), -x[2].views, -x[2].pk))

    full = [p for score, matched, p in scored if matched == len(tokens)]
    if full:
        return full, []
    return [], [p for score, matched, p in scored]
