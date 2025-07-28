import os
import shutil
import random

# 2

# --- 설정 (이 부분을 사용자의 환경에 맞게 수정해주세요) ---
BASE_PATH = r"C:\Users\astro\Downloads\한국인 재식별 이미지\Validation\Validation_Grouped_5_parts" # part_1, part_2 등을 포함하는 상위 폴더
PART_FOLDERS_TO_PROCESS = ["part_1", "part_2", "part_3", "part_4", "part_5"] # 처리할 part 폴더 목록

LABEL_SUBFOLDER_NAME = "[라벨]Validation" # 각 part_X 안의 라벨 폴더 이름
IMAGE_SUBFOLDER_NAME = "[원천]Validation"      # 각 part_X 안의 이미지 폴더 이름
OUTPUT_FOLDER_SUFFIX = "_odd_files"  # 홀수 번째 파일을 저장할 새 폴더 이름에 붙을 접미사

# --- 함수 정의 ---
def process_part_folder(base_part_path: str, label_subfolder: str, image_subfolder: str, output_suffix: str):
    """
    단일 'part' 폴더 내의 홀수 번째 이미지 및 XML 파일을 복사합니다.

    Args:
        base_part_path (str): 현재 처리할 'part_X' 폴더의 전체 경로입니다.
        label_subfolder (str): 라벨 파일이 들어있는 하위 폴더 이름입니다.
        image_subfolder (str): 이미지 파일이 들어있는 하위 폴더 이름입니다.
        output_suffix (str): 출력 폴더 이름에 추가할 접미사입니다.
    """
    print(f"\n{'='*50}")
    print(f"'{os.path.basename(base_part_path)}' 폴더 처리 시작...")
    print(f"{'='*50}")

    # --- 경로 설정 ---
    label_path = os.path.join(base_part_path, label_subfolder)
    image_path = os.path.join(base_part_path, image_subfolder)
    output_base_path = os.path.join(base_part_path, os.path.basename(base_part_path) + output_suffix)

    # 새로 생성될 폴더 경로
    output_label_path = os.path.join(output_base_path, label_subfolder)
    output_image_path = os.path.join(output_base_path, image_subfolder)

    # --- 출력 폴더 생성 (이미 존재하면 에러 방지) ---
    os.makedirs(output_label_path, exist_ok=True)
    os.makedirs(output_image_path, exist_ok=True)

    print(f"원본 라벨 폴더: {label_path}")
    print(f"원본 이미지 폴더: {image_path}")
    print(f"결과 저장될 폴더: {output_base_path}")
    print("-" * 30)

    # --- 1. 이미지 파일 목록 가져오기 ---
    # 파일 이름 순서대로 정렬하여 일관된 '홀수 번째' 기준 마련
    if not os.path.exists(image_path):
        print(f"오류: 이미지 폴더 '{image_path}'를 찾을 수 없습니다. 이 파트를 건너뜝니다.")
        return
    if not os.path.exists(label_path):
        print(f"오류: 라벨 폴더 '{label_path}'를 찾을 수 없습니다. 이 파트를 건너뜝니다.")
        return

    image_files = sorted([f for f in os.listdir(image_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))])

    if not image_files:
        print(f"경고: '{image_path}' 폴더에 이미지 파일이 없습니다. 처리할 데이터가 없습니다.")
        return

    print(f"'{os.path.basename(image_path)}'에서 발견된 이미지 파일 수: {len(image_files)}")

    # --- 2. 홀수 번째 데이터 선택 ---
    # 리스트 인덱스는 0부터 시작하므로, 홀수 인덱스 = 짝수 번째 파일 (1번째, 3번째, 5번째...)
    # [1::2] 슬라이싱은 인덱스 1부터 시작하여 2칸씩 건너뛰며 선택
    selected_files = image_files[1::2] # 홀수 인덱스(0부터 시작)의 파일들만 선택

    print(f"총 {len(image_files)}개 중 {len(selected_files)}개 (홀수 번째) 파일이 선택되었습니다.")

    # --- 3. 파일 복사 ---
    print("\n--- 선택된 파일 복사 중 ---")
    copied_count = 0

    for image_filename in selected_files:
        # 이미지 파일 원본 경로
        source_image_path = os.path.join(image_path, image_filename)
        # 이미지 파일 복사될 경로
        dest_image_path = os.path.join(output_image_path, image_filename)

        # XML 파일 원본 경로 (이미지 파일명에서 확장자만 .xml로 변경)
        xml_filename = os.path.splitext(image_filename)[0] + '.xml'
        source_xml_path = os.path.join(label_path, xml_filename)
        # XML 파일 복사될 경로
        dest_xml_path = os.path.join(output_label_path, xml_filename)

        try:
            # 이미지 파일 복사
            shutil.copy2(source_image_path, dest_image_path)

            # XML 파일 복사
            if os.path.exists(source_xml_path):
                shutil.copy2(source_xml_path, dest_xml_path)
            else:
                print(f"경고: 매칭되는 XML 파일 '{xml_filename}'을 찾을 수 없습니다. 이미지 '{image_filename}'에 대한 라벨은 복사되지 않습니다.")
                
            copied_count += 1

        except FileNotFoundError:
            print(f"오류: 파일 찾을 수 없음 - 이미지: {source_image_path} 또는 XML: {source_xml_path}. 이 쌍은 건너뜨니다.")
        except Exception as e:
            print(f"오류: 파일 복사 실패 - {image_filename} 관련 파일: {e}. 이 쌍은 건너뜝니다.")

    print(f"\n--- '{os.path.basename(base_part_path)}' 작업 완료 ---")
    print(f"총 {copied_count}쌍의 홀수 번째 파일이 '{output_base_path}' 폴더에 복사되었습니다.")


# --- 메인 실행 로직 ---
if __name__ == "__main__":
    print(f"--- 스크립트 시작 ---")
    print(f"기준 경로: {BASE_PATH}")
    print(f"처리할 파트: {', '.join(PART_FOLDERS_TO_PROCESS)}")

    for part_folder_name in PART_FOLDERS_TO_PROCESS:
        current_part_path = os.path.join(BASE_PATH, part_folder_name)
        
        if not os.path.isdir(current_part_path):
            print(f"\n경고: '{current_part_path}' 폴더를 찾을 수 없습니다. 이 파트는 건너뜁니다.")
            continue
        
        process_part_folder(current_part_path, LABEL_SUBFOLDER_NAME, IMAGE_SUBFOLDER_NAME, OUTPUT_FOLDER_SUFFIX)

    print(f"\n--- 모든 지정된 파트 폴더 처리 완료 ---")