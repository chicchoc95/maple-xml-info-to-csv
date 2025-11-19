# xml_info_to_csv_batch.py
import xml.etree.ElementTree as ET
import csv
import sys
from pathlib import Path


def extract_info(xml_path: Path):
    """하나의 XML 파일에서 <dir name="info"> 안의 name/value 들을 추출."""
    tree = ET.parse(xml_path)
    root = tree.getroot()

    info_dir = None
    # <dir name="info"> 찾기
    for child in root.findall("dir"):
        if child.get("name") == "info":
            info_dir = child
            break

    if info_dir is None:
        raise ValueError("No <dir name='info'> found in XML")

    keys = []
    values = []

    # info 안의 태그들(<int32>, <single> 등)을 순서대로 읽기
    for node in list(info_dir):
        name = node.get("name")
        value = node.get("value")

        # name 또는 value가 없는 노드는 스킵
        if name is None or value is None:
            continue

        keys.append(name)
        values.append(value)

    if not keys:
        raise ValueError("No name/value pairs found in <dir name='info'>")

    return keys, values


def process_directory(dir_path: Path):
    """지정한 폴더 안의 모든 .xml 파일을 돌면서 각자 csv 생성."""
    xml_files = sorted(dir_path.glob("*.xml"))

    if not xml_files:
        print(f"[INFO] No .xml files found in: {dir_path}")
        return

    print(f"[INFO] Found {len(xml_files)} XML file(s) in {dir_path}")

    for xml_path in xml_files:
        csv_path = xml_path.with_suffix(".csv")
        print(f"[INFO] Processing {xml_path.name} -> {csv_path.name}")

        try:
            keys, values = extract_info(xml_path)
        except Exception as e:
            print(f"[WARN] Skipping {xml_path.name}: {e}")
            continue

        with csv_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(keys)    # 1행: 항목 이름들
            writer.writerow(values)  # 2행: 값들

        print(f"[OK] Saved CSV: {csv_path.name}")


def process_single_file(xml_path: Path):
    """단일 XML 파일을 CSV로 변환."""
    csv_path = xml_path.with_suffix(".csv")
    print(f"[INFO] Processing {xml_path.name} -> {csv_path.name}")

    keys, values = extract_info(xml_path)

    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(keys)
        writer.writerow(values)

    print(f"[OK] Saved CSV: {csv_path.name}")


def main():
    # 사용법:
    #   python xml_info_to_csv_batch.py            -> 현재 폴더의 *.xml 전부 처리
    #   python xml_info_to_csv_batch.py path/to/folder
    #   python xml_info_to_csv_batch.py path/to/file.xml
    if len(sys.argv) >= 2:
        target = Path(sys.argv[1])
    else:
        target = Path(".")

    if not target.exists():
        print(f"[ERROR] Path not found: {target}")
        sys.exit(1)

    if target.is_file():
        if target.suffix.lower() == ".xml":
            process_single_file(target)
        else:
            print("[ERROR] Target is a file but not .xml")
            sys.exit(1)
    else:
        # 폴더인 경우: 폴더 안의 *.xml 전체 처리
        process_directory(target)


if __name__ == "__main__":
    main()
