#!/usr/bin/env python3
"""
Atheris fuzzing harness for Recipe app forms and model validation.

Targets:
- RecipeForm validation (is_valid)
- RecipeIngredientForm validation (is_valid)
- Recipe model full_clean (field validators only; no DB writes)

Usage:
  # From project root (ensure venv with atheris is active):
  python -m atheris fuzz/atheris_recipe_forms_fuzz.py -rss_limit_mb=2048

You can pass additional libFuzzer flags after the script path, e.g.:
  -runs=0 -max_len=4096 -timeout=5

Notes:
- This harness avoids saving to the DB to keep fuzzing fast and deterministic.
- It requires Django settings to be available.
"""
import atheris
import sys
import os
import io
import typing as t

# Silence Django startup logs for fuzzing
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "recipe_project.settings")
os.environ.setdefault("PYTHONHASHSEED", "0")  # determinism across runs

import django  # noqa: E402
from django.core.exceptions import ValidationError  # noqa: E402

# Initialize Django once.
django.setup()

from recipes.forms import RecipeForm, RecipeIngredientForm  # noqa: E402
from recipes.models import Recipe  # noqa: E402


def _consume_unicode(fp: atheris.FuzzedDataProvider, min_len: int = 0, max_len: int = 5000) -> str:
    length = fp.ConsumeIntInRange(min_len, max_len)
    # Avoid embedding NULs in form fields which can cause lower-level errors unrelated to form logic
    s = fp.ConsumeUnicodeNoSurrogates(length)
    # Trim excessive control characters that may break terminal/output in CI
    return s.replace("\x00", "").replace("\r", "\n")


def _consume_int(fp: atheris.FuzzedDataProvider, min_v: int = -1000, max_v: int = 100000) -> int:
    return fp.ConsumeIntInRange(min_v, max_v)


def _fuzz_recipe_form(fp: atheris.FuzzedDataProvider) -> None:
    data = {
        "name": _consume_unicode(fp, 0, 300),
        "description": _consume_unicode(fp, 0, 2000),
        "instructions": _consume_unicode(fp, 0, 8000),
        "prep_time": str(_consume_int(fp, -1000, 100000)),
        "cook_time": str(_consume_int(fp, -1000, 100000)),
        "servings": str(_consume_int(fp, -1000, 10000)),
    }
    form = RecipeForm(data=data)
    try:
        form.is_valid()  # We don't care if valid; just ensure no unexpected exceptions.
    except Exception as e:
        # Bubble up only truly unexpected errors; filter out common Django validation errors
        if not isinstance(e, (ValidationError,)):
            raise


def _fuzz_recipe_ingredient_form(fp: atheris.FuzzedDataProvider) -> None:
    data = {
        "ingredient_name": _consume_unicode(fp, 0, 200),
        "quantity": _consume_unicode(fp, 0, 100),
    }
    form = RecipeIngredientForm(data=data)
    try:
        form.is_valid()
    except Exception as e:
        if not isinstance(e, (ValidationError,)):
            raise


def _fuzz_recipe_model_full_clean(fp: atheris.FuzzedDataProvider) -> None:
    r = Recipe(
        name=_consume_unicode(fp, 0, 200),
        description=_consume_unicode(fp, 0, 2000),
        instructions=_consume_unicode(fp, 0, 8000),
        prep_time=max(0, _consume_int(fp, -1000, 100000)),  # model field is PositiveIntegerField
        cook_time=max(0, _consume_int(fp, -1000, 100000)),  # enforce non-negative to hit model validators
        servings=max(0, _consume_int(fp, -1000, 10000)),
    )
    try:
        r.full_clean()  # field-level validation only; no DB
    except ValidationError:
        # Expected for many inputs; that's fine.
        pass


def TestOneInput(data: bytes) -> None:
    fp = atheris.FuzzedDataProvider(data)

    # Randomly pick which target to fuzz this iteration to diversify coverage
    choice = fp.ConsumeIntInRange(0, 2)
    if choice == 0:
        _fuzz_recipe_form(fp)
    elif choice == 1:
        _fuzz_recipe_ingredient_form(fp)
    else:
        _fuzz_recipe_model_full_clean(fp)


def main() -> None:
    # libFuzzer expects argv
    atheris.Setup(sys.argv, TestOneInput)
    atheris.Fuzz()


if __name__ == "__main__":
    main()
