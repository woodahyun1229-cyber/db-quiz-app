# 🧠 데이터마이닝 퀴즈 앱

> **중간고사 대체 과제** | 학번: 2024XXXXXXX | 이름: 홍길동

---

## 프로젝트 소개

데이터마이닝 강의에서 배운 핵심 개념(데이터 전처리, 연관규칙, 클러스터링, 의사결정나무, 앙상블)을 복습할 수 있는 **퀴즈 웹 앱**입니다.

---

## 주요 기능

| 기능 | 설명 |
|------|------|
| 🔐 로그인 | 아이디/비밀번호 기반 로그인, 성공/실패 처리 |
| ⚡ 캐싱 | `@st.cache_data`로 퀴즈·유저 데이터 파일 I/O 최소화 |
| 🎯 퀴즈 | 카테고리 선택 → 4지선다 풀이 → 채점 → 해설 확인 |

---

## 실행 방법

```bash
# 1. 저장소 클론
git clone https://github.com/username/dm-quiz-app.git
cd dm-quiz-app

# 2. 가상환경 생성 (선택)
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 3. 의존성 설치
pip install -r requirements.txt

# 4. 실행
streamlit run app.py
```

---

## 테스트 계정

| 아이디 | 비밀번호 |
|--------|---------|
| test | test |
| student1 | pass1234 |
| admin | admin123 |

---

## 캐싱 적용 이유

`load_quiz_data()`와 `load_user_data()`에 `@st.cache_data`를 적용했습니다.  
Streamlit은 사용자 상호작용(버튼 클릭, 라디오 선택 등)마다 전체 스크립트를 재실행합니다.  
캐싱 없이는 매번 JSON 파일 I/O가 발생하지만, 캐싱을 통해 **최초 1회만 파일을 읽고** 이후에는 메모리에서 즉시 반환합니다.

---

## 프로젝트 구조

```
dm-quiz-app/
├── app.py              # 메인 실행 파일
├── requirements.txt    # 의존성
├── .gitignore          # Python .gitignore
├── README.md
└── data/
    ├── quiz_data.json  # 퀴즈 문제 (10문항)
    └── users.json      # 사용자 계정
```
