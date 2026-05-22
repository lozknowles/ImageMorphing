import pytest

from imagemorphing.point_selection import PointSelection


def test_point_selection_enforces_alternating_clicks():
    selection = PointSelection()
    selection.add_point("base", 1.0, 2.0)
    with pytest.raises(ValueError):
        selection.add_point("base", 3.0, 4.0)


def test_point_selection_tracks_completed_pairs():
    selection = PointSelection()
    assert selection.add_point("base", 1.0, 2.0) == 1
    assert selection.add_point("surrogate", 3.0, 4.0) == 1
    assert selection.point_number == 2


def test_point_selection_requires_three_pairs():
    selection = PointSelection()
    selection.add_point("base", 1.0, 2.0)
    selection.add_point("surrogate", 3.0, 4.0)
    with pytest.raises(ValueError):
        selection.validate_ready()
