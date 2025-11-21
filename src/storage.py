import json
from pathlib import Path
from typing import Dict, List, Any


class Storage:
    """Simple JSON-backed storage for recipes and weekly plans."""

    def __init__(self, base_path: Path | str = "data/state.json") -> None:
        self.path = Path(base_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._write({"recipes": [], "plan": {}})

    def _read(self) -> Dict[str, Any]:
        with self.path.open("r", encoding="utf-8") as file:
            return json.load(file)

    def _write(self, data: Dict[str, Any]) -> None:
        with self.path.open("w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)

    def list_recipes(self) -> List[Dict[str, Any]]:
        return self._read()["recipes"]

    def save_recipe(self, recipe: Dict[str, Any]) -> Dict[str, Any]:
        data = self._read()
        recipe_id = recipe.get("id") or (max([r["id"] for r in data["recipes"]] + [0]) + 1)
        recipe["id"] = recipe_id
        data["recipes"].append(recipe)
        self._write(data)
        return recipe

    def save_plan(self, plan: Dict[str, List[int]]) -> None:
        data = self._read()
        data["plan"] = plan
        self._write(data)

    def load_plan(self) -> Dict[str, List[int]]:
        return self._read().get("plan", {})

    def get_recipes_by_ids(self, recipe_ids: List[int]) -> List[Dict[str, Any]]:
        recipes = self.list_recipes()
        lookup = {r["id"]: r for r in recipes}
        return [lookup[rid] for rid in recipe_ids if rid in lookup]
