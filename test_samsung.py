import sys
import yfinance as yf

# Windows 콘솔 한글 깨짐 방지
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

def test_apple_stock(ticker_symbol="AAPL"):
    # 애플 티커 심볼 (AAPL)
    stock = yf.Ticker(ticker_symbol)
    
    # 1. 최근 1개월 역사적 데이터 조회
    print(f"=== [최근 1개월 주가 데이터 (처음 5개 행): {ticker_symbol}] ===")
    df = stock.history(period="1mo")
    
    if df.empty:
        print("데이터를 불러오지 못했습니다.")
        return

    print(df.head())
    print("\n" + "=" * 50 + "\n")

    # 2. 회사 기본 정보 및 시세 정보 조회
    info = stock.info
    company_name = info.get("shortName") or info.get("longName") or "Apple Inc."
    currency = info.get("currency", "USD")
    currency_unit = "$" if currency == "USD" else ("원" if currency == "KRW" else f" {currency}")

    # 현재가 및 전일 종가 확인 (info 또는 history 기반)
    current_price = info.get("currentPrice") or info.get("regularMarketPrice")
    prev_close = info.get("previousClose") or info.get("regularMarketPreviousClose")

    # info에서 가져오지 못한 경우 history의 최근 데이터를 fallback으로 활용
    if current_price is None and len(df) >= 1:
        current_price = df["Close"].iloc[-1]
    if prev_close is None and len(df) >= 2:
        prev_close = df["Close"].iloc[-2]

    # 전일 대비 등락률 계산
    if current_price is not None and prev_close is not None and prev_close != 0:
        change = current_price - prev_close
        change_rate = (change / prev_close) * 100
        if currency == "USD":
            change_str = f"{change:+.2f}{currency_unit} ({change_rate:+.2f}%)"
        else:
            change_str = f"{change:+,.0f}{currency_unit} ({change_rate:+.2f}%)"
    else:
        change_str = "계산 불가"

    print("=== [주식 정보] ===")
    print(f"회사명: {company_name}")
    if current_price is not None:
        price_fmt = f"{current_price:,.2f}" if currency == "USD" else f"{current_price:,.0f}"
        print(f"현재가: {price_fmt}{currency_unit}")
    else:
        print(f"현재가: {current_price}")
    print(f"전일 대비 등락률: {change_str}")

if __name__ == "__main__":
    test_apple_stock()

