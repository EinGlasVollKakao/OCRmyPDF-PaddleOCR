"""
Type aliases for the result returned by PaddleOCR
"""

from typing import Tuple, List


PaddlePosition = Tuple[float, float]

PaddleText = Tuple[str, float]
"""The detected text + a confidence value"""

PaddleQuadBBox = Tuple[PaddlePosition, PaddlePosition, PaddlePosition, PaddlePosition]
"""Quadrilateral bounding box around a detection with - basically a 4 sided polygon"""

PaddleDetection = Tuple[PaddleQuadBBox, PaddleText]
"""A single detection returned by PaddleOCR - consists of a bounding box + the detected text (with the confidence)"""

PaddlePage = List[PaddleDetection]
"""Contains all the detections of one page/image"""

PaddleResult = List[PaddlePage]
"""The type returned by the ocr() method from PaddleOCR"""
