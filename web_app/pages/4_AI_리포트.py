# -*- coding: utf-8 -*-
"""
AI 요약 리포트 페이지 (모바일 최적화 버전) - 원래 UI 유지
"""
import streamlit as st
from datetime import datetime
import sys
import os
# from streamlit_extras.switch_page_button import switch_page
from utils.navigation import switch_page

# utils 모듈 import를 위한 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.news_analyzer import get_day6_news_summary
from utils.sns_analyzer import get_day6_sns_analysis
from utils.dart_analyzer import get_jyp_financial_insight
from utils.vote_system import show_investor_vote_section

# 페이지 설정
st.set_page_config(
    page_title="AI 요약 리포트",
    page_icon="🤖",
    layout="wide"
)


def show_report_header():
    """리포트 헤더 (모바일 최적화)"""
    issue_info = st.session_state.get('selected_issue', {})
    investor_type = st.session_state.get('investor_type', 'UNKNOWN')

    # 메인 제목
    st.title("🤖 AI 요약 리포트")

    # 이슈 제목과 투자자 유형을 한 줄에
    col1, col2 = st.columns([3, 1])

    with col1:
        st.subheader(f"📋 {issue_info.get('title', '데이식스 본인확인 논란')}")

    with col2:
        # 투자자 유형 표시 (작게)
        if investor_type == "MIRAE":
            st.markdown(
                '<div style="text-align: right; font-size: 14px; color: #2E8B57; font-weight: bold;">🎯 MIRAE형</div>',
                unsafe_allow_html=True)
        elif investor_type == "ASAP":
            st.markdown(
                '<div style="text-align: right; font-size: 14px; color: #FF6347; font-weight: bold;">⚡ ASAP형</div>',
                unsafe_allow_html=True)

    # 이슈 정보 (오른쪽 정렬)
    st.markdown(f"""
    <div style="text-align: right; font-size: 12px; color: #666; margin-bottom: 10px;">
        <strong>📅 이슈 발생일:</strong> {issue_info.get('issue_date', '2025-07-18~20')}<br>
        <strong>🏢 관련 종목:</strong> {issue_info.get('stock_symbol', 'JYP')} ({issue_info.get('stock_code', '035900')})<br>
        <strong>📊 분석 시간:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M')}
    </div>
    """, unsafe_allow_html=True)

    # 이슈 설명 (헤더 하단에 추가)
    st.markdown(f"""
    <div style="font-size: 14px; color: #555; font-style: italic; margin-bottom: 20px; padding: 10px; background-color: #f8f9fa; border-radius: 8px;">
        💡 {create_issue_summary()}
    </div>
    """, unsafe_allow_html=True)


# 기존 캐시 함수들 모두 삭제하고 이것으로 교체:

def load_news_analysis(investor_type):
    """뉴스 분석 로드 (캐시 없음)"""
    return get_day6_news_summary(investor_type)

def load_sns_analysis(investor_type):
    """SNS 분석 로드 (캐시 없음)"""
    news_context = "데이식스 팬미팅에서 과도한 본인확인 절차로 인한 팬들의 반발"
    return get_day6_sns_analysis(news_context, investor_type)

def load_financial_insight():
    """재무 인사이트 로드 (캐시 없음)"""
    return get_jyp_financial_insight()


def create_issue_summary():
    """이슈 요약 생성 (1-2줄)"""
    return "데이식스 팬미팅에서 생활기록부, 금융인증서 등을 요구하는 과도한 본인확인 절차로 인해 팬들의 강한 반발이 일어난 사건입니다."


def create_horizontal_sentiment_chart(percentages):
    """가로 바 혼합 차트 생성"""
    pos_pct = percentages.get('긍정', 0)
    neg_pct = percentages.get('부정', 0)
    neu_pct = percentages.get('중립', 0)

    chart_html = f"""
    <div style="
        width: 100%;
        height: 50px;
        border-radius: 25px;
        overflow: hidden;
        display: flex;
        font-size: 14px;
        font-weight: bold;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin: 15px 0;
    ">
        <div style="
            width: {pos_pct}%;
            background-color: #28a745;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
        ">
            긍정 {pos_pct:.1f}%
        </div>
        <div style="
            width: {neg_pct}%;
            background-color: #dc3545;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
        ">
            부정 {neg_pct:.1f}%
        </div>
        <div style="
            width: {neu_pct}%;
            background-color: #6c757d;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
        ">
            중립 {neu_pct:.1f}%
        </div>
    </div>
    """
    return chart_html


def show_news_section(investor_type):
    """뉴스 요약 섹션 (개선됨)"""
    st.subheader("📰 뉴스 요약")

    with st.spinner("뉴스 분석 중..."):
        news_result = load_news_analysis(investor_type)

    if news_result and news_result.get('success'):
        # 뉴스 제목 (전체 표시)
        st.markdown(f"**📰 {news_result['title']}**")

        # 날짜와 원문 링크
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown(f"**📅 {news_result['date']}**")
        with col2:
            if news_result.get('url') and news_result['url'] != '#':
                st.markdown(
                    f'<a href="{news_result["url"]}" target="_blank" style="background-color:#007bff; color:white; padding:5px 15px; border-radius:20px; text-decoration:none; font-size:12px;">📄 원문보기</a>',
                    unsafe_allow_html=True)

        # AI 요약 (문장 형식)
        st.markdown("### 📋 AI 요약")
        # 숫자 정렬 제거하고 문장으로 연결
        summary_text = news_result['summary'].replace('1. ', '').replace('2. ', '').replace('3. ', '').replace('4. ', '').replace('5. ', '').replace('6. ', '').replace('7. ', '').replace('8. ', '')
        st.markdown(summary_text)

    else:
        st.error("뉴스 요약을 불러올 수 없습니다.")


def show_sns_section(investor_type):
    """SNS 반응 분석 섹션 (개선됨)"""
    st.subheader("💬 SNS 반응 분석")

    with st.spinner("SNS 감정분석 중..."):
        sns_result = load_sns_analysis(investor_type)

    if sns_result and sns_result.get('success'):
        # 가로 바 혼합 차트
        percentages = sns_result['percentages']
        st.markdown(create_horizontal_sentiment_chart(percentages), unsafe_allow_html=True)

        # 반응 요약
        st.markdown("### 📝 반응 요약")
        if sns_result.get('reaction_summary'):
            st.markdown(sns_result['reaction_summary'])
        else:
            st.markdown(
                "팬들은 생활기록부 제출 요구에 대해 강한 반발을 보이고 있습니다. '과도한 개인정보 요구', '프라이버시 침해'라는 비판이 주를 이루고 있으며, 일부에서는 '어쩔 수 없다', '이해한다'는 수용적인 반응도 나타나고 있습니다. 전반적으로 부정적 여론이 우세한 상황입니다.")

        # 데이터 수집 안내
        st.markdown(
            '<p style="font-size: 11px; color: #888; margin-top: 15px;">* 이 데이터는 팔로워와 반응 수가 많은 글을 바탕으로 수집했습니다.</p>',
            unsafe_allow_html=True)

    else:
        st.error("SNS 분석을 불러올 수 없습니다.")


def show_financial_section():
    """공시자료 AI 인사이트 섹션 (수정됨)"""
    st.subheader("📊 공시자료 AI 인사이트")

    with st.spinner("재무 분석 중..."):
        financial_result = load_financial_insight()

    if financial_result and financial_result.get('success'):
        # 재무지표 (2x2 배치)
        st.markdown("### 💰 주요 재무지표")
        financial_data = financial_result['financial_data']

        col1, col2 = st.columns(2)
        with col1:
            st.metric("매출액", f"{financial_data['매출액_억원']}억원")
            st.metric("ROE", f"{financial_data['ROE']}%")
        with col2:
            st.metric("영업이익", f"{financial_data['영업이익_억원']}억원")
            st.metric("영업이익률", f"{financial_data['영업이익률']}%")

        # AI 분석
        st.markdown("### 🤖 AI 분석")
        st.markdown(financial_result['ai_insight'])

    # 캐시 파일 구조 확인 및 처리
    elif financial_result and "AI_인사이트" in financial_result:
        # 기존 캐시 파일 구조 처리
        st.markdown("### 💰 주요 재무지표")

        # 재무비율 데이터 사용
        ratios = financial_result.get("재무비율", {})
        col1, col2 = st.columns(2)
        with col1:
            # 매출액은 재무정보에서 가져오기 (억원 단위로 변환)
            revenue = financial_result.get("재무정보", [{}])[0].get("매출액", 0) / 100000000
            st.metric("매출액", f"{revenue:.0f}억원")
            st.metric("ROE", f"{ratios.get('ROE', 0)}%")
        with col2:
            # 영업이익도 재무정보에서 가져오기 (억원 단위로 변환)
            operating_profit = financial_result.get("재무정보", [{}])[0].get("영업이익", 0) / 100000000
            st.metric("영업이익", f"{operating_profit:.0f}억원")
            st.metric("영업이익률", f"{ratios.get('영업이익률', 0):.1f}%")

        # AI 분석
        st.markdown("### 🤖 AI 분석")
        st.markdown(financial_result.get("AI_인사이트", "AI 분석 내용이 없습니다."))

    else:
        st.error("재무 인사이트를 불러올 수 없습니다.")
        # 임시 데이터
        st.markdown("### 💰 주요 재무지표")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("매출액", "1,245억원")
            st.metric("ROE", "15.2%")
        with col2:
            st.metric("영업이익", "187억원")
            st.metric("영업이익률", "15.0%")

        st.markdown("### 🤖 AI 분석")
        st.markdown("""
        **재무현황 요약**: JYP는 안정적인 매출 구조와 양호한 수익성을 보이고 있습니다. **주요 강점**: 글로벌 아티스트 포트폴리오를 통한 다각화된 수익원을 확보하고 있습니다. **주요 리스크**: 경쟁 심화 및 아티스트 계약 관련 불확실성이 존재합니다. **투자관점**: 전반적으로 안정적이나 단기 이슈에 대한 신중한 접근이 필요합니다.
        """)


def show_mirae_report():
    """MIRAE형 리포트 (뉴스 → SNS 순서)"""
    show_news_section("MIRAE")
    st.markdown("---")
    show_sns_section("MIRAE")
    st.markdown("---")
    show_financial_section()


def show_asap_report():
    """ASAP형 리포트 (SNS → 뉴스 순서)"""
    show_sns_section("ASAP")
    st.markdown("---")
    show_news_section("ASAP")
    st.markdown("---")
    show_financial_section()


def show_navigation():
    """네비게이션 버튼"""
    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🏠 홈으로", use_container_width=True):
            switch_page("main")

    with col2:
        if st.button("📋 리포트 메뉴", use_container_width=True):
            switch_page("리포트 메뉴")

    with col3:
        if st.button("🔄 새로고침", use_container_width=True):
            st.cache_data.clear()
            st.rerun()


def main():
    """메인 함수"""
    # 투자자 유형 및 이슈 선택 확인
    investor_type = st.session_state.get('investor_type')
    selected_issue = st.session_state.get('selected_issue')

    if not investor_type:
        st.warning("투자자 유형이 설정되지 않았습니다.")
        if st.button("🎯 유형 테스트 하러가기"):
            switch_page("투자자 유형 테스트")
        return

    if not selected_issue:
        st.warning("분석할 이슈가 선택되지 않았습니다.")
        if st.button("📋 리포트 메뉴로 가기"):
            switch_page("리포트 메뉴")
        return

    # 리포트 헤더
    show_report_header()
    st.markdown("---")

    # 투자자 유형별 리포트 표시
    if investor_type == "MIRAE":
        show_mirae_report()
    else:  # ASAP
        show_asap_report()

    # 투표 섹션 (공통)
    st.markdown("---")
    show_investor_vote_section()

    # 네비게이션
    show_navigation()


if __name__ == "__main__":
    main()