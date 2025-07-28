# euro-ocr-tracker
```
→ OCR: 1,092.9
→ OCR: 1,103.7
→ OCR: 1,113.4
→ OCR: 1,122.4
⚠︎ Invalid OCR result. Reusing last stable value:
  → 1,122.4
→ OCR: 1,154.7
⚠︎ Value dropped from 1218.4 to 140.0. Keeping last stable value:
  → 1,218.4
```

The system automatically detects when OCR output is likely incorrect and logs a warning while displaying the last stable value instead.


This prevents sudden drops or misreadings (e.g., from noise or partial screenshots) from affecting the results.

### Accuracy of OCR Detection

In the sample session, out of **65** captured screenshots:
- 111 were successfully and correctly parsed.
- 4 were marked as invalid and ignored.

**OCR stability rate: 3.48%**

OCR System Functionalities

    Live website monitoring

    Periodic screenshot capturing

    Image cropping

    Image preprocessing (contrast, thresholding, resizing)

    OCR extraction using Tesseract

    Custom character whitelist for OCR

    Locale-aware number parsing

    Decimal and thousand separator normalization

    Currency symbol handling

    Validation of numerical format and digit limits

    Spike/drop filtering based on thresholds

    Rollover detection and handling

    Structured logging (CSV format with timestamp)

    Saving original and processed images

    Error handling for failed OCR or parsing

# MQTT OCR Config Broadcaster

This project reads a local `config.yaml` file, converts it to JSON, and repeatedly sends it via MQTT to a defined topic. It's designed for use cases where systems (e.g., OCR pipelines or embedded devices) subscribe to dynamic configuration parameters.

---

## 🚀 Features

- Reads configuration from a YAML file
- Converts and publishes it as JSON via MQTT
- Publishes periodically (based on interval in config)
- Works in any environment via Docker
- Easily extendable to support camera capture, Selenium, OCR, etc.

---

## ⚙️ How It Works

1. You edit the `config.yaml` file to define parameters (thresholds, regions, intervals, etc.).
2. The Python script reads the file and converts it into a structured JSON payload.
3. The payload is sent to a specific MQTT topic (e.g., `test/ocr/config`) at regular intervals.
4. Any subscriber connected to that topic will receive the updated configuration and can act on it.
5. You can package everything into Docker to eliminate all dependencies.

---

## 🐳 Using Docker

### 1. Build the Docker image:

```bash
docker build -t mqtt-ocr .

docker run --rm -it mqtt-ocr

docker run --rm -it -v $PWD/config.yaml:/app/config.yaml mqtt-ocr


