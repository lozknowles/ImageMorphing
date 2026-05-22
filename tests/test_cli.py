from pathlib import Path

import pytest

from imagemorphing.cli import _positive_int, build_morph_parser, build_resize_parser


def test_positive_int_accepts_positive_values():
    assert _positive_int("3") == 3


def test_positive_int_rejects_zero():
    with pytest.raises(Exception):
        _positive_int("0")


def test_morph_parser_builds_expected_paths():
    parser = build_morph_parser()
    args = parser.parse_args(
        [
            "--base_image",
            "before.jpg",
            "--surrogate_image",
            "after.jpg",
            "--output_folder",
            "morph_output",
        ]
    )
    assert args.base_image == Path("before.jpg")
    assert args.surrogate_image == Path("after.jpg")
    assert args.output_folder == Path("morph_output")


def test_resize_parser_builds_expected_paths():
    parser = build_resize_parser()
    args = parser.parse_args(
        [
            "--base_image",
            "before.jpg",
            "--overlay_image",
            "after.jpg",
        ]
    )
    assert args.base_image == Path("before.jpg")
    assert args.overlay_image == Path("after.jpg")
