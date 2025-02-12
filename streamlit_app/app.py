import streamlit as st
import requests
import re  # ✅ 정규식을 사용하여 Google Drive 파일 ID 추출

# 🔹 FastAPI 서버 주소
API_BASE_URL = "http://localhost:8066"

# 🔹 Streamlit 페이지 설정
st.set_page_config(page_title="🚗 교통사고 AI 상담 챗봇", layout="wide")

# 🔹 Streamlit 제목
st.title("🚗 교통사고 AI 상담 챗봇")

# 🔹 대화 기록과 상태 저장을 위한 세션 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

if "case_options" not in st.session_state:
    st.session_state.case_options = []  # 🚀 유사 사고 리스트 초기화

if "selected_case" not in st.session_state:
    st.session_state.selected_case = None  # 🚀 선택된 사고 초기화

# 🔹 대화 기록 출력
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 🔹 사용자 입력 (사고 상황 설명)
if st.session_state.selected_case is None:
    user_input = st.chat_input("사고 상황을 설명해주세요...")

    if user_input:
        # 🚀 1️⃣ 유사 사고 검색 API 요청
        response = requests.post(f"{API_BASE_URL}/search_accidents/", json={"accident_text": user_input})

        if response.status_code == 200:
            similar_cases = response.json()
            
            # 📌 유사 사고 3가지 리스트 생성 (URL 포함)
            st.session_state.case_options = similar_cases  # ✅ 세션에 전체 데이터 저장
            
            # 🔹 챗봇 대화 기록 업데이트 (사용자 메시지)
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            # 🔹 챗봇 대화 기록 업데이트 (AI 응답)
            case_selection_text = "다음과 같은 유사 사고가 있습니다:\n\n"
            for idx, case in enumerate(st.session_state.case_options):
                case_selection_text += f"**{idx+1}.** {case['accident']}\n\n"
            case_selection_text += "\n사고 번호를 입력해주세요 (예: 1, 2, 3)"
            
            st.session_state.messages.append({"role": "assistant", "content": case_selection_text})
            st.rerun()  # 🚀 UI 업데이트

# 🔹 사고 사례 선택 후 AI 질의응답
if len(st.session_state.case_options) > 0 and st.session_state.selected_case is None:
    selected_case_index = st.chat_input("사고 번호를 입력해주세요 (예: 1, 2, 3)")

    if selected_case_index and selected_case_index.isdigit():
        selected_case_index = int(selected_case_index) - 1

        if 0 <= selected_case_index < len(st.session_state.case_options):
            st.session_state.selected_case = st.session_state.case_options[selected_case_index]  # ✅ 선택된 사고 저장
            st.session_state.messages.append({"role": "user", "content": f"사고 {selected_case_index+1}번 선택"})
            st.rerun()  # 🚀 UI 업데이트

# 🔹 선택한 사고가 있으면 동영상 표시 및 질의응답 가능
if st.session_state.selected_case:
    selected_case = st.session_state.selected_case

    # 🚦 사고 관련 정보 출력
    st.subheader("🚦 선택한 사고 상황")
    st.write(f"**사고 설명:** {selected_case['accident']}")

    # 🎥 Google Drive 동영상 URL 변환 함수
    def convert_drive_url(drive_url):
        match = re.search(r"/d/([a-zA-Z0-9_-]+)", drive_url)
        if match:
            file_id = match.group(1)
            return f"https://drive.google.com/file/d/{file_id}/preview"
        return None  # 유효한 URL이 아닐 경우 None 반환

    # ✅ Google Drive URL 변환
    video_url = convert_drive_url(selected_case["url"])

    if video_url:
        # 🎥 Google Drive iframe으로 동영상 표시
        st.markdown(f"""
        <iframe src="{video_url}" width="700" height="400" allow="autoplay"></iframe>
        """, unsafe_allow_html=True)
    else:
        st.warning("⚠ 동영상을 직접 재생할 수 없습니다. 아래 버튼을 눌러 직접 확인하세요.")
        st.markdown(f"[🔗 동영상 보기]({selected_case['url']})", unsafe_allow_html=True)

    # 💬 AI 질의응답 기능
    user_question = st.chat_input("해당 사고에 대해 질문해주세요!")

    if user_question:
        # 🚀 2️⃣ AI 질의응답 API 요청
        ai_response = requests.post(f"{API_BASE_URL}/ask_ai/", 
                                    json={"accident_text": selected_case["accident"], "user_question": user_question})

        if ai_response.status_code == 200:
            response_text = ai_response.json()["response"]

            # 🔹 챗봇 대화 기록 업데이트 (사용자 질문)
            st.session_state.messages.append({"role": "user", "content": user_question})

            # 🔹 챗봇 대화 기록 업데이트 (AI 응답)
            st.session_state.messages.append({"role": "assistant", "content": response_text})
            st.rerun()  # 🚀 UI 업데이트