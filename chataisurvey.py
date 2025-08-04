import streamlit as st
import openai

openai.api_key = st.secrets["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"]  # OpenAI 계정에서 발급받은 키"]  # streamlit cloud용

st.set_page_config(page_title="시니어 챗봇 설문", page_icon="🧓", layout="centered")

if "step" not in st.session_state:
    st.session_state.step = 0
    st.session_state.answers = []
    st.session_state.clarification_count = 0
    st.session_state.awaiting_clarification = False
    st.session_state.last_question = ""
    st.session_state.last_answer = ""

likert_questions = [
    "1. 이 앱의 메뉴와 기능 배치는 이해하기 쉬웠습니까?",
    "2. 글씨 크기, 색상 등 화면의 시각적 구성이 편안하게 느껴졌습니까?",
    "3. 원하는 기능을 찾고 사용하는 과정이 간단했습니까?",
    "4. 인증, 검색, 예약 등의 절차에서 혼란을 느낀 적이 있었습니까?",
    "5. 이 앱은 시니어를 위한 서비스라고 느껴졌습니까?",
    "6. 일상 속에서 지속적으로 사용할 가치가 있다고 느꼈습니까?"
]

open_questions = [
    "7. 처음 앱을 사용했을 때 가장 어려웠던 점은 무엇이었습니까?",
    "8. 특정 기능을 사용할 때 당황하거나 다시 돌아간 적이 있습니까?",
    "9. 이 앱이 시니어 사용자를 고려했다고 느낀 부분이 있습니까?",
    "10. 이 앱이 평소 생활에서 어떤 상황에 가장 유용할 것 같습니까?"
]

choices = ["1 (전혀 아니다)", "2", "3", "4", "5 (매우 그렇다)"]

st.title("🧓 시니어 챗봇 설문")

def ask_clarification(question, user_answer):
    messages = [
        {"role": "system", "content": "당신은 시니어 인터뷰 응답을 잘 파악하고 명확하게 꼬리질문을 던지는 친절한 인터뷰어입니다."},
        {"role": "user", "content": f"사용자에게 다음 질문을 했습니다: '{question}'\n그리고 그는 이렇게 대답했습니다: '{user_answer}'\n이 답변이 모호하거나 너무 간단하면 좀 더 자세히 듣기 위해 한 문장짜리 추가 질문을 해주세요. 그렇지 않으면 '응답 충분'이라고만 답하세요."}
    ]
    res = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
    return res.choices[0].message.content.strip()

if st.session_state.step < len(likert_questions):
    q = likert_questions[st.session_state.step]
    st.markdown(f"**{q}**")
    choice = st.radio("아래에서 선택해 주세요:", choices, key=f"likert_{st.session_state.step}")
    if st.button("다음"):
        st.session_state.answers.append((q, choice))
        st.session_state.step += 1
        st.experimental_rerun()

elif st.session_state.step < len(likert_questions) + len(open_questions):
    idx = st.session_state.step - len(likert_questions)
    q = open_questions[idx]
    st.markdown(f"**{q}**")
    answer = st.text_input("✍️ 응답을 입력해 주세요", key=f"open_{st.session_state.step}")

    if st.button("입력"):
        st.session_state.last_question = q
        st.session_state.last_answer = answer
        clarification = ask_clarification(q, answer)

        if "응답 충분" in clarification or st.session_state.clarification_count >= 2:
            st.session_state.answers.append((q, answer))
            st.session_state.step += 1
            st.session_state.clarification_count = 0
            st.session_state.awaiting_clarification = False
            st.experimental_rerun()
        else:
            st.session_state.awaiting_clarification = True
            st.session_state.clarification_count += 1
            st.experimental_rerun()

    elif st.session_state.awaiting_clarification:
        clarification = ask_clarification(st.session_state.last_question, st.session_state.last_answer)
        st.markdown(f"🤖 꼬리질문: {clarification}")
        followup = st.text_input("👉 추가 답변:", key=f"clarify_{st.session_state.step}_{st.session_state.clarification_count}")
        if st.button("추가입력"):
            combined = st.session_state.last_answer + " " + followup
            st.session_state.last_answer = combined
            st.experimental_rerun()

else:
    st.success("설문이 완료되었습니다. 감사합니다! 🎉")
    st.subheader("📋 응답 요약")
    for q, a in st.session_state.answers:
        st.write(f"**{q}**\n→ {a}")