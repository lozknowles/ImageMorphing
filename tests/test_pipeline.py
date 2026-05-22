from pathlib import Path

import pytest

from imagemorphing.config import MorphConfig
from imagemorphing.exporters import ExportResult
from imagemorphing.pipeline import MorphRunResult, run_morph


def test_run_morph_rejects_mismatched_points():
    config = MorphConfig(base_image=Path("before.jpg"), surrogate_image=Path("after.jpg"))
    with pytest.raises(ValueError, match="same"):
        run_morph(config, [(1.0, 2.0)], [])


def test_run_morph_rejects_too_few_points():
    config = MorphConfig(base_image=Path("before.jpg"), surrogate_image=Path("after.jpg"))
    points = [(1.0, 2.0), (3.0, 4.0)]
    with pytest.raises(ValueError, match="three pairs"):
        run_morph(config, points, points)


def test_run_morph_happy_path_uses_export_pipeline(monkeypatch):
    config = MorphConfig(base_image=Path("before.jpg"), surrogate_image=Path("after.jpg"))
    points = [(1.0, 2.0), (3.0, 4.0), (5.0, 6.0)]

    calls = {
        "ensure_output_folder": 0,
    }

    class DummyLoaded:
        base_bgr = "base-bgr"
        surrogate_bgr = "surrogate-bgr"

    class DummyWorkspace:
        aligned_cropped = "aligned-image"

    monkeypatch.setattr(
        "imagemorphing.pipeline.prepare_loaded_images",
        lambda *_args: DummyLoaded(),
    )
    monkeypatch.setattr(
        "imagemorphing.pipeline.build_aligned_workspace",
        lambda *_args: DummyWorkspace(),
    )
    monkeypatch.setattr(
        "imagemorphing.pipeline.blend_frame",
        lambda workspace, alpha: f"frame-{alpha:.2f}",
    )
    monkeypatch.setattr(
        "imagemorphing.pipeline.ensure_output_folder",
        lambda path: calls.__setitem__(
            "ensure_output_folder",
            calls["ensure_output_folder"] + 1,
        ),
    )
    monkeypatch.setattr(
        "imagemorphing.pipeline.save_frames",
        lambda frames, output_folder, base_filename: (
            [output_folder / f"{base_filename}-0.jpg"] if list(frames) else []
        ),
    )
    monkeypatch.setattr(
        "imagemorphing.pipeline.save_aligned_image",
        lambda image, output_folder, base_filename: (
            output_folder / f"{base_filename}-aligned.jpg"
        ),
    )
    monkeypatch.setattr(
        "imagemorphing.pipeline.export_gif",
        lambda frame_paths, output_folder, base_filename, duration: (
            output_folder / f"{base_filename}.gif"
        ),
    )
    monkeypatch.setattr(
        "imagemorphing.pipeline.export_mp4",
        lambda output_folder, base_filename, ffmpeg_binary, frame_rate: (
            output_folder / f"{base_filename}.mp4",
            "ok",
        ),
    )

    result = run_morph(config, points, points)

    assert isinstance(result, MorphRunResult)
    assert isinstance(result.export_result, ExportResult)
    assert result.export_result.gif_path == config.output_folder / "before.gif"
    assert result.export_result.mp4_path == config.output_folder / "before.mp4"
    assert calls["ensure_output_folder"] == 1
