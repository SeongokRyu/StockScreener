import pandas as pd


def categorize_trend_condition(
		macd, prev_macd, hist, prev_hist,
		macd_near_zero_thresh=0.05, # 예시 값, 자산 가격 및 변동성에 따라 조정 필요
		hist_near_zero_thresh=0.01  # 예시 값, 자산 가격 및 변동성에 따라 조정 필요
	):
	"""
	주어진 MACD 및 히스토그램 값에 따라 시장 상황을 카테고리화합니다.
	Args:
		macd (float): 현재 MACD 값.
		prev_macd (float): 이전 MACD 값.
		hist (float): 현재 히스토그램 값.
		prev_hist (float): 이전 히스토그램 값.
		macd_near_zero_thresh (float): MACD가 0에 가깝다고 판단하는 임계값.
		hist_near_zero_thresh (float): 히스토그램이 0에 가깝다고 판단하는 임계값.

	Returns:
		str: 분류된 카테고리 문자열.
	"""

	# MACD 값의 상태 (0선 기준)
	is_uptrend_context = macd > macd_near_zero_thresh
	is_downtrend_context = macd < -macd_near_zero_thresh
	is_no_clear_trend_context = abs(macd) <= macd_near_zero_thresh

	# MACD 선의 기울기
	macd_is_rising = macd > prev_macd
	macd_is_falling = macd < prev_macd

	# 히스토그램 상태 및 기울기
	# hist > 0: MACD 선 > 시그널 선 (골든크로스 후 또는 유지)
	# hist < 0: MACD 선 < 시그널 선 (데드크로스 후 또는 유지)

	# 히스토그램 확대 (0선에서 멀어짐)
	hist_expanding_positive = hist > hist_near_zero_thresh and hist > prev_hist  # 양수이며 증가 (확대)
	hist_expanding_negative = hist < -hist_near_zero_thresh and hist < prev_hist # 음수이며 감소 (더 음수로 확대)

	# 히스토그램 축소 (0선으로 가까워짐)
	hist_contracting_from_positive = hist > hist_near_zero_thresh and hist < prev_hist # 양수이며 감소 (0으로 축소)
	hist_contracting_from_negative = hist < -hist_near_zero_thresh and hist > prev_hist # 음수이며 증가 (0으로 축소)

	# 히스토그램이 0에 가까운 상태
	hist_is_near_zero = abs(hist) <= hist_near_zero_thresh

	# 카테고리 분류 로직 (순서 중요)
	# 1. 상승 추세 / 추세 확대중
	if is_uptrend_context and macd_is_rising and hist_expanding_positive:
		return "1. 상승 추세 / 추세 확대중"

	# 5. 하락추세 / 추세 확대중
	elif is_downtrend_context and macd_is_falling and hist_expanding_negative:
		return "5. 하락추세 / 추세 확대중"

	# 2. 상승 추세 / 눌림목
	#    - MACD > 0 (상승 추세 컨텍스트)
	#    - 히스토그램이 양수에서 0으로 축소 중 (MACD선이 시그널선으로 하락 접근)
	#    - 또는 히스토그램이 음수에서 0으로 축소 중 (MACD선이 시그널선 아래로 일시 하락 후 반등 시도)
	elif is_uptrend_context and (hist_contracting_from_positive or hist_contracting_from_negative):
		return "2. 상승 추세 / 눌림목"

	# 6. 하락추세 / 일시적 반등
	#    - MACD < 0 (하락 추세 컨텍스트)
	#    - 히스토그램이 음수에서 0으로 축소 중 (MACD선이 시그널선으로 상승 접근)
	#    - 또는 히스토그램이 양수에서 0으로 축소 중 (MACD선이 시그널선 위로 일시 상승 후 하락 시도)
	elif is_downtrend_context and (hist_contracting_from_negative or hist_contracting_from_positive):
		return "6. 하락추세 / 일시적 반등"

	# 3. 뚜렷한 추세 없음 / 추세 확대
	#    - MACD가 0 근처
	#    - 히스토그램이 0에서 멀어지며 확대 (상승 또는 하락 방향으로 움직임 시작)
	elif is_no_clear_trend_context and (hist_expanding_positive or hist_expanding_negative):
		return "3. 뚜렷한 추세 없음 / 추세 확대"

	# 4. 뚜렷한 추세 없음 / 눌림목 (또는 횡보/응축)
	#    - MACD가 0 근처
	#    - 히스토그램도 0 근처이거나, 0으로 축소 중 (뚜렷한 방향성 없이 힘이 응축되는 모습)
	elif is_no_clear_trend_context and (hist_is_near_zero or hist_contracting_from_positive or hist_contracting_from_negative):
		return "4. 뚜렷한 추세 없음 / 눌림목"

	else:
		return "9. 분류 미정" # 위의 어떤 조건에도 해당하지 않는 경우


def calculate_macd_indicators(date_list, price_list, short_window=12, long_window=26, signal_window=9):
    """
    주어진 주가 리스트와 기간으로 MACD 관련 지표들(MACD, Signal, Histogram)을 계산합니다.

    Args:
        prices (list or pd.Series): 최근 n거래일의 종가 리스트 또는 시리즈.
        short_window (int): 단기 EMA를 위한 기간 (기본값: 12).
        long_window (int): 장기 EMA를 위한 기간 (기본값: 26).
        signal_window (int): 시그널 선을 위한 MACD의 EMA 기간 (기본값: 9).

    Returns:
        pd.DataFrame: 'Price', 'EMA_short', 'EMA_long', 'MACD', 'Signal', 'Histogram' 컬럼을 포함하는 DataFrame.
                     초기값은 EMA 계산에 필요한 데이터 부족으로 NaN일 수 있습니다.
    """
    if not isinstance(price_list, pd.Series):
        prices_series = pd.Series(price_list, name='Price')
    else:
        prices_series = price_list.rename('Price')

    if len(prices_series) < long_window:
        raise ValueError(f"주가 데이터 길이({len(prices_series)})가 장기 EMA 기간({long_window})보다 짧습니다.")

    # 단기 EMA 계산
    ema_short = prices_series.ewm(span=short_window, adjust=False, min_periods=short_window).mean()

    # 장기 EMA 계산
    ema_long = prices_series.ewm(span=long_window, adjust=False, min_periods=long_window).mean()

    # MACD 계산
    macd_line = ema_short - ema_long

    # 시그널 선 계산 (MACD 선의 EMA)
    signal_line = macd_line.ewm(span=signal_window, adjust=False, min_periods=signal_window).mean()

    # MACD 히스토그램 계산
    histogram = macd_line - signal_line

    # 결과 DataFrame 생성
    df = pd.DataFrame({
		'Date': date_list,
        'Price': prices_series,
        f'EMA_{short_window}': ema_short,
        f'EMA_{long_window}': ema_long,
        'MACD': macd_line,
        'Signal': signal_line,
        'Histogram': histogram
    })

    return df
