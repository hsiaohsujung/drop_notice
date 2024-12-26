from selenium import webdriver
from selenium.webdriver.common.by import By
from datetime import datetime, timedelta
import time

# 目標網址
DISCORD_CHANNEL_URL = "https://discord.com/channels/1053982055677046824/1100977750954754108?noapp=1"

# 自定義 Chrome 設定檔路徑
CHROME_USER_DATA_DIR = "C:/Users/Sasha/AppData/Local/Google/Chrome/User Data"
PROFILE_NAME = "Default"  # 例如: "Default", "Profile 1", "Profile 2"

def get_filtered_lines():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument(f"user-data-dir={CHROME_USER_DATA_DIR}")
    chrome_options.add_argument(f"profile-directory={PROFILE_NAME}")

    # 啟動 Chrome 瀏覽器
    driver = webdriver.Chrome(options=chrome_options)
    try:
        driver.get(DISCORD_CHANNEL_URL)
        time.sleep(5)

        # 生成五天的日期清單
        today = datetime.now()
        target_dates = [(today - timedelta(days=i)).strftime("%Y%m%d") for i in range(5)]

        span_elements = driver.find_elements(By.TAG_NAME, "span")
        start_recording = False
        content_lines = []

        for span in span_elements:
            text = span.text.strip()
            if any(date in text for date in target_dates):
                start_recording = True
                continue
            if start_recording and text:
                content_lines.append(text)

        # 過濾標的名稱
        filtered_lines = []
        record_section = None
        for line in content_lines:
            line = line.strip()
            if "強勢族群：" in line or "次強勢族群：" in line:
                record_section = True
                filtered_lines.append(line.split("：")[1].strip().replace(" ", ""))  # 去除空格
                continue
            if record_section and line.startswith(","):
                filtered_lines.append(line.lstrip(",").strip().replace(" ", ""))  # 去除空格

        return sorted(set(filtered_lines))  # 去除重複標的

    except Exception as e:
        print(f"發生錯誤: {e}")
        return []
    finally:
        time.sleep(10)
        driver.quit()