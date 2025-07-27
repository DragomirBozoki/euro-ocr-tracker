#!/usr/bin/env python3
import os
import time
import yaml
import pytesseract
from PIL import Image
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

from helper import preprocess_image  # koristi tvoj preprocessing.py


def load_config(path: str = "config.yaml"):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def ensure_dirs(paths_cfg):
    os.makedirs(paths_cfg["screenshot_folder"], exist_ok=True)
    os.makedirs(paths_cfg["processed_folder"], exist_ok=True)


def clear_old_files(paths_cfg):
    for folder in [paths_cfg["screenshot_folder"], paths_cfg["processed_folder"]]:
        for file_name in os.listdir(folder):
            file_path = os.path.join(folder, file_name)
            if os.path.isfile(file_path):
                os.remove(file_path)
    print("✔ Old files removed from folders.")


def init_driver(url: str, headless: bool = False):
    options = Options()
    if headless:
        options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)
    driver.get(url)
    time.sleep(2)
    return driver


def init_log(log_path: str, jp_levels):
    header = "timestamp," + ",".join([f"{lvl['name']} OCR TEXT" for lvl in jp_levels])
    if not os.path.exists(log_path):
        with open(log_path, "w", encoding="utf-8") as f:
            f.write(header + "\n")


def main():
    config = load_config("config.yaml")

    ensure_dirs(config["paths"])
    clear_old_files(config["paths"])

    init_log(config["paths"]["log_file"], config["jp_levels"])

    driver = init_driver(config["target_url"], headless=False)

    print(f"▶ Monitoring started (interval: {config['interval']}s). Press Ctrl+C to stop.\n")

    try:
        while True:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # === Screenshot
            screenshot_path = os.path.join(
                config["paths"]["screenshot_folder"],
                f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            )
            driver.save_screenshot(screenshot_path)
            print(f"[{timestamp}] Screenshot saved: {screenshot_path}")

            full_img = Image.open(screenshot_path)
            ocr_results = {}

            for level_conf in config["jp_levels"]:
                level_name = level_conf["name"]
                crop_box = tuple(level_conf["crop_region"])
                cropped = full_img.crop(crop_box)

                # Preprocess
                processed_img = preprocess_image(cropped, config, level_name)
                processed_path = os.path.join(
                    config["paths"]["processed_folder"],
                    f"{level_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                )
                processed_img.save(processed_path)

                # OCR
                tesseract_config = (
                    f'--psm {config["ocr"]["psm"]} '
                    f'--oem {config["ocr"]["oem"]} '
                    f'-c tessedit_char_whitelist="{config["ocr"]["whitelist"]}"'
                )
                raw_text = pytesseract.image_to_string(processed_img, config=tesseract_config).strip()

                # Log
                print(f"   {level_name} OCR TEXT: {raw_text}")
                ocr_results[level_name] = raw_text

            # Save to CSV
            with open(config["paths"]["log_file"], "a", encoding="utf-8") as f:
                row = datetime.now().strftime("%Y%m%d_%H%M%S") + "," + ",".join(
                    ocr_results.get(lvl["name"], "") for lvl in config["jp_levels"]
                )
                f.write(row + "\n")

            print("-" * 60)  # separator
            time.sleep(config["interval"])

    except KeyboardInterrupt:
        print("\n■ Monitoring stopped.")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
