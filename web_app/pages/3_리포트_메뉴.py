# -*- coding: utf-8 -*-
"""
리포트 메뉴 페이지
"""
import streamlit as st
from streamlit_extras.switch_page_button import switch_page

# 페이지 설정
st.set_page_config(
    page_title="AI 리포트 메뉴",
    page_icon="📊",
    layout="wide"
)


def show_user_info():
    """사용자 정보 표시"""
    investor_type = st.session_state.get('investor_type')

    if investor_type:
        # 오른쪽 상단에 사용자 유형 표시 (깔끔하게)
        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown("""
            <h1 style="margin: 0; color: #333;">AI 리포트 메뉴</h1>
            """, unsafe_allow_html=True)

        with col2:
            if investor_type == "MIRAE":
                st.markdown("""
                <div style="text-align: right; padding: 0.8rem 1.2rem; background-color: #f8f9ff; border-radius: 8px; border-left: 3px solid #2f5f98;">
                <span style="color: #2f5f98; font-weight: 600;">MIRAE형</span> <span style="color: #666;">투자자</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="text-align: right; padding: 0.8rem 1.2rem; background-color: #fff8f8; border-radius: 8px; border-left: 3px solid #ff6d4d;">
                <span style="color: #ff6d4d; font-weight: 600;">ASAP형</span> <span style="color: #666;">투자자</span>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.title("AI 리포트 메뉴")
        st.warning("투자자 유형이 설정되지 않았습니다.")
        if st.button("유형 테스트 하러가기"):
            switch_page("투자자 유형 테스트")
        return False

    return True


def show_issue_list():
    """이슈 리스트 표시"""
    st.markdown("<div style='padding: 2rem 0 1rem 0;'></div>", unsafe_allow_html=True)

    # 데이식스 이슈 카드 (깔끔하게 개선)
    st.markdown("""
    <div style="background-color: #fafbfc; border-radius: 12px; padding: 2rem; border: 1px solid #e9ecef; margin-bottom: 2rem;">
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([4, 1])

    with col1:
        st.markdown("""
        <h3 style="color: #333; margin: 0 0 1.5rem 0;">데이식스 본인확인 논란</h3>

        <div style="color: #666; line-height: 1.6; margin-bottom: 1.5rem;">
        <strong>발생일</strong>: 2025년 7월 18일-20일<br>
        <strong>관련 종목</strong>: JYP엔터테인먼트 (035900)
        </div>

        <div style="color: #555; line-height: 1.7;">
        데이식스 팬미팅에서 과도한 본인확인 절차(생활기록부, 금융인증서 요구)로 인한 
        팬들의 강한 반발과 논란이 확산된 사건
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("<div style='padding: 2rem 0;'></div>", unsafe_allow_html=True)
        if st.button(
                "리포트 보기",
                use_container_width=True,
                type="primary"):
            # 세션에 선택된 이슈 정보 저장
            st.session_state.selected_issue = {
                "title": "데이식스 본인확인 논란",
                "stock_symbol": "JYP",
                "stock_code": "035900",
                "issue_date": "2025-07-18",
                "query": "데이식스 본인"
            }

            switch_page("AI 리포트")

    st.markdown("</div>", unsafe_allow_html=True)


def show_coming_soon():
    """추후 예정 이슈들"""
    st.markdown("---")
    st.subheader("추후 예정")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        ### 다가오는 이슈들
        - **하이브 분기 실적 발표** (8월 예정)
        - **SM 신인 그룹 데뷔** (9월 예정)  
        - **YG 컴백 라인업** (하반기 예정)
        """)

    with col2:
        st.markdown("""
        ### 실시간 모니터링
        - 주요 엔터 종목 이슈 감지 시스템
        - 소셜미디어 트렌드 분석
        - 자동 리포트 생성 (베타)
        """)


def show_navigation():
    """네비게이션 버튼"""
    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("홈으로", use_container_width=True):
            switch_page("main")

    with col2:
        if st.button("유형 재테스트", use_container_width=True):
            # 기존 테스트 결과 초기화
            for key in ['test_started', 'test_answers', 'test_result']:
                if key in st.session_state:
                    del st.session_state[key]
            switch_page("투자자 유형 테스트")

    with col3:
        if st.button("새로고침", use_container_width=True):
            st.rerun()


def main():
    """메인 함수"""

    # 사용자 정보 확인
    if not show_user_info():
        return

    # 이슈 리스트
    show_issue_list()

    # 추후 예정
    show_coming_soon()

    # 네비게이션
    show_navigation()


if __name__ == "__main__":
    main()