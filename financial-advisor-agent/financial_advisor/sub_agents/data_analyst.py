import yfinance as yf
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm


MODEL = LiteLlm(model="openai/gpt-4o-mini")


def get_company_info(ticker: str) -> str:
    """
    주어진 주식 티커에 대한 기본 기업 정보를 조회합니다.

    이 도구는 Yahoo Finance에서 공식 회사명, 산업 분류, 섹터 분류 등
    기본적인 기업 세부 정보를 가져옵니다.

    Args:
        ticker (str): 주식 티커 심볼 (예: 'AAPL'은 Apple Inc.)

    Returns:
        dict: 다음 항목을 포함하는 딕셔너리:
            - ticker (str): 입력된 티커 심볼
            - success (bool): 작업 성공 여부
            - company_name (str): 회사의 공식 법인명
            - industry (str): 세부 산업 분류
            - sector (str): 광범위한 섹터 분류

    Example:
        >>> get_company_info('MSFT')
        {
            'ticker': 'MSFT',
            'success': True,
            'company_name': 'Microsoft Corporation',
            'industry': 'Software - Infrastructure',
            'sector': 'Technology'
        }
    """
    stock = yf.Ticker(ticker)
    info = stock.info
    return {
        "ticker": ticker,
        "success": True,
        "company_name": info.get("longName", "NA"),
        "industry": info.get("industry", "NA"),
        "sector": info.get("sector", "NA"),
    }


def get_stock_price(ticker: str, period: str) -> str:
    """
    주어진 티커의 과거 주가 데이터와 현재 거래 가격을 가져옵니다.

    이 도구는 시가, 고가, 저가, 종가, 거래량을 포함한 지정된 기간 동안의
    현재 시장 가격과 과거 가격 데이터를 모두 조회합니다.

    Args:
        ticker (str): 주식 티커 심볼 (예: 'AAPL'은 Apple Inc.)
        period (str): 과거 데이터의 기간. 유효한 옵션:
            - '1d': 1일
            - '5d': 5일
            - '1mo': 1개월 (기본값)
            - '3mo': 3개월
            - '6mo': 6개월
            - '1y': 1년
            - '2y': 2년
            - '5y': 5년
            - '10y': 10년
            - 'ytd': 연초부터 현재까지
            - 'max': 최대 가용 데이터

    Returns:
        dict: 다음 항목을 포함하는 딕셔너리:
            - ticker (str): 입력된 티커 심볼
            - success (bool): 작업 성공 여부
            - history (str): OHLCV 데이터를 포함한 JSON 형식의 과거 가격 데이터
            - current_price (float): 주식의 현재 시장 가격

    Example:
        >>> get_stock_price('TSLA', '3mo')
        {
            'ticker': 'TSLA',
            'success': True,
            'history': '{"Open": {...}, "High": {...}, ...}',
            'current_price': 245.67
        }
    """
    stock = yf.Ticker(ticker)
    info = stock.info
    history = stock.history(period=period)
    return {
        "ticker": ticker,
        "success": True,
        "history": history.to_json(),
        "current_price": info.get("currentPrice"),
    }


def get_financial_metrics(ticker: str) -> str:
    """
    주식 분석을 위한 핵심 재무 지표 및 가치 평가 비율을 조회합니다.

    이 도구는 기업의 가치 평가, 수익성, 배당 정책 및 시장 리스크 특성을
    평가하는 데 도움이 되는 필수 재무 지표를 가져옵니다.

    Args:
        ticker (str): 주식 티커 심볼 (예: 'AAPL'은 Apple Inc.)

    Returns:
        dict: 다음 항목을 포함하는 딕셔너리:
            - ticker (str): 입력된 티커 심볼
            - success (bool): 작업 성공 여부
            - market_cap (float): USD 기준 총 시가총액
            - pe_ratio (float): 후행 주가수익비율 (주가/주당순이익)
            - dividend_yield (float): 연간 배당수익률 (백분율, 0.02 = 2%)
            - beta (float): 시장 대비 변동성을 측정하는 베타 계수

    Notes:
        - 시가총액: 기업의 총 가치를 나타냅니다 (주식수 * 주가)
        - PER: 낮을수록 저평가, 높을수록 성장 기대감을 나타낼 수 있습니다.
        - 배당수익률: 주가 대비 연간 배당금 비율
        - 베타: 1 미만이면 시장보다 변동성 낮음, 1 초과이면 높음

    Example:
        >>> get_financial_metrics('JNJ')
        {
            'ticker': 'JNJ',
            'success': True,
            'market_cap': 385000000000,
            'pe_ratio': 15.2,
            'dividend_yield': 0.031,
            'beta': 0.65
        }
    """
    stock = yf.Ticker(ticker)
    info = stock.info
    return {
        "ticker": ticker,
        "success": True,
        "market_cap": info.get("marketCap", "NA"),
        "pe_ratio": info.get("trailingPE", "NA"),
        "dividend_yield": info.get("dividendYield", "NA"),
        "beta": info.get("beta", "NA"),
    }


data_analyst = LlmAgent(
    name="DataAnalyst",
    model=MODEL,
    description="여러 전문 도구를 사용하여 기본 주식 시장 데이터를 수집하고 분석합니다.",
    instruction="""
    당신은 4개의 전문 도구를 사용하여 주식 정보를 수집하는 데이터 분석가입니다:

    1. **get_company_info(ticker)** - 기업 정보 확인 (이름, 섹터, 산업)
    2. **get_stock_price(ticker, period)** - 현재 가격 및 거래 범위 조회
    3. **get_financial_metrics(ticker)** - 핵심 재무 비율 확인

    여러 전문 도구를 사용하여 다양한 유형의 데이터를 수집합니다.
    각 도구가 제공하는 정보를 설명하고 명확하게 제시합니다.
    """,
    tools=[
        get_company_info,
        get_stock_price,
        get_financial_metrics,
    ],
)
