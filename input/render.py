import asyncio
import io
import re
from typing import Callable

import pytest
from rich.console import Console, RenderableType

re_link_ids = re.compile(r"id=[\d\.\-]*?;.*?\x1b")


def replace_link_ids(render: str) -> str:
    return re_link_ids.sub("id=0;foo\x1b", render)
