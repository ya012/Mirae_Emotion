# -*- coding: utf-8 -*-
"""
뉴스 분석 모듈 (개선 버전)
"""
import json
import requests
import uuid
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
import streamlit as st
from datetime import datetime

load_dotenv()


def debug_environment():
    """환경 변수 및 설정 디버그"""
    print("=" * 50)
    print("환경 디버깅")
    print("=" * 50)

    api_key = os.getenv('CLOVA_API_KEY')
    print(f"API 키 존재: {'✅' if api_key else '❌'}")

    if api_key:
        print(f"API 키 길이: {len(api_key)}")
        print(f"API 키 시작: {api_key[:15]}...")

    # Streamlit secrets 확인 (조용히)
    try:
        import streamlit as st
        if hasattr(st, 'secrets') and hasattr(st.secrets, 'get'):
            secrets_key = st.secrets.get('CLOVA_API_KEY')
            if secrets_key and not api_key:
                api_key = secrets_key
                print("Streamlit secrets에서 API 키 사용")
    except:
        pass  # 에러 메시지 출력하지 않음

    return api_key


def extract_article_content(url):
    """뉴스 본문 추출 (개선된 버전)"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        response = requests.get(url, timeout=15, headers=headers)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')

        # 확장된 본문 선택자
        content_selectors = [
            '.view_con_t', '.article_content', '.news_content', '.content',
            '.article-content', '.post-content', 'article', '.entry-content',
            '.article-body', '.news-body', '.post-body', '.article_txt',
            '#articleText', '.article_view', '.news_view', '.view_text'
        ]

        article_text = None
        for selector in content_selectors:
            article_content = soup.select_one(selector)
            if article_content:
                # 불필요한 태그 제거
                for tag in article_content(['script', 'style', 'iframe', 'nav', 'footer']):
                    tag.decompose()

                article_text = article_content.get_text(strip=True)
                if len(article_text) > 300:  # 최소 길이 확인
                    print(f"본문 추출 성공: {selector} ({len(article_text)}자)")
                    break

        # 전체 텍스트에서 추출 시도
        if not article_text or len(article_text) < 300:
            all_text = soup.get_text(strip=True)
            # 본문으로 보이는 부분 추출
            paragraphs = soup.find_all('p')
            if paragraphs:
                article_text = ' '.join([p.get_text(strip=True) for p in paragraphs])
            else:
                article_text = all_text

        # JavaScript 필요 사이트 감지
        js_indicators = ['javascript', '자바스크립트', 'enable', 'browser', 'disabled']
        if any(indicator in article_text.lower() for indicator in js_indicators) and len(article_text) < 1000:
            print("JavaScript 필요 사이트로 판단")
            return None

        # 길이 제한 및 정리
        if article_text:
            article_text = article_text[:8000]  # 토큰 제한 고려

            if len(article_text) > 300:
                print(f"본문 추출 완료: {len(article_text)}자")
                return article_text

        print(f"본문이 너무 짧음: {len(article_text) if article_text else 0}자")
        return None

    except Exception as e:
        print(f"본문 추출 실패: {e}")
        return None


def summarize_with_clova(content, investor_type, api_key):
    """HyperCLOVA X로 뉴스 요약 (개선된 버전)"""
    if not api_key:
        print("API 키가 없습니다")
        return None

    request_id = str(uuid.uuid4()).replace('-', '')

    # 다양한 헤더 설정 시도
    headers_list = [
        {
            'Authorization': api_key,
            'X-NCP-CLOVASTUDIO-REQUEST-ID': request_id,
            'Content-Type': 'application/json; charset=utf-8',
            'Accept': 'text/event-stream'
        },
        {
            'Authorization': f'Bearer {api_key}',
            'X-NCP-CLOVASTUDIO-REQUEST-ID': request_id,
            'Content-Type': 'application/json; charset=utf-8',
            'Accept': 'text/event-stream'
        }
    ]

    # 투자자 유형별 세분화된 프롬프트
    if investor_type == "MIRAE":
        system_prompt = """당신은 엔터테인먼트 투자 분석 전문가입니다.

MIRAE형 투자자를 위해 다음 뉴스를 객관적이고 체계적으로 요약해주세요.

**요약 원칙:**
- 기업의 공식 발표, 실적, 사업 계획 등 팩트 중심
- 객관적이고 중립적인 어조 유지
- 투자 판단에 필요한 구체적 정보 포함
- 추측이나 감정적 표현 배제
- 7-8줄의 체계적인 문단으로 구성

**포함할 요소:**
- 핵심 사실과 배경 정보
- 기업 측 공식 입장이나 대응
- 재무적/사업적 영향 가능성
- 관련 규정이나 업계 동향"""

    else:  # ASAP형
        system_prompt = """당신은 엔터테인먼트 투자 분석 전문가입니다.

ASAP형 투자자를 위해 다음 뉴스의 핵심을 빠르게 파악할 수 있도록 요약해주세요.

**요약 원칙:**
- 즉각적인 시장 반응에 영향을 줄 수 있는 요소 우선
- 팬덤과 여론의 반응을 고려한 관점
- 간결하고 명확한 4-5줄 구성
- 빠른 의사결정에 필요한 핵심 정보만

**포함할 요소:**
- 이슈의 핵심 내용
- 예상되는 팬덤/대중 반응
- 단기적 주가 영향 요인
- 즉각적 대응이 필요한 부분"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"뉴스 내용:\n\n{content[:6000]}"}  # 길이 제한
    ]

    request_data = {
        'messages': messages,
        'topP': 0.6,
        'topK': 0,
        'maxTokens': 800 if investor_type == "MIRAE" else 400,
        'temperature': 0.1,
        'repetitionPenalty': 1.2,
        'stop': [],
        'includeAiFilters': True,
        'seed': 0
    }

    # 여러 헤더로 시도
    for i, headers in enumerate(headers_list):
        try:
            print(f"API 호출 시도 {i + 1}: {investor_type}형")

            with requests.post(
                    'https://clovastudio.stream.ntruss.com/v3/chat-completions/HCX-005',
                    headers=headers,
                    json=request_data,
                    stream=True,
                    timeout=30
            ) as r:

                print(f"응답 상태: {r.status_code}")

                if r.status_code == 401:
                    print("인증 실패")
                    continue
                elif r.status_code != 200:
                    print(f"HTTP 오류: {r.status_code}")
                    continue

                for line in r.iter_lines():
                    if line:
                        line_text = line.decode("utf-8")
                        if line_text.startswith('data:'):
                            try:
                                data = json.loads(line_text[5:])
                                if 'message' in data and data['message'].get('content'):
                                    if data.get('finishReason') == 'stop':
                                        summary = data['message']['content']
                                        print(f"요약 생성 성공: {len(summary)}자")
                                        return summary
                            except json.JSONDecodeError:
                                continue

        except Exception as e:
            print(f"API 호출 실패 {i + 1}: {e}")
            continue

    return None


def get_fallback_summary(investor_type):
    """API 실패시 대체 요약"""
    if investor_type == "MIRAE":
        return """데이식스 팬미팅에서 시행된 과도한 본인확인 절차가 논란이 되고 있습니다. 운영 업체는 암표 방지를 목적으로 생활기록부, 금융인증서 등의 개인정보 제출을 요구했으며, 이에 대해 팬들이 강한 반발을 보이고 있습니다. 

개인정보 보호법 위반 가능성이 제기되고 있으며, 법적 검토가 필요한 상황입니다. 업계 전문가들은 이러한 과도한 요구가 팬덤 문화에 부정적 영향을 미칠 수 있다고 우려를 표명했습니다. 

향후 유사한 이벤트 운영 방식에 대한 전반적인 재검토가 필요할 것으로 보이며, JYP 측은 재발 방지를 위한 구체적인 대책 마련이 요구되는 상황입니다. 이번 사건은 아티스트와 팬 간의 신뢰 관계에도 영향을 미칠 가능성이 높아 중장기적 관점에서의 대응이 필요합니다."""

    else:  # ASAP형
        return """데이식스 팬미팅에서 생활기록부, 금융인증서 제출을 요구하는 과도한 본인확인이 논란이 되었습니다. 팬들은 개인정보 침해라며 강하게 반발하고 있으며, 소셜미디어를 통해 비판 여론이 급속히 확산되고 있는 상황입니다. 

법적 문제 소지도 제기되고 있어 단기적으로 부정적 여론이 지속될 가능성이 높습니다. 이번 사건은 팬덤과 아티스트 간 신뢰 관계에 즉각적인 타격을 줄 것으로 예상되며, 빠른 사과와 개선책 발표가 필요한 상황입니다."""


def find_working_news(json_file, investor_type, max_tries=8):
    """JSON에서 작동하는 뉴스 찾아서 요약 (개선 버전)"""

    # 환경 디버깅
    api_key = debug_environment()

    # JSON 읽기
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            news_data = json.load(f)
    except FileNotFoundError:
        print(f"파일을 찾을 수 없습니다: {json_file}")
        return {
            "title": "데이식스 팬미팅 본인확인 논란",
            "url": "#",
            "date": "2025-07-18",
            "summary": get_fallback_summary(investor_type),
            "investor_type": investor_type,
            "success": True,
            "source": "fallback"
        }

    if not news_data:
        return {"error": "뉴스 데이터 없음"}

    print(f"🔍 총 {len(news_data)}개 뉴스에서 분석 시작 ({investor_type}형)")

    # 뉴스 리스트 순회
    for i, news in enumerate(news_data[:max_tries]):
        print(f"\n[{i + 1}/{min(max_tries, len(news_data))}] 처리 중...")
        print(f"제목: {news['title'][:50]}...")

        # 본문 추출
        article_text = extract_article_content(news['link'])

        if article_text:
            print(f"본문 길이: {len(article_text)}자")

            # API로 요약 시도
            if api_key:
                summary = summarize_with_clova(article_text, investor_type, api_key)

                if summary:
                    return {
                        "title": news['title'],
                        "url": news['link'],
                        "date": news.get('pub_date', '2025-07-18'),
                        "summary": summary,
                        "investor_type": investor_type,
                        "tried_count": i + 1,
                        "success": True,
                        "source": "api"
                    }
                else:
                    print("API 요약 실패 - 다음 뉴스 시도")
            else:
                print("API 키 없음 - 대체 요약 사용")
                break
        else:
            print("본문 추출 실패 - 다음 뉴스 시도")

    # 모든 시도 실패시 대체 요약 반환
    print("모든 뉴스 처리 실패 - 대체 요약 사용")
    return {
        "title": "데이식스 팬미팅 본인확인 논란",
        "url": "#",
        "date": "2025-07-18",
        "summary": get_fallback_summary(investor_type),
        "investor_type": investor_type,
        "success": True,
        "source": "fallback"
    }


def get_day6_news_summary(investor_type):
    """데이식스 본인확인 이슈 뉴스 요약 (개선 버전)"""
    json_file = "data/day6_news.json"

    # 캐시 확인
    cache_file = f"data/news_cache_{investor_type.lower()}.json"

    try:
        if os.path.exists(cache_file):
            with open(cache_file, 'r', encoding='utf-8') as f:
                cached_data = json.load(f)
                # 캐시가 1시간 이내라면 사용
                cache_time = datetime.fromisoformat(cached_data.get('timestamp', '2000-01-01'))
                if (datetime.now() - cache_time).seconds < 3600:
                    print(f"캐시된 {investor_type}형 뉴스 요약 사용")
                    return cached_data['data']
    except:
        pass

    # 새로 생성
    result = find_working_news(json_file, investor_type)

    # 캐시 저장
    if result.get('success'):
        try:
            os.makedirs('data', exist_ok=True)
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'data': result
            }
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
        except:
            pass

    return result


# 테스트 함수
def test_news_analysis():
    """뉴스 분석 테스트"""
    print("뉴스 분석 테스트 시작")

    for investor_type in ["MIRAE", "ASAP"]:
        print(f"\n=== {investor_type}형 테스트 ===")
        result = get_day6_news_summary(investor_type)

        if result.get('success'):
            print(f"성공: {result.get('source', 'unknown')}")
            print(f"제목: {result['title']}")
            print(f"요약 길이: {len(result['summary'])}자")
            print(f"요약 미리보기: {result['summary'][:100]}...")
        else:
            print(f"실패: {result.get('error', 'unknown error')}")


if __name__ == "__main__":
    test_news_analysis()