#"username": "YOUR ACCOUNT",
#"password": "YOUR PASSWORD",

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 設定瀏覽器選項（避免 HTTPS 問題）
options = webdriver.ChromeOptions()
options.add_argument("--ignore-certificate-errors")
driver = webdriver.Chrome(options=options)

try:
    # 開啟目標網站
    driver.get("https://10.231.255.34/")

    # 填寫用戶名
    username_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "textfield-1031-inputEl"))
    )
    username_input.send_keys("YOUR ACCOUNT")

    # 填寫密碼
    password_input = driver.find_element(By.ID, "textfield-1032-inputEl")
    password_input.send_keys("YOUR PASSWORD")

    # 等待按鈕並點擊
    try:
        # 使用 WebDriverWait
        submit_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "main-loginForm-button-login-btnIconEl"))
        )
        submit_button.click()
    except:
        print("按鈕無法點擊，嘗試使用 JavaScript 點擊")
        # 使用 JavaScript 點擊按鈕
        submit_button = driver.find_element(By.ID, "main-loginForm-button-login-btnIconEl")
        driver.execute_script("arguments[0].click();", submit_button)

    print("登入成功")

finally:
    # 保留這個區塊，但不要關閉瀏覽器
    # driver.quit()
    pass
