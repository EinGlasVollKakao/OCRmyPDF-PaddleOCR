"""
Everything related to the generation of the hOCR
"""

from typing import List, Tuple
from xml.etree import ElementTree
from xml.etree.ElementTree import Element, SubElement

from ocrmypdf_paddleocr._detection import AABB, Baseline, Detection, Pos


def generate_hocr(
    dtcts: List[Detection],
    input_dimensions: Tuple[int, int],
    rotation: bool = True,
    file_title: str = "PaddleOCR - XML export (hOCR)",
) -> bytes:
    """Creates a hOCR xml from a list of Detections."""

    page_hocr = Element(
        "html", attrib={"xmlns": "http://www.w3.org/1999/xhtml", "xml:lang": "de"}
    )
    head = SubElement(page_hocr, "head")
    SubElement(head, "title").text = file_title
    SubElement(
        head,
        "meta",
        attrib={"http-equiv": "content-type", "content": "text/html; charset=utf-8"},
    )
    SubElement(head, "meta", attrib={"name": "ocr-system", "content": "python-paddle"})
    SubElement(
        head,
        "meta",
        attrib={
            "name": "ocr-capabilities",
            "content": "ocr_page ocr_carea ocr_par ocr_line ocrx_word",
        },
    )

    width, height = input_dimensions

    body = SubElement(page_hocr, "body")
    page = SubElement(
        body,
        "div",
        attrib={
            "class": "ocr_page",
            "id": "page_1",
            "title": f"image; bbox 0 0 {width} {height}; ppageno 0",
        },
    )

    # calculate page bounds - bound around all other bounds
    # if lines are empty, set the bound to 0,0,0,0
    if dtcts:
        page_bounds = AABB(
            top_left=Pos(
                min(dtcts, key=lambda d: d.aabbox.top_left.x).aabbox.top_left.x,
                min(dtcts, key=lambda d: d.aabbox.top_left.y).aabbox.top_left.y,
            ),
            bot_right=Pos(
                max(dtcts, key=lambda d: d.aabbox.bot_right.x).aabbox.bot_right.x,
                max(dtcts, key=lambda d: d.aabbox.bot_right.y).aabbox.bot_right.y,
            ),
        )
    else:
        page_bounds = AABB(top_left=Pos(0, 0), bot_right=Pos(0, 0))

    block_div = SubElement(
        page,
        "div",
        attrib={
            "class": "ocr_carea",
            "id": "block_1",
            "title": f"{page_bounds.hocr_repr()}",
        },
    )
    paragraph = SubElement(
        block_div,
        "p",
        attrib={
            "class": "ocr_par",
            "id": "par_1",
            "title": f"{page_bounds.hocr_repr()}",
        },
    )

    for d_num, d in enumerate(dtcts):
        if rotation:
            relative_baseline = d.baseline.relative_to(
                Pos(x=d.aabbox.top_left.x, y=d.aabbox.bot_right.y)
            )
        else:
            relative_baseline = Baseline(0, 0)
        line_span = SubElement(
            paragraph,
            "span",
            attrib={
                "class": "ocr_line",
                "id": f"line_{d_num + 1}",
                "title": f"{d.aabbox.hocr_repr()}; \
            {relative_baseline.hocr_repr()}; x_size 0; x_descenders 0; x_ascenders 0;",
            },
        )
        word_span = SubElement(
            line_span,
            "span",
            attrib={
                "class": "ocrx_word",
                "id": f"word_{d_num + 1}",
                "title": f"{d.aabbox.hocr_repr()}; \
            x_wconf {int(round(d.confidence * 100))}",
            },
        )
        word_span.text = d.text

    return ElementTree.tostring(page_hocr, encoding="utf-8", method="xml")
