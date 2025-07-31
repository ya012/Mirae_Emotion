# -*- coding: utf-8 -*-
"""
뉴스 분석 모듈
"""
import json
import requests
import uuid
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

load_dotenv()


def extract_article_content(url):
    """뉴스 본문 추출"""
    try:
        response = requests.get(url, timeout=10)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')

        # 본문 선택자들
        content_selectors = [
            '.view_con_t', '.article_content', '.news_content', '.content',
            '.article-content', '.post-content', 'article', '.entry-content',
            '.article-body', '.news-body', '.post-body'
        ]

        article_text = None
        for selector in content_selectors:
            article_content = soup.select_one(selector)
            if article_content:
                article_text = article_content.get_text(strip=True)
                if len(article_text) > 200:  # 충분한 길이인지 확인
                    print(f"{selector} 선택자로 본문 추출 성공")
                    break

        # 선택자로 안 되면 전체에서 추출
        if not article_text or len(article_text) < 200:
            article_text = soup.get_text(strip=True)

        # JavaScript 안내 메시지 감지
        js_keywords = ['javascript', '자바스크립트', '활성화', 'enable', 'disabled']
        if any(keyword in article_text.lower() for keyword in js_keywords) and len(article_text) < 1000:
            print("❌ JavaScript 필요한 사이트로 판단")
            return None

        # 길이 제한
        article_text = article_text[:10000]

        if len(article_text) > 200:
            print(f"✅ 본문 추출 성공 ({len(article_text)}자)")
            return article_text
        else:
            print(f"❌ 본문이 너무 짧음 ({len(article_text)}자)")
            return None

    except Exception as e:
        print(f"❌ 본문 추출 실패: {e}")
        return None


def summarize_with_clova(content, investor_type, api_key):
    """HyperCLOVA X로 뉴스 요약 (투자자 유형별)"""
    request_id = str(uuid.uuid4()).replace('-', '')

    headers = {
        'Authorization': api_key,
        'X-NCP-CLOVASTUDIO-REQUEST-ID': request_id,
        'Content-Type': 'application/json; charset=utf-8',
        'Accept': 'text/event-stream'
    }

    # 투자자 유형별 프롬프트
    prompts = {
        "MIRAE": """당신은 엔터테인먼트 투자 분석 전문가입니다. 
다음 뉴스를 7-8줄로 구조화하여 요약해주세요.

요구사항:
- 기업의 공식 발표, 실적, 사업 계획 등 펀더멘털 중심으로 작성
- 객관적이고 분석적인 톤을 유지하세요
- 투자 관점에서 중요한 사실들을 포함하세요
- 추측하지 말고 뉴스 내용만을 바탕으로 작성하세요""",

        "ASAP": """당신은 엔터테인먼트 투자 분석 전문가입니다. 
다음 뉴스의 핵심 내용을 정확히 4-5줄로 요약해주세요.

요구사항:
- 팬들의 반응과 여론이 주가에 미칠 즉각적 영향 중심으로 작성
- 간결하고 명확하게 작성하세요
- 시장 반응과 연결될 수 있는 요소들을 포함하세요
- 빠른 판단에 필요한 핵심 정보만 포함하세요"""
    }

    messages = [
        {"role": "system", "content": prompts[investor_type]},
        {"role": "user", "content": f"뉴스 내용:\n\n{content}"}
    ]

    request_data = {
        'messages': messages,
        'topP': 0.6,
        'topK': 0,
        'maxTokens': 512,
        'temperature': 0.1,
        'repetitionPenalty': 1.1,
        'stop': [],
        'includeAiFilters': True,
        'seed': 0
    }

    try:
        with requests.post('https://clovastudio.stream.ntruss.com/v3/chat-completions/HCX-005',
                           headers=headers, json=request_data, stream=True) as r:
            for line in r.iter_lines():
                if line:
                    line_text = line.decode("utf-8")
                    if line_text.startswith('data:'):
                        try:
                            data = json.loads(line_text[5:])
                            if 'message' in data and data['message'].get('content'):
                                if data.get('finishReason') == 'stop':
                                    return data['message']['content']
                        except:
                            continue
    except Exception as e:
        print(f"API 호출 실패: {e}")
        return None

    return None


def find_working_news(json_file, investor_type, max_tries=10):
    """JSON에서 작동하는 뉴스 찾아서 요약"""

    # JSON 읽기
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            news_data = json.load(f)
    except FileNotFoundError:
        print(f"❌ 파일을 찾을 수 없습니다: {json_file}")
        return {"error": "뉴스 파일 없음"}

    if not news_data:
        return {"error": "뉴스 데이터 없음"}

    print(f"🔍 총 {len(news_data)}개 뉴스에서 작동하는 링크 찾는 중...")

    api_key = os.getenv('CLOVA_API_KEY')

    # 뉴스 리스트 순회
    for i, news in enumerate(news_data[:max_tries]):
        print(f"\n[{i + 1}/{min(max_tries, len(news_data))}] 시도 중...")
        print(f"📰 제목: {news['title'][:50]}...")
        print(f"🔗 URL: {news['link']}")

        # 본문 추출 시도
        article_text = extract_article_content(news['link'])

        if article_text:
            print(f"📋 본문 미리보기: {article_text[:150]}...")
            print(f"\n🤖 [{investor_type}형] 요약 생성 중...")

            # 투자자 유형별 요약 생성
            summary = summarize_with_clova(article_text, investor_type, api_key)

            if summary:
                result = {
                    "title": news['title'],
                    "url": news['link'],
                    "date": news['pub_date'],
                    "summary": summary,
                    "investor_type": investor_type,
                    "tried_count": i + 1,
                    "success": True
                }

                print(f"\n✅ [{investor_type}형] 성공! ({i + 1}번째 시도)")
                return result

        print("❌ 다음 뉴스로 넘어갑니다...")

    return {"error": f"{max_tries}개 뉴스 모두 처리 실패"}


# 데이식스 이슈 고정 데이터용
def get_day6_news_summary(investor_type):
    """데이식스 본인확인 이슈 뉴스 요약 (고정 데이터)"""
    json_file = "data/day6_news.json"  # 미리 수집된 데이터
    return find_working_news(json_file, investor_type, max_tries=5)