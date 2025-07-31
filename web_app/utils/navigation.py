# -*- coding: utf-8 -*-
"""
페이지 네비게이션 유틸리티
"""
import streamlit as st


def switch_page(page_name):
    """페이지 전환 함수"""
    page_mapping = {
        "main": "main.py",
        "투자자 유형 테스트": "pages/1_투자자_유형_테스트.py",
        "유형 결과": "pages/2_유형_결과.py",
        "리포트 메뉴": "pages/3_리포트_메뉴.py",
        "AI 리포트": "pages/4_AI_리포트.py"
    }

    if page_name in page_mapping:
        st.switch_page(page_mapping[page_name])
    else:
        st.error(f"알 수 없는 페이지: {page_name}")