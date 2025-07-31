# -*- coding: utf-8 -*-
"""
투자자 의견 투표 시스템 모듈
"""
import streamlit as st

# 데이식스 이슈 초기 투표 데이터
DAY6_INITIAL_VOTES = {
    "sentiment": {"긍정": 365, "부정": 927, "중립": 208},
    "investment": {"매수": 281, "관망": 708, "매도": 511}
}


def initialize_vote_system():
    """투표 시스템 초기화"""
    if 'votes' not in st.session_state:
        st.session_state.votes = DAY6_INITIAL_VOTES.copy()
    if 'user_voted' not in st.session_state:
        st.session_state.user_voted = {"sentiment": False, "investment": False}


def add_vote(category, choice):
    """투표 추가"""
    if not st.session_state.user_voted[category]:
        st.session_state.votes[category][choice] += 1
        st.session_state.user_voted[category] = True
        st.success(f"✅ '{choice}' 투표가 완료되었습니다!")
        st.rerun()


def calculate_vote_percentages(votes_dict):
    """투표 비율 계산"""
    total = sum(votes_dict.values())
    return {choice: (count / total) * 100 for choice, count in votes_dict.items()}


def create_progress_button_html(label, percentage, color, is_clicked=False):
    """둥근 사각형 프로그레스 버튼 HTML"""

    if is_clicked:
        # 투표 후 - 채워지는 버튼
        button_html = f"""
        <div style="
            width: 100%;
            height: 60px;
            background: linear-gradient(to right, {color} {percentage}%, rgba(255,255,255,0.1) {percentage}%);
            border: 2px solid {color};
            border-radius: 15px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 8px 0;
            font-weight: bold;
            font-size: 16px;
            color: white;
            position: relative;
            overflow: hidden;
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
            transition: all 0.5s ease;
        ">
            <div style="
                position: relative;
                z-index: 2;
                text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
            ">
                {label} {percentage:.1f}%
            </div>
            <div style="
                position: absolute;
                top: 0;
                left: 0;
                height: 100%;
                width: {percentage}%;
                background: {color};
                border-radius: 13px;
                z-index: 1;
                animation: fillUp 0.8s ease-out;
            "></div>
        </div>
        <style>
        @keyframes fillUp {{
            from {{ width: 0%; }}
            to {{ width: {percentage}%; }}
        }}
        </style>
        """
    else:
        # 투표 전 - 일반 버튼
        button_html = f"""
        <div style="
            width: 100%;
            height: 60px;
            background: rgba(255,255,255,0.95);
            border: 2px solid {color};
            border-radius: 15px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 8px 0;
            font-weight: bold;
            font-size: 16px;
            color: {color};
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        ">
            {label}
        </div>
        """

    return button_html


def render_sentiment_vote():
    """감정 투표 섹션 렌더링"""
    st.write("### 💭 해당 이슈에 대한 감정은?")

    if not st.session_state.user_voted["sentiment"]:
        # 투표 전 - 일반 버튼
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("긍정", key="pos_sentiment", use_container_width=True):
                add_vote("sentiment", "긍정")

        with col2:
            if st.button("부정", key="neg_sentiment", use_container_width=True):
                add_vote("sentiment", "부정")

        with col3:
            if st.button("중립", key="neu_sentiment", use_container_width=True):
                add_vote("sentiment", "중립")

    else:
        # 투표 후 - 채워지는 버튼들
        percentages = calculate_vote_percentages(st.session_state.votes["sentiment"])
        total_votes = sum(st.session_state.votes["sentiment"].values())

        st.write(f"**총 {total_votes:,}명 참여**")
        st.write("")

        # 프로그레스 버튼들
        st.markdown(
            create_progress_button_html("긍정", percentages["긍정"], "#28a745", True),
            unsafe_allow_html=True
        )
        st.markdown(
            create_progress_button_html("부정", percentages["부정"], "#dc3545", True),
            unsafe_allow_html=True
        )
        st.markdown(
            create_progress_button_html("중립", percentages["중립"], "#6c757d", True),
            unsafe_allow_html=True
        )


def render_investment_vote():
    """투자 액션 투표 섹션 렌더링"""
    st.write("### 💰 투자 액션은?")

    if not st.session_state.user_voted["investment"]:
        # 투표 전 - 일반 버튼
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("매수", key="buy_action", use_container_width=True):
                add_vote("investment", "매수")

        with col2:
            if st.button("관망", key="hold_action", use_container_width=True):
                add_vote("investment", "관망")

        with col3:
            if st.button("매도", key="sell_action", use_container_width=True):
                add_vote("investment", "매도")

    else:
        # 투표 후 - 채워지는 버튼들
        percentages = calculate_vote_percentages(st.session_state.votes["investment"])
        total_votes = sum(st.session_state.votes["investment"].values())

        st.write(f"**총 {total_votes:,}명 참여**")
        st.write("")

        # 프로그레스 버튼들
        st.markdown(
            create_progress_button_html("매수", percentages["매수"], "#007bff", True),
            unsafe_allow_html=True
        )
        st.markdown(
            create_progress_button_html("관망", percentages["관망"], "#ffc107", True),
            unsafe_allow_html=True
        )
        st.markdown(
            create_progress_button_html("매도", percentages["매도"], "#dc3545", True),
            unsafe_allow_html=True
        )


def show_investor_vote_section():
    """투자자 의견 투표 메인 컴포넌트"""
    initialize_vote_system()

    st.subheader("📊 투자자 의견 투표")
    st.write("데이식스 본인확인 이슈에 대한 투자자들의 생각은?")

    col1, col2 = st.columns(2, gap="large")

    with col1:
        render_sentiment_vote()

    with col2:
        render_investment_vote()

    # 투표 안내
    if not st.session_state.user_voted["sentiment"] or not st.session_state.user_voted["investment"]:
        st.info("💡 버튼을 클릭하여 투표에 참여해보세요!")


def get_vote_results():
    """현재 투표 결과 반환"""
    if 'votes' not in st.session_state:
        return DAY6_INITIAL_VOTES
    return st.session_state.votes