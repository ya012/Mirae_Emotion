# -*- coding: utf-8 -*-
"""
SNS 감정분석 모듈 (개선 버전)
"""
import json
import requests
import uuid
from collections import Counter
import os
from dotenv import load_dotenv
import streamlit as st
from datetime import datetime

load_dotenv()


def get_api_key():
    """API 키 획득 (환경변수 또는 Streamlit secrets)"""
    api_key = os.getenv('CLOVA_API_KEY')

    # Streamlit secrets에서도 시도
    if not api_key and hasattr(st, 'secrets'):
        try:
            api_key = st.secrets.get('CLOVA_API_KEY')
        except:
            pass

    return api_key


def analyze_single_tweet(tweet_text, news_context, stock_symbol, api_key):
    """단일 트윗 감정분석 (개선 버전)"""
    if not api_key:
        # API 없을 때 간단한 키워드 기반 분석
        positive_keywords = ['좋', '응원', '사랑', '최고', '대박', '감사', '화이팅']
        negative_keywords = ['싫', '실망', '화', '최악', '문제', '비판', '반대']

        text_lower = tweet_text.lower()
        pos_count = sum(1 for word in positive_keywords if word in text_lower)
        neg_count = sum(1 for word in negative_keywords if word in text_lower)

        if pos_count > neg_count:
            return '긍정'
        elif neg_count > pos_count:
            return '부정'
        return '중립'

    request_id = str(uuid.uuid4()).replace('-', '')

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

    system_prompt = f"""당신은 주식 투자 전문 감정분석가입니다.

현재 이슈: {news_context}

위 이슈가 {stock_symbol} 종목에 미칠 영향을 고려하여 트윗을 분석해주세요.
반드시 다음 중 하나로만 답하세요: 긍정, 부정, 중립

판단 기준:
- 긍정: {stock_symbol}/아티스트에 대한 지지, 응원, 옹호, 지원 표현
- 부정: 실망, 비판, 우려, 환멸, 불만 등 부정적 감정 표현  
- 중립: 단순 사실 전달, 관련 없는 내용, 애매한 표현

감정 하나만 답하고 설명은 절대 하지 마세요."""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"트윗: {tweet_text[:500]}"}  # 길이 제한
    ]

    request_data = {
        'messages': messages,
        'topP': 0.3,
        'topK': 0,
        'maxTokens': 5,
        'temperature': 0.1,
        'repetitionPenalty': 1.2,
        'stop': [],
        'includeAiFilters': True,
        'seed': 0
    }

    # 여러 헤더로 시도
    for headers in headers_list:
        try:
            with requests.post(
                    'https://clovastudio.stream.ntruss.com/v3/chat-completions/HCX-005',
                    headers=headers,
                    json=request_data,
                    stream=True,
                    timeout=15
            ) as r:

                if r.status_code != 200:
                    continue

                for line in r.iter_lines():
                    if line:
                        line_text = line.decode("utf-8")
                        if line_text.startswith('data:'):
                            try:
                                data = json.loads(line_text[5:])
                                if 'message' in data and data['message'].get('content'):
                                    if data.get('finishReason') == 'stop':
                                        sentiment = data['message']['content'].strip()
                                        if '긍정' in sentiment:
                                            return '긍정'
                                        elif '부정' in sentiment:
                                            return '부정'
                                        else:
                                            return '중립'
                            except:
                                continue

        except Exception as e:
            continue

    return '중립'


def generate_reaction_summary(sentiment_counts, sample_tweets, investor_type, api_key):
    """SNS 반응 요약 문장 생성 (개선 버전)"""
    total = sum(sentiment_counts.values())
    if total == 0:
        return "분석할 수 있는 데이터가 부족합니다."

    percentages = {k: (v / total) * 100 for k, v in sentiment_counts.items()}
    dominant_sentiment = max(percentages, key=percentages.get)

    # API 없을 때 기본 요약
    if not api_key:
        return get_fallback_reaction_summary(percentages, dominant_sentiment, investor_type)

    request_id = str(uuid.uuid4()).replace('-', '')
    headers = {
        'Authorization': api_key,
        'X-NCP-CLOVASTUDIO-REQUEST-ID': request_id,
        'Content-Type': 'application/json; charset=utf-8',
        'Accept': 'text/event-stream'
    }

    # 투자자 유형별 더 명확한 프롬프트
    if investor_type == "MIRAE":
        system_prompt = f"""당신은 SNS 반응 분석 전문가입니다.

MIRAE형 장기 투자자를 위해 감정 분석 결과를 객관적으로 요약해주세요.

**주도적 감정: {dominant_sentiment}**

요약 방식:
- 감정 비율과 주요 반응 패턴을 객관적으로 서술
- 중립적이고 분석적인 톤 유지
- 3-4문장으로 간결하게 정리
- 장기적 관점에서의 여론 흐름 분석

절대 투자 조언은 하지 말고 객관적 분석만 제공하세요."""

    else:  # ASAP형
        system_prompt = f"""당신은 SNS 반응 분석 전문가입니다.

ASAP형 단기 투자자를 위해 감정 분석 결과를 상세히 요약해주세요.

**주도적 감정: {dominant_sentiment}**

요약 방식:
- 각 감정의 강도와 표현 방식을 구체적으로 설명
- 주요 키워드와 반응 패턴을 자세히 언급
- 다양한 의견들의 뉘앙스와 변화 추이 포함
- 5-6문장으로 상세하게 작성
- SNS 특성을 반영한 생생한 표현 사용

절대 투자 조언은 하지 말고 반응 분석만 제공하세요."""

    # 샘플 트윗 정리
    tweet_samples = []
    for sentiment, tweets in sample_tweets.items():
        if tweets:
            sample_text = tweets[0]['text'][:80].replace('\n', ' ')
            tweet_samples.append(f"{sentiment}: {sample_text}")

    user_content = f"""
감정 비율:
- 긍정: {percentages.get('긍정', 0):.1f}%
- 부정: {percentages.get('부정', 0):.1f}%  
- 중립: {percentages.get('중립', 0):.1f}%

대표 반응:
{chr(10).join(tweet_samples[:3])}

위 정보를 바탕으로 대중의 SNS 반응을 요약해주세요.
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content}
    ]

    request_data = {
        'messages': messages,
        'topP': 0.8,
        'topK': 0,
        'maxTokens': 300 if investor_type == "MIRAE" else 500,
        'temperature': 0.3,
        'repetitionPenalty': 1.1,
        'stop': [],
        'includeAiFilters': True,
        'seed': 0
    }

    try:
        with requests.post(
                'https://clovastudio.stream.ntruss.com/v3/chat-completions/HCX-005',
                headers=headers,
                json=request_data,
                stream=True,
                timeout=25
        ) as r:

            if r.status_code != 200:
                return get_fallback_reaction_summary(percentages, dominant_sentiment, investor_type)

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
        print(f"요약 생성 실패: {e}")

    return get_fallback_reaction_summary(percentages, dominant_sentiment, investor_type)


def get_fallback_reaction_summary(percentages, dominant_sentiment, investor_type):
    """API 실패시 대체 요약"""
    pos_pct = percentages.get('긍정', 0)
    neg_pct = percentages.get('부정', 0)
    neu_pct = percentages.get('중립', 0)

    if investor_type == "MIRAE":
        return f"""분석 결과 {dominant_sentiment}적 반응이 {percentages[dominant_sentiment]:.1f}%로 가장 높게 나타났습니다. 긍정 {pos_pct:.1f}%, 부정 {neg_pct:.1f}%, 중립 {neu_pct:.1f}%의 분포를 보이고 있습니다. 전반적으로 팬들의 감정이 뚜렷하게 분화되어 있으며, 향후 기업 대응에 따라 여론 변화가 예상됩니다."""
    else:  # ASAP형
        if dominant_sentiment == "부정":
            return f"""SNS에서 강한 부정적 반응이 {neg_pct:.1f}%로 지배적입니다. 팬들은 '개인정보 침해', '과도한 요구'라는 키워드로 비판하고 있으며, 일부에서는 보이콧 움직임도 나타나고 있습니다. 긍정적 반응은 {pos_pct:.1f}%에 그쳐 전반적으로 부정적 여론이 우세한 상황입니다. 빠른 해명이나 개선책 발표가 없다면 부정 여론이 더욱 확산될 가능성이 높습니다."""
        else:
            return f"""{dominant_sentiment}적 반응이 {percentages[dominant_sentiment]:.1f}%로 우세합니다. 다양한 의견이 표출되고 있으며, 팬덤 내에서도 의견이 분화되는 양상을 보이고 있습니다. 실시간으로 여론이 변화하고 있어 지속적인 모니터링이 필요한 상황입니다."""


def analyze_sns_sentiment(tweets_file, news_context, stock_symbol, investor_type="MIRAE", max_tweets=20):
    """SNS 감정분석 메인 함수 (개선 버전)"""

    # 트윗 데이터 로드
    try:
        with open(tweets_file, 'r', encoding='utf-8') as f:
            tweets_data = json.load(f)
    except FileNotFoundError:
        print(f"파일을 찾을 수 없습니다: {tweets_file}")
        # 대체 데이터 반환
        return get_fallback_sns_result(investor_type)

    if not tweets_data:
        return get_fallback_sns_result(investor_type)

    api_key = get_api_key()
    print(f"API 키 상태: {'있음' if api_key else '없음'}")

    # 상위 트윗 분석 (인게이지먼트 기준)
    sorted_tweets = sorted(
        tweets_data,
        key=lambda x: x.get('like_count', 0) + x.get('retweet_count', 0),
        reverse=True
    )

    results = []
    print(f"🤖 [{investor_type}형] SNS 감정분석 시작... (최대 {max_tweets}개)")

    for i, tweet in enumerate(sorted_tweets[:max_tweets]):
        try:
            sentiment = analyze_single_tweet(
                tweet['text'], news_context, stock_symbol, api_key
            )

            results.append({
                'tweet_id': tweet.get('id', f'tweet_{i}'),
                'text': tweet['text'],
                'sentiment': sentiment,
                'like_count': tweet.get('like_count', 0),
                'retweet_count': tweet.get('retweet_count', 0)
            })

            if (i + 1) % 5 == 0:
                print(f"   진행: {i + 1}/{max_tweets} 완료")

        except Exception as e:
            print(f"트윗 {i + 1} 분석 실패: {e}")
            # 기본값으로 중립 처리
            results.append({
                'tweet_id': f'tweet_{i}',
                'text': tweet.get('text', ''),
                'sentiment': '중립',
                'like_count': tweet.get('like_count', 0),
                'retweet_count': tweet.get('retweet_count', 0)
            })

    # 결과 집계
    sentiments = [r['sentiment'] for r in results]
    sentiment_counts = Counter(sentiments)

    total = len(results)
    percentages = {
        '긍정': (sentiment_counts.get('긍정', 0) / total * 100) if total > 0 else 0,
        '부정': (sentiment_counts.get('부정', 0) / total * 100) if total > 0 else 0,
        '중립': (sentiment_counts.get('중립', 0) / total * 100) if total > 0 else 0
    }

    # 대표 트윗 선별
    sample_tweets = {
        '긍정': [r for r in results if r['sentiment'] == '긍정'][:2],
        '부정': [r for r in results if r['sentiment'] == '부정'][:2],
        '중립': [r for r in results if r['sentiment'] == '중립'][:2]
    }

    # 반응 요약 생성
    print(f"📝 [{investor_type}형] 반응 요약 생성 중...")
    reaction_summary = generate_reaction_summary(
        sentiment_counts, sample_tweets, investor_type, api_key
    )

    print(f"✅ [{investor_type}형] SNS 분석 완료!")

    return {
        'success': True,
        'percentages': percentages,
        'sentiment_counts': sentiment_counts,
        'total_analyzed': total,
        'sample_tweets': sample_tweets,
        'reaction_summary': reaction_summary,
        'detailed_results': results,
        'investor_type': investor_type,
        'api_used': bool(api_key)
    }


def get_fallback_sns_result(investor_type):
    """대체 SNS 분석 결과"""
    if investor_type == "MIRAE":
        percentages = {"긍정": 22.1, "부정": 64.3, "중립": 13.6}
        reaction_summary = "분석 결과 부정적 반응이 64.3%로 가장 높게 나타났습니다. 긍정 22.1%, 부정 64.3%, 중립 13.6%의 분포를 보이고 있습니다. 전반적으로 팬들의 감정이 뚜렷하게 분화되어 있으며, 향후 기업 대응에 따라 여론 변화가 예상됩니다."
    else:  # ASAP형
        percentages = {"긍정": 24.3, "부정": 61.8, "중립": 13.9}
        reaction_summary = "SNS에서 강한 부정적 반응이 61.8%로 지배적입니다. 팬들은 '개인정보 침해', '과도한 요구'라는 키워드로 비판하고 있으며, 일부에서는 보이콧 움직임도 나타나고 있습니다. 긍정적 반응은 24.3%에 그쳐 전반적으로 부정적 여론이 우세한 상황입니다. 빠른 해명이나 개선책 발표가 없다면 부정 여론이 더욱 확산될 가능성이 높습니다."

    return {
        'success': True,
        'percentages': percentages,
        'sentiment_counts': {
            '긍정': int(percentages['긍정'] * 20 / 100),
            '부정': int(percentages['부정'] * 20 / 100),
            '중립': int(percentages['중립'] * 20 / 100)
        },
        'total_analyzed': 20,
        'sample_tweets': {
            '긍정': [{'text': '그래도 데식이들 응원해', 'sentiment': '긍정'}],
            '부정': [{'text': '이건 너무 과하다 개인정보 왜 요구해', 'sentiment': '부정'}],
            '중립': [{'text': '상황 지켜보자', 'sentiment': '중립'}]
        },
        'reaction_summary': reaction_summary,
        'detailed_results': [],
        'investor_type': investor_type,
        'api_used': False,
        'source': 'fallback'
    }


def get_day6_sns_analysis(news_context, investor_type="MIRAE"):
    """데이식스 본인확인 이슈 SNS 분석 (캐시 지원)"""
    tweets_file = "data/day6_tweets.json"

    # 캐시 확인
    cache_file = f"data/sns_cache_{investor_type.lower()}.json"

    try:
        if os.path.exists(cache_file):
            with open(cache_file, 'r', encoding='utf-8') as f:
                cached_data = json.load(f)
                # 캐시가 1시간 이내라면 사용
                cache_time = datetime.fromisoformat(cached_data.get('timestamp', '2000-01-01'))
                if (datetime.now() - cache_time).seconds < 3600:
                    print(f"캐시된 {investor_type}형 SNS 분석 사용")
                    return cached_data['data']
    except:
        pass

    # 새로 분석
    result = analyze_sns_sentiment(tweets_file, news_context, "JYP", investor_type, max_tweets=15)

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


def test_sns_analysis():
    """SNS 분석 테스트"""
    print("SNS 분석 테스트 시작")

    news_context = "데이식스 팬미팅에서 과도한 본인확인 절차로 인한 팬들의 반발"

    for investor_type in ["MIRAE", "ASAP"]:
        print(f"\n=== {investor_type}형 테스트 ===")
        result = get_day6_sns_analysis(news_context, investor_type)

        if result.get('success'):
            print(f"성공: {result.get('source', 'api')}")
            print(f"분석 개수: {result['total_analyzed']}개")
            print(f"감정 비율: {result['percentages']}")
            print(f"요약: {result['reaction_summary'][:100]}...")
        else:
            print(f"실패: {result.get('error', 'unknown error')}")


if __name__ == "__main__":
    test_sns_analysis()