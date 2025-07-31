import requests
import json
import datetime

client_id = '_f7DWBVIPxS1suzjejQN'
client_secret = 'kl4NjeHtnQ'
headers = {
    "X-Naver-Client-Id": client_id,
    "X-Naver-Client-Secret": client_secret
}


def get_naver_search(query, start, display):
    url = f"https://openapi.naver.com/v1/search/news.json?query={query}&start={start}&display={display}"
    response = requests.get(url, headers=headers)
    return response.json()


def extract_article_info(json_result, results):
    for item in json_result['items']:
        title = item['title'].replace('<b>', '').replace('</b>', '')
        description = item['description'].replace('<b>', '').replace('</b>', '')
        link = item['originallink']
        pub_date = datetime.datetime.strptime(item['pubDate'], '%a, %d %b %Y %H:%M:%S +0900').strftime(
            '%Y-%m-%d %H:%M:%S')

        results.append({
            'title': title,
            'description': description,
            'link': link,
            'pub_date': pub_date
        })


def save_to_file(results, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        for result in results:
            f.write(f"제목: {result['title']}\n")
            f.write(f"요약: {result['description']}\n")
            f.write(f"링크: {result['link']}\n")
            f.write(f"날짜: {result['pub_date']}\n")
            f.write("-" * 50 + "\n")


def main():
    query = input('검색어를 입력하세요: ')
    results = []

    start = 1
    total_display = 100
    while True:
        json_result = get_naver_search(query, start, 100)
        if not json_result:
            break

        extract_article_info(json_result, results)
        start += 100
        if start > 100:  # 500건
            break  # 네이버 API는 1000건까지만 제공

    print(f'[INFO] 전체 검색 결과: {len(results)}건 수집 완료')

    json_filename = f"{query}_news.json"
    txt_filename = f"{query}_news.txt"

    with open(json_filename, 'w', encoding='utf8') as outfile:
        json.dump(results, outfile, indent=4, sort_keys=False, ensure_ascii=False)
    print(f"[INFO] JSON 저장 완료 → {json_filename}")

    save_to_file(results, txt_filename)


if __name__ == '__main__':
    main()
