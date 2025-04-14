import ocrmypdf

CONTENT = "This should be a perfect circle."

def test_with_text_debug(resources, outpdf):
    outtxt = outpdf.with_suffix(".txt")
    ocrmypdf.ocr(resources / "aspect.pdf", outpdf, paddleocr_debug_txt=True)
    assert outpdf.exists()
    assert outtxt.exists()

    with outtxt.open() as f:
        assert f.read().strip() == CONTENT
