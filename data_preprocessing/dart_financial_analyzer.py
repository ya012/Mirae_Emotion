# -*- coding: utf-8 -*-
"""
DART 공시자료 AI 인사이트 분석기
"""
import dart_fss as dart
import pandas as pd
import requests
import xml.etree.ElementTree as ET
import zipfile
import io
from bs4 import BeautifulSoup
import re
import json
import uuid
from datetime import datetime

# API 키 설정
key = "63b3b1e753b6f1ceabae11c4c94fe0e5dc969922"
CLOVA_API_KEY = 'Bearer nv-4d69f965d3254291a1863335ba9ae203VMRN'
dart.set_api_key(api_key=key)

# 상장 기업명 크롤링
corp_list = dart.api.filings.get_corp_code()
corp_df = pd.DataFrame.from_dict(corp_list)
corp_df = corp_df.dropna(subset='stock_code').sort_values('modify_date', ascending=False).reset_index(drop=True)
corp_df['done_YN'] = "N"


def get_stock_code_by_name(company_name):
    """회사명으로 주식코드 찾기"""
    result = corp_df[corp_df['corp_name'].str.contains(company_name, na=False)]
    if not result.empty:
        corp_name = result.iloc[0]['corp_name']
        stock_code = result.iloc[0]['stock_code']
        print(f"✅ {company_name} → {corp_name} (주식코드: {stock_code})")
        return stock_code
    else:
        print(f"❌ '{company_name}' 기업을 찾을 수 없습니다")
        return None


# 회사명으로 주식코드 찾기
stock_code = get_stock_code_by_name('JYP')
if stock_code is None:
    exit()

# 주식코드로 기업코드 찾기
result = corp_df[corp_df['stock_code'] == stock_code]
corp_code = result.iloc[0]['corp_code']
print(f"📋 기업코드: {corp_code}")

# 사업보고서 리스트
url_json = "https://opendart.fss.or.kr/api/list.json"
params = {
    'crtfc_key': key,
    'corp_code': corp_code,
    'pblntf_ty': 'A',
    'bgn_de': '20240101'
}

response = requests.get(url_json, params=params)
res = response.json()

if res['status'] == '013':
    print("❌ 사업보고서가 없습니다")
    exit()

df_imsi = pd.DataFrame(res['list'])
latest_rcept_no = df_imsi.iloc[0]['rcept_no']
print(f"최신 접수번호: {latest_rcept_no}")

# API로 데이터 가져오기
url = 'https://opendart.fss.or.kr/api/document.xml'
params = {
    'crtfc_key': key,
    'rcept_no': latest_rcept_no,
}
r = requests.get(url, params=params)

# XML 처리
try:
    tree = ET.XML(r.text)
    status = tree.find('status').text
    if status != '000':
        print("❌ XML 다운로드 실패")
        exit()
except ET.ParseError:
    pass

zf = zipfile.ZipFile(io.BytesIO(r.content))
xml_text_list = []
for fname in sorted([info.filename for info in zf.infolist()]):
    xml_data = zf.read(fname)
    try:
        xml_text = xml_data.decode('euc-kr')
    except:
        try:
            xml_text = xml_data.decode('utf-8')
        except:
            xml_text = str(xml_data)
    xml_text_list.append(xml_text)

print(f"✅ {len(xml_text_list)}개 XML 파일 추출")


def extract_financial_info(xml_text_list):
    """재무정보 추출"""
    target_keywords = {
        '매출액': ['매출액', '수익(매출액)', '영업수익'],
        '영업이익': ['영업이익', '영업손익'],
        '당기순이익': ['당기순이익', '순이익'],
        '자산총계': ['자산총계', '자산총액'],
        '부채총계': ['부채총계', '부채총액'],
        '자본총계': ['자본총계', '자본총액']
    }

    financial_data = []
    for i, xml_text in enumerate(xml_text_list):
        soup = BeautifulSoup(xml_text, 'html.parser')
        text_content = soup.get_text()

        file_data = {}
        for main_key, keyword_list in target_keywords.items():
            for keyword in keyword_list:
                pattern = rf'{keyword}[^\d]*?([0-9,]+(?:\.[0-9]+)?)'
                matches = re.findall(pattern, text_content)
                if matches:
                    numbers = [float(match.replace(',', '')) for match in matches
                               if float(match.replace(',', '')) > 1000]
                    if numbers:
                        file_data[main_key] = max(numbers)
                        break

        if file_data:
            financial_data.append(file_data)

    return financial_data


def calculate_financial_ratios(latest_data):
    """재무비율 계산"""
    ratios = {}

    if '당기순이익' in latest_data and '자본총계' in latest_data and latest_data['자본총계'] != 0:
        roe = (latest_data['당기순이익'] / latest_data['자본총계']) * 100
        ratios['ROE'] = round(roe, 2)

    if '당기순이익' in latest_data and '자산총계' in latest_data and latest_data['자산총계'] != 0:
        roa = (latest_data['당기순이익'] / latest_data['자산총계']) * 100
        ratios['ROA'] = round(roa, 2)

    if '부채총계' in latest_data and '자산총계' in latest_data and latest_data['자산총계'] != 0:
        debt_ratio = (latest_data['부채총계'] / latest_data['자산총계']) * 100
        ratios['부채비율'] = round(debt_ratio, 2)

    if '영업이익' in latest_data and '매출액' in latest_data and latest_data['매출액'] != 0:
        operating_margin = (latest_data['영업이익'] / latest_data['매출액']) * 100
        ratios['영업이익률'] = round(operating_margin, 2)

    return ratios


def generate_ai_insight(financial_data, financial_ratios):
    """HyperCLOVA X로 AI 인사이트 생성"""
    print("🤖 AI 인사이트 생성 중...")

    latest = financial_data[-1]

    system_prompt = """당신은 엔터테인먼트 투자 전문가입니다.
제공된 재무정보를 바탕으로 다음 형식으로 분석해주세요:

1. 재무현황 요약 (2줄)
2. 주요 강점 (2줄)
3. 주요 리스크 (2줄)
4. 투자관점 의견 (2줄)

전문적이고 간결하게 작성해주세요."""

    user_content = f"""
재무현황:
- 매출액: {latest.get('매출액', 0) / 1e8:.1f}억원
- 영업이익: {latest.get('영업이익', 0) / 1e8:.1f}억원
- 당기순이익: {latest.get('당기순이익', 0) / 1e8:.1f}억원

재무비율:
- ROE: {financial_ratios.get('ROE', 'N/A')}%
- 영업이익률: {financial_ratios.get('영업이익률', 'N/A')}%
- 부채비율: {financial_ratios.get('부채비율', 'N/A')}%

"""

    request_id = str(uuid.uuid4()).replace('-', '')
    headers = {
        'Authorization': CLOVA_API_KEY,
        'X-NCP-CLOVASTUDIO-REQUEST-ID': request_id,
        'Content-Type': 'application/json; charset=utf-8',
        'Accept': 'text/event-stream'
    }

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content}
    ]

    request_data = {
        'messages': messages,
        'topP': 0.8,
        'topK': 0,
        'maxTokens': 800,
        'temperature': 0.3,
        'repetitionPenalty': 1.1,
        'stop': [],
        'includeAiFilters': True,
        'seed': 0
    }

    try:
        with requests.post('https://clovastudio.stream.ntruss.com/v3/chat-completions/HCX-005',
                           headers=headers, json=request_data, stream=True) as response:
            for line in response.iter_lines():
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
        print(f"❌ AI 인사이트 생성 실패: {e}")
        return None

    return None


# 분석 실행
if __name__ == '__main__':
    print("🚀 DART 공시분석 + AI 인사이트 생성 시작")
    print("=" * 60)

    # 재무정보 추출
    financial_data = extract_financial_info(xml_text_list)
    if not financial_data:
        print("❌ 재무정보 추출 실패")
        exit()

    # 재무비율 계산
    financial_ratios = calculate_financial_ratios(financial_data[-1])

    # 결과 출력
    latest = financial_data[-1]
    print(f"\n💰 재무현황:")
    for key in ['매출액', '영업이익', '당기순이익']:
        if key in latest:
            print(f"  {key}: {latest[key] / 1e8:.1f}억원")

    print(f"\n📊 재무비율:")
    for key, value in financial_ratios.items():
        print(f"  {key}: {value}%")

    # AI 인사이트 생성
    ai_insight = generate_ai_insight(financial_data, financial_ratios)

    if ai_insight:
        print(f"\n🤖 AI 인사이트:")
        print("-" * 60)
        print(ai_insight)
        print("-" * 60)

    # 결과 저장
    result = {
        '기업코드': corp_code,
        '주식코드': stock_code,
        '분석일시': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        '재무정보': financial_data,
        '재무비율': financial_ratios,
        'AI_인사이트': ai_insight
    }

    filename = f'DART_AI분석_{stock_code}.json'
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 저장 완료: {filename}")
    print("🎉 AI 인사이트 분석 완료!")