import os
import pandas as pd

import requests
import html
from bs4 import BeautifulSoup

import FinanceDataReader as fdr


def get_stock_list(market: str):
	df = fdr.StockListing(market)
	return df


def fetch_fics_and_highlight(ticker: str):
    """
    1) FICS 업종 문자열
    2) Financial Highlight 표 (헤더: 계정 + 기간 문자열)
    """
    url = (
        "https://comp.fnguide.com/SVO3/ASP/SVD_Main.asp"
        f"?pGB=4&gicode=A{ticker}&MenuYn=N&NewMenuID=101&stkGb=701"
    )
    hdrs = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://comp.fnguide.com/"
    }
    soup = BeautifulSoup(requests.get(url, headers=hdrs, timeout=10).text, "lxml")

    # ── 1️⃣ FICS ───────────────────────────────────────────────
    fics_span = soup.find("span", class_="stxt stxt2",
                          string=lambda x: x and "FICS" in x)
    if fics_span:
        fics = fics_span.get_text(" ", strip=True).split("FICS", 1)[-1].strip()
        fics = html.unescape(fics).replace('\xa0', ' ')
    else:
        fics = "N/A"

    # ── 2️⃣ Financial Highlight (Annual+Quarter) ───────────────
    div = soup.find("div", id="highlight_D_A")
    if div is None:
        raise RuntimeError("highlight_D_A 테이블을 찾지 못했습니다.")

    # 두 줄 헤더 → MultiIndex 로 로드
    df = pd.read_html(str(div), header=[0, 1])[0]

    # IFRS(연결) 헤더 행 삭제
    df = df.dropna(how="all").loc[~df.iloc[:, 0].str.contains("IFRS", na=False)]

    # ── 헤더 가공 ───────────────────────────────────────────────
    #   col[0] : 'Annual' / 'Net Quarter' / ''(첫열)
    #   col[1] : '2024/12' … 실제 기간
    new_cols = ["계정"] + [c[1].strip() for c in df.columns[1:]]
    df.columns = new_cols

    # ── 숫자형 변환 · 쉼표 제거 ────────────────────────────────
    df = (df.set_index("계정")
            .applymap(lambda x: str(x).replace(",", ""))
            .apply(pd.to_numeric, errors="ignore"))

    return fics, df
