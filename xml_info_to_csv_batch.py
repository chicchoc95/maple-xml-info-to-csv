import xml.etree.ElementTree as ET
import csv
import sys
from pathlib import Path


def extract_info_dict(xml_path: Path):
    """하나의 XML에서 <dir name="info">를 dict로 추출."""
    tree = ET.parse(xml_path)
    root = tree.getroot()

    info_dir = None
    for child in root.findall("dir"):
        if child.get("name") == "info":
            info_dir = child
            break

    if info_dir is None:
        raise ValueError("No <dir name='info'> found in XML")

    keys_in_order = []
    info = {}

    for node in list(info_dir):
        name = node.get("name")
        value = node.get("value")
        if name is None or value is None:
            continue
        if name not in info:
            keys_in_order.append(name)
        info[name] = value

    if not info:
        raise ValueError("No name/value pairs found in <dir name='info'>")

    return keys_in_order, info


def process_directory_to_single_csv(dir_path: Path, output_csv: Path):
    """폴더 안의 모든 XML을 하나의 CSV로 합치기."""
    xml_files = sorted(dir_path.glob("*.xml"))
    if not xml_files:
        print(f"[INFO] No .xml files found in: {dir_path}")
        return

    print(f"[INFO] Found {len(xml_files)} XML file(s) in {dir_path}")

    # 전체 헤더(항목 이름)와 각 XML의 값들 저장
    header_keys = []   # bodyAttack, level, ...
    rows = []          # (id, info_dict)

    for xml_path in xml_files:
        try:
            keys_in_order, info = extract_info_dict(xml_path)
        except Exception as e:
            print(f"[WARN] Skipping {xml_path.name}: {e}")
            continue

        # 전역 헤더 리스트에 없던 키가 나오면 뒤에 추가
        for k in keys_in_order:
            if k not in header_keys:
                header_keys.append(k)

        stem = xml_path.stem            # "Mob.0100100.img"
parts = stem.split(".")         # ["Mob", "0100100", "img"]
mob_id = parts[1]               # "0100100"
        rows.append((mob_id, info))

    if not rows:
        print("[INFO] No valid XML files with <dir name='info'> were processed.")
        return

    # CSV 한 개로 쓰기
    with output_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        # 맨 앞 컬럼은 id(파일 이름), 그 뒤에 항목들
        header = ["id"] + header_keys
        writer.writerow(header)

        for mob_id, info in rows:
            row = [mob_id]
            for key in header_keys:
                row.append(info.get(key, ""))  # 없는 항목은 빈칸
            writer.writerow(row)

    print(f"[OK] Saved combined CSV: {output_csv}")


def main():
    # 사용법:
    #   python xml_info_to_csv_batch.py
    #       -> 현재 폴더의 *.xml 전체를 모아서 mob_info_all.csv 생성
    #
    #   python xml_info_to_csv_batch.py path/to/folder
    #       -> 지정 폴더의 *.xml 전체를 모아서 그 폴더에 mob_info_all.csv 생성
    #
    #   python xml_info_to_csv_batch.py path/to/file.xml
    #       -> 그 파일이 있는 폴더 기준으로 mob_info_all.csv 생성
    if len(sys.argv) >= 2:
        target = Path(sys.argv[1])
    else:
        target = Path(".")

    if not target.exists():
        print(f"[ERROR] Path not found: {target}")
        sys.exit(1)

    if target.is_file():
        if target.suffix.lower() == ".xml":
            dir_path = target.parent
            output_csv = dir_path / "mob_info_all.csv"
            process_directory_to_single_csv(dir_path, output_csv)
        else:
            print("[ERROR] Target is a file but not .xml")
            sys.exit(1)
    else:
        dir_path = target
        output_csv = dir_path / "mob_info_all.csv"
        process_directory_to_single_csv(dir_path, output_csv)


if __name__ == "__main__":
    main()
