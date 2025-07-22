import re
import cv2
import numpy as np
from PIL import Image, ImageOps

def preprocess_image(pil_image, config):
    """
    Preprocesses an image using grayscale, contrast, thresholding, and optional resizing.
    """
    gray = pil_image.convert("L")
    if config["preprocessing"]["contrast"]:
        gray = ImageOps.autocontrast(gray)
    np_img = np.array(gray)
    if config["preprocessing"]["thresholding"]:
        _, np_img = cv2.threshold(np_img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    if config["preprocessing"]["resize"]["enabled"]:
        fx = config["preprocessing"]["resize"]["fx"]
        fy = config["preprocessing"]["resize"]["fy"]
        interp = getattr(cv2, config["preprocessing"]["resize"]["interpolation"])
        np_img = cv2.resize(np_img, None, fx=fx, fy=fy, interpolation=interp)
    return Image.fromarray(np_img)

def extract_number(text, config):
    """
    Converts OCR text to float using config-defined separators and symbol.
    """
    cleaned = text.replace(config["format"]["currency_symbol"], "").strip()
    cleaned = cleaned.replace(config["format"]["thousand_separator"], "")
    cleaned = cleaned.replace(config["format"]["decimal_separator"], ".")
    try:
        return float(cleaned)
    except:
        return None

def validate_numeric_format(text, fmt_cfg):
    """
    Validates if text matches expected numeric format, currency symbol position, and decimal precision.
    """
    symbol = re.escape(fmt_cfg["currency_symbol"])
    prefix = fmt_cfg["currency_position"] == "prefix"
    suffix = fmt_cfg["currency_position"] == "suffix"
    pattern = rf"^{symbol if prefix else ''}\s*[\d{re.escape(fmt_cfg['thousand_separator'])}{re.escape(fmt_cfg['decimal_separator'])}]+{symbol if suffix else ''}$"
    if not re.match(pattern, text):
        return None
    cleaned = text.replace(fmt_cfg["thousand_separator"], "").replace(fmt_cfg["decimal_separator"], ".")
    cleaned = cleaned.replace(fmt_cfg["currency_symbol"], "").strip()
    if fmt_cfg["decimals_required"]:
        if "." not in cleaned:
            return None
        decimals = cleaned.split(".")[1]
        if not (fmt_cfg["min_decimals"] <= len(decimals) <= fmt_cfg["max_decimals"]):
            return None
    return cleaned
