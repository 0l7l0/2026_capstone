from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import numpy as np
import textwrap
from PIL import Image

def load_uniform_canvas_image(
    path,
    canvas_size=(900, 520)
):

    img = Image.open(path).convert("RGB")

    img.thumbnail(canvas_size)

    canvas = Image.new(
        "RGB",
        canvas_size,
        (255, 255, 255)
    )

    x = (canvas_size[0] - img.size[0]) // 2
    y = (canvas_size[1] - img.size[1]) // 2

    canvas.paste(img, (x, y))

    return canvas

ROOT = Path(__file__).resolve().parents[1]

EVENT_LABEL = {
    "hormuz_crisis": "호르무즈 위기",
    "soleimani_assassination": "솔레이마니 암살",
    "russia_ukraine_war": "러-우 전쟁",
    "israel_hamas_war": "이스라엘-하마스",
    "israel_iran": "이스라엘-이란 충돌",
    "us_israel_iran": "미-이스라엘-이란",
}

EVENT_DATE = {
    "hormuz_crisis": "2019-06-13",
    "soleimani_assassination": "2020-01-03",
    "russia_ukraine_war": "2022-02-24",
    "israel_hamas_war": "2023-10-07",
    "israel_iran": "2024-04-14",
    "us_israel_iran": "2026-02-28",
}

ASSET_COLORS = {
    "BTC": "#F7931A",
    "Gold": "#FFD700",
    "SP500": "#1976D2",
    "NASDAQ": "#7B1FA2",
    "TLT": "#388E3C",
    "DXY": "#E64A19",
}

VERDICT_COLOR = {
    "Safe Haven": "#2E7D32",
    "Weak Haven": "#558B2F",
    "Diversifier": "#F9A825",
    "Risky Asset": "#C62828",
}


@st.cache_data
def load_csv(path: str) -> pd.DataFrame | None:
    file_path = ROOT / path
    if not file_path.exists():
        return None
    return pd.read_csv(file_path)


@st.cache_data
def load_image(path: str) -> str | None:
    file_path = ROOT / path
    if not file_path.exists():
        return None
    return str(file_path)


def color_verdict(value: str) -> str:
    color = VERDICT_COLOR.get(value, "#888")
    return f"background-color: {color}; color: white; font-weight: bold;"


# ────────────────────────────────────────────────────────────
# 1. 통합 판정
# ────────────────────────────────────────────────────────────
def render_integrated_judgment() -> None:
    st.markdown("""
        <style>
        .hero-container { padding: 30px 0; margin-bottom: 10px; }
        .hero-subtitle { font-size: 28px; font-weight: 700; color: #555; margin-bottom: 20px; letter-spacing: -0.5px; }
        .hero-title { font-size: 50px; font-weight: 900; line-height: 1.2; color: #111827; letter-spacing: -2px; margin-bottom: 28px; }
        .hero-desc { font-size: 20px; color: #6B7280; line-height: 1.7; font-weight: 500; }
        
        .summary-card { border-radius: 20px; padding: 22px 24px; background: white; border: 1.5px solid; min-height: 130px; }
        .summary-title { font-size: 14px; font-weight: 600; margin-bottom: 14px; opacity: 0.9; }
        .summary-value { font-size: 32px; font-weight: 800; margin-bottom: 8px; line-height: 1.1; }
        .summary-desc { font-size: 14px; opacity: 0.85; }

        /* 타임라인 스타일 */
        .timeline-wrapper { position: relative; width: 100%; height: 260px; margin: 40px 0; }
        .timeline-line { position: absolute; top: 140px; left: 4%; width: 92%; height: 4px; background: #D1D5DB; border-radius: 999px; }
        .timeline-node { position: absolute; top: 132px; width: 18px; height: 18px; border-radius: 999px; background: #2563EB; border: 3px solid white; box-shadow: 0 0 0 2px #2563EB44; }
        .timeline-card { position: absolute; width: 150px; padding: 12px; border-radius: 12px; background: white; border: 1.5px solid #E5E7EB; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }
        .timeline-date { font-size: 11px; color: #6B7280; font-weight: 600; }
        .timeline-title { font-size: 14px; font-weight: 700; color: #111827; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class="hero-container">
            <div class="hero-subtitle">비트코인은 안전자산인가?</div>
            <div class="hero-title">BTC는 전쟁 자체보다<br>시장 심리에 더 민감하게 반응했습니다.</div>
            <div class="hero-desc">2019–2026 주요 지정학 이벤트 기반<br>Safe Haven Hypothesis Dashboard</div>
        </div>
    """, unsafe_allow_html=True)

    st.divider()

    final = load_csv("dashboard/result_csv_png/final_judgment.csv")
    if final is None:
        st.error("🚨 데이터를 불러올 수 없습니다. 경로를 확인해주세요.")
        st.stop() # 이후 코드 실행 방지

    c1, c2, c3, c4 = st.columns(4)
    
    cards = [
        {"t": "BTC 상태 판정", "v": "Risk Asset", "d": "위험자산 성향 강함", "c": "#FCA5A5", "tc": "#DC2626"},
        {"t": "핵심 영향 변수", "v": "Fear & Greed", "d": "반복적 유의 변수", "c": "#C4B5FD", "tc": "#7C3AED"},
        {"t": "GPR 지정 효과", "v": "비유의", "d": "지정학 영향 제한적", "c": "#86EFAC", "tc": "#059669"},
        {"t": "최적 변동성 모델", "v": "Model3", "d": "VIX + Fear&Greed", "c": "#FCD34D", "tc": "#D97706"}
    ]

    for i, col in enumerate([c1, c2, c3, c4]):
        card = cards[i]
        col.markdown(f"""
            <div class="summary-card" style="border-color:{card['c']}; color:{card['tc']};">
                <div class="summary-title">{card['t']}</div>
                <div class="summary-value">{card['v']}</div>
                <div class="summary-desc">{card['d']}</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.divider()

    st.subheader("지정학 이벤트 타임라인")
    events = [
        {"date": "2019-06-13", "title": "호르무즈 위기", "left": "7%"},
        {"date": "2020-01-03", "title": "솔레이마니 암살", "left": "28%"},
        {"date": "2022-02-24", "title": "러-우 전쟁", "left": "49%"},
        {"date": "2023-10-07", "title": "이스라엘-하마스", "left": "68%"},
        {"date": "2024-04-01", "title": "이스라엘-이란", "left": "86%"}
    ]

    timeline_html = '<div class="timeline-wrapper"><div class="timeline-line"></div>'
    
    for ev in events:
        item_html = textwrap.dedent(f"""
            <div class="timeline-card" style="left:{ev['left']}; top:10px;">
                <div class="timeline-date">{ev['date']}</div>
                <div class="timeline-title">{ev['title']}</div>
            </div>
            <div class="timeline-node" style="left:{ev['left']};"></div>
        """)
        timeline_html += item_html
        
    timeline_html += "</div>"
    
    st.markdown(timeline_html, unsafe_allow_html=True)
    # =========================================================
    # HERO CHART
    # =========================================================

    st.subheader("BTC vs Gold vs SP500 — 누적 로그 수익률")

    returns = load_csv(
        "DataPipeline/processed_data/market_returns.csv"
    )

    if returns is None:

        st.error("market_returns.csv 경로 확인 필요")

    else:

        returns["date"] = pd.to_datetime(
            returns["date"]
        )

        asset_cols = ["BTC", "Gold", "SP500"]

        for col in asset_cols:

            returns[f"{col}_log"] = np.log1p(
                returns[col]
            )

            returns[f"{col}_cum"] = returns[
                f"{col}_log"
            ].cumsum()

        fig = go.Figure()

        colors = {
            "BTC": "#F7931A",
            "Gold": "#FFD700",
            "SP500": "#1E88E5"
        }

        for asset in asset_cols:

            fig.add_trace(
                go.Scatter(
                    x=returns["date"],
                    y=returns[f"{asset}_cum"],
                    mode="lines",
                    name=asset,
                    line=dict(
                        width=3,
                        color=colors[asset]
                    ),
                    hovertemplate=
                    "<b>%{fullData.name}</b><br>" +
                    "Date: %{x}<br>" +
                    "Cumulative Log Return: %{y:.3f}<extra></extra>"
                )
            )

        for key, date in EVENT_DATE.items():

            fig.add_vline(
                x=pd.to_datetime(date),
                line_dash="dot",
                line_color="red",
                opacity=0.7
            )

            fig.add_annotation(
                x=pd.to_datetime(date),
                y=returns["BTC_cum"].max(),
                text=EVENT_LABEL[key],
                showarrow=False,
                textangle=-90,
                font=dict(
                    size=10,
                    color="red"
                ),
                yshift=10
            )

        fig.update_layout(

            template="plotly_dark",

            height=650,

            hovermode="x unified",

            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),

            xaxis_title="Date",

            yaxis_title="Cumulative Log Return",

            margin=dict(
                l=20,
                r=20,
                t=30,
                b=20
            )
        )

        st.plotly_chart(
            fig,
            width="stretch"
        )

    st.divider()

    # =========================================================
    # EVENT MATRIX (EMOJI STYLE)
    # =========================================================

    st.subheader("이벤트별 안전자산 판정 매트릭스")

    verdict_color = {
        "Safe Haven": "#16A34A",
        "Weak Haven": "#D97706",
        "Risky Asset": "#DC2626"
    }

    def icon(v):
        return "🛡️" if v else "❌"

    matrix_df = pd.DataFrame({
        "이벤트": final["event_label"],
        "C1 이벤트\n스터디":
            final["C1_event_study_pass"].apply(icon),
        "C2 분위수\n회귀":
            final["C2_quantile_reg_pass"].apply(icon),
        "C3 GARCH":
            final["C3_garch_pass"].apply(icon),
        "최종 판정":
            final["verdict"]
    })

    styled = matrix_df.style.map(
        lambda x:
        f"""
        background-color:
        {verdict_color.get(x, '#333333')};
        color:white;
        font-weight:bold;
        border-radius:8px;
        """,
        subset=["최종 판정"]
    )

    st.dataframe(
        styled,
        width="stretch",
        hide_index=True
    )

    st.caption(
        """
        🛡️ : Safe Haven 조건 충족 방향  
        ❌ : 위험자산 성향 방향
        """
    )

    st.divider()

    # =========================================================
    # KEY FINDINGS
    # =========================================================

    st.subheader("핵심 결과")

    k1, k2, k3 = st.columns(3)

    k1.metric(
        "Quantile Pass",
        "1 / 6"
    )

    k2.metric(
        "SP500-BTC Tail Corr.",
        "+2.2×"
    )

    k3.metric(
        "Fear & Greed γ",
        "+0.157"
    )

    st.info(
        """
        분석 기간(2019–2026) 동안 BTC는  
        주요 지정학 이벤트에서 Gold와 다른 움직임을 보였으며,  
        Safe Haven보다 Risk Asset 특성에 가까운 것으로 나타났다.

        • 극단 하락 분위수에서 BTC-SP500 동조화 강화 확인  
        • GPR 변수는 반복적으로 유의성이 확인되지 않았으며,  
          Fear&Greed 변수는 GARCH·EGARCH 모델에서 반복적으로 유의하게 나타남
        """
    )

    # =========================================================
    # FINAL REPORT
    # =========================================================

    report = ROOT / "MD" / "final_report.md"

    if report.exists():

        st.divider()

        with st.expander(
            "final_report.md (전체)",
            expanded=False
        ):

            st.markdown(
                report.read_text(
                    encoding="utf-8"
                )
            )

# ────────────────────────────────────────────────────────────
# 2. GPR 데이터파이프라인
# ────────────────────────────────────────────────────────────
def render_gpr_pipeline() -> None:

    st.header("GPR 데이터파이프라인 — 자체 지정학 리스크 지수 구축")

    st.markdown(
        """
        GDELT GKG(BigQuery) 기반 글로벌 뉴스 데이터를 수집하고,  
        자체 지정학 리스크 지수(Custom GPR)를 구축하여  
        공식 GPR(Caldara & Iacoviello, 2022)과 비교 검증합니다.
        """
    )

    st.divider()

    # =========================================================
    # CHAPTER TABS
    # =========================================================

    tab1, tab2, tab3 = st.tabs(
        [
            "1️⃣ 데이터 수집 · 정제",
            "2️⃣ Custom GPR 설계",
            "3️⃣  금융시장 통합 데이터 구축",
        ]
    )

    # =========================================================
    # TAB 1
    # =========================================================

    with tab1:

    # =========================================================
    # HEADER
    # =========================================================

        st.subheader("데이터 수집 · 정제")

        st.markdown(
            """
            GDELT GKG(BigQuery) 기반 글로벌 뉴스 데이터를 수집하고,  
            이벤트 단위로 정제 및 전처리를 수행하여  
            Custom GPR 생성에 활용하였다.
            """
        )

        st.divider()

        # =========================================================
        # A. 뉴스 기사 수 분석
        # =========================================================

        st.markdown("### A. 뉴스 기사 수 분석 (Raw Data Overview)")

        col1, col2 = st.columns([1, 1.4])

        with col1:

            st.metric(
                label="수집된 뉴스 기사 수",
                value="약 734만 건"
            )

            st.metric(
                label="분석 이벤트 수",
                value="6개"
            )

            st.metric(
                label="분석 기간",
                value="2019–2026"
            )

            st.info(
                """
                • GDELT GKG(BigQuery) 기반 글로벌 뉴스 데이터를
                이벤트 단위로 수집하였다.
                • 러-우 전쟁 이벤트에서 가장 큰 뉴스 기사량 증가가 확인되었으며,  
                지정학 이벤트 직후 글로벌 뉴스 보도가 집중되는 패턴을 보였다.
                """
            )

        with col2:

            st.markdown("<br>", unsafe_allow_html=True)

            img = load_image(
                "FIGURES/01-2_russia_ukraine_article_count.png"
            )

            if img:

                st.image(
                    img,
                    caption="러-우 전쟁 기간 기사량 급증",
                    width=500
                )

        st.divider()

        # =========================================================
        # B. 이벤트별 기사량 변화
        # =========================================================

        st.markdown("### B. 이벤트별 기사량 변화 (Event Distribution)")

        st.markdown(
            """
            이벤트별 기사량 분포를 비교하여  
            지정학 이벤트 발생 시 뉴스 보도량 증가 패턴을 확인하였다.
            """
        )

        imgs_raw = [

            (
                "FIGURES/01-1_hormuz_article_count.png",
                "호르무즈 위기"
            ),

            (
                "FIGURES/01-2_soleimani_article_count.png",
                "솔레이마니 암살"
            ),

            (
                "FIGURES/01-3_russia_ukraine_article_count.png",
                "러시아-우크라이나 전쟁"
            ),

            (
                "FIGURES/01-4_israel_hamas_article_count.png",
                "이스라엘-하마스"
            ),

            (
                "FIGURES/01-5_israel_iran_article_count.png",
                "이스라엘-이란"
            ),

            (
                "FIGURES/01-6_us_israel_iran_article_count.png",
                "미국-이스라엘-이란"
            ),

        ]

        # =========================================================
        # 첫 번째 줄
        # =========================================================

        col1, col2 = st.columns([0.9, 0.9])

        with col1:

            img = load_uniform_canvas_image(
                imgs_raw[0][0]
            )

            st.image(
                img,
                width=650
            )

            st.caption(imgs_raw[0][1])

        with col2:

            img = load_uniform_canvas_image(
                imgs_raw[1][0]
            )

            st.image(
                img,
                width=650
            )

            st.caption(imgs_raw[1][1])

        # =========================================================
        # 두 번째 줄
        # =========================================================

        col3, col4 = st.columns([0.9, 0.9])

        with col3:

            img = load_uniform_canvas_image(
                imgs_raw[2][0]
            )

            st.image(
                img,
                width=650
            )

            st.caption(imgs_raw[2][1])

        with col4:

            img = load_uniform_canvas_image(
                imgs_raw[3][0]
            )

            st.image(
                img,
                width=650
            )

            st.caption(imgs_raw[3][1])

        # =========================================================
        # 세 번째 줄
        # =========================================================

        col5, col6 = st.columns([0.9, 0.9])

        with col5:

            img = load_uniform_canvas_image(
                imgs_raw[4][0]
            )

            st.image(
                img,
                width=650
            )

            st.caption(imgs_raw[4][1])

        with col6:

            img = load_uniform_canvas_image(
                imgs_raw[5][0]
            )

            st.image(
                img,
                width=650
            )

            st.caption(imgs_raw[5][1])

        st.divider()

        # =========================================================
        # C. 데이터 정제 및 필터링
        # =========================================================

        st.markdown("### C. 데이터 정제 및 필터링 (Cleaning Process)")

        st.markdown(
            """
            이벤트 기반 뉴스 데이터의 신뢰성을 확보하기 위해  
            기초 수준의 데이터 정제 및 유효성 검토를 수행하였다.
            """
        )

        col1, col2 = st.columns([1, 1.5])

        # =========================================================
        # LEFT
        # =========================================================

        with col1:

            st.markdown("#### 전처리 절차")

            st.info(
                """
                Raw Query  
                ↓  
                URL 기준 중복 제거  
                ↓  
                tone 결측치 제거  
                ↓  
                이상값 제거 (|tone_score| > 20)  
                ↓  
                GEO_THEMES 기반 지정학 기사 필터링  
                ↓  
                Daily Aggregation  
                ↓  
                최소 기사 수 조건 적용 (일 기사 수 5건 이상)
                """
            )

        # =========================================================
        # RIGHT
        # =========================================================

        with col2:

            st.markdown("#### Before vs After")

            img = load_image(
                "FIGURES/02-1_hormuz_preprocessed.png"
            )

            if img:

                st.image(
                    img,
                    caption="전처리 이후 기사량 및 tone 분포",
                    width="stretch"
                )

            st.success(
                """
                • 전처리 이후에도 전체 기사량 구조는 크게 유지되었으며,  
                • 이벤트 무관 기사 및 이상값이 제거된 상태에서 이벤트 발생 시 기사량 증가 패턴이 안정적으로 확인되었다.
                """
            )

        st.divider()

        # =========================================================
        # FINAL SUMMARY
        # =========================================================

        st.subheader("데이터 수집 · 정제 핵심")

        st.success(
            """
                ✔ GDELT 기반 글로벌 뉴스 데이터를 이벤트 단위로 수집  
            ✔ 키워드 및 테마 기반 노이즈 제거 수행  
            ✔ 이벤트 직후 뉴스 기사량 급증 패턴 확인  

            """
        )

    # =========================================================
    # TAB 2
    # =========================================================

    with tab2:

        # =========================================================
        # HEADER
        # =========================================================

        st.subheader("Custom GPR 설계 및 검증")

        st.markdown(
            """
            본 연구는 뉴스 감성(tone)과 기사량(volume)을 조합하여  
            F1~F5 형태의 Custom GPR 공식을 설계하고 비교하였다.  

            이후 공식 GPR(Caldara & Iacoviello, 2022)과의 비교를 통해  
            최종적으로 F3 공식을 대표 지표로 선정하였다.
            """
        )

        st.divider()

        # =========================================================
        # A. F1~F5 공식 비교
        # =========================================================

        st.markdown("### A. F1~F5 공식 비교")

        st.markdown(
            """
            뉴스 감성(tone)과 기사량(volume)의 조합 방식을 다르게 설정하여  
            총 5개의 Custom GPR 후보 공식을 설계하였다.
            """
        )

        formula_df = pd.DataFrame(
            {
                "모델": ["F1", "F2", "F3", "F4", "F5"],
                "설계 방식": [
                    "Tone Mean",
                    "Polarity Weighted",
                    "Tone × log(N)",
                    "Negative Ratio",
                    "28D EWMA"
                ],
                "설명": [
                    "평균 tone 기반 감성 지표",
                    "polarity 가중 평균",
                    "tone과 상대 기사량 결합",
                    "부정 기사 비율 기반",
                    "F2 smoothing 적용"
                ]
            }
        )

        st.dataframe(
            formula_df,
            width="stretch",
            hide_index=True
        )

        st.markdown(
            """
            F3는 기사량 급증 구간의 과도한 스케일 문제를 완화하기 위해  
            `log(N)` 구조를 적용한 공식이다.
            """
        )

        st.divider()

        # =========================================================
        # B. 상관관계 비교
        # =========================================================

        st.markdown("### B. 공식 GPR과의 상관관계 비교")

        st.markdown(
            """
            F1~F5 Custom GPR과 공식 GPR 간 상관관계를 비교하여  
            가장 안정적으로 지정학 리스크를 반영하는 공식을 탐색하였다.
            """
        )

        img = load_image("FIGURES/03_correlation_heatmap.png")

        if img:

            st.image(
                img,
                caption="공식 GPR vs Custom GPR 상관관계 히트맵",
                width="stretch"
            )

        st.markdown(
            """
            상관관계 비교 결과, F3가 공식 GPR과 가장 안정적인 방향성을 보이며  
            최종 대표 Custom GPR로 선정되었다.
            """
        )

        st.divider()

        # =========================================================
        # C. Tone × Volume 구조
        # =========================================================

        st.markdown("### C. Tone × Volume 구조")

        st.markdown(
            """
            Custom GPR(F3)은 뉴스 감성(tone)과  
            상대 기사량(volume shock)을 동시에 반영하도록 설계되었다.
            """
        )

        st.info(
            """
            F3 공식

            Custom GPR(F3)
            = - mean_tone × log(1 + N / N_mean)
            """
        )

        st.markdown(
            """
            tone은 뉴스의 부정적 감정 강도를 의미하며,  
            기사량(volume)은 지정학 이벤트에 대한 시장 관심도의 proxy 역할을 수행한다.

            특히 F3는 상대 기사량 증가분을 로그 스케일로 반영하여  
            극단적 기사량 급증에 따른 왜곡을 완화하도록 설계하였다.
            """
        )
        st.divider()

        # =========================================================
        # D. 시계열 비교
        # =========================================================

        st.markdown("### D. 시계열 비교")

        st.markdown(
            """
            이벤트 구간별 Custom GPR(F1~F5)의 시계열 흐름을 비교하여  
            각 공식이 지정학 이벤트를 어떻게 반영하는지 확인하였다.
            """
        )

        img = load_image("FIGURES/05_gpr_timeseries.png")

        if img:

            st.image(
                img,
                caption="Custom GPR(F1~F5) 시계열 비교",
                width="stretch"
            )

        st.success(
            """
            대부분의 이벤트 구간에서 F3는 극단적 스파이크 왜곡이 상대적으로 적었으며,  
            이벤트 발생 전후 반응 방향성을 비교적 일관되게 반영하였다.
            """
        )

        st.divider()

        # =========================================================
        # E. 이벤트 반응 비교
        # =========================================================

        st.markdown("### E. 이벤트 반응 비교")

        st.markdown(
            """
            공식 GPR과 Custom GPR(F3)의 이벤트 반응 흐름을 비교하여  
            실제 지정학 충격에 대한 반응 방향성을 검증하였다.
            """
        )

        img = load_image("FIGURES/07_event_window.png")

        if img:

            st.image(
                img,
                caption="공식 GPR vs Custom GPR(F3) 이벤트 반응 비교",
                width="stretch"
            )


        st.divider()

        # =========================================================
        # TAB 3
        # =========================================================

        with tab3:

            # =========================================================
            # HEADER
            # =========================================================

            st.subheader("금융시장 통합 데이터 구축")

            st.markdown(
                """
                Custom GPR과 금융시장 수익률 데이터를 병합하여  
                BTC 안전자산 분석을 위한 통합 master dataset을 구축하였다.
                """
            )
            
            st.divider()

            # =========================================================
            # A. 금융시장 데이터 수집
            # =========================================================

            st.markdown("### A. 금융시장 데이터 수집")

            st.markdown(
                """
                BTC, Gold, SP500 등 주요 금융시장 데이터를 수집하여  
                지정학 이벤트 기간 시장 반응을 비교할 수 있도록 구성하였다.
                """
            )

            market_df = pd.DataFrame(
                {
                    "자산": [
                        "Bitcoin",
                        "Gold",
                        "TLT",
                        "DXY",
                        "S&P500",
                        "NASDAQ"
                    ],
                    "Ticker": [
                        "BTC-USD",
                        "GC=F",
                        "TLT",
                        "DX-Y.NYB",
                        "^GSPC",
                        "^IXIC"
                    ],
                    "역할": [
                        "위험자산 검증 대상",
                        "전통 안전자산 benchmark",
                        "장기채 proxy",
                        "달러 강세 proxy",
                        "미국 주식시장 benchmark",
                        "기술주 시장 benchmark"
                    ]
                }
            )

            st.dataframe(
                market_df,
                width="stretch",
                hide_index=True
            )

            st.markdown(
                """
                금융시장 데이터는 Yahoo Finance(yfinance)를 통해 수집하였으며,  
                동일 거래일 기준으로 정렬하였다.
                """
            )

            st.divider()

            # =========================================================
            # B. 로그수익률 및 거래일 정렬
            # =========================================================

            st.markdown("### B. 로그수익률 생성 및 거래일 정렬")

            col1, col2 = st.columns([1.2, 1])

            with col1:

                st.markdown(
                    """
                    자산별 가격 데이터를 일별 로그수익률(daily log return) 형태로 변환하고,  
                    미국 거래일 기준으로 시계열을 정렬하였다.
                    """
                )

                st.info(
                    """
                    데이터 처리 절차

                    Raw Price  
                    ↓  
                    Log Return Calculation  
                    ↓  
                    Trading Day Alignment  
                    ↓  
                    Missing Value Handling  
                    ↓  
                    Final Return Dataset
                    """
                )

            with col2:

                st.markdown(
                    """
                    #### 거래일 보정

                    BTC는 24시간 거래되는 반면 전통 금융시장은 휴장일이 존재하므로,  
                    비거래일 동안 발생한 BTC 수익률을  
                    다음 거래일 기준으로 누적 정렬하였다.
                    """
                )

            st.divider()

            # =========================================================
            # C. GPR · 시장심리 변수 병합
            # =========================================================

            st.markdown("### C. GPR · 시장심리 변수 병합")

            st.markdown(
                """
                금융시장 수익률 데이터에  
                Custom GPR(F3), VIX, Fear & Greed Index를 병합하였다.
                """
            )

            col1, col2, col3 = st.columns(3)

            with col1:

                st.markdown(
                    """
                    <div style="
                        border:1px solid #E0E0E0;
                        border-radius:12px;
                        padding:18px;
                        background-color:white;
                    ">
                        <h4>📰 Custom GPR(F3)</h4>
                        <p>
                        뉴스 기반 지정학 리스크 지수
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with col2:

                st.markdown(
                    """
                    <div style="
                        border:1px solid #E0E0E0;
                        border-radius:12px;
                        padding:18px;
                        background-color:white;
                    ">
                        <h4>📉 VIX</h4>
                        <p>
                        시장 변동성 및 공포 지수
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with col3:

                st.markdown(
                    """
                    <div style="
                        border:1px solid #E0E0E0;
                        border-radius:12px;
                        padding:18px;
                        background-color:white;
                    ">
                        <h4>😨 Fear & Greed</h4>
                        <p>
                        투자 심리 기반 시장 불안 지표
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            st.markdown("#### 데이터 병합 구조")

            st.markdown(
                """
                ```text
                BTC / Gold / SP500 Returns
                            +
                Custom GPR(F3)
                            +
                    VIX / Fear&Greed
                            ↓
                    master_data.csv
                ```
                """
            )

            st.markdown(
                """
                날짜 기준 정렬 및 결측치 처리를 수행하였으며,  
                이벤트 메타데이터(event_name, event_date)를 함께 연결하였다.
                """
            )

            st.divider()

            # =========================================================
            # D. 최종 Master Dataset 구축
            # =========================================================

            st.markdown("### D. 최종 Master Dataset 구축")

            st.markdown(
                """
                최종적으로 금융시장 수익률, 지정학 리스크, 시장심리 변수를 통합한  
                분석용 master dataset을 구축하였다.
                """
            )

            master_path = ROOT / "DataPipeline" / "processed_data" / "final" / "master_data.csv"

            if master_path.exists():

                master_df = pd.read_csv(master_path)

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric(
                        "Rows",
                        f"{len(master_df):,}"
                    )

                with col2:
                    st.metric(
                        "Columns",
                        master_df.shape[1]
                    )

                with col3:
                    if "event_name" in master_df.columns:
                        st.metric(
                            "Events",
                            master_df["event_name"].nunique()
                        )

                with col4:
                    st.metric(
                        "Assets",
                        6
                    )

                st.markdown("#### master_data.csv Preview")

                st.dataframe(
                    master_df.head(10),
                    width="stretch",
                    hide_index=True
                )

            st.markdown(
                """
                생성된 master dataset은 이후  
                Event Study, Quantile Regression, GARCH 분석에 활용되었다.
                """
            )

            st.divider()

            # =========================================================
            # FINAL SUMMARY
            # =========================================================

            st.subheader("통합 데이터 구축 핵심")

            st.success(
                """
                ✔ 금융시장 수익률 데이터 수집 및 로그수익률 변환  
                ✔ BTC · Gold · SP500 등 자산별 거래일 정렬  
                ✔ Custom GPR(F3) · VIX · Fear & Greed 병합  
                ✔ Safe Haven 분석용 최종 master dataset 구축
                """
            )
            
# ────────────────────────────────────────────────────────────
# 3. EDA
# ────────────────────────────────────────────────────────────
def render_eda() -> None:

    st.header("EDA — 탐색적 데이터 분석")

    st.markdown(
        """
        지정학적 위기 상황에서  
        BTC·Gold·SP500 등 주요 자산의 가격 흐름·수익률 분포·상관관계 구조를 분석하였다.
        """
    )

    st.divider()

    # =========================================================
    # 1. OVERVIEW
    # =========================================================

    st.markdown("## A. 금융시장 가격 흐름")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "분석 자산",
            "6종"
        )

    with col2:
        st.metric(
            "거래일 수",
            "1,691일"
        )

    with col3:
        st.metric(
            "이벤트 수",
            "5개"
        )

    with col4:
        st.metric(
            "분석 기간",
            "2019–2026"
        )

    st.markdown(
        """
        BTC·Gold·TLT·SP500·NASDAQ·DXY 데이터를 기반으로  
        이벤트 전후 시장 반응 및 변동성 구조를 탐색적으로 분석하였다.
        """
    )

    st.divider()

    # =========================================================
    # 2. FINANCIAL MARKET DYNAMICS
    # =========================================================

    st.markdown("## B. 이벤트별 가격 반응")

    st.markdown(
        """
        전체 기간 자산 가격 흐름과  
        이벤트 구간별 가격 반응 패턴을 비교하였다.
        """
    )

    # ---------------------------------------------------------
    # 전체 기간 가격 추이
    # ---------------------------------------------------------

    img = load_image(
        "eda/result_csv_png/plot1_price_trend.png"
    )

    if img:

        st.image(
            img,
            caption="전체 기간 자산 가격 추이",
            width=900
        )

    st.markdown("")

    # ---------------------------------------------------------
    # 이벤트별 가격 반응
    # ---------------------------------------------------------

    img = load_image(
        "eda/result_csv_png/plot2_event_price.png"
    )

    if img:

        st.image(
            img,
            caption="이벤트 구간별 정규화 가격 흐름",
            width=950
        )

    st.markdown(
        """
        이벤트 발생 이후 BTC는 전통 안전자산 대비 높은 가격 변동성과  
        위험자산과 유사한 방향성을 부분적으로 보였다.
        """
    )

    st.divider()

    # =========================================================
    # 3. FINANCIAL DISTRIBUTION
    # =========================================================

    st.markdown("## C. 수익률 분포 및 변동성")

    st.markdown(
        """
        자산별 수익률 분포 및 변동성 구조를 통해  
        금융시장 특성과 fat-tail 현상을 분석하였다.
        """
    )

    # ---------------------------------------------------------
    # Returns Distribution
    # ---------------------------------------------------------

    img = load_image(
        "eda/result_csv_png/plot4_returns_dist.png"
    )

    if img:

        st.image(
            img,
            caption="자산별 수익률 분포 및 변동성 군집",
            width=1000
        )

    st.markdown("")

    # ---------------------------------------------------------
    # BTC High-Low
    # ---------------------------------------------------------

    img = load_image(
        "eda/result_csv_png/plot5_btc_highlow.png"
    )

    if img:

        st.image(
            img,
            caption="BTC 이벤트별 일별 변동폭",
            width=1050
        )

    st.markdown(
        """
        BTC는 Gold·SP500 대비 높은 첨도와 변동성을 보였으며,  
        이벤트 구간에서 급격한 변동폭 확대 현상이 관찰되었다.
        """
    )

    st.divider()

    # =========================================================
    # 4. CORRELATION STRUCTURE
    # =========================================================

    st.markdown("## D. 상관관계 구조 분석")

    st.markdown(
        """
        전체 기간 및 이벤트 구간에서  
        자산 간 상관관계 변화 구조를 분석하였다.
        """
    )

    # ---------------------------------------------------------
    # 전체 / 전쟁 전후 heatmap
    # ---------------------------------------------------------

    img = load_image(
        "eda/result_csv_png/plot6_corr_heatmap.png"
    )

    if img:

        st.image(
            img,
            caption="전체·전쟁 전·전쟁 중 상관관계 비교",
            width=900
        )

    st.markdown("")

    # ---------------------------------------------------------
    # 이벤트별 heatmap
    # ---------------------------------------------------------

    img = load_image(
        "eda/result_csv_png/plot7_event_heatmap.png"
    )

    if img:

        st.image(
            img,
            caption="이벤트별 ±60일 상관관계 히트맵",
            width=950
        )

    st.markdown("")

    # ---------------------------------------------------------
    # Rolling Correlation
    # ---------------------------------------------------------

    img = load_image(
        "eda/result_csv_png/plot8_rolling_corr.png"
    )

    if img:

        st.image(
            img,
            caption="BTC 30일 Rolling Correlation",
            width=1100
        )

    st.markdown(
        """
        일부 지정학 이벤트 구간에서 BTC와 SP500·NASDAQ의 상관관계가 상승하며  
        위험자산 동조화 경향이 부분적으로 나타났다.
        """
    )

    st.divider()
    # =========================================================
    # 5. VOLATILITY & STATISTICAL TEST
    # =========================================================

    st.markdown("## E. 변동성 및 통계 검정")

    st.markdown(
        """
        변동성 구조 및 시계열 특성을 검정하여  
        이후 GARCH 분석 적용 가능성을 확인하였다.
        """
    )

    col1, col2 = st.columns(2)

    with col1:

        img = load_image(
            "eda/result_csv_png/plot3_moving_average.png"
        )

        if img:

            st.image(
                img,
                caption="MA20·MA60 이동평균 추세",
                width="stretch"
            )

    with col2:

        returns = load_csv(
            "eda/result_csv_png/returns.csv"
        )

        if returns is not None:

            st.markdown("#### Returns Summary")

            st.dataframe(
                returns.describe().round(4),
                width="stretch",
                hide_index=False
            )


    st.divider()

    # =========================================================
    # EDA 핵심 발견
    # =========================================================

    st.subheader("F. EDA 핵심 발견")

    st.info(
        """
        - BTC는 Gold·SP500 대비 높은 변동성과 fat-tail 구조를 보임  
        - 러-우 및 이란 전쟁 구간에서 BTC-SP500 상관관계 상승 현상 확인  
        - BTC는 위험자산과 안전자산 특성이 혼재된 반응 구조를 보임  
        - ARCH 효과가 유의하게 나타나 GARCH 모형 적용 정당성 확보
        """
    )

# ────────────────────────────────────────────────────────────
# 4. 이벤트 스터디
# ────────────────────────────────────────────────────────────
def render_event_study() -> None:

    st.header("Event Study — Safe Haven Validation")

    st.markdown(
        """
        지정학 이벤트 발생 시 자산별 누적 비정상 수익률(CAR)을 분석하여  
        BTC의 안전자산(Safe Haven) 여부를 검증하였다.
        """
    )

    # =========================================================
    # 1. KPI CARDS
    # =========================================================

    st.markdown("## A. 핵심 결과 요약")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "BTC Positive CAR",
            "5 / 6"
        )

    with col2:
        st.metric(
            "BTC Significant",
            "0 / 6"
        )

    with col3:
        st.metric(
            "Gold Safe Haven",
            "1 Event"
        )

    with col4:
        st.metric(
            "BH-FDR Significant",
            "0"
        )

    st.info(
        """
        BTC는 대부분 이벤트에서 양(+)의 CAR을 보였으나,  
        높은 고유 변동성으로 인해 통계적 유의성은 확보하지 못하였다.
        """
    )

    st.divider()

    # =========================================================
    # 2. SAFE HAVEN CLASSIFICATION
    # =========================================================

    st.markdown("## B. 안전자산 분류")

    st.markdown(
        """
        Baur & Lucey (2010) 기준을 활용하여  
        이벤트별 자산 특성을 Safe Haven / Diversifier / Risky Asset으로 분류하였다.
        """
    )

    event = load_csv(
        "EventStudy/result_csv_png/event_study_car_bh.csv"
    )

    if event is not None:

        classify_df = event.copy()

        classify_df["event_label"] = (
            classify_df["event"]
            .map(EVENT_LABEL)
            .fillna(classify_df["event"])
        )

        def classify(row):

            p = row.get("p_norm", np.nan)
            car = row.get("CAR", np.nan)

            if pd.isna(car):
                return "—"

            if car > 0 and p < 0.05:
                return "🟢 Safe Haven"

            elif car > 0:
                return "🟡 Diversifier"

            elif car < 0 and p < 0.05:
                return "🔴 Risky Asset"

            else:
                return "⚪ Neutral"

        classify_df["classification"] = (
            classify_df.apply(classify, axis=1)
        )

        pivot = classify_df.pivot_table(
            index="event_label",
            columns="asset",
            values="classification",
            aggfunc="first"
        )

        st.dataframe(
            pivot,
            use_container_width=True
        )

    st.divider()

    # =========================================================
    # 3. INTERACTIVE CAR DYNAMICS
    # =========================================================

    st.markdown("## C. 이벤트별 CAR 반응")

    st.markdown(
        """
        이벤트 발생 전후(±17일) CAR 흐름을 통해  
        자산별 시장 반응 방향성을 비교하였다.
        """
    )

    tab1, tab2 = st.tabs(
        [
            "CAR Time-Series",
            "CAR Comparison"
        ]
    )

    # ---------------------------------------------------------
    # TAB 1
    # ---------------------------------------------------------

    with tab1:

        img_ts = load_image(
            "EventStudy/result_csv_png/event_study_CAR_timeseries.png"
        )

        if img_ts:

            st.image(
                img_ts,
                caption="이벤트별 CAR 시계열",
                width=1000
            )

    # ---------------------------------------------------------
    # TAB 2
    # ---------------------------------------------------------

    with tab2:

        if event is not None:

            assets = sorted(
                event["asset"]
                .dropna()
                .unique()
            )

            default_assets = (
                ["BTC", "Gold"]
                if "BTC" in assets
                else assets[:2]
            )

            selected_assets = st.multiselect(
                "자산 선택",
                assets,
                default=default_assets
            )

            sub = event[
                event["asset"].isin(selected_assets)
            ].copy()

            sub["event_label"] = (
                sub["event"]
                .map(EVENT_LABEL)
                .fillna(sub["event"])
            )

            fig = px.bar(
                sub,
                x="event_label",
                y="CAR",
                color="asset",
                barmode="group",
                color_discrete_map=ASSET_COLORS,
                title="Event-wise CAR Comparison"
            )

            fig.add_hline(
                y=0,
                line_color="white",
                line_width=1
            )

            fig.update_layout(
                height=500,
                xaxis_title="Event",
                yaxis_title="Cumulative Abnormal Return",
                legend_title="Asset"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

    st.markdown(
        """
        BTC는 다수 이벤트에서 양(+)의 CAR을 보였으나,  
        Gold 대비 반응 일관성과 안정성은 제한적으로 나타났다.
        """
    )

    st.divider()

    # =========================================================
    # 4. BTC vs GOLD
    # =========================================================

    st.markdown("## D. BTC vs Gold 비교")

    st.markdown(
        """
        전통 안전자산인 Gold와 비교하여  
        BTC의 Safe Haven 특성을 상대적으로 비교하였다.
        """
    )

    img_bar = load_image(
        "EventStudy/result_csv_png/event_study_CAR_bar_final.png"
    )

    if img_bar:

        st.image(
            img_bar,
            caption="BTC vs Gold CAR 비교",
            width=1000
        )

    st.info(
        """
        Israel-Iran 이벤트에서 Gold만 유의한 Safe Haven 반응을 보였으며,  
        BTC는 이벤트별 반응 방향성이 일관되지 않았다.
        """
    )

    st.divider()

    # =========================================================
    # 5. STATISTICAL SIGNIFICANCE
    # =========================================================

    st.markdown("## E. 통계적 유의성 검정")

    st.markdown(
        """
        t-test·Bootstrap·BH-FDR 보정을 통해  
        CAR 유의성을 검증하였다.
        """
    )

    with st.expander("통계 검정 결과 보기"):

        if event is not None:

            sub = event.copy()

            sub["event_label"] = (
                sub["event"]
                .map(EVENT_LABEL)
                .fillna(sub["event"])
            )

            keep = [
                "event_label",
                "asset",
                "CAR",
                "t_stat",
                "p_norm",
                "p_boot"
            ]

            if "p_norm_bh" in sub.columns:
                keep.append("p_norm_bh")

            if "sig_bh" in sub.columns:
                keep.append("sig_bh")

            keep = [
                c for c in keep
                if c in sub.columns
            ]

            st.dataframe(
                sub[keep].round(4),
                use_container_width=True,
                hide_index=True
            )

    st.caption(
        "BH-FDR 보정 이후 전체 검정에서 통계적 유의성은 관찰되지 않음"
    )

    st.divider()

    # =========================================================
    # 6. PLACEBO / ROBUSTNESS
    # =========================================================

    st.markdown("## F. Placebo 및 강건성 검정")

    st.markdown(
        """
        무작위 이벤트 창 기반 placebo 검정을 통해  
        실제 이벤트 반응의 강건성을 추가 검증하였다.
        """
    )

    placebo = load_csv(
        "EventStudy/result_csv_png/event_study_placebo.csv"
    )

    if placebo is not None:

        placebo["event_label"] = (
            placebo["event_name"]
            .map(EVENT_LABEL)
            .fillna(placebo["event_name"])
        )

        keep_p = [
            "event_label",
            "real_CAR",
            "placebo_mean_CAR",
            "percentile_of_real",
            "placebo_p"
        ]

        st.dataframe(
            placebo[
                [
                    c for c in keep_p
                    if c in placebo.columns
                ]
            ].round(4),
            use_container_width=True,
            hide_index=True
        )

    st.caption(
        "placebo_p > 0.05 → 실제 이벤트 효과가 무작위 창과 통계적으로 구분되지 않음"
    )

    st.divider()

    # =========================================================
    # 7. FINAL INSIGHT
    # =========================================================

    st.markdown("## G. 최종 해석")

    st.success(
        """
        • BTC는 일부 지정학 이벤트에서 양(+)의 CAR을 보였으나  
        전반적으로 통계적 유의성을 확보하지 못하였다.

        • Gold는 Israel-Iran 이벤트에서만 부분적인 Safe Haven 특성을 보였다.

        • BTC는 전통적 Safe Haven이라기보다  
        이벤트별 반응이 혼재된 고변동성 위험자산 특성에 가까운 모습을 나타냈다.

        • 따라서 Event Study 단독으로 BTC를 Safe Haven으로 결론짓기 어려우며,  
        이후 Quantile Regression·GARCH 분석이 추가적으로 수행되었다.
        """
    )
# ────────────────────────────────────────────────────────────
# 5. 분위수 회귀
# ────────────────────────────────────────────────────────────
def render_quantile() -> None:

    # =========================================================
    # TITLE
    # =========================================================

    st.header("분위수 회귀 — Quantile Regression")

    st.markdown(
        """
        극단적 시장 하락 분위수(τ ≤ 0.10)에서  
        BTC의 Safe Haven 특성을 조건부 분위 회귀로 분석하였다.
        """
    )

    st.caption(
        "Koenker & Bassett (1978) · HAC(Newey-West) · BH-FDR"
    )

    st.divider()

    # =========================================================
    # LOAD CSV
    # =========================================================

    quant_main = load_csv(
        "quantile/result_csv_png/quantreg_main.csv"
    )

    quant_bh = load_csv(
        "quantile/result_csv_png/quantile_results_bh.csv"
    )

    robust_loo = load_csv(
        "quantile/result_csv_png/robust_loo.csv"
    )

    robust_mm = load_csv(
        "quantile/result_csv_png/robust_mm.csv"
    )

    # =========================================================
    # A. KPI SUMMARY
    # =========================================================

    st.markdown("## A. 핵심 결과 요약")

    k1, k2, k3, k4 = st.columns(4)

    with k1:
        st.metric(
            "BTC Safe Haven",
            "0 / 6"
        )

    with k2:
        st.metric(
            "Risky Asset",
            "6 / 6"
        )

    with k3:
        st.metric(
            "β > 0 (τ≤0.10)",
            "100%"
        )

    with k4:
        st.metric(
            "GPR δ",
            "+0.005"
        )

    st.info(
        """
        BTC는 모든 극단 하락 분위수에서  
        SP500과 양(+)의 동조화를 보이며 Safe Haven 조건을 충족하지 못하였다.
        """
    )

    st.divider()

    # =========================================================
    # B. β QUANTILE PATH
    # =========================================================

    st.markdown("## B. β 분위 경로 분석")

    st.markdown(
        """
        분위수(τ) 변화에 따른 β 계수 경로를 통해  
        BTC-시장 간 동조화 구조를 분석하였다.
        """
    )

    beta_col1, beta_col2 = st.columns(2)

    with beta_col1:

        img = load_image(
            "quantile/result_csv_png/quantreg_beta_path.png"
        )

        if img:

            st.image(
                img,
                caption="SP500 · Gold β 분위 경로",
                width="stretch"
            )

    with beta_col2:

        img = load_image(
            "quantile/result_csv_png/quantreg_gamma_path.png"
        )

        if img:

            st.image(
                img,
                caption="GPR γ 분위 경로",
                width="stretch"
            )

    st.warning(
        """
        τ가 낮아질수록 BTC-SP500 β 계수가 증가하며  
        위기 상황에서 위험자산 동조화가 강화되었다.
        """
    )

    st.divider()

    # =========================================================
    # C. SAFE HAVEN CLASSIFICATION
    # =========================================================

    st.markdown("## C. Safe Haven 분류")

    c1, c2, c3 = st.columns(3)

    with c1:

        st.error("❌ 전체 합산 → Risky Asset")

        st.warning("⚪ 호르무즈 위기 → 비유의")

    with c2:

        st.error("❌ 솔레이마니 암살")

        st.error("❌ 러시아-우크라이나")

    with c3:

        st.error("❌ 이스라엘-하마스")

        st.error("❌ 이란 전쟁")

    st.info(
        """
        전체 이벤트에서 BTC는  
        Safe Haven보다 Risky Asset 특성에 가까운 모습을 보였다.
        """
    )

    st.divider()

    # =========================================================
    # D. GPR INTERACTION EFFECT
    # =========================================================

    st.markdown("## D. GPR 상호작용 효과")

    st.markdown(
        """
        지정학 리스크(GPR) 상승 시  
        BTC-주식시장 동조화 구조 변화를 분석하였다.
        """
    )

    d1, d2 = st.columns([1.5, 1])

    with d1:

        img = load_image(
            "quantile/result_csv_png/quantreg_gamma_path.png"
        )

        if img:

            st.image(
                img,
                caption="GPR γ 계수 변화",
                width="stretch"
            )

    with d2:

        st.success(
            """
            ### δ = +0.005  
            ### p = 0.037
            """
        )

        st.markdown(
            """
            GPR 상승 시 BTC는  
            Safe Haven 방향이 아니라  
            SP500과의 동조화 방향으로 이동하였다.
            """
        )

    # ---------------------------------------------------------
    # INTERACTION TABLE
    # ---------------------------------------------------------

    if quant_bh is not None:

        st.markdown("#### GPR Interaction Summary")

        interaction_cols = [
            c for c in quant_bh.columns
            if any(
                k in c.lower()
                for k in ["tau", "τ", "beta", "gamma", "p"]
            )
        ]

        if len(interaction_cols) > 0:

            st.dataframe(
                quant_bh[interaction_cols].head(15),
                width="stretch",
                hide_index=True
            )

    st.divider()

    # =========================================================
    # E. EVENT HEATMAP
    # =========================================================

    st.markdown("## E. 이벤트별 분위수 Heatmap")

    st.markdown(
        """
        이벤트 × 분위수별 β 계수 변화를 통해  
        자산 반응 구조를 비교하였다.
        """
    )

    img = load_image(
        "quantile/result_csv_png/quantreg_heatmap.png"
    )

    if img:

        st.image(
            img,
            caption="Event × Quantile β Heatmap",
            width=1000
        )

    st.caption(
        "Red → Risky Asset / Blue → Safe Haven"
    )

    st.divider()

    # =========================================================
    # F. ROBUSTNESS CHECK
    # =========================================================

    st.markdown("## F. 강건성 검정")

    st.markdown(
        """
        다양한 강건성 검정을 통해  
        분위수 회귀 결과의 안정성을 검증하였다.
        """
    )

    r1, r2, r3, r4 = st.columns(4)

    with r1:
        st.success("① GPR 제거\n\n결론 유지")

    with r2:
        st.success("② Leave-One-Out\n\n결론 유지")

    with r3:
        st.success("③ Min-Max Scaling\n\n결론 유지")

    with r4:
        st.success("④ Bootstrap\n\n결론 유지")

    # ---------------------------------------------------------
    # ROBUST TABLES
    # ---------------------------------------------------------

    robust_tab1, robust_tab2 = st.tabs([
        "LOO Robustness",
        "Min-Max Robustness"
    ])

    with robust_tab1:

        if robust_loo is not None:

            st.dataframe(
                robust_loo.head(20),
                width="stretch",
                hide_index=True
            )

    with robust_tab2:

        if robust_mm is not None:

            st.dataframe(
                robust_mm.head(20),
                width="stretch",
                hide_index=True
            )

    st.info(
        """
        모든 강건성 검정에서  
        BTC = Risky Asset 결론이 안정적으로 유지되었다.
        """
    )

    st.divider()

    # =========================================================
    # G. FINAL INSIGHT
    # =========================================================

    st.markdown("## G. 최종 해석")

    st.success(
        """
        • BTC는 극단적 시장 하락 분위수에서  
        Safe Haven보다 Risky Asset 성격에 가까운 모습을 보였다.

        • τ가 낮아질수록 BTC-SP500 β 계수가 증가하며  
        위기 상황에서 위험자산 동조화가 강화되었다.

        • GPR 상승은 Safe Haven 성격을 강화하지 않았으며,  
        오히려 주식시장 동조화를 증가시켰다.

        • 모든 강건성 검정에서도 결과가 안정적으로 유지되었다.
        """
    )

# =========================================================
# 6. GARCH
# =========================================================

def render_garch() -> None:

    st.header("GARCH-X & EGARCH Robustness")

    # =====================================================
    # KPI
    # =====================================================

    st.markdown("## 핵심 결과")

    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        st.metric("최적 모델", "Model3")

    with c2:
        st.metric("Lowest AIC", "9578.71")

    with c3:
        st.metric("α + β", "0.996")

    with c4:
        st.metric("유의 변수", "Fear&Greed")

    with c5:
        st.metric("GPR", "비유의")

    st.divider()

    # =====================================================
    # A
    # =====================================================

    st.markdown("## A. 변동성 체제")

    img = load_image(
        "garch/result_csv_png/garch_conditional_vol.png"
    )

    if img:
        st.image(
            img,
            caption="BTC Conditional Volatility σ(t)",
            width="stretch"
        )

    event_vol = load_csv("garch/result_csv_png/garch_event_volatility.csv")

    if event_vol is not None:

        fig = px.bar(
            event_vol,
            x="event",
            y="max_volatility",
            color="model",
            barmode="group",
            title="이벤트별 최대 BTC 변동성"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )
    st.divider()

    # =====================================================
    # B
    # =====================================================

    st.markdown("## B. 최적 모델 선정")

    col1, col2 = st.columns([1.4, 1])

    with col1:

        img = load_image(
            "garch/result_csv_png/garch_model_comparison.png"
        )

        if img:
            st.image(
                img,
                caption="AIC / BIC Model Comparison",
                width="stretch"
            )

    ranking = load_csv(
    "garch/result_csv_png/garch_model_ranking.csv"
    )

    if ranking is not None:

        top3 = ranking.head(3)

        c1,c2,c3 = st.columns(3)

        with c1:
            st.metric(
                "🥇 Best",
                top3.iloc[0]["model"]
            )

        with c2:
            st.metric(
                "🥈 Second",
                top3.iloc[1]["model"]
            )

        with c3:
            st.metric(
                "🥉 Third",
                top3.iloc[2]["model"]
            )

    st.divider()

    # =====================================================
    # C
    # =====================================================

    st.markdown("## C. 위험요인 영향력")

    col1, col2 = st.columns([1,1])

    with col1:

        img = load_image(
            "garch/result_csv_png/garch_gamma_coefficients.png"
        )

        if img:
            st.image(
                img,
                caption="γ Coefficient Comparison",
                width="stretch"
            )

    with col2:

        gamma = load_csv(
            "garch/result_csv_png/garch_gamma_long.csv"
        )

        if gamma is not None and "coef" in gamma.columns:

            fig = px.scatter(
                gamma,
                x="coef",
                y="var",
                color="model",
                size=np.abs(gamma["coef"]),
                hover_data=["pvalue"],
                title="Interactive Gamma Effect"
            )

            fig.add_vline(
                x=0,
                line_dash="dash"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

    st.divider()

    # =====================================================
    # D
    # =====================================================

    st.markdown("## D. 변동성 지속성 구조")

    persist = load_csv(
        "garch/result_csv_png/garch_persistence.csv"
    )

    if persist is not None:

        c1, c2 = st.columns([4,1])

        with c1:

            fig = px.bar(
                persist,
                x="model",
                y="alpha_plus_beta",
                color="alpha_plus_beta",
                title="Persistence (α + β)"
            )

            fig.add_hline(
                y=1,
                line_dash="dash",
                line_color="red"
            )

            fig.add_hrect(
                y0=0.95,
                y1=1.00,
                opacity=0.15
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        with c2:

            st.metric(
                "Max α+β",
                f"{persist['alpha_plus_beta'].max():.3f}"
            )

            st.metric(
                "해석",
                "Near-IGARCH"
            )

    st.divider()

    # =====================================================
    # E
    # =====================================================

    st.markdown("## E. EGARCH 강건성 검증")

    col1, col2, col3 = st.columns(3)

    with col1:

        img = load_image(
            "garch/result_csv_png/egarch_model_aic_bic.png"
        )

        if img:
            st.image(
                img,
                caption="EGARCH AIC/BIC",
                width="stretch"
            )

    with col2:

        img = load_image(
            "garch/result_csv_png/egarch_cond_vol_comparison.png"
        )

        if img:
            st.image(
                img,
                caption="Conditional Volatility",
                width="stretch"
            )

    with col3:

        img = load_image(
            "garch/result_csv_png/egarch_gpr_coef_compare.png"
        )

        if img:
            st.image(
                img,
                caption="GPR Coefficient",
                width="stretch"
            )

    egarch = load_csv(
        "garch/result_csv_png/egarch_model_comparison.csv"
    )

    if egarch is not None:

        fig = px.scatter(
            egarch,
            x="AIC",
            y="BIC",
            color="유형",
            hover_name="설명",
            size=np.abs(egarch["LogLik"]),
            title="GARCH vs EGARCH Position Map"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    st.divider()

    # =====================================================
    # F
    # =====================================================

    st.markdown("## F. 추가 강건성 검증")

    integrated = load_csv(
        "garch/result_csv_png/garch_egarch_integrated_summary.csv"
    )

    if integrated is not None:

        fig = px.treemap(
            integrated,
            path=["section","model"],
            values="AIC",
            color="AIC",
            title="Robustness Validation Structure"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.caption(
            "GARCH 기본 → 이벤트 더미 → EGARCH 순서로 강건성을 검증"
        )

    st.divider()

    # =====================================================
    # G
    # =====================================================

    st.markdown("## G. 최종 결론")

    st.success(
        """
        • Fear & Greed만 반복적으로 유의

        • GPR은 모든 모형에서 비유의

        • α+β ≈ 0.996 (near-IGARCH)

        • EGARCH 및 이벤트 더미 검증에서도 동일 결론 유지

        → BTC 변동성은 지정학 리스크보다 투자자 심리에 의해 설명됨
        """
    )



# ────────────────────────────────────────────────────────────
# 진입점
# ────────────────────────────────────────────────────────────
def run() -> None:
    st.set_page_config(
        page_title="BTC 안전자산 가설 (최종)",
        page_icon="₿",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.title("₿ BTC 안전자산 가설 검증 대시보드")
    st.caption("master_data · 6개 지정학 이벤트 · 3종 본분석 + BH-FDR 다중비교 보정 + Placebo")

    st.sidebar.header("탐색")
    section = st.sidebar.radio(
        "섹션",
        ["통합 판정", "GPR 데이터파이프라인", "EDA", "이벤트 스터디", "분위수 회귀", "GARCH"],
    )
    st.sidebar.divider()
    st.sidebar.markdown("**6개 이벤트**")
    for key, label in EVENT_LABEL.items():
        st.sidebar.caption(f"• {label} ({EVENT_DATE[key]})")

    if section == "통합 판정":
        render_integrated_judgment()
    elif section == "GPR 데이터파이프라인":
        render_gpr_pipeline()
    elif section == "EDA":
        render_eda()
    elif section == "이벤트 스터디":
        render_event_study()
    elif section == "분위수 회귀":
        render_quantile()
    else:
        render_garch()


    st.divider()
    st.caption("2026 캡스톤 | BTC 안전자산 가설 검증")
