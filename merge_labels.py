import os

TARGET_LABEL_ROOT = "/home/leelang/Downloads/HardGatWorkers/train/test_post_labels/" # person이 2로 바뀐 labels 경로
RE_TARGET_LABEL_ROOT = "/home/leelang/Downloads/HardGatWorkers/test/labels/" # 원본 데이터셋의 /labels

os.makedirs(RE_TARGET_LABEL_ROOT, exist_ok=True)

cnt = 0
for file_name in os.listdir(TARGET_LABEL_ROOT):
    if not file_name.endswith(".txt"):
        continue

    src_path = os.path.join(TARGET_LABEL_ROOT, file_name)
    dst_path = os.path.join(RE_TARGET_LABEL_ROOT, file_name)

    # 1) src에서 class=2 라인만 추출
    add_lines = []
    with open(src_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            if len(parts) < 5:
                continue
            if parts[0] != "2":
                continue
            # 필요 없으면 전체 line 그대로 써도 됨: add_lines.append(line)
            add_lines.append(" ".join(parts[:5]))

    if not add_lines:
        continue

    # 2) dst 쪽 기존 내용 유지 + 안전하게 append
    # 파일이 이미 있으면: 마지막이 개행으로 끝나는지 확인
    if os.path.exists(dst_path):
        # 마지막 1바이트만 확인해서 개행 없으면 개행 추가
        with open(dst_path, "rb") as f:
            f.seek(0, os.SEEK_END)
            size = f.tell()
            last_char_newline = False
            if size > 0:
                f.seek(-1, os.SEEK_END)
                last_char_newline = (f.read(1) == b"\n")

        with open(dst_path, "a") as f:
            if size > 0 and not last_char_newline:
                f.write("\n")
            for line in add_lines:
                f.write(line + "\n")
                cnt += 1
    else:
        # 파일이 없으면 새로 만들고 class 2 라인만 기록
        with open(dst_path, "w") as f:
            for line in add_lines:
                f.write(line + "\n")
                cnt += 1

print(f"{cnt} 라인 추가 완료")