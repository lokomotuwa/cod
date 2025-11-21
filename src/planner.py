from calendar import day_name
from typing import Dict, List


DAYS = [day for day in day_name]


def build_weekly_plan(recipe_ids: List[int]) -> Dict[str, List[int]]:
    if not recipe_ids:
        return {day: [] for day in DAYS}
    plan: Dict[str, List[int]] = {}
    for index, day in enumerate(DAYS):
        plan[day] = [recipe_ids[index % len(recipe_ids)]]
    return plan
