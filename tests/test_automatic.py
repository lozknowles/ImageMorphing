from pathlib import Path

import numpy as np
import pytest

from imagemorphing.automatic import AutoMorphResult, run_auto_morph
from imagemorphing.config import MorphConfig
from imagemorphing.exporters import ExportResult


def test_run_auto_morph_rejects_invalid_feature_count():
    config = MorphConfig(base_image=Path("before.jpg"), surrogate_image=Path("after.jpg"))
    with pytest.raises(ValueError, match="max_features"):
        run_auto_morph(config, max_features=0)


def test_run_auto_morph_happy_path_uses_export_pipeline(monkeypatch):
    config = MorphConfig(base_image=Path("before.jpg"), surrogate_image=Path("after.jpg"))

    class DummyLoaded:
        base_bgr = np.zeros((10, 10, 3), dtype=np.uint8)
        surrogate_bgr = np.zeros((10, 10, 3), dtype=np.uint8)

    class DummyKeyPoint:
        def __init__(self, x: float, y: float) -> None:
            self.pt = (x, y)

    class DummyMatch:
        def __init__(self, query_idx: int, train_idx: int, distance: float) -> None:
            self.queryIdx = query_idx
            self.trainIdx = train_idx
            self.distance = distance

    class DummyOrb:
        def detectAndCompute(self, image, mask):
            return [DummyKeyPoint(1.0, 2.0)] * 4, "descriptors"

    monkeypatch.setattr(
        "imagemorphing.automatic.prepare_loaded_images", lambda *_args: DummyLoaded()
    )
    monkeypatch.setattr("imagemorphing.automatic.cv2.cvtColor", lambda image, code: "gray")
    monkeypatch.setattr("imagemorphing.automatic.cv2.ORB_create", lambda max_features: DummyOrb())
    monkeypatch.setattr(
        "imagemorphing.automatic.cv2.BFMatcher",
        lambda norm, crossCheck: type(
            "DummyMatcher",
            (),
            {"match": staticmethod(lambda a, b: [DummyMatch(i, i, float(i)) for i in range(4)])},
        )(),
    )
    monkeypatch.setattr("imagemorphing.automatic.cv2.findHomography", lambda *args: ("H", None))
    monkeypatch.setattr("imagemorphing.automatic.ensure_output_folder", lambda path: None)
    monkeypatch.setattr(
        "imagemorphing.automatic.cv2.drawMatches", lambda *args, **kwargs: "preview"
    )
    monkeypatch.setattr("imagemorphing.automatic.cv2.imwrite", lambda *args, **kwargs: True)
    monkeypatch.setattr(
        "imagemorphing.automatic.cv2.warpPerspective", lambda *args, **kwargs: "aligned"
    )
    monkeypatch.setattr(
        "imagemorphing.automatic.cv2.addWeighted",
        lambda *args, **kwargs: "frame",
    )
    monkeypatch.setattr(
        "imagemorphing.automatic.save_frames",
        lambda frames, output_folder, base_filename: [output_folder / f"{base_filename}-0.jpg"],
    )
    monkeypatch.setattr(
        "imagemorphing.automatic.save_aligned_image",
        lambda image, output_folder, base_filename: output_folder / f"{base_filename}-aligned.jpg",
    )
    monkeypatch.setattr(
        "imagemorphing.automatic.export_gif",
        lambda frame_paths, output_folder, base_filename, duration: output_folder
        / f"{base_filename}.gif",
    )
    monkeypatch.setattr(
        "imagemorphing.automatic.export_mp4",
        lambda output_folder, base_filename, ffmpeg_binary, frame_rate: (
            output_folder / f"{base_filename}.mp4",
            "ok",
        ),
    )

    result = run_auto_morph(config)

    assert isinstance(result, AutoMorphResult)
    assert isinstance(result.export_result, ExportResult)
    assert result.match_visualization_path == config.output_folder / "matches_before.jpg"
    assert result.match_count == 4
