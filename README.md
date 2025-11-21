# Planer przepisów

Prosty skrypt CLI, który pobiera przepisy z internetu, zapisuje je lokalnie, buduje plan żywienia na cały tydzień oraz generuje listę zakupów na podstawie wybranych przepisów.

## Wymagania

- Python 3.10+
- Standardowa biblioteka Pythona (brak zewnętrznych zależności)

## Instalacja

```bash
python -m venv .venv
source .venv/bin/activate
```

## Użycie

1. Pobierz przepis i zapisz go lokalnie:
   ```bash
   python -m src.app fetch https://przyklad.pl/przepis
   ```

2. Wyświetl zapisane przepisy:
   ```bash
   python -m src.app list
   ```

3. Zbuduj plan tygodniowy (podaj identyfikatory zapisanych przepisów):
   ```bash
   python -m src.app plan 1 2 3
   ```

4. Pokaż zapisany plan:
   ```bash
   python -m src.app show-plan
   ```

5. Wygeneruj listę zakupów z zapisanego planu:
   ```bash
   python -m src.app shopping-list
   ```

Stan aplikacji domyślnie zapisywany jest w `data/state.json`. Możesz podać inną ścieżkę za pomocą `--state`.

## Pliki w repozytorium

- `src/app.py`, `src/recipe_fetcher.py`, `src/planner.py`, `src/shopping_list.py`, `src/storage.py` – główne moduły CLI wraz z logiką pobierania, planowania i agregacji składników.
- `README.md`, `.gitignore`, `requirements.txt` – pliki pomocnicze, które również znajdują się w repozytorium.

Wszystkie powyższe pliki są już dodane i wersjonowane, co można zweryfikować poleceniem `git status` (brak plików w stanie "untracked").

## Publikacja na GitHub

Jeżeli repozytorium jest wyłącznie lokalne, utwórz puste repozytorium na GitHubie, a następnie wykonaj:

```bash
git remote add origin git@github.com:<uzytkownik>/<nazwa-repo>.git
git push -u origin work
```

Po udanym `git push` wszystkie wymienione pliki powinny być widoczne w serwisie GitHub.
