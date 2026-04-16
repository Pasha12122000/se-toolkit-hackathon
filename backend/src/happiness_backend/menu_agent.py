import re


def answer_menu_question(question: str, locale: str, items: list[dict]) -> dict:
    budget = _extract_budget(question)
    tokens = _extract_tokens(question)
    scored_items = []

    for item in items:
        score = _score_item(item, tokens, budget)
        if budget is not None and item["price_rub"] > budget:
            continue
        if score > 0:
            scored_items.append((score, item))

    if not scored_items:
        fallback_items = sorted(
            items,
            key=lambda item: (not item["is_popular"], item["price_rub"]),
        )
        if budget is not None:
            fallback_items = [item for item in fallback_items if item["price_rub"] <= budget]
        scored_items = [(1, item) for item in fallback_items[:3]]

    recommendations = [
        _format_recommendation(item, locale, tokens, budget)
        for _, item in sorted(scored_items, key=lambda pair: (-pair[0], pair[1]["price_rub"]))[:3]
    ]

    return {
        "answer": _build_answer(question, locale, budget, recommendations),
        "recommendations": recommendations,
    }


def _extract_budget(question: str) -> int | None:
    normalized = question.replace(",", " ")
    numbers = [int(match) for match in re.findall(r"\b\d{2,5}\b", normalized)]
    sensible_numbers = [number for number in numbers if 50 <= number <= 10000]
    return min(sensible_numbers) if sensible_numbers else None


def _extract_tokens(question: str) -> list[str]:
    aliases = {
        "coffee": "кофе",
        "latte": "латте",
        "tea": "чай",
        "drink": "напиток",
        "drinks": "напиток",
        "water": "вода",
        "food": "еда",
        "shawarma": "шаурма",
        "burger": "бургер",
        "salad": "салат",
        "sushi": "суши",
        "roll": "ролл",
        "sweet": "сладкое",
        "dessert": "десерт",
        "breakfast": "завтрак",
    }
    raw_tokens = re.findall(r"[a-zA-Zа-яА-ЯёЁ]+", question.casefold())
    tokens: list[str] = []
    for token in raw_tokens:
        normalized = aliases.get(token, token)
        if len(normalized) < 3:
            continue
        if normalized not in tokens:
            tokens.append(normalized)
    return tokens


def _score_item(item: dict, tokens: list[str], budget: int | None) -> int:
    haystack = " ".join(
        [
            item["name"],
            item["description"],
            item["category_label"],
            item["section_label"],
        ]
    ).casefold()
    score = 0
    for token in tokens:
        if token in haystack:
            score += 4
    if item["is_popular"]:
        score += 2
    if budget is not None and item["price_rub"] <= budget:
        score += 1
    return score


def _format_recommendation(item: dict, locale: str, tokens: list[str], budget: int | None) -> dict:
    reason_parts = []
    haystack = f"{item['name']} {item['description']} {item['category_label']}".casefold()
    if any(token in haystack for token in tokens):
        reason_parts.append("matches your request" if locale == "en" else "подходит под запрос")
    if budget is not None and item["price_rub"] <= budget:
        reason_parts.append(f"under {budget} RUB" if locale == "en" else f"до {budget} RUB")
    if item["is_popular"]:
        reason_parts.append("popular pick" if locale == "en" else "популярная позиция")
    if not reason_parts:
        reason_parts.append("good menu option" if locale == "en" else "хороший вариант из меню")

    return {
        "id": item["id"],
        "name": item["name"],
        "category_label": item["category_label"],
        "price_rub": item["price_rub"],
        "reason": ", ".join(reason_parts),
    }


def _build_answer(question: str, locale: str, budget: int | None, recommendations: list[dict]) -> str:
    if not recommendations:
        return (
            "I could not find a suitable option in the current menu."
            if locale == "en"
            else "Я не нашёл подходящих вариантов в текущем меню."
        )

    if locale == "en":
        if budget is not None:
            return f"I found {len(recommendations)} option(s) within {budget} RUB based on the live menu."
        return f"I found {len(recommendations)} suitable option(s) based on the live menu."

    if budget is not None:
        return f"Я нашёл {len(recommendations)} вариант(а) до {budget} RUB по актуальному меню."
    return f"Я подобрал {len(recommendations)} вариант(а) по актуальному меню."

