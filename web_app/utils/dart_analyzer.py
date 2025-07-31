# -*- coding: utf-8 -*-
"""
DART 공시자료 분석 모듈 (디버깅 버전)
"""
import json
import requests
import uuid
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()


def debug_api_connection():
    """API 연결 상태 디버깅"""
    api_key = os.getenv('CLOVA_API_KEY')

    print("🔍 CLOVA API 연결 상태 체크:")
    print(f"1. API 키 존재 여부: {'✅' if api_key else '❌'}")

    if api_key:
        print(f"2. API 키 길이: {len(api_key)}자")
        print(f"3. API 키 시작 부분: {api_key[:10]}...")
        print(f"4. API 키 형식 체크: {'✅' if api_key.startswith('NCP-') else '❌'}")
    else:
        print("❌ .env 파일에 CLOVA_API_KEY가 설정되지 않았습니다!")
        return False

    return True


def generate_jyp_ai_insight():
    """JYP 공시자료 AI 인사이트 생성 (디버깅 버전)"""

    # API 연결 상태 먼저 체크
    if not debug_api_connection():
        return None

    # JYP 재무 데이터
    jyp_financial_data = {
        "매출액_억원": 1245.3,
        "영업이익_억원": 187.2,
        "ROE": 15.2,
        "영업이익률": 15.0
    }

    api_key = os.getenv('CLOVA_API_KEY')

    system_prompt = """당신은 엔터테인먼트 투자 전문가입니다.
제공된 재무정보를 바탕으로 분석해주세요:

**재무현황 요약**: (전반적인 재무 상태)
**주요 강점**: (긍정적 요소들)  
**주요 리스크**: (우려 요소들)
**투자관점**: (투자 의견)

간결하고 전문적으로 작성해주세요."""

    user_content = f"""
JYP엔터테인먼트 재무현황:
- 매출액: {jyp_financial_data['매출액_억원']}억원
- 영업이익: {jyp_financial_data['영업이익_억원']}억원
- ROE: {jyp_financial_data['ROE']}%
- 영업이익률: {jyp_financial_data['영업이익률']}%

위 정보로 투자 분석을 해주세요.
"""

    request_id = str(uuid.uuid4()).replace('-', '')

    # 다양한 헤더 형식 시도
    headers_options = [
        {
            'Authorization': f'Bearer {api_key}',
            'X-NCP-CLOVASTUDIO-REQUEST-ID': request_id,
            'Content-Type': 'application/json; charset=utf-8',
            'Accept': 'text/event-stream'
        },
        {
            'Authorization': api_key,
            'X-NCP-CLOVASTUDIO-REQUEST-ID': request_id,
            'Content-Type': 'application/json; charset=utf-8',
            'Accept': 'text/event-stream'
        }
    ]

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content}
    ]

    request_data = {
        'messages': messages,
        'topP': 0.8,
        'topK': 0,
        'maxTokens': 500,
        'temperature': 0.3,
        'repetitionPenalty': 1.1,
        'stop': [],
        'includeAiFilters': True,
        'seed': 0
    }

    # 두 가지 헤더 형식으로 시도
    for i, headers in enumerate(headers_options, 1):
        try:
            print(f"\n🤖 시도 {i}: {'Bearer' if 'Bearer' in headers['Authorization'] else '기본'} 인증 방식")

            with requests.post('https://clovastudio.stream.ntruss.com/v3/chat-completions/HCX-005',
                               headers=headers, json=request_data, stream=True, timeout=30) as response:

                print(f"   응답 상태: {response.status_code}")

                if response.status_code == 401:
                    print("   ❌ 인증 실패 (401)")
                    continue
                elif response.status_code == 403:
                    print("   ❌ 권한 없음 (403)")
                    continue
                elif response.status_code != 200:
                    print(f"   ❌ HTTP 오류: {response.status_code}")
                    print(f"   응답 내용: {response.text[:200]}")
                    continue

                print("   ✅ 연결 성공, 응답 대기 중...")

                response_count = 0
                for line in response.iter_lines():
                    if line:
                        response_count += 1
                        line_text = line.decode("utf-8")

                        if response_count <= 3:  # 처음 3개 라인 로그
                            print(f"   응답 라인 {response_count}: {line_text[:100]}")

                        if line_text.startswith('data:'):
                            try:
                                data = json.loads(line_text[5:])
                                if 'message' in data and data['message'].get('content'):
                                    if data.get('finishReason') == 'stop':
                                        ai_insight = data['message']['content']
                                        print("   ✅ AI 인사이트 생성 완료!")

                                        return {
                                            'success': True,
                                            'financial_data': jyp_financial_data,
                                            'ai_insight': ai_insight,
                                            'analysis_date': datetime.now().strftime('%Y-%m-%d'),
                                            'auth_method': f"시도 {i}"
                                        }
                            except json.JSONDecodeError as e:
                                print(f"   JSON 파싱 오류: {e}")
                                continue

                print(f"   ⚠️ {response_count}개 응답 라인 처리했지만 완료 신호 없음")

        except requests.exceptions.Timeout:
            print(f"   ❌ 시도 {i} 타임아웃")
        except requests.exceptions.ConnectionError:
            print(f"   ❌ 시도 {i} 연결 오류")
        except Exception as e:
            print(f"   ❌ 시도 {i} 기타 오류: {e}")

    print("\n❌ 모든 시도 실패")
    return None


def get_jyp_financial_insight():
    """JYP 재무 인사이트 조회 (디버깅 버전)"""

    print("\n" + "=" * 50)
    print("🔍 JYP 재무 인사이트 생성 시작")
    print("=" * 50)

    # 캐시 파일 체크
    cache_file = "data/jyp_financial_cache.json"

    try:
        if os.path.exists(cache_file):
            print("📁 캐시 파일 발견")
            with open(cache_file, 'r', encoding='utf-8') as f:
                cached_data = json.load(f)
                print("✅ 캐시된 데이터 사용")
                return cached_data
    except Exception as e:
        print(f"⚠️ 캐시 읽기 실패: {e}")

    print("🚀 새로운 API 호출 시작...")

    # 새로 생성
    result = generate_jyp_ai_insight()

    if result and result.get('success'):
        print(f"✅ API 성공! ({result.get('auth_method', '알 수 없음')})")

        # 캐시 저장
        try:
            os.makedirs('data', exist_ok=True)
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print("💾 캐시 저장 완료")
        except Exception as e:
            print(f"⚠️ 캐시 저장 실패: {e}")

        return result
    else:
        print("❌ API 호출 실패 - 임시 데이터 사용")
        return {
            'success': True,
            'financial_data': {
                "매출액_억원": 1245.3,
                "영업이익_억원": 187.2,
                "ROE": 15.2,
                "영업이익률": 15.0
            },
            'ai_insight': """**재무현황 요약**: JYP엔터테인먼트는 안정적인 매출 구조와 양호한 수익성을 보이고 있습니다. **주요 강점**: 글로벌 아티스트 포트폴리오를 통한 다각화된 수익원을 확보하고 있습니다. **주요 리스크**: 엔터테인먼트 산업 특성상 아티스트 이슈에 따른 변동성이 존재합니다. **투자관점**: 전반적으로 안정적이나 단기 이슈에 대한 신중한 접근이 필요합니다.""",
            'analysis_date': datetime.now().strftime('%Y-%m-%d'),
            'source': 'fallback_data'
        }


# 테스트 함수
def test_jyp_analysis():
    """JYP 분석 테스트"""
    print("🧪 JYP 분석 테스트 시작")
    result = get_jyp_financial_insight()

    if result:
        print("\n📊 결과:")
        print(f"성공 여부: {result.get('success')}")
        print(f"데이터 소스: {result.get('source', 'API')}")
        print(f"매출액: {result['financial_data']['매출액_억원']}억원")
        print(f"AI 인사이트 길이: {len(result['ai_insight'])}자")
        print(f"인사이트 미리보기: {result['ai_insight'][:100]}...")
    else:
        print("❌ 테스트 완전 실패")


if __name__ == "__main__":
    test_jyp_analysis()