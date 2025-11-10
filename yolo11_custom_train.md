# <yolo11 커스텀 학습>



1. **데이터 다운로드**

   ##### "Hard Hat Workers Dataset" - https://public.roboflow.com/object-detection/hard-hat-workers

   resize-416x416-reflectEdges 7,041장 데이터셋 선택하고 format은 yolo11을 선택한다. 사용할 데이터셋은 resize되어 있다는 것에 주목하라. 해당 annotation 파일들은 리사이징된 이미지의 좌표값으로 셋팅되어있다. 이미지 크기가 제각각이거나 정돈되지 않은 데이터셋의 경우 반드시 좌표체계를 사전에 확인해야 수고로움을 줄일 수 있다. 데이터셋을 통찰할 때 모든 이미지크기가 같을 것이라 단정짓지 말아야한다.



2. **데이터셋 구조**

   데이터셋을 다운받고 압축을 해제하면 아래와 같이 구성되어있다.

   <p align="center"> <img width="621" height="156" alt="image-20251109000750842" src="https://github.com/user-attachments/assets/62b9900b-fc0e-4ef9-93bb-1f2cbb1ba6cb" /> </p>

     train, test 폴더로 분리되어있고 각 폴더의 하위 폴더는 images와 labels로 구성되어있다. 

    <p align="center"> <img width="724" height="266" alt="image-20251109001031863" src="https://github.com/user-attachments/assets/4701adf7-5f20-4ba0-9e8e-dfa843ba5131" /> </p>

   data.yaml을 보면 훈련시 중요한 설정 정보들이 있다. train은 훈련데이터셋(이미지)의 경로, val은 검증데이터셋(이미지)의 폴더 경로이다.

   nc(numbers of classes)는 클래스의 갯수이다. 클래스를 몇개로 구성할 것인가를 기술한다.

   names는 클래스와 맵핑되는 객체명이다. 한글도 사용가능하지만 직관적인 객체명(클래스명)을 사용하는 것이 좋다. 라벨 맵핑은 순서대로 0번이 head, 1번이 helmet, 2번이 person이다.

   


3. **클래스 추출**

   클래스별 분포를 살펴보면 person의 인스턴스 갯수가 현저하게 적다. task는 헤드, 헬멧, 사람을 탐지하는 것인데 이 상태로 학습을 하면 사람 클래스는 과소적합이 일어나 거의 탐지할 수가 없다.(애초에 인스턴스가 너무 부족하다. 본 글에서는 객체에 annotation이 있는 것을 인스턴스라고 지칭하겠다. 즉, 사람은 이미지에 존재하지만 라벨링(bbox)작업이 제대로 되어있지 않다.)

   모델을 만들 때(구울 때)는 어떤 환경에서 어떻게 추론하고 서비스할지를 사전에 고민해야 한다. 본 데이터셋은 산업안전현장 등 광범위하게 쓰이므로 person 클래스 보완이 필수불가결해보인다. 

   그렇다고 person 데이터셋을 수집하여(person이미지와 annotation이 있는) 현재 데이터셋에 단순히 더하는 방법은 매우 위험하다. 현재 데이터셋은 헤드와 헬멧 인스턴스가 많다. 예를 들어 외부 데이터셋을 수집한 것이 person 인스턴스이고 현재 데이터셋에 그대로 더하면(단순히 데이터의 갯수만 늘려) 모델은 외부데이터셋으로 인해 헤드와 헬멧이라고 생각했던 답안지와 헤드와 헬멧은 명시하지 않고 person이라고 만들어논 답안지 때문에 왜곡이 일어나게된다. 쉽게 말해, 모델을 인간이 보고 생각하는 것처럼 만들어줘야는데 사람을 놓고 헤드와 헬멧이라고 만들어논 답안지는 person을 못보게 되고 person만 만들어논 답안지는 헤드와 헬멧을 보지못하게 만들어논 꼴이 된다. **즉, 인간의 시각정보 측면에서 헤드와 헬멧은 사람의 부분집합이므로 모든 답안지 파일에 헬멧, 헤드, 사람이 모두 라벨링되도록 만들어줘야한다.**   

   이를 위해 본 task에서는 외부데이터셋의 수집 없이 person 클래스만 추출하여 답안지를 보완한다. yolo는 coco 데이터셋을 사용하므로 pre-trained된 전이학습 대상모델의 0번 클래스는 person이다. 삼국지에서 제갈량이 적벽대전 전에 화살을 모았던 것처럼 yolo11x모델을 활용하여 /train/images와 /test/images 폴더를 타겟으로 하여 person 클래스를 추론 후 추출한다. 일각에서는 이 작업을 오토라벨링이라고 칭하기도 한다.(정확도가 핵심인 task가 아니라면 yolo11n모델을 사용하다 충분하다. x모델을 사용해서 성능과 속도의 trade-off 체감을 위해 명령어는 x모델을 사용하였다.)

   ```
   (yolo) leelang@leelang:~/ultralytics$ yolo detect predict model=yolo11n.pt source=/home/leelang/Downloads/HardGatWorkers/test/images/ save_txt=True save=False classes=0
   ```

   ```
   (yolo) leelang@leelang:~/ultralytics$ yolo detect predict model=yolo11n.pt source=/home/leelang/Downloads/HardGatWorkers/test/images/ save_txt=True save=False classes=0
   ```

   위의 명령어는 train셋과 test셋에 대해 각각 person 클래스를 추론/추출하여 답안지 파일 .txt를 출력해 준다. 프로젝트 하위의 runs/detect/predict에 가면 아래와 같은 person(0번)이 추출된 답안지 파일을 확인할 수 있다. 임의의 파일을 선택해 내용을 확인해본다.

 <p align="center"> <img width="546" height="329" alt="image-20251109005721465" src="https://github.com/user-attachments/assets/fe25d599-8b1d-4dca-a5de-f41e73e6ef0d" /> </p>

​       person detection 좌표를 라인별로 잘 추출한 모습이다.(정수클래스명 x y w h) yolo5부터 정규화 좌표를 사용한다.



4. **클래스명 변경**

   class_converter.py를 활용해 0번으로 추출된 모든 좌표를 2번으로 바꿔준다. 본 데이터셋은 0번이 helmet이고 2번이 person이기 때문이다. 작업 관리를 위해 세부적으로 나누어 작업하고 덮어씌우지 않고 새로 답안지를 생성하는 것이 실수를 줄이고 문제가 발생했을시 원인파악을 하는데 도움이 된다.

   class_converter.py의 RAW_LABEL_ROOT는 /runs/detect/predict/labels/로 person이 0번으로 추출된 답안지들이 있는 폴더이며 TARGET_LABEL_ROOT는 이해하기 쉽고 직관적인 곳으로 출력 폴더를 설정하면 person이 2번으로 바뀐 답안지가 생성될 것이다.

   마찬가지로 train과 test 각 각 수행하여 person을 0번에서 2번으로 바꾼 답안지를 생성/확인한다.

   <p align="center"> <img width="540" height="612" alt="image-20251109011210042" src="https://github.com/user-attachments/assets/bf3e8dc7-d35b-4908-8dda-1a6618d011d7" /> </p>
   
​    

5. **최종 답안지 Merge**

   merge_labels.py를 통해 최종답안지를 생성한다. TATGET_LABEL_ROOT는 위 4번의 출력 경로이며 RE_TARGET_LABEL_ROOT는 원본 데이터셋의 labels 경로이다.(/train/labels, /test/labels)

   잘못 merge하게 되면 원본 라벨지가 손상되므로 원본 데이터셋의 labels는 백업해두는 것이 좋다.

   마찬가지로 train, test 각 각 merge를 수행한다.

   <p align="center"> <img width="1048" height="574" alt="image-20251109012931694" src="https://github.com/user-attachments/assets/4be5fcb5-b032-48b7-89fc-f768c02326fc" /> </p>

​     임의의 파일을 선택했을 때 최종 답안지 파일은 위처럼 0, 1, 2로 merge되어야 한다. merge시에 원래 좌표에 옆으로 붙는 실수가 있을 수 있으니 유의한다.



6. **최종 답안지로 커스텀 학습**

   o data.yaml 수정 및 구조 점검

   아래와 같이 data.yaml 파일을 수정한다. train과 val의 images 폴더 경로만 기입하면 된다. yolo는 images 폴더 레벨에서 자동으로 labels 폴더를 찾아서 학습한다. 학습만 할 것이므로 train, val 경로만 지정한다.

    <p align="center"> <img width="1043" height="621" alt="image" src="https://github.com/user-attachments/assets/bbb492f2-3ca8-4525-82cc-4223044643b8" /> </p>

   ```
   (yolo) leelang@leelang:~/ultralytics$ yolo train model=yolo11n.pt data='/home/leelang/Downloads/HardGatWorkers/data.yaml' epochs=10
   ```

   위의 명령어를 통해 원본 images와 커스텀한 최종 답안지 labels로 학습한 결과는 아래와 같다.

<img width="1064" height="1062" alt="image-20251109013455620" src="https://github.com/user-attachments/assets/f4306b15-a812-409c-9f6f-29e00abc10d6" />

원본 이미지와 최종 답안지로 학습을 시작하고 바로 생성되는 /runs/detect/train의 train_batch.jpg를 확인하면 0, 1, 2 person과 helmet, head모두 잘 학습하고 있음을 볼 수 있다. 반드시 bbox는 인스턴스를 잘 표기하고 있어야 한다. 좌표 변환 실수가 있거나 이미지 resize 등의 실수가 있다면 엉뚱한 곳에 bbox를 그리고 있을 수 있다. 이럴 땐 다시 한 번 꼼꼼히 체크하자. 인공지능의 근본은 데이터이며 모델/데이터 엔지니어는 데이터를 잘 이해하고 활용하는 것이 기본기 오브 기본기이다. 귀찮더라도 경로, 폴더명, 구조, 환경, 자동화, 형상관리를 소홀히 하지 말자.

테스트 조건을 통일하게 맞추고 다운로드 받은 순수 원본 데이터로 학습한 결과와 커스텀한 데이터로 학습 결과를 비교해 보면 경이로운 성능 향상을 직접 경험해 볼 수 있을 것이다.
