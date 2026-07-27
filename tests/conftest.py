import json
from pathlib import Path

import pytest

TEST_QDRANT_COLLECTION = "poe2-skill-gems-test"
SAMPLE_DATA_PATH = Path(__file__).parent / "fixtures" / "sample_gems.json"


@pytest.fixture
def sample_gems() -> list[dict]:
    return json.loads(SAMPLE_DATA_PATH.read_text())
