from collections import defaultdict
from typing import Dict, Iterable, List


def aggregate_ingredients(recipes: Iterable[Dict]) -> List[Dict[str, str]]:
    accumulator: Dict[str, List[str]] = defaultdict(list)
    for recipe in recipes:
        for item in recipe.get("ingredients", []):
            key = item.lower().strip()
            accumulator[key].append(item.strip())
    return [
        {"name": name, "details": "; ".join(sorted(set(values)))}
        for name, values in sorted(accumulator.items())
    ]
