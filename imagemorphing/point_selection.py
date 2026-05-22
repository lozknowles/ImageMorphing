from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Sequence, Tuple


Point = Tuple[float, float]


@dataclass
class PointSelection:
    """Stores paired point selections while enforcing alternating clicks."""

    base_points: List[Point] = field(default_factory=list)
    surrogate_points: List[Point] = field(default_factory=list)
    point_number: int = 1
    last_side: Optional[str] = None

    def add_point(self, side: str, x: float, y: float) -> int:
        if side not in {"base", "surrogate"}:
            raise ValueError("side must be either 'base' or 'surrogate'")
        if self.last_side == side:
            raise ValueError("Please click on the other image next.")

        if side == "base":
            self.base_points.append((x, y))
            self.last_side = "base"
            return self.point_number

        self.surrogate_points.append((x, y))
        current_number = self.point_number
        self.last_side = "surrogate"
        self.point_number += 1
        return current_number

    def reset(self) -> None:
        self.base_points.clear()
        self.surrogate_points.clear()
        self.point_number = 1
        self.last_side = None

    def validate_ready(self, minimum_pairs: int = 3) -> None:
        if len(self.base_points) != len(self.surrogate_points):
            raise ValueError("The number of points in both images must be the same.")
        if len(self.base_points) < minimum_pairs:
            raise ValueError(
                f"At least {minimum_pairs} pairs of points are required for affine transformation."
            )

    def as_float32_pairs(self) -> Tuple[Sequence[Point], Sequence[Point]]:
        self.validate_ready()
        return self.base_points, self.surrogate_points
