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

    header_keys = []
    rows = []

    for xml_path in xml_files:
        try:
            keys_in_order, info = extract_info_dict(xml_path)
        except Exception as e:
            print(f"[WARN] Skipping {xml_path.name}: {e}")
            continue

        for k in keys_in_order:
            if k not in header_keys:
                header_keys.append(k)

        # ---------- 파일명에서 0100100 추출 ----------
        stem = xml_path.stem                 # "Mob.0100100.img"
        parts = stem.split(".")              # ["Mob","0100100","img"]
        if len(parts) >= 2:
            mob_id = parts[1]               # "0100100"
        else:
            mob_id = stem                    # 혹시 예외적 파일명일 경우 대비
        # ---------------------------------------------

        rows.append((mob_id, info))

    if not rows:
        print("[INFO] No valid XML files found.")
        return

    # ---------- CSV 생성 ----------
    with output_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        header = ["id"] + header_keys
        writer.writerow(header)

        for mob_id, info in rows:
            row = [mob_id]
            for key in header_keys:
                row.append(info.get(key, ""))
            writer.writerow(row)

    print(f"[OK] Saved combined CSV: {output_csv}")


def main():
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
