from pathlib import Path

import pytest


@pytest.fixture(scope="module")
def data_folder_path():
    main_path = Path(__file__).resolve().parent
    return main_path / "data"
