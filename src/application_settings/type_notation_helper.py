# pylint: disable=consider-alternative-union-syntax, useless-suppression
"""Defines type aliases that handle notational differences between python versions."""

from pathlib import Path
from typing import TypeAlias

PathOrStr: TypeAlias = Path | str
