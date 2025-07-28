import os
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path
from collections import defaultdict
import random

# ---- CONFIGURATION ----
RAW_BASE = Path("DATA/Training/raw/TS")
LABEL_BASE = Path("DATA/Training/label/TS")
OUTPUT_BASE = Path("DATA/TRAIN")
NUM_SETS = 20


def parse_xml(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()

    mode = root.findtext("CAMERA/mode", default="0")
    obj = root.find("OBJECT")
    object_id = obj.attrib.get("ID")
    upper = obj.findtext("upperclothes", "NULL")
    upper_color = obj.findtext("upperclothes_color", "NULL")
    lower = obj.findtext("lowerclothes", "NULL")
    lower_color = obj.findtext("lowerclothes_color", "NULL")

    foldername = f"{object_id}_{upper}_{upper_color}_{lower}_{lower_color}"
    return mode, foldername


def collect_valid_images():
    folder_to_images = defaultdict(list)

    for group in os.listdir(RAW_BASE):
        group_path = RAW_BASE / group
        label_group_path = LABEL_BASE / group

        for human_id in os.listdir(group_path):
            for cam_setting in os.listdir(group_path / human_id):
                for camera_id in os.listdir(group_path / human_id / cam_setting):
                    img_dir = group_path / human_id / cam_setting / camera_id
                    xml_dir = label_group_path / human_id / cam_setting / camera_id

                    if not img_dir.exists() or not xml_dir.exists():
                        continue

                    all_images = sorted(f for f in os.listdir(img_dir) if f.endswith(".png"))

                    for idx, img_file in enumerate(all_images):
                        xml_file = img_file.replace(".png", ".xml")
                        xml_path = xml_dir / xml_file

                        if not xml_path.exists():
                            continue

                        try:
                            mode, foldername = parse_xml(xml_path)
                        except Exception:
                            continue

                        # Step 0: remove mode=1000
                        if mode == "1000":
                            try:
                                os.remove(img_dir / img_file)
                                os.remove(xml_path)
                            except:
                                pass
                            continue

                        # Step 1: skip even-indexed (1-based: 2nd, 4th...)
                        if idx % 2 == 1:
                            continue

                        folder_to_images[foldername].append((img_dir / img_file).resolve())

    return folder_to_images


def distribute_images(folder_to_images):
    grouped = list(folder_to_images.items())
    random.shuffle(grouped)

    sets = [[] for _ in range(NUM_SETS)]
    for i, item in enumerate(grouped):
        sets[i % NUM_SETS].append(item)

    for set_idx, group in enumerate(sets, 1):
        set_path = OUTPUT_BASE / f"set{set_idx}"
        for foldername, img_list in group:
            target_folder = set_path / foldername
            target_folder.mkdir(parents=True, exist_ok=True)
            for img_path in img_list:
                shutil.copy(img_path, target_folder / img_path.name)


def main():
    folder_to_images = collect_valid_images()
    distribute_images(folder_to_images)


if __name__ == "__main__":
    main()