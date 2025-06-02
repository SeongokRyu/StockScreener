import os
import asyncio
import requests
from bs4 import BeautifulSoup
import re

# strands & gemini 관련 라이브러리
from strands.model_provider import ModelProvider, ModelProviderMessage
from strands.agent import StrandsAgent
from strands.tool import tool

import google.generativeai as genai

# --- 1. Gemini 모델 프로바이더 설정 (이전과 동일) ---
genai.configure(api_key="YOUR_GEMINI_API_KEY") # 실제 API 키 입력

class GeminiModelProvider(ModelProvider):
    def __init__(self, model_name: str = "gemini-1.5-flash"):
        self.model = genai.GenerativeModel(model_name)

    def invoke(self, messages: list[ModelProviderMessage]) -> ModelProviderMessage:
        gemini_messages = [{"role": msg.role if msg.role != "agent" else "model", "parts": [msg.content]} for msg in messages]
        response = self.model.generate_content(gemini_messages)
        return ModelProviderMessage(role="model", content=response.text)

# --- 2. 웹 스크레이핑을 수행하는 '도구' 정의 ---

def _calculate_growth_rate(current, past):
    """EPS 성장률 계산 함수"""
    if past is None or current is None or past == 0:
        return None
    return round(((current - past) / abs(past)) * 100, 2)

@tool
def get_financial_metrics(stock_code: str):
    """
    주어진 종목 코드에 해당하는 주식의 주요 재무지표(PER, PBR, ROE, EPS 성장률)를 FnGuide에서 스크레이핑하여 가져옵니다.
    사용자가 특정 회사의 재무 정보나 실적을 물어보면 이 도구를 사용해야 합니다.
    
    :param stock_code: 조회할 종목의 코드 (예: '005930')
    """
    try:
        # FnGuide URL 생성
        url = f"https://comp.fnguide.com/SVO3/ASP/SVD_Main.asp?pGB=1&gicode=A{stock_code}"
        headers = {'User-Agent': 'Mozilla/5.0'} # 웹사이트 차단 방지를 위한 헤더
        
        response = requests.get(url, headers=headers)
        response.raise_for_status() # 오류 발생 시 예외 처리
        
        soup = BeautifulSoup(response.text, 'html.parser')

        # --- 데이터 추출 ---
        # PER, PBR, ROE 데이터가 있는 하이라이트 테이블 추출
        highlight_table = soup.select_one("#highlight_D_A")
        
        # 텍스트 클리닝 함수
        def get_value(metric_name):
            try:
                # 테이블에서 항목 이름(th)을 찾고, 그 다음 셀(td)의 텍스트를 가져옴
                value_text = highlight_table.find(string=re.compile(metric_name)).find_next('td').text.strip()
                return float(value_text.replace(',', ''))
            except (AttributeError, ValueError):
                return None # 값을 찾지 못하거나 숫자로 변환 실패 시 None 반환

        per = get_value("PER")
        pbr = get_value("PBR")
        roe = get_value("ROE")

        # EPS 데이터가 있는 재무제표 테이블 추출
        sonik_table = soup.select_one("#sonik-IFRS")
        eps_row = sonik_table.find(string=re.compile("EPS\(원\)")).find_parent('tr')
        eps_values_raw = [td.text.strip() for td in eps_row.find_all('td')]

        # 최근 4개년 실적 및 1개년 예상 실적 추출
        eps_values = [float(v.replace(',', '')) if v else None for v in eps_values_raw[:5]]
        
        # 연도 정보 추출
        year_row = sonik_table.select("thead > tr")[1]
        years = [th.text.strip().split('/')[0] for th in year_row.find_all('th')][:5]

        # EPS 성장률 계산
        eps_growth = {}
        for i in range(1, 4): # 최근 3개년 성장률
            growth = _calculate_growth_rate(eps_values[i], eps_values[i-1])
            eps_growth[f"{years[i]} vs {years[i-1]}"] = growth
        
        # 올해 예상 실적 기반 성장률
        forecast_growth = _calculate_growth_rate(eps_values[4], eps_values[3])
        eps_growth[f"{years[4]}(E) vs {years[3]}"] = forecast_growth

        # 최종 결과 정리
        result = {
            "종목코드": stock_code,
            "PER": per,
            "PBR": pbr,
            "ROE": roe,
            "최근_EPS": dict(zip(years, eps_values)),
            "EPS_성장률": eps_growth
        }
        return str(result) # AI가 쉽게 이해하도록 문자열로 변환하여 반환

    except Exception as e:
        return f"오류가 발생했습니다: {e}. 종목코드가 올바른지 확인해주세요."


# --- 3. 에이전트 생성 및 실행 ---

async def main():
    agent = StrandsAgent("Financial Analyst Agent")

    # 에이전트에 Gemini 모델과 재무지표 도구 등록
    agent.add_model_provider(name="gemini", provider=GeminiModelProvider())
    agent.add_tool(get_financial_metrics)

    print("--- Financial Analyst Agent가 준비되었습니다. ---")
    print("예시 질문: '삼성전자(005930) 재무지표 좀 알려줘.')\n")
    
    # 사용자 질문
    # user_query = "삼성전자(005930) 재무지표 좀 알려줘."
    user_query = "네이버의 PER, PBR, 그리고 최근 EPS 성장률이 궁금해. 종목코드는 035420이야."

    # 에이전트 실행
    response = await agent.run(user_query, default_model="gemini")
    
    print(f"\n[사용자 질문]\n{user_query}")
    print("\n[AI 에이전트 답변]")
    print(response)

if __name__ == "__main__":
    asyncio.run(main())
