# -*- coding: utf-8 -*-
"""
SNS 감정분석 모듈 (투자자 유형별 차별화)
"""
import json
import requests
import uuid
from collections import Counter
import os
from dotenv import load_dotenv

load_dotenv()


def analyze_single_tweet(tweet_text, news_context, stock_symbol, api_key):
    """단일 트윗 감정분석"""
    request_id = str(uuid.uuid4()).replace('-', '')

    headers = {
        'Authorization': api_key,
        'X-NCP-CLOVASTUDIO-REQUEST-ID': request_id,
        'Content-Type': 'application/json; charset=utf-8',
        'Accept': 'text/event-stream'
    }

    system_prompt = f"""당신은 주식 투자 전문 감정분석가입니다.

현재 이슈: {news_context}

위 이슈가 {stock_symbol} 종목에 미칠 영향을 고려하여 트윗을 분석해주세요.
다음 중 하나로만 답하세요: 긍정, 부정, 중립

판단 기준:
- 긍정: {stock_symbol}/아티스트에 대한 지지, 응원, 옹호 표현
- 부정: 실망, 비판, 우려, 환멸 등 부정적 감정 표현  
- 중립: 단순 사실 전달, 관련 없는 내용, 애매한 표현

감정만 답하고 설명은 하지 마세요."""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"트윗: {tweet_text}"}
    ]

    request_data = {
        'messages': messages,
        'topP': 0.6,
        'topK': 0,
        'maxTokens': 10,
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
        print(f"API 호출 실패: {e}")
        return '중립'

    return '중립'


def generate_reaction_summary(sentiment_counts, sample_tweets, investor_type, api_key):
    """SNS 반응 요약 문장 생성 (투자자 유형별)"""
    total = sum(sentiment_counts.values())
    percentages = {k: (v / total) * 100 for k, v in sentiment_counts.items()}

    # 가장 높은 비율의 감정
    dominant_sentiment = max(percentages, key=percentages.get)

    request_id = str(uuid.uuid4()).replace('-', '')
    headers = {
        'Authorization': api_key,
        'X-NCP-CLOVASTUDIO-REQUEST-ID': request_id,
        'Content-Type': 'application/json; charset=utf-8',
        'Accept': 'text/event-stream'
    }

    # 투자자 유형별 프롬프트
    if investor_type == "MIRAE":
        system_prompt = f"""당신은 SNS 반응 분석 전문가입니다.
장기 투자자를 위해 감정 분석 결과를 간결하고 객관적으로 요약해주세요.

주도적 감정이 '{dominant_sentiment}'이므로, {dominant_sentiment}적 반응을 중심으로 요약하되,
객관적 사실 위주로 간결하게 작성해주세요.

요약 방식:
- 감정 비율과 주요 키워드 중심
- 객관적이고 중립적인 톤
- 3-4문장으로 간결하게 정리
- 사실 기반의 분석적 접근

주의사항: 투자 조언은 하지 말고 객관적 반응 분석만 제공하세요."""

    else:  # ASAP
        system_prompt = f"""당신은 SNS 반응 분석 전문가입니다.
단기 투자자를 위해 감정 분석 결과를 상세하게 요약해주세요.

주도적 감정이 '{dominant_sentiment}'이므로, {dominant_sentiment}적 반응을 중심으로 시작하고
다른 반응들도 자세히 언급해주세요.

요약 방식:
- 감정의 강도와 표현 방식 상세 설명
- 주요 키워드와 반응 패턴 구체적 언급
- 다양한 의견들의 뉘앙스 포함
- 6-7문장으로 상세하게 작성
- SNS 특성을 반영한 생생한 표현

주의사항: 투자 조언은 하지 말고 반응 분석만 제공하세요."""

    # 샘플 트윗들 정리
    tweet_samples = []
    for sentiment, tweets in sample_tweets.items():
        if tweets:
            tweet_samples.append(f"{sentiment} 반응: {tweets[0]['text'][:100]}")

    user_content = f"""
감정 비율:
- 긍정: {percentages.get('긍정', 0):.1f}%
- 부정: {percentages.get('부정', 0):.1f}%  
- 중립: {percentages.get('중립', 0):.1f}%

대표 트윗 샘플:
{chr(10).join(tweet_samples)}

위 정보를 바탕으로 대중 반응을 요약해주세요.
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content}
    ]

    request_data = {
        'messages': messages,
        'topP': 0.8,
        'topK': 0,
        'maxTokens': 200 if investor_type == "MIRAE" else 400,  # ASAP형이 더 길게
        'temperature': 0.3,
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
        print(f"요약 생성 실패: {e}")
        return None

    return None


def analyze_sns_sentiment(tweets_file, news_context, stock_symbol, investor_type="MIRAE", max_tweets=20):
    """SNS 감정분석 메인 함수 (투자자 유형별)"""

    # 트윗 데이터 로드
    try:
        with open(tweets_file, 'r', encoding='utf-8') as f:
            tweets_data = json.load(f)
    except FileNotFoundError:
        print(f"파일을 찾을 수 없습니다: {tweets_file}")
        return None

    if not tweets_data:
        return None

    api_key = os.getenv('CLOVA_API_KEY')

    # 상위 트윗 분석 (인게이지먼트 기준)
    sorted_tweets = sorted(tweets_data,
                           key=lambda x: x.get('like_count', 0) + x.get('retweet_count', 0),
                           reverse=True)

    results = []

    print(f"🤖 [{investor_type}형] SNS 감정분석 시작...")

    for i, tweet in enumerate(sorted_tweets[:max_tweets]):
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

        if (i + 1) % 5 == 0:  # 5개마다 진행상황 출력
            print(f"   진행: {i + 1}/{max_tweets} 완료")

    # 결과 집계
    sentiments = [r['sentiment'] for r in results]
    sentiment_counts = Counter(sentiments)

    total = len(results)
    percentages = {
        '긍정': (sentiment_counts['긍정'] / total * 100) if total > 0 else 0,
        '부정': (sentiment_counts['부정'] / total * 100) if total > 0 else 0,
        '중립': (sentiment_counts['중립'] / total * 100) if total > 0 else 0
    }

    # 대표 트윗 선별
    sample_tweets = {
        '긍정': [r for r in results if r['sentiment'] == '긍정'][:2],
        '부정': [r for r in results if r['sentiment'] == '부정'][:2],
        '중립': [r for r in results if r['sentiment'] == '중립'][:2]
    }

    # 반응 요약 생성 (투자자 유형별)
    print(f"📝 [{investor_type}형] 반응 요약 생성 중...")
    reaction_summary = generate_reaction_summary(sentiment_counts, sample_tweets, investor_type, api_key)

    print(f"✅ [{investor_type}형] SNS 분석 완료!")

    return {
        'success': True,
        'percentages': percentages,
        'sentiment_counts': sentiment_counts,
        'total_analyzed': total,
        'sample_tweets': sample_tweets,
        'reaction_summary': reaction_summary,
        'detailed_results': results,
        'investor_type': investor_type
    }


# 데이식스 이슈 고정 데이터용 (기존 코드와 호환)
def get_day6_sns_analysis(news_context, investor_type="MIRAE"):
    """데이식스 본인확인 이슈 SNS 분석 (투자자 유형별)"""
    tweets_file = "data/day6_tweets.json"  # 미리 수집된 데이터
    return analyze_sns_sentiment(tweets_file, news_context, "JYP", investor_type, max_tweets=15)

