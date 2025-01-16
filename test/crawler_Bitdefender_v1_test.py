import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 將參數存入 JSON 格式
config = {
    "url": "https://10.231.255.34/",
    "username": "2019051401@ad.dc",
    "password": "Zz800619",
    "elements": {
        "username_input": "textfield-1031-inputEl",
        "password_input": "textfield-1032-inputEl",
        "login_button": "main-loginForm-button-login-btnIconEl",
        "menu_item": "menu_item_license-btnInnerEl",
        "data_class": "x-grid-cell-inner"
    }
}

# 設定瀏覽器選項（避免 HTTPS 問題）
options = webdriver.ChromeOptions()
options.add_argument("--ignore-certificate-errors")
driver = webdriver.Chrome(options=options)

try:
    # 開啟目標網站
    driver.get(config["url"])

    # 填寫用戶名
    username_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, config["elements"]["username_input"]))
    )
    username_input.send_keys(config["username"])

    # 填寫密碼
    password_input = driver.find_element(By.ID, config["elements"]["password_input"])
    password_input.send_keys(config["password"])

    # 點擊登入按鈕
    try:
        submit_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, config["elements"]["login_button"]))
        )
        submit_button.click()
    except:
        print("按鈕無法點擊，嘗試使用 JavaScript 點擊")
        submit_button = driver.find_element(By.ID, config["elements"]["login_button"])
        driver.execute_script("arguments[0].click();", submit_button)

    print("登入成功")

    # 等待左側選單加載並點擊選項
    menu_item = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, config["elements"]["menu_item"]))
    )
    menu_item.click()
    print("已點擊左側選單項目")

    # 等待右側數據加載
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, config["elements"]["data_class"]))
    )

    # 抓取所有指定 class 的內容
    elements = driver.find_elements(By.CLASS_NAME, config["elements"]["data_class"])
    print("抓取的內容:")
    for element in elements:
        if "endpoints" in element.text:
            # 提取數字/數字的部分
            usage, total = element.text.split(" endpoints")[0].split("/")
            result = {
                "usage": int(usage.strip()),
                "total": int(total.strip())
            }
            print(json.dumps(result, indent=4))
            break

    # 停留在畫面，防止瀏覽器關閉
    input("操作完成，按 Enter 鍵關閉瀏覽器...")

finally:
    # 保留這個區塊，但不要關閉瀏覽器
    # driver.quit()
    pass
