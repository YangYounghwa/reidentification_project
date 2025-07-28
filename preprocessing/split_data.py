import os
import xml.etree.ElementTree as ET
import shutil
import math
from collections import defaultdict
import random

# 1

# --- 설정 (이 부분을 사용자의 환경에 맞게 수정해주세요) ---
BASE_PATH = r"C:\Users\astro\Downloads\한국인 재식별 이미지\Validation"
LABEL_FOLDER_NAME = "[라벨]Validation" # 라벨(XML) 파일이 있는 폴더명
IMAGE_FOLDER_NAME = "[원천]Validation"      # 이미지 파일이 있는 폴더명 (정확한 폴더명으로 변경 필요)
OUTPUT_BASE_FOLDER = os.path.join(BASE_PATH, "Validation_Grouped_5_parts") # 결과물이 저장될 최상위 폴더

# --- 경로 설정 ---
LABEL_PATH = os.path.join(BASE_PATH, LABEL_FOLDER_NAME)
IMAGE_PATH = os.path.join(BASE_PATH, IMAGE_FOLDER_NAME)

# --- 출력 폴더 생성 (이미 존재하면 에러 방지) ---
os.makedirs(OUTPUT_BASE_FOLDER, exist_ok=True)
for i in range(1, 6): # part_1 부터 part_5 까지
    os.makedirs(os.path.join(OUTPUT_BASE_FOLDER, f"part_{i}", LABEL_FOLDER_NAME), exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_BASE_FOLDER, f"part_{i}", IMAGE_FOLDER_NAME), exist_ok=True)

print(f"라벨 폴더 경로: {LABEL_PATH}")
print(f"이미지 폴더 경로: {IMAGE_PATH}")
print(f"결과 저장될 폴더: {OUTPUT_BASE_FOLDER}")
print("-" * 30)

# --- 1. XML 파일 파싱 및 정보 추출 ---
# all_data 리스트는 필요 없고, 바로 grouped_data로 수집
grouped_data = defaultdict(list) # key: group_key, value: list of (xml_file_path, image_filename)

for xml_filename in os.listdir(LABEL_PATH):
    if xml_filename.endswith('.xml'):
        xml_file_path = os.path.join(LABEL_PATH, xml_filename)
        
        try:
            tree = ET.parse(xml_file_path)
            root = tree.getroot()

            # 이미지 파일명 추출
            image_name_element = root.find('.//FILE/name')
            image_filename = image_name_element.text if image_name_element is not None else None

            # OBJECT 정보 추출
            obj_element = root.find('.//OBJECT')
            if obj_element is not None:
                obj_id = obj_element.get('ID', 'N/A')
                upperclothes = obj_element.find('upperclothes').text if obj_element.find('upperclothes') is not None else 'N/A_UC'
                upperclothes_color = obj_element.find('upperclothes_color').text if obj_element.find('upperclothes_color') is not None else 'N/A_UCC'
                lowerclothes = obj_element.find('lowerclothes').text if obj_element.find('lowerclothes') is not None else 'N/A_LC'
                lowerclothes_color = obj_element.find('lowerclothes_color').text if obj_element.find('lowerclothes_color') is not None else 'N/A_LCC'

                # 그룹 키 생성
                group_key = f"{obj_id}_{upperclothes}_{upperclothes_color}_{lowerclothes}_{lowerclothes_color}"
                # 해당 그룹 키의 리스트에 (xml_file_path, image_filename) 튜플 추가
                grouped_data[group_key].append((xml_file_path, image_filename))
            else:
                print(f"경고: {xml_filename} 파일에 <OBJECT> 태그가 없습니다. 건너뜁니다.")
        except ET.ParseError as e:
            print(f"오류: {xml_filename} 파싱 중 오류 발생 - {e}")
        except Exception as e:
            print(f"오류: {xml_filename} 처리 중 알 수 없는 오류 발생 - {e}")

if not grouped_data:
    print("처리할 XML 데이터가 없습니다. 경로 또는 파일 내용을 확인해주세요.")
    exit()

total_xml_files = sum(len(items) for items in grouped_data.values())
print(f"총 {total_xml_files}개의 XML 파일을 처리했습니다. ({len(grouped_data)}개의 고유 그룹)")

# --- 2. 각 그룹을 5개의 파트 중 한 곳에만 할당 ---
# 모든 그룹 키를 리스트로 만들고 섞기
all_group_keys = list(grouped_data.keys())
random.shuffle(all_group_keys) # 그룹 자체를 무작위로 섞어서 분배

# 각 파트에 할당될 그룹 키 리스트
parts_group_keys = [[] for _ in range(5)]

# 그룹 키들을 5개의 파트에 균등하게 분배
for i, group_key in enumerate(all_group_keys):
    parts_group_keys[i % 5].append(group_key) # 0,1,2,3,4,0,1,2,3,4... 순으로 할당

# 각 파트별 실제 파일 리스트 초기화
parts_data = [[] for _ in range(5)]

# 각 파트의 그룹 키에 해당하는 모든 파일들을 parts_data에 추가
for i, group_keys_in_part in enumerate(parts_group_keys):
    for group_key in group_keys_in_part:
        parts_data[i].extend(grouped_data[group_key])

# 선택된 데이터의 총 개수 확인 (디버깅용)
total_selected = sum(len(part) for part in parts_data)
print(f"총 {total_selected}개의 데이터가 5개 파트로 분배됩니다.")
print("각 파트에는 특정 그룹의 전체 데이터가 할당됩니다.")

# --- 3. 파일 복사 (이전 코드와 동일) ---
for i, part_items in enumerate(parts_data):
    part_number = i + 1
    output_label_dir = os.path.join(OUTPUT_BASE_FOLDER, f"part_{part_number}", LABEL_FOLDER_NAME)
    output_image_dir = os.path.join(OUTPUT_BASE_FOLDER, f"part_{part_number}", IMAGE_FOLDER_NAME)
    
    print(f"\n--- part_{part_number} 에 {len(part_items)}개 파일 복사 중 ---")
    
    for xml_file_path, image_filename in part_items:
        # XML 파일 복사
        xml_basename = os.path.basename(xml_file_path)
        dest_xml_path = os.path.join(output_label_dir, xml_basename)
        try:
            shutil.copy2(xml_file_path, dest_xml_path)
            # print(f"  복사: {xml_basename} -> {output_label_dir}")
        except FileNotFoundError:
            print(f"경고: XML 파일 찾을 수 없음 - {xml_file_path}. 건너뜁니다.")
        except Exception as e:
            print(f"오류: XML 파일 복사 실패 - {xml_file_path}: {e}")

        # 이미지 파일 복사 (image_filename이 None이 아닌 경우에만)
        if image_filename:
            source_image_path = os.path.join(IMAGE_PATH, image_filename)
            dest_image_path = os.path.join(output_image_dir, image_filename)
            try:
                shutil.copy2(source_image_path, dest_image_path)
                # print(f"  복사: {image_filename} -> {output_image_dir}")
            except FileNotFoundError:
                print(f"경고: 이미지 파일 찾을 수 없음 - {source_image_path}. 건너뜁니다.")
            except Exception as e:
                print(f"오류: 이미지 파일 복사 실패 - {source_image_path}: {e}")
        else:
            print(f"경고: {xml_basename} 파일에 해당하는 이미지 파일명이 없습니다. 이미지 복사를 건너뜁니다.")

print("\n--- 작업 완료 ---")
print(f"그룹별로 5등분된 데이터는 '{OUTPUT_BASE_FOLDER}' 폴더에 저장되었습니다.")