import os
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path
from collections import defaultdict
import random


# 🔍 Scanning group: TS3_2022_IN
# 🔍 Scanning group: TS4_2022_OUT
# ✅ Mode=1000 files removed: 598206
# ✅ Valid images kept: 573985
# ✅ Unique grouped folders: 816
# 📦 Distributing folders into 20 sets...
# 🎉 All images copied successfully into sets.
# ✅ Done.




# 🔍 Scanning group: VS3_2022_IN
# 🔍 Scanning group: VS4_2022_OUT
# ✅ Mode=1000 files removed: 73598
# ✅ Valid images kept: 71438
# ✅ Unique grouped folders: 98
# 📦 Distributing folders into 5 sets...
# 🎉 All images copied successfully into sets.
# ✅ Done.
# ---- CONFIGURATION ----





RAW_BASE = Path("DATA/Validation/raw/VS")
LABEL_BASE = Path("DATA/Validation/label/VS")
OUTPUT_BASE = Path("DATA/VALID")
NUM_SETS = 5


def parse_xml(xml_path):
    try:
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
    except Exception as e:
        print(f"❌ Failed to parse XML: {xml_path} → {e}")
        return None, None


def collect_valid_images():
    folder_to_images = defaultdict(list)
    removed_mode_count = 0
    kept_image_count = 0

    if not RAW_BASE.exists():
        print(f"❌ RAW_BASE path not found: {RAW_BASE}")
        return folder_to_images

    for group in os.listdir(RAW_BASE):
        group_path = RAW_BASE / group
        label_group_path = LABEL_BASE / group

        if not group_path.is_dir():
            continue
        if group_path.name == "VS1_2020_IN" or group_path.name == "VS2_2020_OUT":
            print("Skipping 2020 data")
            continue    
        print(f"🔍 Scanning group: {group}")

        for human_id in os.listdir(group_path):
            # print(f"🔍 Scanning Human : {human_id}")
            for cam_setting in os.listdir(group_path / human_id):
                # print(f"🔍 Scanning Cam_setting : {cam_setting}")
                for camera_id in os.listdir(group_path / human_id / cam_setting):
                    # print(f"🔍 Scanning Camera_id: {camera_id}")
                    img_dir = group_path / human_id / cam_setting / camera_id
                    xml_dir = label_group_path / human_id / cam_setting / camera_id

                    if not img_dir.exists() or not xml_dir.exists():

                        continue

                    all_images = sorted(f for f in os.listdir(img_dir) if f.endswith(".png"))

                    for idx, img_file in enumerate(all_images):
                        xml_file = img_file.replace(".png", ".xml")
                        xml_path = xml_dir / xml_file
                        img_path = img_dir / img_file

                        if not xml_path.exists():
                            print(f"⚠️ Missing XML for {img_path} ")
                            print(f"⚠️ Missing XML     {xml_path} ")
                            continue

                        mode, foldername = parse_xml(xml_path)
                        if mode is None:
                            continue

                        # Step 0: Remove files with mode=1000
                        if mode == "1000":
                            try:
                                os.remove(img_path)
                                os.remove(xml_path)
                                removed_mode_count += 1
                            except:
                                pass
                            continue

                        # Step 1: skip even index (keep only 0, 2, 4, ...)
                        if idx % 2 == 1:
                            continue

                        folder_to_images[foldername].append(img_path.resolve())
                        kept_image_count += 1

    print(f"✅ Mode=1000 files removed: {removed_mode_count}")
    print(f"✅ Valid images kept: {kept_image_count}")
    print(f"✅ Unique grouped folders: {len(folder_to_images)}")
    return folder_to_images


def distribute_images(folder_to_images):
    grouped = list(folder_to_images.items())
    random.shuffle(grouped)

    sets = [[] for _ in range(NUM_SETS)]
    for i, item in enumerate(grouped):
        sets[i % NUM_SETS].append(item)

    print(f"📦 Distributing folders into {NUM_SETS} sets...")

    for set_idx, group in enumerate(sets, 1):
        set_path = OUTPUT_BASE / f"set{set_idx}"
        for foldername, img_list in group:
            target_folder = set_path / foldername
            target_folder.mkdir(parents=True, exist_ok=True)
            for img_path in img_list:
                shutil.copy(img_path, target_folder / img_path.name)

    print("🎉 All images copied successfully into sets.")


def main():
    print("🚀 Starting dataset processing...")
    folder_to_images = collect_valid_images()
    if not folder_to_images:
        print("⚠️ No images collected. Exiting.")
        return
    distribute_images(folder_to_images)
    print("✅ Done.")


if __name__ == "__main__":
    main()