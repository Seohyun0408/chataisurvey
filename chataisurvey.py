# chataisurvey.py

import streamlit as st
import openai

# 🔐 OpenAI API 키
openai.api_key = st.secrets["openai_key"]  # secrets.toml에 저장

st.set_page_config(page_title="소프트웨어 제품 설문 챗봇", page_icon="🧓", layout="centered")
st.title("소프트웨어 제품 사용자 챗봇 설문")

# --------------------------------
# GPT 꼬리질문 생성 함수 (최대 3회)
# --------------------------------
def generate_followup(question, prev_answers):
    base_prompt = f"질문: {question}\n"
    for idx, a in enumerate(prev_answers):
        base_prompt += f"답변 {idx+1}: {a}\n"
    base_prompt += "이 내용을 바탕으로 더 깊이 있는 후속 질문을 한 문장으로 해주세요."

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "당신은 친절한 UX 인터뷰 AI입니다. 답변을 바탕으로 구체적인 후속 질문을 생성하세요."},
                {"role": "user", "content": base_prompt}
            ],
            temperature=0.7
        )
        return response.choices[0].message["content"].strip()
    except Exception as e:
        return f"GPT 오류: {str(e)}"

# ----------------------
# 정량 질문 (Likert)
# ----------------------
likert_qs = [
    "1. 이 앱의 메뉴와 기능 배치는 이해하기 쉬웠습니까?",
    "2. 글씨 크기, 색상 등 화면의 시각적 구성이 편안하게 느껴졌습니까?",
    "3. 원하는 기능을 찾고 사용하는 과정이 간단했습니까?",
    "4. 인증, 검색, 예약 등의 절차에서 혼란을 느낀 적이 있었습니까?",
    "5. 이 앱은 시니어를 위한 서비스라고 느꼈습니까?",
    "6. 일상 속에서 지속적으로 사용할 가치가 있다고 느꼈습니까?"
]
likert_choices = ["1 (전혀 아니다)", "2", "3", "4", "5 (매우 그렇다)"]

with st.form("likert"):
    st.subheader("📊 정량 평가")
    likert_answers = [st.radio(q, likert_choices, key=f"likert_{i}") for i, q in enumerate(likert_qs)]
    if st.form_submit_button("다음"):
        st.session_state["likert_done"] = True
        st.rerun()

# ----------------------
# 정성 평가 + 꼬리질문
# ----------------------
open_qs = [
    "1. 처음 앱을 사용했을 때 가장 어려웠던 점은 무엇이었습니까?",
    "2. 특정 기능을 사용할 때 당황하거나 다시 돌아간 적이 있습니까?",
    "3. 이 앱이 시니어 사용자를 고려했다고 느낀 부분이 있습니까?",
    "4. 이 앱이 평소 생활에서 어떤 상황에 가장 유용할 것 같습니까?"
]

if "likert_done" in st.session_state:
    st.subheader("💬 정성 평가 (GPT 꼬리질문 최대 3회)")
    if "qa_progress" not in st.session_state:
        st.session_state["qa_progress"] = {q: {"answers": [], "done": False} for q in open_qs}

    for q in open_qs:
        if st.session_state["qa_progress"][q]["done"]:
            continue

        answers = st.session_state["qa_progress"][q]["answers"]
        if len(answers) == 0:
            user_input = st.text_input(f"질문: {q}", key=f"{q}_a0")
            if user_input:
                answers.append(user_input)
                st.rerun()
        elif len(answers) < 3:
            followup = generate_followup(q, answers)
            user_input = st.text_input(f"꼬리질문: {followup}", key=f"{q}_a{len(answers)}")
            if user_input:
                answers.append(user_input)
                st.rerun()
        else:
            st.session_state["qa_progress"][q]["done"] = True
            st.rerun()
        break

# ----------------------
# 완료 메시지
# ----------------------
if "qa_progress" in st.session_state:
    done_count = sum([v["done"] for v in st.session_state["qa_progress"].values()])
    if done_count == len(open_qs):
        st.success("🎉 모든 설문이 완료되었습니다! 감사합니다.")
