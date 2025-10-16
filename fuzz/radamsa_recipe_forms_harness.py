#!/usr/bin/env python3
"""
Radamsa fuzzing harness for Recipe app form processing.

This harness reads a single mutated POST body (application/x-www-form-urlencoded)
from stdin, attempts to parse it, and feeds it into Django forms used by the
recipe creation endpoint:
- RecipeForm
- RecipeIngredientFormSet

It avoids database writes and treats validation errors as expected outcomes.
A non-zero exit indicates an unexpected crash/exception in form handling.

Usage (normally invoked by the shell runner):
  cat fuzz/seeds/recipe_create_valid.txt | radamsa | fuzz/radamsa_recipe_forms_harness.py

Environment:
  DJANGO_SETTINGS_MODULE must point to recipe_project.settings.
"""
import os
import sys
import re
import traceback
from typing import List, Tuple
from urllib.parse import parse_qsl

# Ensure project root is on sys.path so 'recipe_project' and 'recipes' can be imported
_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.abspath(os.path.join(_CURRENT_DIR, ".."))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "recipe_project.settings")
os.environ.setdefault("PYTHONHASHSEED", "0")

import django  # noqa: E402
from django.core.exceptions import ValidationError  # noqa: E402
from django.http import QueryDict  # noqa: E402

# Initialize Django
django.setup()

from recipes.forms import RecipeForm, RecipeIngredientFormSet  # noqa: E402


PREFIX = "recipeingredient_set"
MGMT_KEYS = (
    f"{PREFIX}-TOTAL_FORMS",
    f"{PREFIX}-INITIAL_FORMS",
    f"{PREFIX}-MIN_NUM_FORMS",
    f"{PREFIX}-MAX_NUM_FORMS",
)


def _safe_decode(b: bytes) -> str:
    # Try utf-8 then fallback to latin-1 to preserve byte values
    try:
        return b.decode("utf-8", errors="ignore")
    except Exception:
        return b.decode("latin-1", errors="ignore")


def _parse_pairs(s: str) -> List[Tuple[str, str]]:
    # parse_qsl returns list of (key, value), keep blank values
    try:
        return parse_qsl(s, keep_blank_values=True, strict_parsing=False, encoding="utf-8", errors="ignore")
    except Exception:
        # As a last resort, attempt with latin-1
        return parse_qsl(s, keep_blank_values=True, strict_parsing=False, encoding="latin-1", errors="ignore")


def _count_indexed_forms(pairs: List[Tuple[str, str]]) -> int:
    # Detect indices present like recipeingredient_set-<i>-field
    idx_re = re.compile(rf"^{re.escape(PREFIX)}-(\d+)-")
    max_idx = -1
    for k, _ in pairs:
        m = idx_re.match(k)
        if m:
            try:
                i = int(m.group(1))
                if i > max_idx:
                    max_idx = i
            except Exception:
                continue
    return max_idx + 1 if max_idx >= 0 else 0


def _ensure_mgmt_fields(qd: QueryDict, n_forms: int) -> None:
    # Ensure management form keys exist; choose reasonable defaults
    if n_forms <= 0:
        n_forms = 1
    defaults = {
        f"{PREFIX}-TOTAL_FORMS": str(n_forms),
        f"{PREFIX}-INITIAL_FORMS": "0",
        f"{PREFIX}-MIN_NUM_FORMS": "1",
        f"{PREFIX}-MAX_NUM_FORMS": "1000",
    }
    for k, v in defaults.items():
        if k not in qd:
            qd[k] = v
        else:
            # If mutated to non-numeric, coerce back to a safe value to let formset init
            if not str(qd.get(k, "")).isdigit():
                qd[k] = v


def main() -> int:
    # Read up to a limit to avoid pathological sizes
    raw = sys.stdin.buffer.read()
    if len(raw) > 500_000:
        raw = raw[:500_000]

    s = _safe_decode(raw)
    pairs = _parse_pairs(s)

    # Build a QueryDict with all values
    qd = QueryDict("", mutable=True)
    for k, v in pairs:
        # Limit key/value sizes to prevent excessive memory in Django internals
        if len(k) > 5000:
            k = k[:5000]
        if len(v) > 20000:
            v = v[:20000]
        try:
            qd.appendlist(k, v)
        except Exception:
            # Skip keys Django QueryDict rejects
            continue

    # Ensure management form values so formset can instantiate
    n_forms = _count_indexed_forms(pairs)
    _ensure_mgmt_fields(qd, n_forms)

    # Create forms and run validation; treat ValidationError as expected
    form = RecipeForm(data=qd)
    formset = RecipeIngredientFormSet(qd)

    try:
        form.is_valid()
        formset.is_valid()
    except ValidationError:
        return 0
    except Exception:
        # Unexpected crash path; print for debugging and return non-zero
        sys.stderr.write("Unexpected exception in form handling:\n")
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
