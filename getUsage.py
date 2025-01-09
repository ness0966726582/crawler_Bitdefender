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
    username_input.send_keys("2019051401@ad.dc")

    # 填寫密碼
    password_input = driver.find_element(By.ID, "textfield-1032-inputEl")
    password_input.send_keys("Zz800619")

    # 點擊登入按鈕
    try:
        submit_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "main-loginForm-button-login-btnIconEl"))
        )
        submit_button.click()
    except:
        print("按鈕無法點擊，嘗試使用 JavaScript 點擊")
        submit_button = driver.find_element(By.ID, "main-loginForm-button-login-btnIconEl")
        driver.execute_script("arguments[0].click();", submit_button)

    print("登入成功")

    # 等待左側選單加載並點擊選項（menu_item_license）
    menu_item = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "menu_item_license-btnInnerEl"))
    )
    menu_item.click()
    print("已點擊左側選單項目")

    # 等待右側數據加載
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "x-grid-cell-inner"))
    )

    # 抓取所有 class="x-grid-cell-inner " 的內容
    elements = driver.find_elements(By.CLASS_NAME, "x-grid-cell-inner")
    print("抓取的內容:")
    for i, element in enumerate(elements):
        print(f"元素 {i + 1}: {element.text}")

    # 停留在畫面，防止瀏覽器關閉
    input("操作完成，按 Enter 鍵關閉瀏覽器...")

finally:
    # 保留這個區塊，但不要關閉瀏覽器
    # driver.quit()
    pass
