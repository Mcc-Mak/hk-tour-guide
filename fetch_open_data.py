#!/usr/bin/env python3
"""
香港開放資料下載腳本：從官方來源下載歷史建築與古蹟資料
"""
import os
import urllib.request

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

DATA_SOURCES = {
    "monuments_info.xml": "https://www.amo.gov.hk/filemanager/amo/common/form/declared_monuments_tc.xml",
    "historic_buildings.json": "https://api.data.gov.hk/v1/filter?q=%7B%22resource%22%3A%22http%3A%2F%2Fwww.amo.gov.hk%2Fdatagovhk%2Fmonument_tc.json%22%7D"
}

def download_open_data():
    print("⬇️ 開始下載香港開放資料集...")
    for filename, url in DATA_SOURCES.items():
        filepath = os.path.join(DATA_DIR, filename)
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response, open(filepath, 'wb') as out_file:
                out_file.write(response.read())
            print(f"✅ 成功下載: {filename}")
        except Exception as e:
            print(f"⚠️ 下載 {filename} 失敗: {e}，建立本地參考備用檔。")
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("<data><status>Local Fallback Reference</status></data>")

if __name__ == "__main__":
    download_open_data()
