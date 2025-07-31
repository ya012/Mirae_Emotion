# -*- coding: utf-8 -*-
"""
E:motion - 메인 앱
"""
import streamlit as st
from dotenv import load_dotenv
import os
from streamlit_extras.switch_page_button import switch_page
# from utils.navigation import switch_page

# 환경변수 로드
load_dotenv()

# 페이지 설정
st.set_page_config(
    page_title="E:motion",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)


# 사이드바 네비게이션
def sidebar_navigation():
    st.sidebar.title("🎵 E:motion")
    st.sidebar.markdown("---")

    # 진행 단계 표시
    if 'investor_type' not in st.session_state:
        st.session_state.investor_type = None
    if 'query' not in st.session_state:
        st.session_state.query = None
    if 'stock_symbol' not in st.session_state:
        st.session_state.stock_symbol = None

    # 단계별 진행 상황
    st.sidebar.subheader("진행 단계")

    # 1단계: 투자자 유형
    if st.session_state.investor_type:
        st.sidebar.success(f"투자자 유형: {st.session_state.investor_type}형")
    else:
        st.sidebar.info("투자자 유형 테스트 필요")

    # 2단계: 종목 선택
    if st.session_state.query:
        st.sidebar.success(f"분석 주제: {st.session_state.query}")
    else:
        st.sidebar.info("종목/이슈 선택 필요")

    # 3단계: 리포트 생성
    if st.session_state.investor_type and st.session_state.query:
        st.sidebar.success("AI 리포트 생성 가능")
    else:
        st.sidebar.info("AI 리포트 대기 중")

    st.sidebar.markdown("---")

    # 페이지 링크
    st.sidebar.subheader("페이지 이동")

    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("유형 테스트", use_container_width=True):
            switch_page("투자자 유형 테스트")
    with col2:
        if st.button("리포트 메뉴", use_container_width=True):
            switch_page("리포트 메뉴")

    if st.sidebar.button("AI 리포트", use_container_width=True):
        if st.session_state.investor_type:
            switch_page("리포트 메뉴")
        else:
            st.sidebar.error("먼저 투자자 유형 테스트를 완료해주세요!")


def main_page():
    """메인 페이지"""
    # 헤더 (여백 충분히 확보)
    st.markdown("""
    <div style="text-align: center; padding: 3rem 0 2rem 0;">
        <h1 style="font-size: 3.5rem; margin: 0; font-weight: 700;">🎵 E:motion</h1>
        <h3 style="color: #666; margin: 1rem 0 0 0; font-weight: 400;">감정을 읽는 금융 리포트</h3>
        <p style="color: #888; font-size: 1.1rem; line-height: 1.6; margin: 2rem auto; max-width: 600px;">
        SNS의 소비자 반응이 주가를 움직이는 엔터테인먼트 시장,<br>
        투자자가 SNS 속 소비자 감정을 파악하여<br>
        현명한 투자 결정을 내릴 수 있도록 도와주는 AI 요약 리포트
        </p>
    </div>
    """, unsafe_allow_html=True)

    # 소개 섹션 (충분한 여백과 깔끔한 디자인)
    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown("""
        <div style="padding: 2rem; background: linear-gradient(135deg, #f8f9ff 0%, #ffffff 100%); border-radius: 12px; box-shadow: 0 2px 20px rgba(47, 95, 152, 0.08); border: 1px solid #f0f2f6;">
            <div style="display: flex; align-items: center; margin-bottom: 1.5rem;">
                <span style="font-size: 2rem; margin-right: 0.8rem;">🎯</span>
                <span style="font-size: 1.5rem; font-weight: 600; color: #2f5f98;">MIRAE형</span>
            </div>
            <h4 style="color: #333; margin: 0 0 1.5rem 0; font-weight: 500;">펀더멘털 중심 투자자</h4>
            <div style="color: #555; line-height: 1.8;">
                • 기업 공식 발표, 실적 신뢰<br>
                • 근본적 펀더멘털 중시<br>
                • 객관적 분석 선호
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style="padding: 2rem; background: linear-gradient(135deg, #fff8f8 0%, #ffffff 100%); border-radius: 12px; box-shadow: 0 2px 20px rgba(255, 109, 77, 0.08); border: 1px solid #f6f0f0;">
            <div style="display: flex; align-items: center; margin-bottom: 1.5rem;">
                <span style="font-size: 2rem; margin-right: 0.8rem;">⚡</span>
                <span style="font-size: 1.5rem; font-weight: 600; color: #ff6d4d;">ASAP형</span>
            </div>
            <h4 style="color: #333; margin: 0 0 1.5rem 0; font-weight: 500;">여론 반응 중심 투자자</h4>
            <div style="color: #555; line-height: 1.8;">
                • SNS 실시간 반응 중시<br>
                • 팬들 감정 변화 추적<br>
                • 빠른 시장 대응
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 시작하기 버튼 (충분한 여백)
    st.markdown("<div style='padding: 3rem 0;'></div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("투자자 유형 테스트 시작하기",
                     use_container_width=True,
                     type="secondary",
                     help="6개 질문으로 당신의 투자 성향을 분석합니다"):
            switch_page("투자자 유형 테스트")

    # 서비스 특징 (여백과 타이포그래피 개선)
    st.markdown("<div style='padding: 2rem 0;'></div>", unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align: center;">
        <h3 style="color: #333; margin-bottom: 2rem;">서비스 특징</h3>
        <div style="max-width: 700px; margin: 0 auto; font-size: 1rem; color: #666; line-height: 1.8; background-color: #fafbfc; padding: 2rem; border-radius: 12px;">
            <strong style="color: #333;">주요 기능</strong><br><br>
            네이버 뉴스와 트위터 SNS 데이터를 수집하여 HyperCLOVA X 기반 AI 분석을 통해<br>
            투자자 유형별 맞춤형 리포트를 제공합니다.<br><br>
            실시간 감정분석과 뉴스 요약으로 효율적인 투자 의사결정을 지원합니다.
        </div>
    </div>
    """, unsafe_allow_html=True)


# 메인 실행
if __name__ == "__main__":
    sidebar_navigation()
    main_page()