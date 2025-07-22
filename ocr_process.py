import os
import time
import yaml
import pytesseract
from PIL import Image
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

from helper import preprocess_image, extract_number

# === Load config ===
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

# === Create folders ===
os.makedirs(config["paths"]["screenshot_folder"], exist_ok=True)
os.makedirs(config["paths"]["processed_folder"], exist_ok=True)

# === Selenium setup ===
options = Options()
driver = webdriver.Firefox(options=options)
driver.get(config["target_url"])
time.sleep(2)

# === Init log ===
if not os.path.exists(config["paths"]["log_file"]):
    with open(config["paths"]["log_file"], "w") as f:
        f.write("timestamp,ocr_result\n")

print("▸ Monitoring started (interval: {}s). Press Ctrl+C to stop.".format(config["interval"]))
last_valid_text = None

try:
    while True:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Screenshot
        screenshot_path = os.path.join(config["paths"]["screenshot_folder"], f"screenshot_{timestamp}.png")
        driver.save_screenshot(screenshot_path)
        print(f"✓ Screenshot saved: {screenshot_path}")

        # Crop & preprocess
        full_img = Image.open(screenshot_path)
        cropped = full_img.crop(tuple(config["crop_region"]))
        processed_img = preprocess_image(cropped, config)
        processed_path = os.path.join(config["paths"]["processed_folder"], f"processed_{timestamp}.png")
        processed_img.save(processed_path)
        print(f"✓ Processed image saved: {processed_path}")

        # OCR
        tesseract_config = f"--psm {config['ocr']['psm']} -c tessedit_char_whitelist={config['ocr']['whitelist']}"
        raw_text = pytesseract.image_to_string(processed_img, config=tesseract_config).strip()
        print(f"→ Raw OCR: {raw_text}")

        # Parse
        extracted = extract_number(raw_text, config)
        if extracted is None:
            print("⚠︎ Could not parse OCR text to number. Keeping last stable value:")
            print(f"  → {last_valid_text if last_valid_text else 'None'}")
            time.sleep(config["interval"])
            continue

        # Check digits before decimal
        before_decimal = str(int(extracted)).replace(config["format"]["thousand_separator"], "")
        if len(before_decimal) > config["format"]["max_digits_before_decimal"]:
            print(f"⚠︎ Too many digits before decimal point ({before_decimal}). Ignoring OCR result.")
            time.sleep(config["interval"])
            continue

        print(f"✓ Valid OCR: {extracted}")

        # Compare to last valid
        if last_valid_text:
            previous = extract_number(last_valid_text, config)
            if previous is not None:
                delta = abs(extracted - previous)

                # Ignore unrealistic jump up
                if extracted > previous and delta > config["format"]["max_change"]:
                    print(f"⚠︎ Value jumped from {previous} to {extracted} (Δ={delta}). Keeping last stable value:")
                    print(f"  → {last_valid_text}")
                    time.sleep(config["interval"])
                    continue

                # Ignore unrealistic drop down unless previous was too high
                if extracted < previous and delta > config["format"]["max_drop"]:
                    if previous < config["format"]["reset_threshold"]:
                        print(f"⚠︎ Value dropped from {previous} to {extracted} (Δ={delta}). Keeping last stable value:")
                        print(f"  → {last_valid_text}")
                        time.sleep(config["interval"])
                        continue

        # Accept
        last_valid_text = raw_text
        with open(config["paths"]["log_file"], "a") as f:
            f.write(f"{timestamp},{raw_text}\n")

        time.sleep(config["interval"])

except KeyboardInterrupt:
    print("\n■ Monitoring stopped.")
    driver.quit()
