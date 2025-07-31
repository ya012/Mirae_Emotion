# -*- coding: utf-8 -*-
"""
투자자 유형 결과 페이지
"""
import streamlit as st
import sys
import os
from streamlit_extras.switch_page_button import switch_page

# utils 모듈 import를 위한 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web_app.utils.investor_classifier import get_type_info

# 페이지 설정
st.set_page_config(
    page_title="투자자 유형 결과",
    page_icon="🎭",
    layout="wide"
)


def show_result_animation():
    """결과 애니메이션 효과"""
    result = st.session_state.get('test_result', {})
    investor_type = result.get('investor_type')

    if not investor_type or investor_type == "TIE":
        st.error("테스트 결과가 없습니다. 다시 테스트를 진행해주세요.")
        if st.button("테스트 다시하기"):
            switch_page("투자자 유형 테스트")
        return

    type_info = get_type_info(investor_type)

    # 결과 발표 (깔끔하고 여백 충분히)
    st.markdown(
        f"""
        <div style="text-align: center; padding: 3rem 2rem; background: linear-gradient(135deg, {type_info['color']}08 0%, #ffffff 100%); border-radius: 16px; margin: 2rem 0; border: 1px solid {type_info['color']}20;">
            <div style="font-size: 4rem; margin-bottom: 1rem;">{type_info['character']}</div>
            <h2 style="color: #333; margin: 0 0 0.5rem 0; font-weight: 600;">
                당신은 <span style="color: {type_info['color']};">{type_info['name']}</span>입니다!
            </h2>
            <p style="font-size: 1.1rem; color: #666; margin: 0;">
                {type_info['subtitle']}
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


def show_detailed_result():
    """상세 결과 화면"""
    result = st.session_state.get('test_result', {})
    investor_type = result.get('investor_type')
    type_info = get_type_info(investor_type)

    # 두 컬럼으로 나누어 표시 (여백 개선)
    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.markdown("""
        <div style="background-color: #fafbfc; padding: 2rem; border-radius: 12px; margin-bottom: 2rem;">
        <h3 style="color: #333; margin-bottom: 2rem;">당신의 점수</h3>
        """, unsafe_allow_html=True)

        # 점수 시각화
        mirae_score = result.get('mirae_score', 0)
        asap_score = result.get('asap_score', 0)

        st.markdown(f"""
        <div style="margin-bottom: 1.5rem;">
        <strong>MIRAE형 점수</strong>: {mirae_score}/15점 ({result.get('mirae_percentage', 0)}%)
        </div>
        """, unsafe_allow_html=True)
        st.progress(mirae_score / 15)

        st.markdown("<div style='padding: 1rem 0;'></div>", unsafe_allow_html=True)

        st.markdown(f"""
        <div style="margin-bottom: 1.5rem;">
        <strong>ASAP형 점수</strong>: {asap_score}/15점 ({result.get('asap_percentage', 0)}%)
        </div>
        """, unsafe_allow_html=True)
        st.progress(asap_score / 15)

        # 우세 유형 표시
        if mirae_score > asap_score:
            st.success(f"**MIRAE형**이 {mirae_score - asap_score}점 더 높습니다!")
        else:
            st.success(f"**ASAP형**이 {asap_score - mirae_score}점 더 높습니다!")

        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style="background-color: #fafbfc; padding: 2rem; border-radius: 12px; margin-bottom: 2rem;">
        <h3 style="color: #333; margin-bottom: 2rem;">유형별 특성</h3>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="line-height: 1.8; margin-bottom: 2rem;">
        <strong style="color: {type_info['color']};">{type_info['name']}</strong>의 특징<br><br>
        <span style="color: #555;">{type_info['description']}</span>
        </div>
        """, unsafe_allow_html=True)

        # 키워드 태그 (색상은 기본색으로, 간소화)
        st.markdown("<strong>핵심 특성</strong>", unsafe_allow_html=True)
        st.markdown("<div style='padding: 0.5rem 0;'></div>", unsafe_allow_html=True)

        keyword_html = ""
        for keyword in type_info['keywords']:
            keyword_html += f"""
            <span style="
                background-color: #e9ecef; 
                color: #495057; 
                padding: 0.4rem 0.8rem; 
                border-radius: 20px; 
                margin: 0.2rem; 
                display: inline-block;
                font-size: 0.9rem;
                border: 1px solid #dee2e6;
            ">{keyword}</span>
            """

        st.markdown(keyword_html, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)


def show_action_buttons():
    """액션 버튼들"""
    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("홈으로 돌아가기", use_container_width=True):
            switch_page("main")

    with col2:
        if st.button("테스트 다시하기", use_container_width=True):
            # 테스트 관련 세션 초기화
            for key in ['test_started', 'test_answers', 'test_result']:
                if key in st.session_state:
                    del st.session_state[key]
            switch_page("투자자 유형 테스트")

    with col3:
        if st.button("AI 리포트 보기", use_container_width=True, type="primary"):
            switch_page("리포트 메뉴")


def main():
    """메인 함수"""
    st.title("투자자 유형 결과")

    # 결과가 없으면 테스트 페이지로 리다이렉트
    if 'test_result' not in st.session_state:
        st.warning("투자자 유형 테스트를 먼저 진행해주세요.")
        if st.button("테스트 하러가기"):
            switch_page("투자자 유형 테스트")
        return

    # 결과 화면들
    show_result_animation()
    show_detailed_result()
    show_action_buttons()


if __name__ == "__main__":
    main()