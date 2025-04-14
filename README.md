# OCRmyPDF PaddleOCR

This plugin for [OCRmyPDF](https://github.com/ocrmypdf/OCRmyPDF) replaces the
default Tesseract OCR Engine with [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR).

## Installation

### Requirements

#### Ubuntu/Debian

```bash
apt install libgomp1 libgl1 libglib2.0-0 ccache
```

### Plugin installation

```bash
pip install git+https://github.com/EinGlasVollKakao/OCRmyPDF-PaddleOCR.git
```

This plugin automaically overwrites the default OCR engine, but OCRmyPDF still
needs Tesseract for some tasks.

## Additional parameters

- **`--paddleocr-no-rotation`**  
  Disables rotating text based on PaddleOCRs bounding boxes

- **`--paddleocr-model-dir`**  
  You can use this option to specify custom or pre-downloaded models directly.  
  It expects three subdirectories - `det`, `rec` & `cls` - with the respective
  extracted model inside it.
  It these don't exist, it will download them for the specified language
  (But it won't redowload them if you change the language later).  
  You can find a list of models [here](https://paddlepaddle.github.io/PaddleOCR/main/en/ppocr/model_list.html)

  > [!NOTE]
  > If you just want to customize the download location but still want the default
  > behaviour of swiching models based on the language, consider setting the `PADDLE_OCR_BASE_DIR`
  > env variable.  
  > See [here](https://paddlepaddle.github.io/PaddleOCR/main/en/quick_start.html#1-install-paddlepaddle)

- **`--paddleocr-det-dir`**  
  Specify a custom detection model directory.  
  Overwrites `--paddleocr-model-dir`, if it is also set.

- **`--paddleocr-rec-dir`**  
  Specify a custom recognition model directory.  
  Overwrites `--paddleocr-model-dir`, if it is also set.

- **`--paddleocr-cls-dir`**  
  Specify a custom classification model directory.  
  Overwrites `--paddleocr-model-dir`, if it is also set.

### Debug options

- **`--paddleocr-debug-hocr`**  
  Stores a hOCR file alongside the output file

- **`--paddleocr-degug-png`**  
  Generates an image with bounding boxes

- **`--paddleocr-debug-txt`**  
  Stores the detected text in a textfile
  Writes each detection on a new line

## Credits

[OCRmyPDF-EasyOCR](https://github.com/ocrmypdf/OCRmyPDF-EasyOCR) for providing a
good starting point for writing a OCRmyPDF plugin :)
