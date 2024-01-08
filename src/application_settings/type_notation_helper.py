# pylint: disable=consider-alternative-union-syntax, useless-suppression
"""Defines type aliases that handle notational differences between python versions."""
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

if sys.version_info >= (3, 10):
    from typing import TypeAlias

    PathOrStr: TypeAlias = Path | str
    PathOpt: TypeAlias = Path | None
    LoaderOpt: TypeAlias = Callable[[Path], dict[str, Any]] | None
    SaverOpt: TypeAlias = Callable[[Path, dict[str, Any]], None] | None
else:
    from typing import Union

    from typing_extensions import TypeAlias

    PathOrStr: TypeAlias = Union[Path, str]
    PathOpt: TypeAlias = Union[Path, None]
    LoaderOpt: TypeAlias = Union[Callable[[Path], dict[str, Any]], None]
    SaverOpt: TypeAlias = Union[Callable[[Path, dict[str, Any]], None], None]
