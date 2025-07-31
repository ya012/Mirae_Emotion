import requests
import pandas as pd
import json
import re
import html
from datetime import datetime, timedelta

BEARER_TOKEN = 'AAAAAAAAAAAAAAAAAAAAAPiK3AEAAAAAQQbgHy9F0QmH3yIiGIBxcHlsGHo%3DtU20amYMVz9sNCHn53oRZE95b1djcQpKdZXVtMH6SSb3zAS3YW'


def collect_tweets(query, max_results=100, start_date=None, end_date=None):
    """트위터 데이터 수집"""

    # 리트윗만 제외 (인용 트윗은 포함)
    enhanced_query = f'{query} -is:retweet'

    url = 'https://api.twitter.com/2/tweets/search/recent'
    headers = {
        'Authorization': f'Bearer {BEARER_TOKEN}',
        'Content-Type': 'application/json'
    }

    # 날짜 설정
    if start_date:
        start_time_str = start_date + 'T00:00:00Z'
    else:
        start_time_str = None

    # 다음과 같이 수정:
    if end_date:
        end_time_str = end_date + 'T23:59:59Z'
    else:
        # 현재 시간에서 1분 전으로 설정
        end_time = datetime.utcnow() - timedelta(minutes=1)
        end_time_str = end_time.strftime('%Y-%m-%dT%H:%M:%SZ')

    params = {
        'query': enhanced_query,
        'max_results': min(max_results, 50),  # API 한계
        'tweet.fields': 'text,created_at,public_metrics,lang',
        'expansions': 'author_id',
        'user.fields': 'public_metrics'
    }

    # 날짜 범위 추가
    if start_time_str:
        params['start_time'] = start_time_str
    if end_time_str:
        params['end_time'] = end_time_str

    print(f"검색 쿼리: {enhanced_query}")
    if start_date:
        print(f"검색 기간: {start_date} ~ {end_date if end_date else '현재'}")

    all_tweets = []
    seen_texts = set()  # 중복 텍스트 방지

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        tweets = data.get('data', [])
        users = {user['id']: user for user in data.get('includes', {}).get('users', [])}

        print(f"✅ {len(tweets)}개 트윗 수집 완료")

        for tweet in tweets:
            text = tweet['text'].strip()
            text = html.unescape(text)  # HTML 엔티티 디코딩 (&quot; 등)
            text = re.sub(r'http[s]?://[^\s]+', '', text)  # URL 제거
            text = re.sub(r'[^\w\s가-힣#@]', ' ', text)  # 한글, 영어, 숫자, 공백, #, @ 만 남기기
            text = re.sub(r'\s+', ' ', text).strip()  # 연속된 공백을 하나로 변경

            # 중복 텍스트 제거
            if text in seen_texts:
                continue
            seen_texts.add(text)

            # 봇 계정이나 링크만 있는 트윗 필터링
            if (len(text) < 10 or  # 너무 짧은 트윗
                    text.count('https://') > 1 or  # 링크만 여러 개
                    any(bot_keyword in text.lower() for bot_keyword in ['bot', '자동', 'automatic'])):
                continue

            # 사용자 정보 가져오기
            author_id = tweet['author_id']
            user_info = users.get(author_id, {})

            tweet_data = {
                'id': tweet['id'],
                'text': text,
                'created_at': tweet['created_at'],
                'lang': tweet.get('lang', 'unknown'),
                'like_count': tweet['public_metrics']['like_count'],
                'retweet_count': tweet['public_metrics']['retweet_count'],
                'reply_count': tweet['public_metrics']['reply_count'],
                'quote_count': tweet['public_metrics']['quote_count'],
                'author_followers': user_info.get('public_metrics', {}).get('followers_count', 0),
                'author_following': user_info.get('public_metrics', {}).get('following_count', 0)
            }

            all_tweets.append(tweet_data)

        # 한국어 트윗만 필터링
        korean_tweets = [t for t in all_tweets if t['lang'] in ['ko', 'unknown']]

        print(f"🇰🇷 한국어 트윗: {len(korean_tweets)}개")
        print(f"중복 제거 완료")

        return korean_tweets

    else:
        print(f"❌ API 오류 {response.status_code}: {response.text}")
        return []


def save_tweets(tweets, filename='twitter_data.json'):
    """트윗 데이터 저장"""
    if not tweets:
        print("❌ 저장할 데이터가 없습니다")
        return

    # JSON 저장 (원본 데이터)
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(tweets, f, indent=2, ensure_ascii=False)

    # CSV 저장 (분석용)
    df = pd.DataFrame(tweets)
    csv_filename = filename.replace('.json', '.csv')
    df.to_csv(csv_filename, index=False, encoding='utf-8-sig')

    print(f"JSON 저장: {filename}")
    print(f"CSV 저장: {csv_filename}")

    # 미리보기
    print(f"\n수집된 트윗 미리보기:")
    for i, tweet in enumerate(tweets[:3]):
        print(f"[{i + 1}] {tweet['text'][:100]}...")
        print(f"    👍 {tweet['like_count']} | 🔄 {tweet['retweet_count']} | 👥 {tweet['author_followers']}명")
        print()


def analyze_tweets_preview(tweets):
    """간단한 트윗 분석 미리보기"""
    if not tweets:
        return

    total = len(tweets)
    avg_likes = sum(t['like_count'] for t in tweets) / total
    avg_retweets = sum(t['retweet_count'] for t in tweets) / total

    print("=" * 50)
    print("수집 결과 요약")
    print("=" * 50)
    print(f"총 트윗 수: {total}개")
    print(f"평균 좋아요: {avg_likes:.1f}개")
    print(f"평균 리트윗: {avg_retweets:.1f}개")
    print(f"수집 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


# 사용법
if __name__ == '__main__':
    # 데이식스 본인확인 이슈 관련 트윗 수집
    query = '데이식스 본인확인 -양도 -판매 -구매 -대리 -교환 -팬싸컷 -항공편'

    print("트위터 데이터 수집 시작")
    print("=" * 50)

    tweets = collect_tweets(query, max_results=50, start_date='2025-07-22', end_date='2025-07-24')

    if tweets:
        save_tweets(tweets, 'dayx6_tweets.json')
        analyze_tweets_preview(tweets)
    else:
        print("❌ 수집된 트윗이 없습니다")