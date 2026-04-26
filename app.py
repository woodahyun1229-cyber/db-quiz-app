import streamlit as st
import json
import time
from pathlib import Path

# ─────────────────────────────────────────────
# 페이지 설정
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="데이터베이스 퀴즈 앱",
    page_icon="🗄️",
    layout="centered",
    initial_sidebar_state="auto",
)

# ─────────────────────────────────────────────
# 캐싱: 데이터 로드 (퀴즈 / 유저)
# 반복 실행 시 파일을 다시 읽지 않도록 캐싱 적용
# ─────────────────────────────────────────────
@st.cache_data
def load_quiz_data() -> list[dict]:
    """
    퀴즈 데이터를 JSON 파일에서 읽어 반환합니다.
    @st.cache_data 덕분에 최초 1회만 파일 I/O가 발생하며,
    이후 실행에서는 메모리에 캐시된 결과를 즉시 반환합니다.
    """
    path = Path(__file__).parent / "data" / "quiz_data.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@st.cache_data
def load_user_data() -> dict:
    """
    사용자 계정 데이터를 JSON 파일에서 읽어 반환합니다.
    캐싱을 통해 로그인 시도마다 파일을 반복 읽는 비용을 제거합니다.
    """
    path = Path(__file__).parent / "data" / "users.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ─────────────────────────────────────────────
# 세션 상태 초기화
# ─────────────────────────────────────────────
def init_session():
    defaults = {
        "logged_in": False,
        "username": "",
        "display_name": "",
        "quiz_started": False,
        "quiz_finished": False,
        "current_q": 0,
        "answers": {},        # {question_id: selected_option_index}
        "score": 0,
        "selected_categories": [],
        "quiz_questions": [],
        "start_time": None,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


init_session()

# ─────────────────────────────────────────────
# 공통 스타일
# ─────────────────────────────────────────────
st.markdown("""
<style>
    .student-info {
        background: linear-gradient(135deg, #1e3a5f, #2d6a9f);
        color: white;
        padding: 18px 24px;
        border-radius: 12px;
        margin-bottom: 20px;
        font-size: 15px;
        line-height: 1.7;
    }
    .student-info h2 {
        margin: 0 0 8px 0;
        font-size: 20px;
    }
    .quiz-card {
        background: #1e3a5f;
        color: white;
        border-left: 5px solid #60a5fa;
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 16px;
    }
    .result-box {
        text-align: center;
        padding: 32px;
        border-radius: 16px;
        margin: 20px 0;
    }
    .correct { color: #16a34a; font-weight: bold; }
    .wrong   { color: #dc2626; font-weight: bold; }
    .badge {
        display: inline-block;
        background: #e0edff;
        color: #1e3a5f;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 13px;
        margin-bottom: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 학번 / 이름 고정 표시 (첫 화면 포함 항상 표시)
# ─────────────────────────────────────────────
st.markdown("""
<div class="student-info">
  <h2>🗄️ 데이터베이스 퀴즈 앱</h2>
  <b>학번:</b> 2024404094 &nbsp;|&nbsp; <b>이름:</b> 우다현<br>
  <span style="font-size:13px; opacity:0.85;">Database Quiz — 관계형 DB · 관계대수 · SQL · 정규화 · 트랜잭션 · 인덱스</span>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 로그인 화면
# ─────────────────────────────────────────────
def show_login():
    st.subheader("🔐 로그인")
    st.caption("계정 정보를 입력하여 퀴즈를 시작하세요.")

    col1, col2 = st.columns([3, 1])
    with col1:
        username = st.text_input("아이디", placeholder="예: student1")
        password = st.text_input("비밀번호", type="password", placeholder="비밀번호 입력")

    st.caption("테스트 계정: `test` / `test`")

    if st.button("로그인", use_container_width=True, type="primary"):
        user_data = load_user_data()
        matched = None
        for u in user_data["users"]:
            if u["username"] == username and u["password"] == password:
                matched = u
                break

        if matched:
            st.session_state.logged_in = True
            st.session_state.username = matched["username"]
            st.session_state.display_name = matched["display_name"]
            st.success(f"✅ 환영합니다, {matched['display_name']}님!")
            time.sleep(0.8)
            st.rerun()
        else:
            st.error("❌ 아이디 또는 비밀번호가 올바르지 않습니다.")

    with st.expander("ℹ️ 사용 가능한 테스트 계정"):
        st.markdown("""
| 아이디 | 비밀번호 |
|--------|---------|
| test | test |
| student1 | pass1234 |
| admin | admin123 |
""")


# ─────────────────────────────────────────────
# 카테고리 선택 화면
# ─────────────────────────────────────────────
def show_category_select():
    quiz_data = load_quiz_data()
    category_order = ["관계형 데이터베이스", "관계대수", "SQL", "정규화", "트랜잭션", "인덱스"]
    all_cats = set(q["category"] for q in quiz_data)
    categories = [c for c in category_order if c in all_cats] + sorted(all_cats - set(category_order))

    st.subheader(f"👋 안녕하세요, {st.session_state.display_name}님!")
    st.markdown("퀴즈에 도전할 **카테고리**를 선택하세요.")

    selected = st.multiselect(
        "카테고리 선택 (복수 선택 가능)",
        options=categories,
        default=categories,
    )

    # 선택된 카테고리의 문제 수 표시
    if selected:
        filtered = [q for q in quiz_data if q["category"] in selected]
        st.info(f"선택된 문제 수: **{len(filtered)}문제**")
    else:
        st.warning("최소 1개 이상의 카테고리를 선택하세요.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 퀴즈 시작", use_container_width=True, type="primary", disabled=not selected):
            category_order = ["관계형 데이터베이스", "관계대수", "SQL", "정규화", "트랜잭션", "인덱스"]
            filtered = [q for q in quiz_data if q["category"] in selected]
            filtered = sorted(filtered, key=lambda q: category_order.index(q["category"]) if q["category"] in category_order else 999)
            st.session_state.quiz_questions = filtered
            st.session_state.quiz_started = True
            st.session_state.quiz_finished = False
            st.session_state.current_q = 0
            st.session_state.answers = {}
            st.session_state.score = 0
            st.session_state.start_time = time.time()
            st.session_state.selected_categories = selected
            st.rerun()

    with col2:
        if st.button("🚪 로그아웃", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()


# ─────────────────────────────────────────────
# 퀴즈 화면
# ─────────────────────────────────────────────
def show_quiz():
    questions = st.session_state.quiz_questions
    idx = st.session_state.current_q
    total = len(questions)

    if idx >= total:
        # 모든 문제 완료 → 결과 화면
        st.session_state.quiz_finished = True
        st.session_state.quiz_started = False
        st.rerun()
        return

    q = questions[idx]

    # 진행 바
    progress = (idx) / total
    st.progress(progress, text=f"문제 {idx + 1} / {total}")

    # 카테고리 배지 + 문제
    st.markdown(f'<span class="badge">📂 {q["category"]}</span>', unsafe_allow_html=True)
    st.markdown(f'<div class="quiz-card"><b>Q{idx+1}. {q["question"]}</b></div>', unsafe_allow_html=True)

    # 이미 답한 경우 인덱스를 기본값으로
    prev_answer = st.session_state.answers.get(q["id"], None)
    default_idx = prev_answer if prev_answer is not None else 0

    choice = st.radio(
        "답을 선택하세요:",
        options=range(len(q["options"])),
        format_func=lambda i: f"{'①②③④'[i]} {q['options'][i]}",
        index=default_idx,
        key=f"radio_{q['id']}",
    )

    col1, col2 = st.columns([1, 1])
    with col1:
        if idx > 0:
            if st.button("⬅️ 이전", use_container_width=True):
                st.session_state.answers[q["id"]] = choice
                st.session_state.current_q -= 1
                st.rerun()

    with col2:
        btn_label = "다음 ➡️" if idx < total - 1 else "✅ 제출"
        if st.button(btn_label, use_container_width=True, type="primary"):
            st.session_state.answers[q["id"]] = choice
            if idx < total - 1:
                st.session_state.current_q += 1
                st.rerun()
            else:
                # 채점
                score = 0
                for qq in questions:
                    user_ans = st.session_state.answers.get(qq["id"])
                    if user_ans == qq["answer"]:
                        score += 1
                st.session_state.score = score
                st.session_state.quiz_finished = True
                st.session_state.quiz_started = False
                st.rerun()


# ─────────────────────────────────────────────
# 결과 화면
# ─────────────────────────────────────────────
def show_result():
    questions = st.session_state.quiz_questions
    score = st.session_state.score
    total = len(questions)
    pct = score / total * 100

    elapsed = time.time() - st.session_state.start_time if st.session_state.start_time else 0
    minutes, seconds = divmod(int(elapsed), 60)

    # 점수에 따른 등급/메시지
    if pct >= 90:
        grade, msg, color = "🏆 S", "완벽합니다! 데이터베이스 마스터!", "#fbbf24"
    elif pct >= 70:
        grade, msg, color = "🥈 A", "훌륭해요! 핵심 개념을 잘 이해하고 있군요.", "#60a5fa"
    elif pct >= 50:
        grade, msg, color = "🥉 B", "좋아요! 조금만 더 복습하면 완벽해질 거예요.", "#34d399"
    else:
        grade, msg, color = "📘 C", "아직 갈 길이 있어요. 강의 자료를 다시 확인해 보세요!", "#f87171"

    st.markdown(f"""
    <div class="result-box" style="background: {color}22; border: 2px solid {color};">
        <h1 style="font-size: 48px; margin:0;">{grade}</h1>
        <h2 style="color: {color};">{score} / {total} 정답 ({pct:.0f}%)</h2>
        <p style="font-size:16px;">{msg}</p>
        <p style="color:#666;">⏱️ 소요 시간: {minutes}분 {seconds}초</p>
    </div>
    """, unsafe_allow_html=True)

    # 문제별 상세 결과
    st.subheader("📋 문제별 결과")
    for q in questions:
        user_ans = st.session_state.answers.get(q["id"])
        is_correct = (user_ans == q["answer"])
        icon = "✅" if is_correct else "❌"

        with st.expander(f"{icon} Q{q['id']}. {q['question'][:40]}..."):
            st.markdown(f'<span class="badge">📂 {q["category"]}</span>', unsafe_allow_html=True)
            st.write(f"**문제:** {q['question']}")
            for i, opt in enumerate(q["options"]):
                prefix = "①②③④"[i]
                if i == q["answer"] and i == user_ans:
                    st.markdown(f"<span class='correct'>{prefix} {opt} ✅ (정답 & 내 답)</span>", unsafe_allow_html=True)
                elif i == q["answer"]:
                    st.markdown(f"<span class='correct'>{prefix} {opt} ← 정답</span>", unsafe_allow_html=True)
                elif i == user_ans:
                    st.markdown(f"<span class='wrong'>{prefix} {opt} ← 내 답</span>", unsafe_allow_html=True)
                else:
                    st.write(f"{prefix} {opt}")
            st.info(f"💡 **해설:** {q['explanation']}")

    # 다시하기 버튼
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 같은 설정으로 다시하기", use_container_width=True):
            st.session_state.quiz_started = True
            st.session_state.quiz_finished = False
            st.session_state.current_q = 0
            st.session_state.answers = {}
            st.session_state.score = 0
            st.session_state.start_time = time.time()
            st.rerun()
    with col2:
        if st.button("🏠 카테고리 선택으로 돌아가기", use_container_width=True):
            st.session_state.quiz_started = False
            st.session_state.quiz_finished = False
            st.rerun()


# ─────────────────────────────────────────────
# 라우팅
# ─────────────────────────────────────────────
if not st.session_state.logged_in:
    show_login()
elif st.session_state.quiz_started:
    show_quiz()
elif st.session_state.quiz_finished:
    show_result()
else:
    show_category_select()
