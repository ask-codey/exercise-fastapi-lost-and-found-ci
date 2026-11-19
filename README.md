# Exercise: Lost and Found CI

Exercise code for the lesson **Exercise: Lost and Found CI** in the Python Web APIs course on [ask-codey.com](https://www.ask-codey.com).

The Lost and Found Desk is a campus API that keeps the things students find and hand in, and records who claims each one. Three students work on it together. The API works and its tests pass, but each student writes code a little differently, a few likely mistakes have crept in, and nothing checks a push before it lands on GitHub. You'll set up Ruff and mypy in `pyproject.toml`, fix everything they report without changing what the API answers, and add a GitHub Actions workflow that runs Ruff, mypy and pytest on every push.

## What's here

- `routers/items.py`: the items routes (`GET /items`, `GET /items/{item_id}`, `POST /items`). The comment at its top lists every request it answers. It works, but Ruff will have things to say about it. For you to clean up.
- `routers/claims.py`: the claims route (`POST /items/{item_id}/claims`), with the same kind of comment. For you to clean up too.
- `items_data.py`: the data module, every SQL statement the API runs. For you to clean up too.
- `main.py`: makes the app, adds the routers, runs the migrations at startup, and gives every error the API's one shape. Ready to use.
- `database.py`: opens the SQLite database, runs the migrations and gives each request its connection (`get_db`). Ready to use.
- `migrations/`: the two numbered SQL scripts that make the `items` and `claims` tables. Ready to use.
- `routers/__init__.py`: makes the `routers` folder a package. Ready to use.
- `tests/test_api.py`: the API's own 8 tests, which pass already and must still pass at the end. You don't need to change this file.
- `tests/test_quality.py`: the exercise's 11 checks, on your `pyproject.toml`, a clean run of Ruff and mypy, and your workflow file. You don't need to change this file.
- `requirements.txt`: the packages at exact versions: FastAPI and what it runs on, pytest, Ruff 0.17.5 and mypy 2.4.1, and PyYAML with its type hints (`types-PyYAML`), which the checks use to read your workflow file. Ready to use.
- `pytest.ini`: tells pytest where the tests are and where to find the app. Ready to use.
- `.gitignore`: tells Git to leave out the virtual environment, the database file, and the files Python, pytest, Ruff and mypy make as they run. Ready to use.

## Before you start

The app, the tests, Ruff and mypy go in a virtual environment: a private set of packages for this folder only. In VS Code's terminal, in this folder, run these three commands.

On Windows (PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

On a Mac (zsh):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

- The first command makes the virtual environment, in a folder named `.venv`.
- The second turns it on for this terminal: the prompt starts with `(.venv)` from then on.
- The third installs the packages `requirements.txt` lists into it. It takes a minute.

*Virtual Environments and pip* explains all three. The `.venv` folder is in `.gitignore`, so Git leaves it out: these commands make it again on any computer, GitHub's runner included. Ruff and mypy skip it.

If PowerShell answers that running scripts is disabled on this system, run this once, then run the second command again:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

Each new terminal starts with the virtual environment off. If the prompt doesn't start with `(.venv)`, run the second command again. (VS Code often turns it on for you.)

## Run it

```bash
fastapi dev main.py
```

Then open `http://127.0.0.1:8000/docs` in your browser to try every route: click one, then **Try it out** and **Execute**. The first start makes the database file, `lost_and_found.db`, with empty tables. Stop the server with **Ctrl+C**.

## What to do

1. **Make `pyproject.toml`** in this folder, with exactly these settings:

   ```toml
   [tool.ruff]
   line-length = 100

   [tool.ruff.lint]
   select = ["E", "F", "I"]

   [tool.mypy]
   disallow_untyped_defs = true
   ```

2. **Run `ruff check .` and fix all four problems it reports**, in `items_data.py`, `routers/items.py` and `routers/claims.py`. `ruff check --fix .` makes two of the fixes for you; the other two are yours.
3. **Run `ruff format .`**, so every file has the same layout. It reformats two files.
4. **Run `mypy .` and fix all three errors it reports**, in `items_data.py` and `routers/claims.py`.
5. **Make `.github/workflows/ci.yml`** (the folder `.github`, the folder `workflows` inside it, then the file): a workflow with `name: CI` that runs `on: [push, pull_request]`, with one job that `runs-on: ubuntu-latest` and has these steps, in this order:
   1. `uses: actions/checkout@v7`
   2. `uses: actions/setup-python@v7`, `with:` `python-version: "3.15"` (in quotes) and `cache: pip`
   3. `run: pip install -r requirements.txt`
   4. `run: ruff check .`
   5. `run: ruff format --check .`
   6. `run: mypy .`
   7. `run: pytest`

Run `pytest` after each fix: the API's 8 tests must stay green.

## Check your work

```bash
pytest
```

No server needs to be running. It runs the API's 8 tests (`test_api_1` to `test_api_8`), which pass from the start, and the exercise's 11 checks (`test_1` to `test_11`), which all fail at first: that's expected. Each part you finish turns its checks green, and a failing check's message says what's missing, for example *There's no pyproject.toml yet. Make it in the exercise folder.* Checks 4 to 6 run Ruff and mypy themselves and show what they still report, so they take a while: up to a minute or two the first time, while mypy reads FastAPI's and Pydantic's types, and much less after that.

When all 19 are green, push your work to GitHub: the **Actions** tab shows your workflow running the same checks on GitHub's computer.

## The rules

- Fix the code, never the settings: no `# noqa` or `# type: ignore` comments, and no rule left out of `select`.
- Every request in the comments at the top of `routers/items.py` and `routers/claims.py` answers exactly as it does now. The API's tests check that.
- A function you add hints to keeps its name and what it does: add the hints, don't rewrite it.
- Don't change `tests/test_api.py` or `tests/test_quality.py`.
- The workflow file is `.github/workflows/ci.yml`, exactly: GitHub only looks for workflows in that folder.

## Tips

- Read each finding's first line, then the file, line and column under it. `[*]` marks a fix Ruff makes with `--fix`.
- Python asks whether a value is `None` with `is None`, never `== None`.
- A comment is never wrapped by `ruff format`: split a long one over two lines yourself, each starting with `#`.
- mypy knows a Pydantic model's field types: a field typed `date` is a `date`, and `.isoformat()` turns it into text such as `"2026-11-17"`.
- `cursor.lastrowid` can be `None` as far as mypy knows. `add_item` in `items_data.py` already shows one way to deal with that.
- A function with no hints at all needs one on every parameter and a return type. Its docstring says what it takes and gives back, and the functions around it show how the same things are written.
- YAML is fussy about spaces: indent with two spaces, never tabs, and line up each step's `-` under the one before. Check 7 shows the line YAML couldn't read.
- Run the workflow's steps yourself before you push: `ruff check .`, `ruff format --check .`, `mypy .` and `pytest`. If they pass on your computer, they pass on GitHub's.

## Hand it in

When it works, push your solution to a public repo of your own on GitHub, then paste that repo's address into **Submit your exercise** on the lesson page at [ask-codey.com](https://www.ask-codey.com). That's what completes the lesson. The lesson page shows the Git commands, step by step.
