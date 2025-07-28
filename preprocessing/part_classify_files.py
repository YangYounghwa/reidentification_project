import os
import shutil
import xml.etree.ElementTree as ET

# 3

# --- 설정값 (이 부분을 사용자의 환경에 맞게 수정해주세요) ---
# 모든 part_X 폴더를 포함하는 상위 폴더
BASE_VALIDATION_PATH = r"C:\Users\astro\Downloads\한국인 재식별 이미지\Validation\Validation_Grouped_5_parts"

# 처리할 part_X 폴더 목록
# 예: ["part_1", "part_2", "part_3", "part_4", "part_5"]
# 이미 part_1을 처리했다면, 목록에서 part_1을 제거해도 됩니다.
PART_FOLDERS_TO_PROCESS = ["part_1", "part_2", "part_3", "part_4", "part_5"]

# 홀수 번째 파일을 저장했던 폴더 이름의 접미사
ODD_FILES_SUBFOLDER_SUFFIX = "_odd_files"

# 각 'xxx_odd_files' 폴더 안의 라벨(XML) 파일이 들어있는 폴더 이름
LABEL_SUBFOLDER_NAME = "[라벨]Validation"

# 각 'xxx_odd_files' 폴더 안의 원본 이미지 파일이 들어있는 폴더 이름
IMAGE_SUBFOLDER_NAME = "[원천]Validation"

# --- 함수 정의 ---
def process_odd_files_folder(base_part_odd_path: str, label_sub: str, image_sub: str):
    """
    단일 '_odd_files' 폴더 내의 이미지 및 XML 파일을 메타데이터에 따라 분류하고 이동합니다.

    Args:
        base_part_odd_path (str): 현재 처리할 'part_X_odd_files' 폴더의 전체 경로입니다.
        label_sub (str): 라벨 파일이 들어있는 하위 폴더 이름입니다.
        image_sub (str): 이미지 파일이 들어있는 하위 폴더 이름입니다.
    """
    print(f"\n{'='*50}")
    print(f"'{os.path.basename(base_part_odd_path)}' 폴더 처리 시작...")
    print(f"{'='*50}")

    label_source_dir = os.path.join(base_part_odd_path, label_sub)
    image_source_dir = os.path.join(base_part_odd_path, image_sub)

    if not os.path.isdir(label_source_dir):
        print(f"오류: 라벨 폴더 '{label_source_dir}'를 찾을 수 없습니다. 이 파트를 건너뜝니다.")
        return
    if not os.path.isdir(image_source_dir):
        print(f"오류: 이미지 폴더 '{image_source_dir}'를 찾을 수 없습니다. 이 파트를 건너뜝니다.")
        return

    print(f"'{label_source_dir}' 폴더에서 XML 파일 처리 시작...")

    processed_xml_count = 0
    processed_image_count = 0
    not_found_image_count = 0
    error_count = 0

    for filename in os.listdir(label_source_dir):
        if filename.endswith('.xml'):
            xml_file_path = os.path.join(label_source_dir, filename)
            
            try:
                tree = ET.parse(xml_file_path)
                root = tree.getroot()

                # OBJECT ID 추출
                object_element = root.find('OBJECT')
                human_id = object_element.get('ID') if object_element is not None else "UNKNOWN_ID"

                # 상의 정보 추출 (None 값 방지)
                upperclothes = object_element.find('upperclothes').text if object_element is not None and object_element.find('upperclothes') is not None and object_element.find('upperclothes').text else "no_upperclothes"
                upperclothes_color = object_element.find('upperclothes_color').text if object_element is not None and object_element.find('upperclothes_color') is not None and object_element.find('upperclothes_color').text else "no_upperclothes_color"
                
                # 하의 정보 추출 (None 값 방지)
                lowerclothes = object_element.find('lowerclothes').text if object_element is not None and object_element.find('lowerclothes') is not None and object_element.find('lowerclothes').text else "no_lowerclothes"
                lowerclothes_color = object_element.find('lowerclothes_color').text if object_element is not None and object_element.find('lowerclothes_color') is not None and object_element.find('lowerclothes_color').text else "no_lowerclothes_color"

                # 새 폴더 이름 생성 (ID_상의종류_상의색상_하의종류_하의색상)
                # 폴더명에 불필요한 공백이나 특수문자가 들어가지 않도록 처리
                new_folder_name = f"{human_id}_{upperclothes.replace(' ', '_')}_{upperclothes_color.replace(' ', '_')}_{lowerclothes.replace(' ', '_')}_{lowerclothes_color.replace(' ', '_')}"
                
                # 분류된 파일이 들어갈 최종 목적지 폴더 (base_part_odd_path 바로 아래에 생성)
                destination_folder_path = os.path.join(base_part_odd_path, new_folder_name)
                os.makedirs(destination_folder_path, exist_ok=True)

                # XML 파일 이동
                shutil.move(xml_file_path, os.path.join(destination_folder_path, filename))
                processed_xml_count += 1

                # 해당 이미지 파일 찾아서 이동 (XML 파일명에서 이미지 파일명을 가져옴)
                image_filename_from_xml_tag = root.find('FILE/name').text if root.find('FILE/name') is not None else None
                
                if image_filename_from_xml_tag:
                    # 이미지 파일은 image_source_dir에서 찾습니다.
                    image_file_path = os.path.join(image_source_dir, image_filename_from_xml_tag)
                    if os.path.exists(image_file_path):
                        shutil.move(image_file_path, os.path.join(destination_folder_path, image_filename_from_xml_tag))
                        processed_image_count += 1
                    else:
                        not_found_image_count += 1
                        print(f"경고: 대응 이미지 '{image_filename_from_xml_tag}'를 '{image_source_dir}'에서 찾을 수 없습니다. XML '{filename}'에 대한 이미지는 이동되지 않습니다.")
                else:
                    print(f"경고: XML 파일 '{filename}'에서 이미지 파일명을 찾을 수 없습니다.")

            except ET.ParseError as e:
                error_count += 1
                print(f"오류: XML 파일 '{filename}' 파싱 중 오류 발생: {e}. 건너뜝니다.")
            except Exception as e:
                error_count += 1
                print(f"오류: '{filename}' 처리 중 예상치 못한 오류 발생: {e}. 건너뜝니다.")
        # else: # XML 파일이 아닌 다른 파일은 건너뜠다는 메시지를 원하지 않으면 이 부분 주석 처리
        #     print(f"Skipping non-XML file: '{filename}'")

    print(f"\n'{os.path.basename(base_part_odd_path)}' 폴더 처리 완료.")
    print(f"  처리된 XML 파일: {processed_xml_count}개")
    print(f"  이동된 이미지 파일: {processed_image_count}개")
    print(f"  대응 이미지 찾을 수 없음: {not_found_image_count}개")
    print(f"  처리 중 오류 발생: {error_count}개")

    # 모든 작업이 완료된 후, 혹시 image_source_dir에 남은 이미지 파일이 있는지 확인
    remaining_images = [f for f in os.listdir(image_source_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
    if remaining_images:
        print(f"\n  경고: '{image_source_dir}' 폴더에 처리되지 않은 이미지 파일이 {len(remaining_images)}개 남아있습니다.")
        print("  이들은 XML 파일에 매칭되지 않았거나, XML 파일에서 이미지 파일명이 잘못된 경우일 수 있습니다.")
    else:
        print(f"\n  '{image_source_dir}' 폴더의 모든 이미지가 성공적으로 처리되었습니다.")

    # 최종적으로 label_source_dir에 남은 파일이 있는지 확인
    remaining_labels = os.listdir(label_source_dir)
    if remaining_labels:
        print(f"\n  경고: '{label_source_dir}' 폴더에 처리되지 않은 XML 파일이 {len(remaining_labels)}개 남아있습니다.")
        print("  이들은 XML 파싱에 실패했거나, 스크립트가 인식하지 못한 파일일 수 있습니다.")
    else:
        print(f"\n  '{label_source_dir}' 폴더의 모든 XML 파일이 성공적으로 처리되었습니다.")

# --- 메인 실행 로직 ---
if __name__ == "__main__":
    print(f"--- 스크립트 시작 ---")
    print(f"기준 경로: {BASE_VALIDATION_PATH}")
    print(f"처리할 파트: {', '.join(PART_FOLDERS_TO_PROCESS)}")
    print("-" * 50)

    for part_folder_name in PART_FOLDERS_TO_PROCESS:
        # 'part_X_odd_files' 폴더의 전체 경로 구성
        odd_files_folder_path = os.path.join(BASE_VALIDATION_PATH, part_folder_name, part_folder_name + ODD_FILES_SUBFOLDER_SUFFIX)
        
        if not os.path.isdir(odd_files_folder_path):
            print(f"\n경고: '{odd_files_folder_path}' 폴더를 찾을 수 없습니다. 이 파트는 건너뜠니다.")
            continue
        
        process_odd_files_folder(odd_files_folder_path, LABEL_SUBFOLDER_NAME, IMAGE_SUBFOLDER_NAME)

    print(f"\n--- 모든 지정된 파트 폴더 처리 완료 ---")