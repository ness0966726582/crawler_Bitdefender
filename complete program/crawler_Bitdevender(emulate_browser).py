#不開啟瀏覽器的模擬emulate版本 .env增加config

import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from dotenv import load_dotenv
import psycopg2
import time

# 加載.env文件
load_dotenv()

# 獲取環境變數
DB_CONFIG = {
    "host": os.getenv("N_POSTGRES_SERVER"),
    "port": os.getenv("N_POSTGRES_PORT"),
    "user": os.getenv("N_POSTGRES_USER"),
    "password": os.getenv("N_POSTGRES_PASSWORD"),
    "dbname": os.getenv("N_POSTGRES_DB"),
}

# 將參數存入 JSON 格式
config = {
    "url": "https://10.231.255.34/",
    "username": "YOUR ACCOUNT",
    "password": "YOUR PASSWORD",
    "elements": {
        "username_input": "textfield-1031-inputEl",
        "password_input": "textfield-1032-inputEl",
        "login_button": "main-loginForm-button-login",
        "menu_item": "menu_item_license-btnInnerEl",
        "data_class": "x-grid-cell-inner"
    }
}

# 設定瀏覽器選項（模擬正常瀏覽器 + 避免 HTTPS 問題）
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # 啟用無頭模式
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--ignore-certificate-errors")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)
driver = webdriver.Chrome(options=options)

try:
    # 開啟目標網站
    driver.get(config["url"])

    # 填寫用戶名
    try:
        username_input = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, config["elements"]["username_input"]))
        )
        username_input.send_keys(config["username"])
    except TimeoutException:
        driver.save_screenshot("timeout_username_input.png")
        print("用戶名輸入框加載超時，已捕獲截圖")
        raise

    # 填寫密碼
    try:
        password_input = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, config["elements"]["password_input"]))
        )
        password_input.send_keys(config["password"])
    except TimeoutException:
        driver.save_screenshot("timeout_password_input.png")
        print("密碼輸入框加載超時，已捕獲截圖")
        raise
    
    # 點擊登入按鈕
    try:
        submit_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, config["elements"]["login_button"]))
        )
        submit_button.click()
    except TimeoutException:
        driver.save_screenshot("timeout_login_button.png")
        print("登入按鈕無法點擊，已捕獲截圖")
        raise

    print("登入成功")

    # 等待左側選單加載並點擊選項
    try:
        menu_item = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.ID, config["elements"]["menu_item"]))
        )
        menu_item.click()
        print("已點擊左側選單項目")
    except TimeoutException:
        driver.save_screenshot("timeout_menu_item.png")
        print("選單項目無法點擊，已捕獲截圖")
        raise

    # 等待右側數據加載
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, config["elements"]["data_class"]))
        )
    except TimeoutException:
        driver.save_screenshot("timeout_data_class.png")
        print("數據加載超時，已捕獲截圖")
        raise

    # 抓取所有指定 class 的內容
    elements = driver.find_elements(By.CLASS_NAME, config["elements"]["data_class"])
    print("抓取的內容:")

    # 初始化資料庫連線
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    for element in elements:
        if "endpoints" in element.text:
            # 提取數字/數字的部分
            usage, total = element.text.split(" endpoints")[0].split("/")
            result = {
                "usage": int(usage.strip()),
                "total": int(total.strip())
            }
            print(json.dumps(result, indent=4))

            # 插入或更新資料表
            cursor.execute("""
                INSERT INTO bitdefender_license (id, usage, total, updated_at)
                VALUES (1, %s, %s, NOW())
                ON CONFLICT (id) DO UPDATE SET usage = EXCLUDED.usage, total = EXCLUDED.total, updated_at = NOW()
            """, (result["usage"], result["total"]))

            conn.commit()
            print("資料已更新至資料表")
            break

finally:
    # 釋放資源
    if 'cursor' in locals():
        cursor.close()
    if 'conn' in locals():
        conn.close()
    driver.quit()
    print("瀏覽器已關閉")



