#!/usr/bin/env python3
"""
香港開放資料下載腳本：從官方開放數據平台下載法定古蹟及樓宇資料

資料來源：
1. 法定古蹟（Declared Monuments）— CSDI 開放數據（KML/KMZ 格式）
   https://static.csdi.gov.hk/csdi-webpage/download/423f82156f665956930626d3c303e2e1/kml
   KMZ 為 ZIP 壓縮檔，內含 .kml 檔案，解析 Placemark/SchemaData 取得結構化欄位。

2. 樓宇資料（Buildings）— 差餉物業估價署 RVD（XML 格式）
   市區: bnb-u.xml  |  新界: bnb-nt.xml
   XML 內含 <Record> 元素，欄位包括中英文名稱、地址、建成年份等。
"""
import io
import json
import os
import ssl
import urllib.request
import xml.etree.ElementTree as ET
import zipfile

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE

CSDI_KML_URL = (
    "https://static.csdi.gov.hk/csdi-webpage/download/"
    "423f82156f665956930626d3c303e2e1/kml"
)
RVD_URBAN_URL = (
    "https://res.data.gov.hk/api/get-download-file?"
    "name=https%3A%2F%2Fwww.rvd.gov.hk%2Fdatagovhk%2Fbnb-u.xml"
)
RVD_NT_URL = (
    "https://res.data.gov.hk/api/get-download-file?"
    "name=https%3A%2F%2Fwww.rvd.gov.hk%2Fdatagovhk%2Fbnb-nt.xml"
)

KML_NS = {"kml": "http://www.opengis.net/kml/2.2"}


def fetch_bytes(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, context=SSL_CTX, timeout=120) as resp:
        return resp.read()


def fetch_declared_monuments() -> list:
    print("⬇️  下載法定古蹟資料（來源：CSDI 開放數據 KML/KMZ）...")
    raw = fetch_bytes(CSDI_KML_URL)

    with zipfile.ZipFile(io.BytesIO(raw), "r") as zf:
        kml_names = [n for n in zf.namelist() if n.endswith(".kml")]
        if not kml_names:
            raise RuntimeError("KML 檔案不存在於 KMZ 壓縮檔內")
        kml_bytes = zf.read(kml_names[0])

    root = ET.fromstring(kml_bytes)
    placemarks = root.findall(".//kml:Placemark", KML_NS)

    monuments = []
    for pm in placemarks:
        schema_data = pm.find(".//kml:SchemaData", KML_NS)
        if schema_data is None:
            continue
        fields = {}
        for sd in schema_data.findall("kml:SimpleData", KML_NS):
            fields[sd.get("name")] = (sd.text or "").strip()

        monuments.append({
            "file_ref": fields.get("FILE_REF", ""),
            "name_en": fields.get("NAME", ""),
            "name_tc": fields.get("NAME_TC", ""),
            "address_en": fields.get("ADDRESS", ""),
            "address_tc": fields.get("ADDRESS_TC", ""),
            "district_en": fields.get("DISTRICT", ""),
            "district_tc": fields.get("DISTRIC_TC", ""),
            "declared_year": fields.get("DEC_YEAR", ""),
            "detail_url": fields.get("DETAIL", ""),
            "image_url": fields.get("URL_IMAGE", ""),
        })

    monuments.sort(key=lambda m: (m["declared_year"], m["name_tc"]))

    output_path = os.path.join(DATA_DIR, "declared_monuments.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "source": "CSDI Open Data (KML/KMZ)",
                "source_url": CSDI_KML_URL,
                "total_count": len(monuments),
                "monuments": monuments,
            },
            f,
            ensure_ascii=False,
            indent=2,
        )
    print(f"✅  法定古蹟：{len(monuments)} 項 → {output_path}")
    return monuments


def fetch_rvd_buildings(url: str, label: str) -> list:
    print(f"⬇️  下載樓宇資料（來源：差餉物業估價署 RVD — {label}）...")
    raw = fetch_bytes(url)
    root = ET.fromstring(raw)

    records = root.findall(".//Record")

    def get_text(rec, tag):
        el = rec.find(tag)
        return el.text.strip() if el is not None and el.text else ""

    buildings = []
    for rec in records:
        buildings.append({
            "name_en": get_text(rec, "EnglishBuildingName1"),
            "name_tc": get_text(rec, "ChineseBuildingName1"),
            "address_en": get_text(rec, "EnglishAddress1"),
            "address_tc": get_text(rec, "ChineseAddress1"),
            "year_built": get_text(rec, "YearBuild"),
            "owners_corporation": get_text(rec, "OwnersCorporation"),
            "housing_type_en": get_text(rec, "EnglishPublicHousingType"),
            "housing_type_tc": get_text(rec, "ChinesePublicHousingType"),
        })

    output_path = os.path.join(DATA_DIR, f"buildings_{label}.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "source": "Rating and Valuation Department (RVD)",
                "source_url": url,
                "total_count": len(buildings),
                "buildings": buildings,
            },
            f,
            ensure_ascii=False,
            indent=2,
        )
    print(f"✅  樓宇（{label}）：{len(buildings)} 項 → {output_path}")
    return buildings


def main():
    print("=== 香港開放資料下載 ===\n")
    fetch_declared_monuments()
    print()
    fetch_rvd_buildings(RVD_URBAN_URL, "urban")
    print()
    fetch_rvd_buildings(RVD_NT_URL, "nt")
    print("\n=== 下載完成 ===")


if __name__ == "__main__":
    main()
