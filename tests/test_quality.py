# The check for this exercise: your settings in pyproject.toml, a clean run of Ruff and mypy,
# and your workflow file. Every check fails at first; each part you finish turns its checks green.
# Run it with the API's tests: pytest (in the exercise folder, with the virtual environment on).
# Checks 4 to 6 run Ruff and mypy themselves, so they take a while the first time.
# You don't need to change this file.
import subprocess
import sys
import tomllib
from pathlib import Path
from typing import Any

import yaml

PROJECT = Path(__file__).parent.parent
PYPROJECT = PROJECT / "pyproject.toml"
WORKFLOW = PROJECT / ".github" / "workflows" / "ci.yml"

RUN_STEPS = [
    "pip install -r requirements.txt",
    "ruff check .",
    "ruff format --check .",
    "mypy .",
    "pytest",
]


def settings() -> dict[str, Any]:
    """Reads pyproject.toml, or fails with a message that says to make it."""
    assert PYPROJECT.exists(), "There's no pyproject.toml yet. Make it in the exercise folder."
    with PYPROJECT.open("rb") as file:
        return tomllib.load(file)


def run(*command: str) -> tuple[int, str]:
    """Runs a tool from the virtual environment in the exercise folder, and gives back its exit
    code and everything it printed."""
    done = subprocess.run(
        [sys.executable, "-m", *command], cwd=PROJECT, capture_output=True, text=True
    )
    return done.returncode, (done.stdout + done.stderr).strip()


def workflow() -> dict[Any, Any]:
    """Reads .github/workflows/ci.yml, or fails with a message that says what's wrong."""
    assert WORKFLOW.exists(), (
        "There's no .github/workflows/ci.yml yet. Make the folder .github, the folder workflows "
        "inside it, then the file ci.yml."
    )
    try:
        data = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))
    except yaml.YAMLError as error:
        raise AssertionError(f"ci.yml isn't valid YAML:\n{error}") from None
    assert isinstance(data, dict), "ci.yml should hold name, on and jobs, each on its own line."
    return data


def the_job() -> dict[str, Any]:
    """The workflow's one job."""
    jobs = workflow().get("jobs")
    assert isinstance(jobs, dict) and len(jobs) == 1, (
        f"The workflow should have exactly one job under jobs:, but it has {jobs!r}."
    )
    job = next(iter(jobs.values()))
    assert isinstance(job, dict), "The job should hold runs-on and steps."
    return job


def the_steps() -> list[dict[str, Any]]:
    """The job's steps."""
    steps = the_job().get("steps")
    assert isinstance(steps, list) and all(isinstance(step, dict) for step in steps), (
        "The job's steps: should be a list, each step starting with - (a dash)."
    )
    return steps


def test_1_pyproject_sets_ruff_line_length_to_100() -> None:
    ruff = settings().get("tool", {}).get("ruff", {})
    assert ruff.get("line-length") == 100, (
        f"Under [tool.ruff], set line-length = 100. It's {ruff.get('line-length')!r} now."
    )


def test_2_pyproject_selects_ruff_rules_e_f_and_i() -> None:
    lint = settings().get("tool", {}).get("ruff", {}).get("lint", {})
    selected = lint.get("select")
    assert isinstance(selected, list) and {"E", "F", "I"} <= set(selected), (
        f'Under [tool.ruff.lint], set select = ["E", "F", "I"]. It\'s {selected!r} now.'
    )


def test_3_pyproject_sets_mypy_disallow_untyped_defs_to_true() -> None:
    mypy = settings().get("tool", {}).get("mypy", {})
    assert mypy.get("disallow_untyped_defs") is True, (
        "Under [tool.mypy], set disallow_untyped_defs = true. "
        f"It's {mypy.get('disallow_untyped_defs')!r} now."
    )


def test_4_ruff_check_finds_no_problems() -> None:
    settings()
    code, output = run("ruff", "check", ".", "--output-format", "concise")
    assert code == 0, f"ruff check . still finds problems. Fix the code, not the rule:\n{output}"


def test_5_ruff_format_check_finds_every_file_formatted() -> None:
    settings()
    code, output = run("ruff", "format", "--check", ".")
    assert code == 0, f"Some files aren't formatted yet. Run ruff format .\n{output}"


def test_6_mypy_finds_no_errors() -> None:
    settings()
    code, output = run("mypy", ".")
    assert code == 0, f"mypy . still reports errors. Fix the code it points at:\n{output}"


def test_7_ci_yml_is_valid_yaml_and_named_ci() -> None:
    name = workflow().get("name")
    assert name == "CI", f"Start ci.yml with the line name: CI. Its name is {name!r} now."


def test_8_the_workflow_runs_on_push_and_pull_request() -> None:
    data = workflow()
    # YAML reads the word on by itself as true, so the key can arrive as True.
    triggers = data.get("on", data.get(True))
    if isinstance(triggers, str):
        triggers = [triggers]
    assert isinstance(triggers, (list, dict)) and {"push", "pull_request"} <= set(triggers), (
        f"Add the line on: [push, pull_request]. The workflow runs on {triggers!r} now."
    )


def test_9_the_job_runs_on_ubuntu_latest() -> None:
    runs_on = the_job().get("runs-on")
    assert runs_on == "ubuntu-latest", f"Give the job runs-on: ubuntu-latest. It's {runs_on!r}."


def test_10_the_first_steps_are_checkout_and_setup_python_315_with_the_pip_cache() -> None:
    steps = the_steps()
    assert len(steps) >= 2, "The job needs its steps, starting with checkout and setup-python."
    assert steps[0].get("uses") == "actions/checkout@v7", (
        f"Step 1 should be uses: actions/checkout@v7. It's {steps[0]!r}."
    )
    assert steps[1].get("uses") == "actions/setup-python@v7", (
        f"Step 2 should be uses: actions/setup-python@v7. It's {steps[1]!r}."
    )
    given = steps[1].get("with") or {}
    assert str(given.get("python-version")) == "3.15" and given.get("cache") == "pip", (
        'Give setup-python with: python-version: "3.15" (in quotes) and cache: pip. '
        f"It has {given!r}."
    )


def test_11_then_the_steps_run_the_install_ruff_mypy_and_pytest_in_order() -> None:
    runs = [str(step.get("run", "")).strip() for step in the_steps()[2:]]
    assert runs == RUN_STEPS, (
        "After setup-python, the steps should run, in this order:\n"
        + "\n".join(f"  run: {command}" for command in RUN_STEPS)
        + f"\nThey run {runs!r} now."
    )
