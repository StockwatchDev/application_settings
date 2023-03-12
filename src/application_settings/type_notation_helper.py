# pylint: disable=consider-alternative-union-syntax
"""Defines type aliasses that handle notational differences between python versions."""
import sys
from pathlib import Path

if sys.version_info >= (3, 10):
    from typing import TypeAlias

    PathOrStrT: TypeAlias = Path | str
    PathOptT: TypeAlias = Path | None
else:
    from typing import Optional, Union

    from typing_extensions import TypeAlias

    PathOrStrT: TypeAlias = Union[Path, str]
    PathOptT: TypeAlias = Optional[Path]
