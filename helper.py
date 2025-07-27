import re
import cv2
import numpy as np
from PIL import Image, ImageOps


def preprocess_image(pil_image, config, level_name):
    """
    Preprocesses an image using grayscale, contrast, thresholding (with per-level thresholds),
    and optional resizing.
    """
    gray = pil_image.convert("L")

    # Apply autocontrast if enabled
    if config["preprocessing"].get("contrast", False):
        gray = ImageOps.autocontrast(gray)

    np_img = np.array(gray)

    # Thresholding
    if config["preprocessing"].get("thresholding", False):
        thr_map = config["preprocessing"].get("threshold_values", {})
        thr_key = level_name.lower()
        threshold_value = thr_map.get(thr_key, 150)  # default 150 if not found
        _, np_img = cv2.threshold(np_img, threshold_value, 255, cv2.THRESH_BINARY)

    # Resize
    resize_cfg = config["preprocessing"].get("resize", {})
    if resize_cfg.get("enabled", False):
        fx = resize_cfg.get("fx", 1)
        fy = resize_cfg.get("fy", 1)
        interp_name = resize_cfg.get("interpolation", "INTER_CUBIC")
        interp = getattr(cv2, interp_name, cv2.INTER_CUBIC)
        np_img = cv2.resize(np_img, None, fx=fx, fy=fy, interpolation=interp)

    return Image.fromarray(np_img)


def extract_number(text, config):
    """
    Converts OCR text to float using config-defined separators and symbol.
    """
    if not text:
        return None
    cleaned = text.replace(config["format"]["currency_symbol"], "").strip()
    cleaned = cleaned.replace(config["format"]["thousand_separator"], "")
    cleaned = cleaned.replace(config["format"]["decimal_separator"], ".")
    try:
        return float(cleaned)
    except ValueError:
        return None


def validate_numeric_format(text, fmt_cfg):
    """
    Validates if text matches expected numeric format, currency symbol position, and decimal precision.
    """
    if not text:
        return None

    symbol = re.escape(fmt_cfg["currency_symbol"])
    prefix = fmt_cfg["currency_position"] == "prefix"
    suffix = fmt_cfg["currency_position"] == "suffix"

    pattern = (
        rf"^{symbol if prefix else ''}\s*"
        rf"[\d{re.escape(fmt_cfg['thousand_separator'])}{re.escape(fmt_cfg['decimal_separator'])}]+"
        rf"{symbol if suffix else ''}$"
    )

    if not re.match(pattern, text):
        return None

    cleaned = (
        text.replace(fmt_cfg["thousand_separator"], "")
        .replace(fmt_cfg["decimal_separator"], ".")
        .replace(fmt_cfg["currency_symbol"], "")
        .strip()
    )

    if fmt_cfg.get("decimals_required", False):
        if "." not in cleaned:
            return None
        decimals = cleaned.split(".")[1]
        if not (fmt_cfg["min_decimals"] <= len(decimals) <= fmt_cfg["max_decimals"]):
            return None

    return cleaned
