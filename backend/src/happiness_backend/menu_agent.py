import re
from dataclasses import dataclass


@dataclass(frozen=True)
class MenuIntent:
    budget_max: int | None
    budget_min: int | None
    sections: set[str]
    categories: set[str]
    terms: list[str]
    wants_popular: bool
    wants_cheap: bool


def answer_menu_question(question: str, locale: str, items: list[dict]) -> dict:
    intent = _extract_intent(question)
    candidates = _filter_by_price(items, intent)
    scored_items = []

    for item in candidates:
        score = _score_item(item, intent)
        if score > 0:
            scored_items.append((score, item))

    if not scored_items:
        scored_items = _fallback_items(candidates or items, intent)

    recommendations = [
        _format_recommendation(item, locale, intent)
        for _, item in _rank_items(scored_items, intent)[:3]
    ]

    return {
        "answer": _build_answer(locale, intent, recommendations),
        "recommendations": recommendations,
    }


def _extract_intent(question: str) -> MenuIntent:
    normalized = question.casefold().replace("ё", "е")
    words = _extract_words(normalized)
    budget_max, budget_min = _extract_budget(normalized)
    sections: set[str] = set()
    categories: set[str] = set()
    terms: list[str] = []

    section_aliases = {
        "drinks": {"drink", "drinks", "beverage", "beverages", "напиток", "напитки", "пить", "попить"},
        "food": {"food", "eat", "meal", "lunch", "dinner", "еда", "еды", "еду", "поесть", "обед", "ужин"},
        "sushi": {"sushi", "roll", "rolls", "set", "sets", "суши", "ролл", "роллы", "сет", "сеты"},
    }
    category_aliases = {
        "breakfast": {"breakfast", "завтрак", "завтраки", "омлет", "waffle", "waffles", "вафли"},
        "pizza": {"pizza", "пицца", "пепперони"},
        "burgers": {"burger", "burgers", "бургер", "бургеры", "gyros", "гирос"},
        "shawarma": {"shawarma", "шаурма", "шаверма"},
        "snacks": {"snack", "snacks", "fries", "nuggets", "снек", "снеки", "снеков", "фри", "наггетсы", "картошка"},
        "salads": {"salad", "salads", "салат", "салаты", "салатов", "цезарь"},
        "hot and soups": {"soup", "soups", "hot", "суп", "супы", "горячее", "горячий"},
        "poke": {"poke", "поке"},
        "wok": {"wok", "вок", "лапша"},
        "coffee": {"coffee", "latte", "cappuccino", "americano", "raf", "кофе", "латте", "капучино", "американо", "раф"},
        "tea": {"tea", "чай"},
        "cold bar": {
            "water",
            "lemonade",
            "smoothie",
            "juice",
            "iced",
            "cold",
            "вода",
            "лимонад",
            "смузи",
            "сок",
            "холодный",
            "холодное",
        },
        "seasonal": {"seasonal", "winter", "summer", "сезон", "сезонное", "зимнее", "летнее"},
        "rolls": {"roll", "rolls", "ролл", "роллы"},
        "sets": {"set", "sets", "ассорти", "сет", "сеты"},
    }

    for word in words:
        for section, aliases in section_aliases.items():
            if word in aliases:
                sections.add(section)
        for category, aliases in category_aliases.items():
            if word in aliases:
                categories.add(category)

    if categories & {"coffee", "tea", "cold bar", "seasonal"}:
        sections.add("drinks")
    if categories & {"rolls", "sets"}:
        sections.add("sushi")
    if categories & {"breakfast", "pizza", "burgers", "shawarma", "snacks", "salads", "hot and soups", "poke", "wok"}:
        sections.add("food")

    stopwords = {
        "what",
        "which",
        "can",
        "get",
        "give",
        "recommend",
        "something",
        "please",
        "under",
        "within",
        "rub",
        "rubles",
        "ruble",
        "что",
        "чего",
        "можно",
        "мне",
        "посоветуй",
        "порекомендуй",
        "взять",
        "заказать",
        "до",
        "руб",
        "рублей",
        "рубля",
        "есть",
        "из",
        "для",
        "хочу",
    }
    for word in words:
        if len(word) < 3 or word in stopwords:
            continue
        if word not in terms:
            terms.append(word)

    return MenuIntent(
        budget_max=budget_max,
        budget_min=budget_min,
        sections=sections,
        categories=categories,
        terms=terms[:8],
        wants_popular=any(word in words for word in {"popular", "best", "топ", "популярное", "популярный", "лучшее"}),
        wants_cheap=any(word in words for word in {"cheap", "cheaper", "budget", "дешево", "дешевле", "недорого", "бюджетно"}),
    )


def _extract_words(normalized_question: str) -> list[str]:
    return re.findall(r"[a-zA-Zа-яА-Я]+", normalized_question)


def _extract_budget(normalized_question: str) -> tuple[int | None, int | None]:
    numbers = [int(match) for match in re.findall(r"\b\d{2,5}\b", normalized_question)]
    sensible_numbers = [number for number in numbers if 50 <= number <= 10000]
    if not sensible_numbers:
        return None, None

    value = min(sensible_numbers)
    if re.search(r"\b(from|over|above|more than|от|дороже|больше)\b", normalized_question):
        return None, value
    return value, None


def _filter_by_price(items: list[dict], intent: MenuIntent) -> list[dict]:
    filtered = items
    if intent.budget_max is not None:
        filtered = [item for item in filtered if item["price_rub"] <= intent.budget_max]
    if intent.budget_min is not None:
        filtered = [item for item in filtered if item["price_rub"] >= intent.budget_min]
    return filtered


def _score_item(item: dict, intent: MenuIntent) -> int:
    score = 0
    section_id = item.get("section_id", "").casefold()
    haystack = _item_haystack(item)

    if intent.sections:
        if section_id in intent.sections:
            score += 35
        else:
            score -= 40

    if intent.categories:
        if _category_matches(item, intent.categories):
            score += 55
        else:
            return 0

    for term in intent.terms:
        if term in haystack:
            score += 8

    if intent.wants_popular and item["is_popular"]:
        score += 12
    elif item["is_popular"]:
        score += 2

    if intent.budget_max is not None:
        score += max(0, 8 - item["price_rub"] // 200)
    if intent.wants_cheap:
        score += max(0, 10 - item["price_rub"] // 100)

    return score


def _item_haystack(item: dict) -> str:
    keywords = item.get("keywords") or []
    return " ".join(
        [
            item["name"],
            item["description"],
            item["category_label"],
            item["section_label"],
            item.get("category", ""),
            item.get("section_id", ""),
            " ".join(str(keyword) for keyword in keywords),
        ]
    ).casefold().replace("ё", "е")


def _fallback_items(items: list[dict], intent: MenuIntent) -> list[tuple[int, dict]]:
    scoped_items = [
        item
        for item in items
        if (not intent.sections or item.get("section_id", "").casefold() in intent.sections)
        and (not intent.categories or _category_matches(item, intent.categories))
    ]
    fallback_source = scoped_items or items
    return [
        (1, item)
        for item in sorted(
            fallback_source,
            key=lambda item: (not item["is_popular"], item["price_rub"]),
        )[:5]
    ]


def _rank_items(scored_items: list[tuple[int, dict]], intent: MenuIntent) -> list[tuple[int, dict]]:
    if intent.wants_cheap or intent.budget_max is not None:
        return sorted(scored_items, key=lambda pair: (-pair[0], pair[1]["price_rub"]))
    if intent.wants_popular:
        return sorted(scored_items, key=lambda pair: (-pair[0], not pair[1]["is_popular"], pair[1]["price_rub"]))
    return sorted(scored_items, key=lambda pair: (-pair[0], pair[1]["price_rub"]))


def _format_recommendation(item: dict, locale: str, intent: MenuIntent) -> dict:
    reason_parts = []
    if intent.categories and _category_matches(item, intent.categories):
        reason_parts.append("right category" if locale == "en" else "нужная категория")
    elif intent.sections and item.get("section_id", "").casefold() in intent.sections:
        reason_parts.append("right section" if locale == "en" else "нужный раздел")

    if intent.budget_max is not None:
        reason_parts.append(f"under {intent.budget_max} RUB" if locale == "en" else f"до {intent.budget_max} RUB")
    if intent.budget_min is not None:
        reason_parts.append(f"from {intent.budget_min} RUB" if locale == "en" else f"от {intent.budget_min} RUB")
    if intent.wants_popular and item["is_popular"]:
        reason_parts.append("popular pick" if locale == "en" else "популярная позиция")
    if not reason_parts:
        reason_parts.append("good match from the live menu" if locale == "en" else "подходящий вариант из актуального меню")

    return {
        "id": item["id"],
        "name": item["name"],
        "category_label": item["category_label"],
        "price_rub": item["price_rub"],
        "reason": ", ".join(reason_parts),
    }


def _build_answer(locale: str, intent: MenuIntent, recommendations: list[dict]) -> str:
    if not recommendations:
        return (
            "I could not find a suitable option in the current menu. Try adding a category or budget."
            if locale == "en"
            else "Я не нашёл подходящих вариантов в текущем меню. Попробуй указать категорию или бюджет."
        )

    if locale == "en":
        details = _english_details(intent)
        return f"I found {len(recommendations)} suitable option(s){details} from the live menu."

    details = _russian_details(intent)
    return f"Я подобрал {len(recommendations)} подходящ{_ru_option_suffix(len(recommendations))}{details} по актуальному меню."


def _category_matches(item: dict, categories: set[str]) -> bool:
    keywords = item.get("keywords") or []
    haystack = " ".join(
        [
            item["name"],
            item["category_label"],
            item.get("category", ""),
            " ".join(str(keyword) for keyword in keywords),
        ]
    ).casefold().replace("ё", "е")
    category_matchers = {
        "breakfast": {"breakfast", "завтрак", "завтраки", "омлет", "вафли"},
        "pizza": {"pizza", "пицца"},
        "burgers": {"burger", "burgers", "бургер", "бургеры", "гирос", "gyros"},
        "shawarma": {"shawarma", "шаурма", "шаверма"},
        "snacks": {"snack", "snacks", "снек", "снеки", "фри", "наггетсы", "картошка"},
        "salads": {"salad", "salads", "салат", "салаты", "цезарь"},
        "hot and soups": {"soup", "soups", "hot", "суп", "супы", "горячее"},
        "poke": {"poke", "поке"},
        "wok": {"wok", "вок", "лапша"},
        "coffee": {"coffee", "кофе", "латте", "капучино", "американо", "раф"},
        "tea": {"tea", "чай"},
        "cold bar": {"cold bar", "water", "lemonade", "smoothie", "juice", "вода", "лимонад", "смузи", "сок"},
        "seasonal": {"seasonal", "сезон", "сезонное"},
        "rolls": {"roll", "rolls", "ролл", "роллы"},
        "sets": {"set", "sets", "ассорти", "сет", "сеты"},
    }
    for category in categories:
        if category in haystack:
            return True
        if any(alias in haystack for alias in category_matchers.get(category, set())):
            return True
    return False


def _english_details(intent: MenuIntent) -> str:
    details = []
    if intent.categories:
        details.append("in the requested category")
    elif intent.sections:
        details.append("in the requested section")
    if intent.budget_max is not None:
        details.append(f"within {intent.budget_max} RUB")
    if intent.budget_min is not None:
        details.append(f"from {intent.budget_min} RUB")
    if not details:
        return ""
    return " " + " and ".join(details)


def _russian_details(intent: MenuIntent) -> str:
    details = []
    if intent.categories:
        details.append("в нужной категории")
    elif intent.sections:
        details.append("в нужном разделе")
    if intent.budget_max is not None:
        details.append(f"до {intent.budget_max} RUB")
    if intent.budget_min is not None:
        details.append(f"от {intent.budget_min} RUB")
    if not details:
        return ""
    return " " + " и ".join(details)


def _ru_option_suffix(count: int) -> str:
    if count == 1:
        return "ий вариант"
    return "их варианта"
