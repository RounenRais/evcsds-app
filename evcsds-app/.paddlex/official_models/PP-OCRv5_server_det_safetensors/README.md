---
license: apache-2.0
library_name: PaddleOCR
language:
- en
- zh
pipeline_tag: image-to-text
tags:
- OCR
- PaddlePaddle
- PaddleOCR
- textline_detection
---

# PP-OCRv5_server_det

## Introduction

PP-OCRv5_server_det is one of the PP-OCRv5_det series, the latest generation of text detection models developed by the PaddleOCR team. Designed for high-performance applications, it supports the detection of text in diverse scenarios—including handwriting, vertical, rotated, and curved text—across multiple languages such as Simplified Chinese, Traditional Chinese, English, and Japanese. Key features include robust handling of complex layouts, varying text sizes, and challenging backgrounds, making it suitable for practical applications like document analysis, license plate recognition, and scene text detection. The key accuracy metrics are as follow:

| Handwritten Chinese | Handwritten English | Printed Chinese | Printed English | Traditional Chinese | Ancient Text | Japanese | General Scenario | Pinyin | Rotation | Distortion | Artistic Text | Average | 
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0.803 | 0.841 | 0.945	| 0.917	| 0.815 | 0.676 | 0.772	 | 0.797 | 0.671 | 0.8 | 0.876 | 0.673 | 0.827 |

## Model Usage

```python
import requests
from PIL import Image
from transformers import AutoImageProcessor, AutoModelForObjectDetection

model_path = "PaddlePaddle/PP-OCRV5_server_det_safetensors"
model = AutoModelForObjectDetection.from_pretrained(
    model_path,
    device_map="auto"
)
image_processor = AutoImageProcessor.from_pretrained(model_path)

image = Image.open(requests.get("https://paddle-model-ecology.bj.bcebos.com/paddlex/imgs/demo_image/general_ocr_001.png", stream=True).raw).convert("RGB")
inputs = image_processor(images=image, return_tensors="pt").to(model.device)
outputs = model(**inputs)

results = image_processor.post_process_object_detection(outputs, target_sizes=inputs["target_sizes"])

for result in results:
    print(result)
```