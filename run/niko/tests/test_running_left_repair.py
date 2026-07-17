"""Regression checks for Niko's deterministic running-left repair."""

from __future__ import annotations

import argparse
import sys
import unittest
from collections import deque
from pathlib import Path

from PIL import Image

CELL_WIDTH = 192
CELL_HEIGHT = 208
RUNNING_RIGHT_ROW = 1
RUNNING_LEFT_ROW = 2
FRAME_COUNT = 8
ATLAS_PATH: Path | None = None


def cell(image: Image.Image, row: int, column: int) -> Image.Image:
    return image.crop(
        (
            column * CELL_WIDTH,
            row * CELL_HEIGHT,
            (column + 1) * CELL_WIDTH,
            (row + 1) * CELL_HEIGHT,
        )
    )


def component_count(image: Image.Image, alpha_threshold: int = 16) -> int:
    alpha = image.convert("RGBA").getchannel("A")
    pixels = alpha.load()
    visited: set[tuple[int, int]] = set()
    count = 0
    for y in range(CELL_HEIGHT):
        for x in range(CELL_WIDTH):
            if (x, y) in visited or pixels[x, y] < alpha_threshold:
                continue
            count += 1
            queue: deque[tuple[int, int]] = deque([(x, y)])
            visited.add((x, y))
            while queue:
                current_x, current_y = queue.popleft()
                for delta_x, delta_y in (
                    (-1, -1),
                    (0, -1),
                    (1, -1),
                    (-1, 0),
                    (1, 0),
                    (-1, 1),
                    (0, 1),
                    (1, 1),
                ):
                    next_x = current_x + delta_x
                    next_y = current_y + delta_y
                    if (
                        0 <= next_x < CELL_WIDTH
                        and 0 <= next_y < CELL_HEIGHT
                        and (next_x, next_y) not in visited
                        and pixels[next_x, next_y] >= alpha_threshold
                    ):
                        visited.add((next_x, next_y))
                        queue.append((next_x, next_y))
    return count


def visible_rgba_bytes(image: Image.Image) -> bytes:
    """Canonicalize fully transparent pixels before comparing rendered frames."""
    output = bytearray()
    for red, green, blue, alpha in image.convert("RGBA").get_flattened_data():
        output.extend((red, green, blue, alpha) if alpha else (0, 0, 0, 0))
    return bytes(output)


class RunningLeftRepairTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if ATLAS_PATH is None:
            raise RuntimeError("--atlas is required")
        cls.atlas = Image.open(ATLAS_PATH).convert("RGBA")

    def test_left_running_frames_are_exact_mirrors_of_right_running_frames(self) -> None:
        self.assertEqual(self.atlas.size, (1536, 2288))
        for frame in range(FRAME_COUNT):
            left = cell(self.atlas, RUNNING_LEFT_ROW, frame)
            expected = cell(self.atlas, RUNNING_RIGHT_ROW, frame).transpose(
                Image.Transpose.FLIP_LEFT_RIGHT
            )
            self.assertEqual(
                visible_rgba_bytes(left),
                visible_rgba_bytes(expected),
                f"running-left frame {frame} is not the corresponding right-frame mirror",
            )

    def test_left_running_frames_contain_one_connected_sprite(self) -> None:
        for frame in range(FRAME_COUNT):
            sprite = cell(self.atlas, RUNNING_LEFT_ROW, frame)
            self.assertEqual(
                component_count(sprite),
                1,
                f"running-left frame {frame} contains a detached fragment",
            )

    def test_transparent_pixels_have_zero_rgb_residue(self) -> None:
        for index, (red, green, blue, alpha) in enumerate(
            self.atlas.get_flattened_data()
        ):
            if alpha == 0:
                self.assertEqual(
                    (red, green, blue),
                    (0, 0, 0),
                    f"transparent pixel {index} retains RGB residue",
                )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--atlas", required=True)
    arguments, unittest_arguments = parser.parse_known_args()
    ATLAS_PATH = Path(arguments.atlas)
    unittest.main(argv=[sys.argv[0], *unittest_arguments])
