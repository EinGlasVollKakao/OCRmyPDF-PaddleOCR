import ocrmypdf
import pikepdf


def test_paddleocr(resources, outpdf):
    ocrmypdf.ocr(resources / "jbig2.pdf", outpdf)
    assert outpdf.exists()
    assert not outpdf.with_suffix(".hocr").exists()
    assert not outpdf.with_suffix(".txt").exists()
    assert not outpdf.with_suffix(".png").exists()

    with pikepdf.open(outpdf) as pdf:
        assert "PaddleOCR" in str(pdf.docinfo["/Creator"])
