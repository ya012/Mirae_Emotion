# -*- coding: utf-8 -*-
"""
투자자 유형 분류 모듈
"""

# 투자자 분류 질문 데이터
INVESTOR_QUESTIONS = [
    {
        "id": "Q1",
        "question": "나는 투자에서 장기적인 수익이 더 중요하다고 생각한다.",
        "type": "MIRAE"
    },
    {
        "id": "Q2",
        "question": "손실이 발생하면 바로 반응하거나 매매하고 싶어진다.",
        "type": "ASAP"
    },
    {
        "id": "Q3",
        "question": "실적, 재무제표 등 기초 정보가 더 믿을 만하다고 느낀다.",
        "type": "MIRAE"
    },
    {
        "id": "Q4",
        "question": "소셜미디어, 뉴스 등 이슈를 투자 판단 기준으로 삼는다.",
        "type": "ASAP"
    },
    {
        "id": "Q5",
        "question": "투자 종목의 가격을 자주 확인하지 않는다.",
        "type": "MIRAE"
    },
    {
        "id": "Q6",
        "question": "투자 정보를 실시간으로 탐색하거나 커뮤니티를 자주 본다.",
        "type": "ASAP"
    }
]

# 투자자 유형별 특성
INVESTOR_TYPES = {
    "MIRAE": {
        "name": "MIRAE형",
        "subtitle": "펀더멘털 중심 투자자",
        "description": "엔터테인먼트 산업의 감정적 특성을 인정하면서도, 근본적으로는 기업의 펀더멘털이 중요하다고 생각하는 투자자입니다. SNS 반응보다는 뉴스에서 나오는 기업의 공식 발표, 실적, 사업 계획 등을 더 신뢰합니다.",
        "keywords": ["펀더멘털 중심", "객관적 분석", "공식 정보 신뢰"],
        "character": "🎯",
        "color": "#2f5f98"
    },
    "ASAP": {
        "name": "ASAP형",
        "subtitle": "여론 반응 중심 투자자",
        "description": "엔터테인먼트 산업에서는 팬들의 반응과 여론이 즉시 주가로 연결된다는 것을 잘 아는 투자자입니다. 뉴스보다는 SNS에서 실시간으로 일어나는 팬들의 감정 변화를 더 중요하게 생각합니다.",
        "keywords": ["여론 중심", "실시간 반응", "감정 변화 추적"],
        "character": "⚡",
        "color": "#ff6d4d"
    }
}


def classify_investor_type(answers):
    """
    투자자 유형 분류

    Args:
        answers: dict - {"Q1": 4, "Q2": 2, "Q3": 5, ...}

    Returns:
        dict - 분류 결과 및 점수
    """

    # 점수 계산
    mirae_score = answers.get("Q1", 0) + answers.get("Q3", 0) + answers.get("Q5", 0)
    asap_score = answers.get("Q2", 0) + answers.get("Q4", 0) + answers.get("Q6", 0)

    # 유형 결정
    if mirae_score > asap_score:
        investor_type = "MIRAE"
    elif asap_score > mirae_score:
        investor_type = "ASAP"
    else:
        # 동점일 경우 사용자 선택 필요
        investor_type = "TIE"

    # 결과 반환
    result = {
        "investor_type": investor_type,
        "mirae_score": mirae_score,
        "asap_score": asap_score,
        "total_possible": 15,  # 각 유형당 최대 점수 (3문항 × 5점)
        "mirae_percentage": round((mirae_score / 15) * 100, 1),
        "asap_percentage": round((asap_score / 15) * 100, 1)
    }

    # 유형별 상세 정보 추가
    if investor_type != "TIE":
        result.update(INVESTOR_TYPES[investor_type])

    return result


def get_questions():
    """투자자 분류 질문 목록 반환"""
    return INVESTOR_QUESTIONS


def get_type_info(investor_type):
    """특정 투자자 유형 정보 반환"""
    return INVESTOR_TYPES.get(investor_type, {})


def calculate_compatibility(answers):
    """
    투자자 성향 호환성 분석

    Args:
        answers: dict - 답변 데이터

    Returns:
        dict - 상세 분석 결과
    """
    mirae_score = answers.get("Q1", 0) + answers.get("Q3", 0) + answers.get("Q5", 0)
    asap_score = answers.get("Q2", 0) + answers.get("Q4", 0) + answers.get("Q6", 0)

    # 성향 강도 계산
    total_score = mirae_score + asap_score
    mirae_ratio = (mirae_score / total_score * 100) if total_score > 0 else 50
    asap_ratio = (asap_score / total_score * 100) if total_score > 0 else 50

    # 성향 강도 판정
    if abs(mirae_ratio - asap_ratio) >= 40:
        intensity = "강함"
    elif abs(mirae_ratio - asap_ratio) >= 20:
        intensity = "보통"
    else:
        intensity = "약함"

    return {
        "mirae_ratio": round(mirae_ratio, 1),
        "asap_ratio": round(asap_ratio, 1),
        "intensity": intensity,
        "balance_score": 100 - abs(mirae_ratio - asap_ratio)  # 균형 점수
    }


# 테스트용 함수
def test_classification():
    """분류 테스트"""
    test_cases = [
        # MIRAE형 예시
        {"Q1": 5, "Q2": 2, "Q3": 4, "Q4": 1, "Q5": 5, "Q6": 2},
        # ASAP형 예시
        {"Q1": 2, "Q2": 5, "Q3": 1, "Q4": 4, "Q5": 2, "Q6": 5},
        # 동점 예시
        {"Q1": 3, "Q2": 3, "Q3": 3, "Q4": 3, "Q5": 3, "Q6": 3}
    ]

    for i, answers in enumerate(test_cases, 1):
        print(f"\n=== 테스트 케이스 {i} ===")
        result = classify_investor_type(answers)
        print(f"유형: {result['investor_type']}")
        print(f"MIRAE 점수: {result['mirae_score']}/15 ({result['mirae_percentage']}%)")
        print(f"ASAP 점수: {result['asap_score']}/15 ({result['asap_percentage']}%)")

        if result['investor_type'] != "TIE":
            print(f"특성: {result['name']} - {result['subtitle']}")


if __name__ == "__main__":
    test_classification()