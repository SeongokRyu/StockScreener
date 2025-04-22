import sys
from google import genai


def sector_analysis_input(sector_list, inp_list):
	gemini_input = """
	너는 한국주식시장을 분석하는 역할을 하게 될거야.
	
	먼저, 내가 아래와 같이 한국 상장주식들이 속할 업종을 리스트로 만들어보았어.
	"""
	for sector in sector_list:
		gemini_input += " - " + sector + "\n"
	
	gemini_input += """
	다음과 같이 기업들의 종목코드와 이름이 주어졌을때, 각 기업이 속하는 업종을 골라줘.
	"""

	for inp in inp_list:
		gemini_input += " - " + inp[0] + ", " + inp[1] + "\n"
	
	gemini_input += """
	답변은 아래와 같은 포맷으로 해줘.
	- 종목코드 <sep> 기업이름 <sep> 속하는 업종
	속하는 업종을 답변할때, 내가 제안한 업종 외 다른 부연설명을 하지말아줘,
	"""

	return gemini_input


def run_gemini(
		contents,
		api_key,
		model="gemini-2.0-flash",
	):
	client = genai.Client(api_key=api_key)
	response = client.models.generate_content(
		contents=contents,
		model=model,
	)
	return response.text


if __name__ == '__main__':
	if len(sys.argv) > 1:
		answer = run_gemini(sys.argv[1])
