import argparse
from pprint import pprint
from typing import List

from .planner import DAYS, build_weekly_plan
from .recipe_fetcher import RecipeFetcher
from .shopping_list import aggregate_ingredients
from .storage import Storage


def cmd_fetch(args: argparse.Namespace) -> None:
    storage = Storage(args.state)
    fetcher = RecipeFetcher()
    recipe = fetcher.fetch(args.url)
    saved = storage.save_recipe(recipe)
    print("Zapisano przepis:")
    pprint(saved)


def cmd_list(args: argparse.Namespace) -> None:
    storage = Storage(args.state)
    recipes = storage.list_recipes()
    if not recipes:
        print("Brak zapisanych przepisów.")
        return
    for recipe in recipes:
        print(f"[{recipe['id']}] {recipe['title']} — {recipe['url']}")


def cmd_plan(args: argparse.Namespace) -> None:
    storage = Storage(args.state)
    recipe_ids: List[int] = [int(rid) for rid in args.recipe_ids]
    plan = build_weekly_plan(recipe_ids)
    storage.save_plan(plan)
    print("Zapisano plan tygodniowy:")
    for day, ids in plan.items():
        label = ", ".join(str(rid) for rid in ids) if ids else "brak"
        print(f"- {day}: {label}")


def cmd_show_plan(args: argparse.Namespace) -> None:
    storage = Storage(args.state)
    plan = storage.load_plan()
    if not plan:
        print("Brak zapisanego planu.")
        return
    print("Aktualny plan tygodniowy:")
    for day in DAYS:
        ids = plan.get(day, [])
        label = ", ".join(str(rid) for rid in ids) if ids else "brak"
        print(f"- {day}: {label}")


def cmd_shopping_list(args: argparse.Namespace) -> None:
    storage = Storage(args.state)
    plan = storage.load_plan()
    if not plan:
        print("Brak planu. Najpierw utwórz plan tygodniowy.")
        return
    recipe_ids = [rid for ids in plan.values() for rid in ids]
    recipes = storage.get_recipes_by_ids(recipe_ids)
    shopping_items = aggregate_ingredients(recipes)
    if not shopping_items:
        print("Brak składników do kupienia.")
        return
    print("Lista zakupów:")
    for item in shopping_items:
        print(f"- {item['details']}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Planer posiłków i lista zakupów")
    parser.add_argument("--state", default="data/state.json", help="Ścieżka do pliku ze stanem")
    subparsers = parser.add_subparsers(dest="command", required=True)

    fetch = subparsers.add_parser("fetch", help="Pobierz przepis z internetu i zapisz")
    fetch.add_argument("url", help="Adres URL przepisu")
    fetch.set_defaults(func=cmd_fetch)

    list_recipes = subparsers.add_parser("list", help="Wyświetl zapisane przepisy")
    list_recipes.set_defaults(func=cmd_list)

    plan = subparsers.add_parser("plan", help="Zbuduj plan tygodniowy")
    plan.add_argument("recipe_ids", nargs="+", help="Identyfikatory przepisów")
    plan.set_defaults(func=cmd_plan)

    show_plan = subparsers.add_parser("show-plan", help="Pokaż zapisany plan tygodniowy")
    show_plan.set_defaults(func=cmd_show_plan)

    shopping = subparsers.add_parser("shopping-list", help="Wygeneruj listę zakupów z planu")
    shopping.set_defaults(func=cmd_shopping_list)

    return parser


def main(argv: List[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
