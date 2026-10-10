import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 페이지 설정
st.set_page_config(
    page_title="주식 데이터 분석기",
    page_icon="📈",
    layout="wide"
)

# 커스텀 스타일
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .sub-text {
        color: #6c757d;
        margin-bottom: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">📈 주식 데이터 분석기</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-text">Yahoo Finance를 기반으로 국내 및 해외 주식의 실시간 시세와 과거 데이터를 조회합니다.</div>', unsafe_allow_html=True)

# 사이드바 또는 상단 입력 영역
with st.sidebar:
    st.header("⚙️ 검색 설정")
    
    ticker_input = st.text_input(
        "종목 코드 (Ticker)",
        value="005930.KS",
        help="한국 주식은 .KS(코스피) 또는 .KQ(코스닥), 미국 주식은 심볼(예: AAPL, TSLA, NVDA)을 입력하세요."
    ).strip().upper()

    period_options = {
        "1개월": "1mo",
        "3개월": "3mo",
        "6개월": "6mo",
        "1년": "1y"
    }

    selected_period_label = st.selectbox(
        "조회 기간 선택",
        options=list(period_options.keys()),
        index=0
    )
    period_value = period_options[selected_period_label]

    search_button = st.button("🔍 데이터 조회", type="primary", use_container_width=True)

# 세션 상태로 이전 조회 결과 유지 (페이지 리렌더링 시에도 유지)
if "ticker" not in st.session_state:
    st.session_state.ticker = "005930.KS"
if "period_label" not in st.session_state:
    st.session_state.period_label = "1개월"
if "has_searched" not in st.session_state:
    st.session_state.has_searched = False

if search_button:
    st.session_state.ticker = ticker_input
    st.session_state.period_label = selected_period_label
    st.session_state.has_searched = True

# 조회 실행 로직
if st.session_state.has_searched:
    ticker = st.session_state.ticker
    selected_label = st.session_state.period_label
    period = period_options[selected_label]

    with st.spinner(f"[{ticker}] 데이터를 불러오는 중..."):
        try:
            stock = yf.Ticker(ticker)
            
            # 이동평균선(20일, 60일) 계산을 위해 넉넉한 기간(2년) 데이터를 로드
            df_full = stock.history(period="2y")
            if df_full.empty:
                df_full = stock.history(period=period)

            if df_full.empty:
                st.error(f"'{ticker}'에 해당하는 주식 데이터를 찾을 수 없습니다. 올바른 종목 코드인지 확인해 주세요.")
            else:
                # 20일, 60일 이동평균선 사전 계산
                df_full["MA20"] = df_full["Close"].rolling(window=20).mean()
                df_full["MA60"] = df_full["Close"].rolling(window=60).mean()

                # 사용자가 선택한 기간에 맞추어 슬라이싱
                offset_map = {
                    "1개월": pd.DateOffset(months=1),
                    "3개월": pd.DateOffset(months=3),
                    "6개월": pd.DateOffset(months=6),
                    "1년": pd.DateOffset(years=1)
                }
                cutoff_date = df_full.index[-1] - offset_map.get(selected_label, pd.DateOffset(months=1))
                df = df_full.loc[df_full.index >= cutoff_date].copy()

                # 1. 완료 메시지
                st.success(f"'{ticker}' 주식 데이터 조회가 완료되었습니다! (조회 기간: {selected_label})")

                # 정보 추출
                info = stock.info
                company_name = info.get("shortName") or info.get("longName") or ticker
                currency = info.get("currency", "KRW" if ticker.endswith((".KS", ".KQ")) else "USD")
                currency_symbol = "원" if currency == "KRW" else ("$" if currency == "USD" else f" {currency}")

                current_price = info.get("currentPrice") or info.get("regularMarketPrice")
                prev_close = info.get("previousClose") or info.get("regularMarketPreviousClose")

                # fallback: history 데이터 기준
                if current_price is None and len(df) >= 1:
                    current_price = df["Close"].iloc[-1]
                if prev_close is None and len(df) >= 2:
                    prev_close = df["Close"].iloc[-2]

                # 등락 및 등락률 계산
                price_delta_str = None
                if current_price is not None and prev_close is not None and prev_close != 0:
                    delta = current_price - prev_close
                    delta_pct = (delta / prev_close) * 100
                    if currency == "KRW":
                        price_delta_str = f"{delta:+,.0f}{currency_symbol} ({delta_pct:+.2f}%)"
                    else:
                        price_delta_str = f"{delta:+.2f}{currency_symbol} ({delta_pct:+.2f}%)"

                # 2. 요약 카드 표시 (회사명, 현재가, 전일 대비 등락률)
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric(label="회사명", value=company_name)
                with col2:
                    if current_price is not None:
                        val_str = f"{current_price:,.0f}{currency_symbol}" if currency == "KRW" else f"{current_price:,.2f}{currency_symbol}"
                        st.metric(label="현재가", value=val_str, delta=price_delta_str)
                    else:
                        st.metric(label="현재가", value="정보 없음")
                with col3:
                    st.metric(label="전일 대비 등락률", value=price_delta_str if price_delta_str else "계산 불가")

                st.divider()

                # 이동평균선 표시 체크박스
                st.markdown("##### 📌 보조지표 설정 (이동평균선)")
                col_ma1, col_ma2, _ = st.columns([1, 1, 2])
                with col_ma1:
                    show_ma20 = st.checkbox("20일 이동평균선 (주황색)", value=True)
                with col_ma2:
                    show_ma60 = st.checkbox("60일 이동평균선 (초록색)", value=True)

                # 3. 주가 차트 (탭 분리: 선 차트 & 캔들스틱 차트)
                price_format_str = ":,.0f" if currency == "KRW" else ":,.2f"

                tab1, tab2 = st.tabs(["선 차트", "캔들스틱 차트"])

                with tab1:
                    fig_line = go.Figure()
                    fig_line.add_trace(go.Scatter(
                        x=df.index,
                        y=df["Close"],
                        mode="lines",
                        name="종가",
                        line=dict(color="#2962FF", width=2.5),
                        hovertemplate="<b>종가</b>: %{y" + price_format_str + "}" + currency_symbol + "<extra></extra>"
                    ))

                    # 20일 이평선 (주황색)
                    if show_ma20 and "MA20" in df.columns:
                        fig_line.add_trace(go.Scatter(
                            x=df.index,
                            y=df["MA20"],
                            mode="lines",
                            name="20일 이평선",
                            line=dict(color="#FF9800", width=1.8),
                            hovertemplate="<b>20일 이평선</b>: %{y" + price_format_str + "}" + currency_symbol + "<extra></extra>"
                        ))

                    # 60일 이평선 (초록색)
                    if show_ma60 and "MA60" in df.columns:
                        fig_line.add_trace(go.Scatter(
                            x=df.index,
                            y=df["MA60"],
                            mode="lines",
                            name="60일 이평선",
                            line=dict(color="#2E7D32", width=1.8),
                            hovertemplate="<b>60일 이평선</b>: %{y" + price_format_str + "}" + currency_symbol + "<extra></extra>"
                        ))

                    fig_line.update_layout(
                        title=dict(
                            text=f"{company_name} 주가 추이",
                            font=dict(size=20)
                        ),
                        xaxis=dict(
                            title="날짜",
                            showgrid=True
                        ),
                        yaxis=dict(
                            title=f"가격 ({currency_symbol})",
                            showgrid=True
                        ),
                        hovermode="x unified",
                        height=520,
                        margin=dict(l=40, r=40, t=60, b=40),
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                    )

                    st.plotly_chart(fig_line, use_container_width=True)

                with tab2:
                    # 상단: 캔들스틱 (70%), 하단: 거래량 막대 (30%), x축(날짜) 공유 및 상호 연동
                    fig_candle = make_subplots(
                        rows=2, cols=1,
                        shared_xaxes=True,
                        vertical_spacing=0.04,
                        subplot_titles=(None, "거래량"),
                        row_heights=[0.7, 0.3]
                    )

                    # 1. 캔들스틱 (상단 서브플롯)
                    fig_candle.add_trace(
                        go.Candlestick(
                            x=df.index,
                            open=df["Open"],
                            high=df["High"],
                            low=df["Low"],
                            close=df["Close"],
                            name="주가",
                            increasing_line_color="#2962FF",   # 상승: 파란색
                            decreasing_line_color="#E53935",   # 하락: 빨간색
                        ),
                        row=1, col=1
                    )

                    # 20일 이평선 (상단 서브플롯: 주황색)
                    if show_ma20 and "MA20" in df.columns:
                        fig_candle.add_trace(
                            go.Scatter(
                                x=df.index,
                                y=df["MA20"],
                                mode="lines",
                                name="20일 이평선",
                                line=dict(color="#FF9800", width=1.8),
                                hovertemplate="<b>20일 이평선</b>: %{y" + price_format_str + "}" + currency_symbol + "<extra></extra>"
                            ),
                            row=1, col=1
                        )

                    # 60일 이평선 (상단 서브플롯: 초록색)
                    if show_ma60 and "MA60" in df.columns:
                        fig_candle.add_trace(
                            go.Scatter(
                                x=df.index,
                                y=df["MA60"],
                                mode="lines",
                                name="60일 이평선",
                                line=dict(color="#2E7D32", width=1.8),
                                hovertemplate="<b>60일 이평선</b>: %{y" + price_format_str + "}" + currency_symbol + "<extra></extra>"
                            ),
                            row=1, col=1
                        )

                    # 2. 거래량 막대 색상 계산 (거래량이 평균 이상인 날 강조)
                    avg_volume = df["Volume"].mean()
                    volume_colors = []
                    for close, open_p, vol in zip(df["Close"], df["Open"], df["Volume"]):
                        is_up = close >= open_p
                        is_high_vol = vol >= avg_volume
                        if is_up:
                            volume_colors.append("#1565C0" if is_high_vol else "#90CAF9")  # 상승: 고거래량(진한 파랑) / 일반(연한 파랑)
                        else:
                            volume_colors.append("#C62828" if is_high_vol else "#EF9A9A")  # 하락: 고거래량(진한 빨강) / 일반(연한 빨강)

                    # 3. 거래량 막대 그래프 (하단 서브플롯)
                    fig_candle.add_trace(
                        go.Bar(
                            x=df.index,
                            y=df["Volume"],
                            name="거래량",
                            showlegend=False,
                            marker=dict(color=volume_colors),
                            hovertemplate="<b>날짜</b>: %{x|%Y-%m-%d}<br><b>거래량</b>: %{y:,}주<extra></extra>"
                        ),
                        row=2, col=1
                    )

                    fig_candle.update_layout(
                        title=dict(
                            text=f"{company_name} 캔들스틱 및 거래량 추이",
                            font=dict(size=20)
                        ),
                        yaxis=dict(
                            title=f"가격 ({currency_symbol})",
                            showgrid=True
                        ),
                        yaxis2=dict(
                            title="거래량",
                            showgrid=True
                        ),
                        xaxis2=dict(
                            title="날짜",
                            showgrid=True
                        ),
                        xaxis_rangeslider_visible=False,
                        hovermode="x unified",
                        height=620,
                        margin=dict(l=40, r=40, t=60, b=40),
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                    )

                    st.plotly_chart(fig_candle, use_container_width=True)
                    st.caption("💡 거래량이 기간 평균 거래량 이상인 날은 **진한 색상(파랑/빨강)**으로 강조되어 표시됩니다.")



                st.divider()


                # 4. 역사적 데이터 테이블
                st.subheader(f"📊 역사적 데이터 테이블 ({selected_label})")

                
                # 테이블 보기 편하게 포맷팅
                df_display = df.copy()
                df_display.index = df_display.index.strftime('%Y-%m-%d')
                df_display.index.name = "날짜"

                # 최신 날짜가 맨 위에 오도록 역순 정렬
                df_display = df_display.sort_index(ascending=False)

                # 숫자 포맷 적용
                format_dict = {
                    "Open": "{:,.2f}" if currency != "KRW" else "{:,.0f}",
                    "High": "{:,.2f}" if currency != "KRW" else "{:,.0f}",
                    "Low": "{:,.2f}" if currency != "KRW" else "{:,.0f}",
                    "Close": "{:,.2f}" if currency != "KRW" else "{:,.0f}",
                    "Volume": "{:,}",
                    "Dividends": "{:.2f}",
                    "Stock Splits": "{:.2f}"
                }
                if "MA20" in df_display.columns:
                    format_dict["MA20"] = "{:,.2f}" if currency != "KRW" else "{:,.0f}"
                if "MA60" in df_display.columns:
                    format_dict["MA60"] = "{:,.2f}" if currency != "KRW" else "{:,.0f}"

                st.dataframe(
                    df_display.style.format(format_dict, na_rep="-"),
                    use_container_width=True,
                    height=400
                )


        except Exception as e:
            st.error(f"데이터를 조회하는 중 오류가 발생했습니다: {str(e)}")
else:
    # 기본 초기 화면 안내
    st.info("👈 사이드바에서 종목 코드와 기간을 선택한 후 **'데이터 조회'** 버튼을 클릭하세요.")
