FROM alpine AS dwnld
ADD https://paddleocr.bj.bcebos.com//PP-OCRv3/english/en_PP-OCRv3_det_infer.tar /tmp/
ADD https://paddleocr.bj.bcebos.com/PP-OCRv3/multilingual/latin_PP-OCRv3_rec_infer.tar /tmp/
ADD https://paddleocr.bj.bcebos.com/dygraph_v2.0/ch/ch_ppocr_mobile_v2.0_cls_infer.tar /tmp/

ADD . /tmp/app



FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

RUN apt-get update && apt-get install -y \
    libgomp1 \
    libgl1 \
    libglib2.0-0 \
    tesseract-ocr \
    ghostscript \
    ccache


RUN mkdir -p /paddleocr/models/det /paddleocr/models/rec /paddleocr/models/cls

# strip-components excludes the first level, which is just a folder (eg. Multilingual_PP-OCRv3_det_infer/)
RUN --mount=type=bind,from=dwnld,source=/tmp,target=/tmp tar --strip-components=1 -xf /tmp/en_PP-OCRv3_det_infer.tar -C /paddleocr/models/det
RUN --mount=type=bind,from=dwnld,source=/tmp,target=/tmp tar --strip-components=1 -xf /tmp/latin_PP-OCRv3_rec_infer.tar -C /paddleocr/models/rec
RUN --mount=type=bind,from=dwnld,source=/tmp,target=/tmp tar --strip-components=1 -xf /tmp/ch_ppocr_mobile_v2.0_cls_infer.tar -C /paddleocr/models/cls


RUN --mount=type=bind,from=dwnld,source=/tmp/app,target=/tmp/app uv pip install --system --no-cache-dir /tmp/app
