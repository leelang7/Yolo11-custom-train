import os

RAW_LABEL_ROOT = "/home/leelang/ultralytics/runs/detect/predict6/labels/" # person class 답안지
TARGET_LABEL_ROOT = "/home/leelang/Downloads/HardGatWorkers/train/test_post_labels/" # 클래스명 변경된 답안지 출력 경로

yolo_file = os.listdir(RAW_LABEL_ROOT)

# .txt로 끝나는 파일 탐색
cnt = 0
for file_name in yolo_file:

    if not file_name.endswith(".txt"):
        continue

    file_path = RAW_LABEL_ROOT + file_name
    with open(file_path, "r") as f:
        for line in f.readlines():
            # 0 : person 을 다른 class로 일괄 변경
            if line.split()[0] == '0': # 사람이면
                line = list(line)
                line[0] = '2'
                line = ''.join(line).strip()
                print(line)
                # 주석파일에 추가
                data_path = TARGET_LABEL_ROOT + file_name
                with open(data_path, "a") as fd:
                    cnt += 1
                    fd.write(line)
                    fd.write("\n")
print(f'{cnt} 라인을 변경했습니다.')