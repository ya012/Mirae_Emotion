# -*- coding: utf-8 -*-
"""
투자자 유형 테스트 페이지
"""
import streamlit as st
import sys
import os
from streamlit_extras.switch_page_button import switch_page

# utils 모듈 import를 위한 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web_app.utils.investor_classifier import get_questions, classify_investor_type

# 페이지 설정
st.set_page_config(
    page_title="투자자 유형 테스트",
    page_icon="🎯",
    layout="wide"
)


def show_test_intro():
    """테스트 소개 화면"""
    st.title("투자자 유형 테스트")
    st.markdown("### 당신의 투자 성향을 알아보세요")

    st.markdown("""
    ---
    **테스트 안내**
    - 총 6개 질문으로 구성되어 있습니다
    - 각 질문에 대해 1점(전혀 그렇지 않다) ~ 5점(매우 그렇다)로 평가해주세요
    - 솔직하게 답변할수록 정확한 결과를 얻을 수 있습니다

    **결과 유형**
    - **MIRAE형**: 기업의 펀더멘털과 공식 발표를 신뢰하는 투자자
    - **ASAP형**: SNS 여론과 팬들의 실시간 반응을 중시하는 투자자
    """)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("테스트 시작하기",
                     use_container_width=True,
                     type="secondary"):
            st.session_state.test_started = True
            st.rerun()


def show_questions():
    """질문 화면"""
    st.title("투자자 유형 테스트")
    st.markdown("### 각 문항에 대해 가장 적절한 점수를 선택해주세요")

    questions = get_questions()

    # 진행률 표시
    progress_container = st.container()

    with st.form("investor_test_form"):
        answers = {}

        for i, q in enumerate(questions, 1):
            st.markdown(f"---")
            st.markdown(f"**Q{i}. {q['question']}**")

            # 5점 척도 라디오 버튼 (간소화)
            score = st.radio(
                f"Q{i} 점수:",
                options=[1, 2, 3, 4, 5],
                format_func=lambda x: f"{x}점 - {'전혀 그렇지 않다' if x==1 else '그렇지 않다' if x==2 else '보통이다' if x==3 else '그렇다' if x==4 else '매우 그렇다'}",
                horizontal=True,
                key=f"q{i}_score"
            )

            answers[q['id']] = score

        st.markdown("---")

        # 제출 버튼
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submitted = st.form_submit_button(
                "결과 확인하기",
                use_container_width=True,
                type="secondary"
            )

    # 진행률 업데이트
    with progress_container:
        st.progress(1.0, text="모든 질문 완료")

    if submitted:
        # 결과 계산
        result = classify_investor_type(answers)

        # 세션에 저장
        st.session_state.test_answers = answers
        st.session_state.test_result = result
        st.session_state.investor_type = result['investor_type']

        # 결과 페이지로 이동
        if result['investor_type'] != "TIE":
            switch_page("유형 결과")
        else:
            show_tie_breaker(result)


def show_tie_breaker(result):
    """동점일 경우 선택 화면"""
    st.markdown("---")
    st.subheader("투자 성향이 균형적이네요!")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"""
        **점수 결과**
        - MIRAE 점수: {result['mirae_score']}/15점
        - ASAP 점수: {result['asap_score']}/15점

        두 성향이 비슷하게 나타났습니다.
        """)

    with col2:
        st.markdown("""
        **어떤 유형으로 분류될까요?**

        더 끌리는 투자 스타일을 선택해주세요:
        """)

        if st.button("MIRAE형 (펀더멘털 중심)", use_container_width=True):
            st.session_state.investor_type = "MIRAE"
            st.session_state.test_result['investor_type'] = "MIRAE"
            switch_page("유형 결과")

        if st.button("ASAP형 (여론 반응 중심)", use_container_width=True):
            st.session_state.investor_type = "ASAP"
            st.session_state.test_result['investor_type'] = "ASAP"
            switch_page("유형 결과")


def main():
    """메인 함수"""
    # 세션 초기화
    if 'test_started' not in st.session_state:
        st.session_state.test_started = False

    # 홈 버튼
    if st.button("홈으로", key="home_btn"):
        # 테스트 상태 초기화
        for key in ['test_started', 'test_answers', 'test_result']:
            if key in st.session_state:
                del st.session_state[key]
        switch_page("main")

    # 화면 분기
    if not st.session_state.test_started:
        show_test_intro()
    else:
        show_questions()


if __name__ == "__main__":
    main()