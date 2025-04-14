"""PaddleOCR plugin for OCRmyPDF"""

from __future__ import annotations

import logging
import os
from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import List, Optional, Set

from ocrmypdf import OrientationConfidence, hookimpl
from ocrmypdf._exec import tesseract
from ocrmypdf.pluginspec import OcrEngine
from paddleocr import PaddleOCR
from paddleocr import __version__ as PADDLEOCR_VERSION
from PIL import Image, ImageDraw

import ocrmypdf_paddleocr._hocr as hocr
from ocrmypdf_paddleocr._detection import Detection
from ocrmypdf_paddleocr._paddle_types import PaddlePage, PaddleResult

logging.getLogger().handlers = []  # reset weird shit that paddle does to our logging


# From https://github.com/PaddlePaddle/PaddleOCR/blob/main/docs/ppocr/blog/multi_languages.en.md#5-support-languages-and-abbreviations
LANGS: dict[str, str] = {
    "chi": "ch",
    "eng": "en",
    "fra": "fr",
    "deu": "german",
    "jpn": "japan",
    "kor": "korean",
    "chi_tra": "chinese_cht",
    "ita": "it",
    "spa": "es",
    "por": "pt",
    "rus": "ru",
    "ukr": "uk",
    "bel": "be",
    "tel": "te",
    "san": "sa",
    "tam": "ta",
    "afr": "af",
    "aze": "az",
    "bos": "bs",
    "ces": "cs",
    "cym": "cy",
    "dan": "da",
    "mlt": "mt",
    "nld": "nl",
    "nor": "no",
    "pol": "pl",
    "ron": "ro",
    "slk": "sk",
    "slv": "sl",
    "sqi": "sq",
    "swe": "sv",
    "swa": "sw",
    "tgl": "tl",
    "tur": "tr",
    "uzb": "uz",
    "vie": "vi",
    "mon": "mn",
    "abq": "abq",
    "che": "che",
    "bgc": "bgc",
    "ara": "ar",
    "hin": "hi",
    "uig": "ug",
    "fas": "fa",
    "urd": "ur",
    "srp": "rs_latin",
    "srp_latin": "rs_latin",
    "srp_cyrillic": "rs_cyrillic",
    "oci": "oc",
    "mar": "mr",
    "nep": "ne",
    "bul": "bg",
    "est": "et",
    "gle": "ga",
    "hrv": "hr",
    "hun": "hu",
    "ind": "id",
    "isl": "is",
    "kur": "ku",
    "lit": "lt",
    "lav": "lv",
    "mri": "mi",
    "msa": "ms",
    "ady": "ady",
    "kbd": "kbd",
    "ava": "ava",
    "dar": "dar",
    "inh": "inh",
    "lbe": "lbe",
    "lez": "lez",
    "tab": "tab",
    "bih": "bh",
    "mai": "mai",
    "anp": "ang",
    "bho": "bho",
    "mag": "mah",
    "sck": "sck",
    "new": "new",
    "gom": "gom",
    "pli": "pi",
    "lat": "la",
}


@hookimpl
def add_options(parser: ArgumentParser):
    paddleocr_options = parser.add_argument_group("PaddleOCR", "PaddleOCR options")
    paddleocr_options.add_argument(
        "--paddleocr-no-rotation",
        action="store_false",
        dest="paddleocr_rotation",
        help="Disable rotating text in PDF based on PaddleOCR's detection",
    )
    paddleocr_options.add_argument(
        "--paddleocr-model-dir",
        help="custom directory for PaddleOCR'r models - uses subfolders: det, rec & cls"
    )
    paddleocr_options.add_argument(
        "--paddleocr-det-dir",
        help="custom directory for PaddleOCR's detection model - this overwrites --paddleocr-model-dir",
    )
    paddleocr_options.add_argument(
        "--paddleocr-rec-dir",
        help="custom directory for PaddleOCR's recognition model - this overwrites --paddleocr-model-dir",
    )
    paddleocr_options.add_argument(
        "--paddleocr-cls-dir",
        help="custom directory for PaddleOCR's angle classification model - this overwrites --paddleocr-model-dir - Note: PaddleOCR's angle classification is turned off, but it still downloads this model, therefore there's the option to specify its location.",
    )
    paddleocr_options.add_argument(
        "--paddleocr-debug-hocr",
        action="store_true",
        help="store hOCR file alongside output for debugging purposes",
    )
    paddleocr_options.add_argument(
        "--paddleocr-debug-png",
        action="store_true",
        help="generate image with bounding boxes for debugging purposes",
    )
    paddleocr_options.add_argument(
        "--paddleocr-debug-txt",
        action="store_true",
        help="store txt file with recognized text alongside output for debugging purposes",
    )


class PaddleOcrEngine(OcrEngine):
    @staticmethod
    def version() -> str:
        return PADDLEOCR_VERSION

    @staticmethod
    def creator_tag(options: Namespace) -> str:
        return f"PaddleOCR {PaddleOcrEngine.version()}"

    def __str__(self):
        return f"PaddleOCR {PaddleOcrEngine.version()}"

    @staticmethod
    def languages(options: Namespace) -> Set[str]:
        return LANGS.keys()

    @staticmethod
    def get_orientation(input_file: Path, options: Namespace) -> OrientationConfidence:
        return tesseract.get_orientation(
            input_file,
            engine_mode=options.tesseract_oem,
            timeout=options.tesseract_non_ocr_timeout,
        )

    @staticmethod
    def generate_pdf(
        input_file: Path, output_pdf: Path, output_text: Path, options: Namespace
    ) -> None:
        raise NotImplementedError(
            "PaddleOCR currently only works with hOCR render mode -- use --pdf-renderer=hocr."
        )

    @staticmethod
    def generate_hocr(
        input_file: Path, output_hocr: Path, output_text: Path, options: Namespace
    ) -> None:
        base_dir: Optional[str] = options.paddleocr_model_dir
        det_dir: Optional[str] = options.paddleocr_det_dir
        if det_dir is None and base_dir is not None:
            det_dir = os.path.join(base_dir, "det")

        rec_dir: Optional[str] = options.paddleocr_rec_dir
        if rec_dir is None and base_dir is not None:
            rec_dir = os.path.join(base_dir, "rec")

        cls_dir: Optional[str] = options.paddleocr_cls_dir
        if cls_dir is None and base_dir is not None:
            cls_dir = os.path.join(base_dir, "cls")

        output_wo_ext = Path(options.output_file).parent.joinpath(
            Path(options.output_file).stem
        )

        ocr = PaddleOCR(
            use_angle_cls=False,
            lang=LANGS.get(options.languages[0]),
            use_gpu=False,
            det_model_dir=det_dir,
            rec_model_dir=rec_dir,
            cls_model_dir=cls_dir,
            show_log=False,
        )

        result: PaddleResult = ocr.ocr(str(input_file))
        result: PaddlePage = (
            result[0] or []
        )  # we only have a single page - ever (i hope)

        input_img = Image.open(input_file)

        detections = Detection.from_paddle_detections(result)

        hocr_bytes = hocr.generate_hocr(
            detections, (input_img.width, input_img.height), options.paddleocr_rotation
        )

        if options.paddleocr_debug_png:
            draw_debug_image(input_file, detections, f"{output_wo_ext}.png")

        with open(output_hocr, "wb") as f:
            f.write(hocr_bytes)

        if options.paddleocr_debug_hocr:
            with open(f"{output_wo_ext}.hocr", "wb") as f:
                f.write(hocr_bytes)

        text = generate_text(detections)
        with open(output_text, "wb") as f:
            f.write(text)

        if options.paddleocr_debug_txt:
            with open(f"{output_wo_ext}.txt", "wb") as f:
                f.write(text)


@hookimpl
def get_ocr_engine():
    return PaddleOcrEngine()


def draw_debug_image(source_img: Path, dtcts: List[Detection], output_filename: str) -> None:
    img = Image.open(source_img).convert("RGB")
    draw = ImageDraw.Draw(img)

    for d in dtcts:
        draw.polygon(
            (
                d.quad_bbox.top_left.xy(),
                d.quad_bbox.bot_left.xy(),
                d.quad_bbox.bot_right.xy(),
                d.quad_bbox.top_right.xy(),
            ),
            outline=(224, 142, 69),
        )

        draw.rectangle(
            (d.aabbox.top_left.xy(), d.aabbox.bot_right.xy()), outline=(52, 36, 68)
        )

        draw.circle(d.quad_bbox.bot_left.xy(), radius=4, fill=(137, 96, 142))
        draw.circle(d.quad_bbox.bot_right.xy(), radius=4, fill=(98, 59, 90))

        # baseline drawing
        start_x = d.aabbox.top_left.x
        start_y = d.baseline.y_from_x(start_x)
        end_x = d.aabbox.bot_right.x
        end_y = d.baseline.y_from_x(end_x)
        draw.line((start_x, start_y, end_x, end_y), fill=(57, 67, 183))

        draw.circle((start_x, start_y), radius=2, fill=(4, 220, 73))
        draw.circle((end_x, end_y), radius=2, fill=(4, 139, 31))

    img.save(output_filename)


def generate_text(dtcts: List[Detection]) -> bytes:
    """
    Outputs only the text detected in from detection results.
    Currently, it makes a new line for every detection box, which isn't optimal...
    """
    return "\n".join([d.text for d in dtcts]).encode("utf-8")
