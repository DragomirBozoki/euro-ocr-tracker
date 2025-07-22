from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from PIL import Image, ImageOps
import pytesseract
import cv2
import numpy as np
import time
from datetime import datetime
import os

# If you're on Windows and Tesseract is not in PATH, set its full path below
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# === Parameters and Paths ===
interval = 1  # Time delay between each screenshot (in seconds)
screenshot_folder = "./screenshots/"
processed_folder = "./processed/"
log_file = "ocr_log.csv"

# Create folders if they do not exist
os.makedirs(screenshot_folder, exist_ok=True)
os.makedirs(processed_folder, exist_ok=True)

# === Initialize Firefox WebDriver ===
options = Options()
driver = webdriver.Firefox(options=options)

# Open the target webpage where the number is displayed
driver.get("https://v0-random-number-display-olive.vercel.app/")
time.sleep(2)  # Wait for the page to load fully

# === Image Preprocessing Function ===
def preprocess_image(pil_image):
    """
    Converts the input PIL image to grayscale, enhances contrast,
    applies Otsu's thresholding, and resizes it for better OCR accuracy.
    """
    gray = pil_image.convert("L")
    gray = ImageOps.autocontrast(gray)
    np_img = np.array(gray)
    _, thresh = cv2.threshold(np_img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    resized = cv2.resize(thresh, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    return Image.fromarray(resized)

# Create log file with header if it doesn't exist yet
if not os.path.exists(log_file):
    with open(log_file, "w") as f:
        f.write("timestamp,ocr_result\n")

print("▸ Monitoring started (1s interval). Press Ctrl+C to stop.")

# Keep track of the last stable OCR result to prevent invalid drops
last_valid_text = None

# === Helper Function to Parse OCR Text ===
def extract_number(text):
    """
    Converts OCR string to a float by removing € and commas.
    Returns None if conversion fails.
    """
    try:
        return float(text.replace("€", "").replace(",", ""))
    except:
        return None

# === Main Monitoring Loop ===
try:
    while True:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # 1. Take Screenshot
        screenshot_path = os.path.join(screenshot_folder, f"screenshot_{timestamp}.png")
        driver.save_screenshot(screenshot_path)
        print(f"✓ Screenshot saved: {screenshot_path}")

        # 2. Crop region where the number appears
        full_img = Image.open(screenshot_path)
        cropped = full_img.crop((0, 200, 1550, 600))  # These coordinates depend on your screen setup

        # 3. Preprocess the cropped image
        processed_img = preprocess_image(cropped)

        # 4. Save the processed image
        processed_path = os.path.join(processed_folder, f"processed_{timestamp}.png")
        processed_img.save(processed_path)
        print(f"✓ Processed image saved: {processed_path}")

        # 5. Perform OCR using Tesseract with a restricted character set
        raw_text = pytesseract.image_to_string(
            processed_img,
            config='--psm 7 -c tessedit_char_whitelist=0123456789.,€'
        ).strip()

        # 6. Validate and compare with last valid result
        if len(raw_text) < 3:
            # Likely garbage (e.g. just "€", "", or "1")
            print("⚠︎ Invalid OCR result. Reusing last stable value:")
            print(f"  → {last_valid_text if last_valid_text else 'None'}")
        else:
            current_value = extract_number(raw_text)
            previous_value = extract_number(last_valid_text) if last_valid_text else None

            # Reject current value if it's numerically lower than the last (assumes monotonic increase)
            if previous_value is not None and current_value is not None and current_value < previous_value:
                print(f"⚠︎ Value dropped from {previous_value} to {current_value}. Keeping last stable value:")
                print(f"  → {last_valid_text}")
            else:
                # Accept new value
                print(f"→ OCR: {raw_text}")
                last_valid_text = raw_text

                # Write to log
                with open(log_file, "a") as f:
                    f.write(f"{timestamp},{raw_text}\n")

        # Wait before next iteration
        time.sleep(interval)

except KeyboardInterrupt:
    print("\n■ Monitoring stopped.")
    driver.quit()
