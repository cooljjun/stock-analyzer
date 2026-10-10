# 📈 Stock Analyzer (주식 데이터 분석기)

Python, **Streamlit**, **yfinance**, **Plotly**를 활용하여 국내외 주식 시세 데이터 및 과거 주가 추이를 실시간으로 조회하고 시각화하는 웹 애플리케이션입니다.

---

## ✨ 주요 기능

1. **국내 및 해외 주식 검색**
   - 한국 주식 (예: 삼성전자 `005930.KS`, SK하이닉스 `000660.KS`, 카카오 `035720.KQ` 등)
   - 미국 주식 (예: 애플 `AAPL`, 테슬라 `TSLA`, 엔비디아 `NVDA` 등)
   - 통화 단위(원/$) 및 숫자 포맷팅 자동 반영

2. **다양한 기간별 조회 지원**
   - `1개월`, `3개월`, `6개월`, `1년` 단위 데이터 조회

3. **핵심 주식 요약 정보 카드**
   - 회사명, 현재가, 전일 대비 등락 금액 및 등락률(% 단위) 제공

4. **인터랙티브 대시보드 차트 (Plotly)**
   - **📈 선 차트 탭**: 종가 기준의 깔끔한 라인 그래프
   - **🕯️ 캔들스틱 & 거래량 탭**:
     - 시가/고가/저가/종가 반영 캔들스틱 (상승: **파란색**, 하락: **빨간색**)
     - 상단 캔들스틱과 하단 거래량 그래프간 **동일 x축(날짜) 줌/스크롤 및 호버 연동**
     - 기간 평균 거래량 이상 발생일 **진한 색상 하이라이트**

5. **이동평균선 보조지표**
   - **20일 이동평균선** (주황색 `#FF9800`) 및 **60일 이동평균선** (초록색 `#2E7D32`) 지원
   - 체크박스를 통한 실시간 표시/숨김 토글
   - 짧은 기간(1개월 등) 조회 시에도 끊김 없는 연속성 제공

6. **역사적 데이터 상세 테이블**
   - 일자별 주가(시가/고가/저가/종가/이평선/거래량) 데이터 포맷팅 및 역순 정렬 제공

---

## 🛠️ 기술 스택 (Tech Stack)

- **Language**: Python 3.8+
- **Web Framework**: Streamlit
- **Data Source**: yfinance
- **Data Analysis**: Pandas
- **Data Visualization**: Plotly Express & Graph Objects

---

## 🚀 시작하기 (Getting Started)

### 1. 저장소 클론 (Clone Repository)
```bash
git clone https://github.com/<your-username>/stock_analyzer.git
cd stock_analyzer
```

### 2. 가상환경 생성 및 활성화
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. 필요 패키지 설치
```bash
pip install -r requirements.txt
```

### 4. 앱 실행
```bash
streamlit run app.py
```

브라우저에서 `http://localhost:8501` 주소로 접속하면 앱을 이용할 수 있습니다.

---

## 📁 프로젝트 구조 (Directory Structure)

```text
stock_analyzer/
├── app.py              # Streamlit 메인 애플리케이션
├── test_samsung.py     # yfinance API 데이터 수집 테스트 스크립트
├── requirements.txt    # 의존성 패키지 목록
├── .gitignore          # Git 제외 파일 설정
└── README.md           # 프로젝트 안내 문서
```
