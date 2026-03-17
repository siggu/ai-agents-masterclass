import yfinance as yf
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

MODEL = LiteLlm(model="openai/gpt-4o-mini")


def get_income_statement(ticker: str):
    """
    포괄적인 수익 및 수익성 분석을 위한 손익계산서를 조회합니다.

    이 도구는 최근 보고 기간 동안의 수익, 비용, 다양한 수준의 이익 마진을 포함한
    기업의 재무 성과를 보여주는 상세한 손익계산서 데이터를 가져옵니다.

    Args:
        ticker (str): 주식 티커 심볼 (예: 'AAPL'은 Apple Inc.)

    Returns:
        dict: 다음 항목을 포함하는 딕셔너리:
            - ticker (str): 입력된 티커 심볼
            - success (bool): 작업 성공 여부
            - income_statement (str): JSON 형식의 손익계산서 데이터:
                * 총 수익 (Total Revenue)
                * 매출원가 (Cost of Revenue)
                * 매출총이익 (Gross Profit)
                * 영업비용 (Operating Expenses)
                * 영업이익 (Operating Income)
                * EBITDA
                * 순이익 (Net Income)
                * 주당순이익 (EPS)

    Notes:
        - 데이터는 일반적으로 최근 4분기 및 연간 기간을 포함합니다.
        - 모든 재무 수치는 회사의 보고 통화 기준입니다.
        - 수익 성장, 마진 추세 및 수익성 분석에 유용합니다.

    Example:
        >>> get_income_statement('GOOGL')
        {
            'ticker': 'GOOGL',
            'success': True,
            'income_statement': '{"Total Revenue": {...}, "Net Income": {...}}'
        }
    """
    stock = yf.Ticker(ticker)
    # return stock.income_stmt.to_json()
    return {
        "ticker": ticker,
        "success": True,
        "income_statement": stock.income_stmt.to_json(),
    }


def get_balance_sheet(ticker: str):
    """
    재무 상태 및 자본 구조 분석을 위한 대차대조표를 조회합니다.

    이 도구는 특정 시점에서 기업의 자산, 부채, 주주 자본을 보여주는
    포괄적인 대차대조표 데이터를 가져와 재무 건전성 및 자본 효율성에 대한
    인사이트를 제공합니다.

    Args:
        ticker (str): 주식 티커 심볼 (예: 'AAPL'은 Apple Inc.)

    Returns:
        dict: 다음 항목을 포함하는 딕셔너리:
            - ticker (str): 입력된 티커 심볼
            - success (bool): 작업 성공 여부
            - balance_sheet (str): JSON 형식의 대차대조표 데이터:
                * 유동자산 (현금, 매출채권, 재고)
                * 비유동자산 (유형자산, 무형자산, 투자)
                * 유동부채 (매입채무, 단기부채)
                * 비유동부채 (장기부채, 이연항목)
                * 총 주주 자본
                * 운전자본 구성요소

    Notes:
        - 분기/연도 말 재무 상태의 스냅샷을 제공합니다.
        - 유동성 비율(유동비율, 당좌비율) 계산에 필수적입니다.
        - 부채 수준, 자산 효율성 및 장부가치 평가에 사용됩니다.
        - 모든 값은 회사의 보고 통화 기준입니다.

    Example:
        >>> get_balance_sheet('AMZN')
        {
            'ticker': 'AMZN',
            'success': True,
            'balance_sheet': '{"Total Assets": {...}, "Total Liabilities": {...}}'
        }
    """
    stock = yf.Ticker(ticker)
    # return stock.balance_sheet.to_json()
    return {
        "ticker": ticker,
        "success": True,
        "balance_sheet": stock.balance_sheet.to_json(),
    }


def get_cash_flow(ticker: str):
    """
    현금 창출 및 자본 배분 분석을 위한 현금흐름표를 조회합니다.

    이 도구는 기업이 영업, 투자, 재무 활동 전반에 걸쳐 현금을 어떻게 창출하고
    사용하는지 보여주는 상세한 현금흐름 데이터를 가져와 재무 지속 가능성과
    성장 역량 평가에 활용합니다.

    Args:
        ticker (str): 주식 티커 심볼 (예: 'AAPL'은 Apple Inc.)

    Returns:
        dict: 다음 항목을 포함하는 딕셔너리:
            - ticker (str): 입력된 티커 심볼
            - success (bool): 작업 성공 여부
            - cash_flow (str): JSON 형식의 현금흐름표 데이터:
                * 영업현금흐름 (핵심 사업 현금)
                * 자본적 지출 (CapEx)
                * 잉여현금흐름 (영업CF - CapEx)
                * 투자활동 (인수, 투자)
                * 재무활동 (부채, 배당금, 자사주 매입)
                * 순현금 변동

    Notes:
        - 영업현금흐름은 핵심 사업의 현금 창출 능력을 나타냅니다.
        - 잉여현금흐름은 주주/성장에 사용 가능한 현금을 보여줍니다.
        - 음수 투자CF는 종종 성장 투자를 의미합니다.
        - 재무CF는 자본 구조 결정을 나타냅니다.
        - 배당금 지속 가능성 및 성장 자금 평가에 중요합니다.

    Example:
        >>> get_cash_flow('META')
        {
            'ticker': 'META',
            'success': True,
            'cash_flow': '{"Operating Cash Flow": {...}, "Free Cash Flow": {...}}'
        }
    """
    stock = yf.Ticker(ticker)
    # return stock.balance_sheet.to_json()
    return {
        "ticker": ticker,
        "success": True,
        "cash_flow": stock.cash_flow.to_json(),
    }


financial_analyst = Agent(
    name="FinancialAnalyst",
    model=MODEL,
    description="손익계산서, 대차대조표, 현금흐름표를 포함한 상세 재무제표를 분석합니다.",
    instruction="""
    당신은 심층적인 재무제표 분석을 수행하는 재무 분석가입니다. 담당 업무:

    1. **손익 분석**: get_income_statement()를 사용하여 수익, 수익성 및 마진을 분석합니다.
    2. **대차대조표 분석**: get_balance_sheet()를 사용하여 자산, 부채 및 재무 상태를 검토합니다.
    3. **현금흐름 분석**: get_cash_flow()를 사용하여 현금 창출 및 자본 배분을 평가합니다.

    **사용 가능한 재무 도구:**
    - **get_income_statement(ticker)**: 수익, 이익 마진 및 수익성 분석
    - **get_balance_sheet(ticker)**: 자산, 부채, 자본 및 재무 건전성 비율
    - **get_cash_flow(ticker)**: 영업현금흐름, 잉여현금흐름 및 자본적 지출

    포괄적인 재무제표 데이터를 사용하여 기업의 재무 건전성과 성과를 분석합니다.
    기업의 재무 강점을 나타내는 핵심 재무 비율, 추세 및 지표에 집중합니다.
    """,
    output_key="financial_analysis_results",
    tools=[
        get_income_statement,
        get_balance_sheet,
        get_cash_flow,
    ],
)
