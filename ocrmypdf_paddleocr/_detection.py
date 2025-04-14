"""
All classes related to a detection and its components.
It's our representation of what PaddleOCR returns and what is then used to construct the hOCR.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

from ocrmypdf_paddleocr._paddle_types import PaddleDetection, PaddlePage


@dataclass
class Pos:
    x: float
    y: float

    def xy(self) -> Tuple[float, float]:
        """Return x and y coordinates as a Tupple"""
        return self.x, self.y


@dataclass
class QuadBB:
    """
    Quadrilateral bounding box
    A box consisting of four points around a detection.
    We get these from PaddleOCR and need to convert them into the
    simpler AxisAlignedBoundingBox (AABB)
    """

    top_left: Pos
    top_right: Pos
    bot_left: Pos
    bot_right: Pos

    def to_aabb(self) -> AABB:
        """
        Returns an axis aligned bounding box (AABB) that encloses this polygon bound.

        Used to convert the bounds returned from PaddleOCR to bboxes used by hOCR.
        """
        positions = [self.top_left, self.top_right, self.bot_right, self.bot_left]
        return AABB(
            top_left=Pos(
                min(positions, key=lambda p: p.x).x, min(positions, key=lambda p: p.y).y
            ),
            bot_right=Pos(
                max(positions, key=lambda p: p.x).x,
                max(positions, key=lambda p: p.y).y,
            ),
        )

    def to_baseline(self) -> Baseline:
        """
        Returns the baseline (basically the bottom side of the quadrilateral bound)

        This is used in hOCR for specifying the text orientation
        See: https://kba.github.io/hocr-spec/1.2/#baseline
        """
        delta_x = self.bot_right.x - self.bot_left.x
        delta_y = self.bot_right.y - self.bot_left.y

        # Calculate slope (k) and intercept (d)
        if delta_x != 0:
            k = delta_y / delta_x
        else:
            k = 0
        d = self.bot_left.y - (k * self.bot_left.x)

        return Baseline(d, k)


@dataclass
class AABB:
    """
    Axis Aligned Bounding Box
    A non-rotated rectangle around a detection.
    hOCR uses theses (+ a baseline) to determine where a detection is
    """

    top_left: Pos
    bot_right: Pos

    def hocr_repr(self) -> str:
        """String format of the bbox used in hOCR"""
        return f"bbox {int(self.top_left.x)} {int(self.top_left.y)} {int(self.bot_right.x)} {int(self.bot_right.y)}"


@dataclass
class Baseline:
    """
    Used together with an axis aligned bounding box in hOCR.
    This determines the angle and offset of the text inside the AABB.
    """

    offset: float
    slope: float

    def relative_to(self, point: Pos) -> Baseline:
        """
        Returns a new Baseline with a coordinate system relative to the provided point.

        Used for hOCR output, because the baseline has to be relative to the bottom left point of the bbox.
        """
        y_intercept = self.slope * point.x + self.offset
        rel_intercept = y_intercept - point.y
        return Baseline(rel_intercept, self.slope)

    def y_from_x(self, x: float) -> float:
        """Calculate y for a given x value"""
        return self.slope * x + self.offset

    def hocr_repr(self) -> str:
        """String format of the baseline used in hOCR"""
        return f"baseline {self.slope} {self.offset}"


@dataclass
class Detection:
    text: str
    confidence: float
    quad_bbox: QuadBB
    aabbox: AABB
    baseline: None

    @staticmethod
    def __from_paddle_detection(result: PaddleDetection) -> Detection:
        text: str = result[1][0]
        confidence: float = result[1][1]

        quad_box = QuadBB(
            Pos(*result[0][0]),
            Pos(*result[0][1]),
            Pos(*result[0][2]),
            Pos(*result[0][3]),
        )

        aabb = quad_box.to_aabb()
        baseline = quad_box.to_baseline()

        return Detection(text, confidence, quad_box, aabb, baseline)

    @staticmethod
    def from_paddle_detections(detections: PaddlePage) -> List[Detection]:
        """
        Converts the raw data recieved from PaddleOCR into a list of this class.

        Also calculates the axis aligned bounding box + baseline needed for hOCR from
        the quadrilateral box returned by PaddleOCR
        """
        return [Detection.__from_paddle_detection(detection) for detection in detections]
