# pylint: disable=consider-alternative-union-syntax, useless-suppression
"""Defines type aliasses that handle notational differences between python versions."""
import sys
from pathlib import Path
from typing import Any

if sys.version_info >= (3, 10):
    from typing import TypeAlias

    PathOrStr: TypeAlias = Path | str
    dictOrAny: TypeAlias = dict[str, Any] | Any  # pylint: disable=invalid-name
    PathOpt: TypeAlias = Path | None
else:
    from typing import Optional, Union

    from typing_extensions import TypeAlias

    PathOrStr: TypeAlias = Union[Path, str]
    dictOrAny: TypeAlias = Union[dict[str, Any], Any]  # pylint: disable=invalid-name
    PathOpt: TypeAlias = Optional[Path]
