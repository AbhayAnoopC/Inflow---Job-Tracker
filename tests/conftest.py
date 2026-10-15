import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "ingestion"))


@pytest.fixture(autouse=True)
def no_rate_limit(monkeypatch: pytest.MonkeyPatch) -> None:
    from adapters import _http

    monkeypatch.setattr(_http, "RATE_LIMIT_S", 0)
