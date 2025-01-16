from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from dotenv import load_dotenv
import psycopg2
import os
import json
import time

def crawl_bitdefender():
    # Load environment variables
    load_dotenv()

    # Database configuration
    DB_CONFIG = {
        "host": os.getenv("N_POSTGRES_SERVER"),
        "port": os.getenv("N_POSTGRES_PORT"),
        "user": os.getenv("N_POSTGRES_USER"),
        "password": os.getenv("N_POSTGRES_PASSWORD"),
        "dbname": os.getenv("N_POSTGRES_DB"),
    }

    # Selenium configuration
    config = {
        "url": "https://10.231.255.34/",
        "username": "2019051401@ad.dc",
        "password": "Zz800619",
        "elements": {
            "username_input": "textfield-1031-inputEl",
            "password_input": "textfield-1032-inputEl",
            "login_button": "main-loginForm-button-login",
            "menu_item": "menu_item_license-btnInnerEl",
            "data_class": "x-grid-cell-inner"
        }
    }

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-dev-shm-usage")   
    options.add_argument("--window-size=1920,1080") 
    options.add_argument("--disable-extensions")    
    options.add_argument("--remote-debugging-port=9222")  
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome(options=options)


    try:
        driver.get(config["url"])

        # Username input
        username_input = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, config["elements"]["username_input"]))
        )
        username_input.send_keys(config["username"])

        # Password input
        password_input = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, config["elements"]["password_input"]))
        )
        password_input.send_keys(config["password"])

        # Login button
        submit_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, config["elements"]["login_button"]))
        )
        submit_button.click()

        # Menu item
        menu_item = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.ID, config["elements"]["menu_item"]))
        )
        menu_item.click()

        # Data class elements
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, config["elements"]["data_class"]))
        )
        elements = driver.find_elements(By.CLASS_NAME, config["elements"]["data_class"])

        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        for element in elements:
            if "endpoints" in element.text:
                usage, total = element.text.split(" endpoints")[0].split("/")
                result = {
                    "usage": int(usage.strip()),
                    "total": int(total.strip())
                }

                cursor.execute(
                    """
                    INSERT INTO bitdefender_license (id, usage, total, updated_at)
                    VALUES (1, %s, %s, NOW())
                    ON CONFLICT (id) DO UPDATE SET usage = EXCLUDED.usage, total = EXCLUDED.total, updated_at = NOW()
                    """,
                    (result["usage"], result["total"])
                )
                conn.commit()
                break

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
        driver.quit()

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
dag = DAG(
    'crawl_bitdefender',
    default_args=default_args,
    description='A DAG to crawl Bitdefender license data and store in PostgreSQL',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2025, 1, 17),
    catchup=False,
)

# Python Operator to run the function
crawl_task = PythonOperator(
    task_id='crawl_bitdefender_task',
    python_callable=crawl_bitdefender,
    dag=dag,
)
