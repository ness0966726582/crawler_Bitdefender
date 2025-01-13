import os
import psycopg2
from dotenv import load_dotenv

# 載入 .env 檔案
load_dotenv()

# 獲取環境變數
DB_CONFIG = {
    "host": os.getenv("N_POSTGRES_SERVER"),
    "port": os.getenv("N_POSTGRES_PORT"),
    "user": os.getenv("N_POSTGRES_USER"),
    "password": os.getenv("N_POSTGRES_PASSWORD"),
    "dbname": os.getenv("N_POSTGRES_DB"),
}

# 創建資料表
def create_table():
    try:
        connection = psycopg2.connect(**DB_CONFIG)
        cursor = connection.cursor()

        create_table_query = """
        CREATE TABLE IF NOT EXISTS bitdefender_license (
            id SERIAL PRIMARY KEY,
            usage INTEGER NOT NULL,
            total INTEGER NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        cursor.execute(create_table_query)

        # 如果資料表已存在，檢查並新增缺少的欄位
        add_column_query = """
        DO $$ 
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name='bitdefender_license' AND column_name='updated_at'
            ) THEN
                ALTER TABLE bitdefender_license
                ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
            END IF;
        END;
        $$;
        """
        cursor.execute(add_column_query)

        connection.commit()
        print("資料表創建或更新成功")

    except Exception as e:
        print(f"發生錯誤: {e}")
    finally:
        if connection:
            cursor.close()
            connection.close()

if __name__ == "__main__":
    create_table()
