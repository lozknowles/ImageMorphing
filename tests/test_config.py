from pathlib import Path

import pytest

from imagemorphing.config import MorphConfig


def test_morph_config_rejects_zero_frames():
    with pytest.raises(ValueError):
        MorphConfig(base_image=Path("before.jpg"), surrogate_image=Path("after.jpg"), num_frames=0)


def test_morph_config_exposes_base_filename():
    config = MorphConfig(base_image=Path("assets/before.jpg"), surrogate_image=Path("after.jpg"))
    assert config.base_filename == "before"


def test_morph_config_rejects_invalid_frame_duration():
    with pytest.raises(ValueError):
        MorphConfig(
            base_image=Path("before.jpg"),
            surrogate_image=Path("after.jpg"),
            frame_duration_seconds=0,
        )
