from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import numpy as np
import textwrap
from PIL import Image
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", message=".*use_column_width.*")

def load_uniform_canvas_image(path, canvas_size=(900, 520)):
    img = Image.open(path).convert("RGB")
    img.thumbnail(canvas_size)
    canvas = Image.new("RGB", canvas_size, (255, 255, 255))
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
        st.stop()

    c1, c2, c3, c4 = st.columns(4)
    cards = [
        {"t": "BTC 상태 판정", "v": "Weak Haven", "d": "Safe Haven 5/6 미통과 (C2 기준)", "c": "#FCA5A5", "tc": "#DC2626"},
        {"t": "핵심 영향 변수", "v": "Fear & Greed", "d": "반복적 유의 변수", "c": "#C4B5FD", "tc": "#7C3AED"},
        {"t": "GPR 지정 효과", "v": "비유의", "d": "지정학 영향 제한적", "c": "#86EFAC", "tc": "#059669"},
        {"t": "최적 변동성 모델", "v": "Model3 (EGARCH)", "d": "VIX + Fear&Greed 반영", "c": "#FCD34D", "tc": "#D97706"}
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
        {"date": "2019-06-13", "title": "호르무즈 위기", "left": "4%"},
        {"date": "2020-01-03", "title": "솔레이마니 암살", "left": "22%"},
        {"date": "2022-02-24", "title": "러-우 전쟁", "left": "40%"},
        {"date": "2023-10-07", "title": "이스라엘-하마스", "left": "58%"},
        {"date": "2024-04-14", "title": "이스라엘-이란", "left": "74%"},
        {"date": "2026-02-28", "title": "미-이스라엘-이란", "left": "88%"}
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

    st.subheader("BTC vs Gold vs SP500 — 누적 로그 수익률")
    returns = load_csv("DataPipeline/processed_data/market_returns.csv")

    if returns is None:
        st.error("market_returns.csv 경로 확인 필요")
    else:
        returns["date"] = pd.to_datetime(returns["date"])
        asset_cols = ["BTC", "Gold", "SP500"]

        for col in asset_cols:
            returns[f"{col}_log"] = np.log1p(returns[col])
            returns[f"{col}_cum"] = returns[f"{col}_log"].cumsum()

        fig = go.Figure()
        colors = {"BTC": "#F7931A", "Gold": "#FFD700", "SP500": "#1E88E5"}

        for asset in asset_cols:
            fig.add_trace(
                go.Scatter(
                    x=returns["date"],
                    y=returns[f"{asset}_cum"],
                    mode="lines",
                    name=asset,
                    line=dict(width=3, color=colors[asset]),
                    hovertemplate="<b>%{fullData.name}</b><br>Date: %{x}<br>Cumulative Log Return: %{y:.3f}<extra></extra>"
                )
            )

        for key, date in EVENT_DATE.items():
            fig.add_vline(x=pd.to_datetime(date), line_dash="dot", line_color="red", opacity=0.7)
            fig.add_annotation(
                x=pd.to_datetime(date),
                y=returns["BTC_cum"].max(),
                text=EVENT_LABEL[key],
                showarrow=False,
                textangle=-90,
                font=dict(size=10, color="red"),
                yshift=10
            )

        fig.update_layout(
            template="plotly_dark",
            height=650,
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            xaxis_title="Date",
            yaxis_title="Cumulative Log Return",
            margin=dict(l=20, r=20, t=30, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    st.subheader("이벤트별 안전자산 판정 매트릭스")
    verdict_color = {"Safe Haven": "#16A34A", "Weak Haven": "#D97706", "Risky Asset": "#DC2626"}

    def icon(v):
        return "🛡️" if v else "❌"

    matrix_df = pd.DataFrame({
        "이벤트": final["event_label"],
        "C1 이벤트 스터디": final["C1_event_study_pass"].apply(icon),
        "C2 분위수 회귀": final["C2_quantile_reg_pass"].apply(icon),
        "C3 GARCH": final["C3_garch_pass"].apply(icon),
        "최종 판정": final["verdict"]
    })

    styled = matrix_df.style.map(
        lambda x: f"background-color: {verdict_color.get(x, '#333333')}; color:white; font-weight:bold; border-radius:8px;",
        subset=["최종 판정"]
    )
    st.dataframe(styled, use_container_width=True, hide_index=True)
    st.caption("🛡️ : Safe Haven 조건 충족 방향  |  ❌ : 위험자산 성향 방향")
    st.divider()

    st.subheader("핵심 결과")
    k1, k2, k3 = st.columns(3)
    k1.metric("Quantile Pass (C2)", "1 / 6")
    k2.metric("SP500-BTC Tail Corr.", "+2.2×")
    k3.metric("Fear & Greed γ", "+0.157")

    st.info("""
        ### 최종 결론

        ✅ 변동성 측면에서는 일부 안전자산 특성 확인

        ⚠️ 시장 급락 구간에서는 주식시장과 동조화 경향 존재

        🎯 BTC는 완전한 Safe Haven이 아닌
        **Weak Haven(조건부 안전자산)** 으로 판단
        """)

    report = ROOT / "MD" / "final_report.md"
    if report.exists():
        st.divider()
        with st.expander("final_report.md (전체)", expanded=False):
            st.markdown(report.read_text(encoding="utf-8"))

def render_gpr_pipeline() -> None:
    st.header("GPR 데이터파이프라인 — 자체 지정학 리스크 지수 구축")
    st.markdown("""
        <div style="background:#FAFAFA; border-left:6px solid #6B7280; padding:18px 22px; border-radius:8px; margin-bottom:20px;">
            <p style="font-size:17px; font-weight:700; color:#111827; margin:0 0 6px 0;">분석 배경 및 목적 — 고빈도 일별 리스크 지수 포착</p>
            <p style="font-size:15px; color:#1f2937; margin:0;">기존 학계에서 범용적으로 사용되는 Caldara &amp; Iacoviello(2022) 공식 GPR 지수는 <b>월 단위 집계 지수</b>이므로, 본 연구가 타겟으로 삼는 단기 이벤트 창(±17 거래일) 내의 급격한 지정학적 충격과 일별 가격 변동성을 미시적으로 추적하기 어렵다. 이를 해결하고자 GDELT GKG 빅데이터 파이프라인을 구축하여 약 734만 건의 글로벌 뉴스 기사를 정제하고, 일별 추적이 가능한 <b>Custom GPR 지수</b>를 자체 모델링하였다.</p>
        </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["1️⃣ 데이터 수집 · 정제", "2️⃣ Custom GPR 설계", "3️⃣ 금융시장 통합 데이터 구축"])

    with tab1:
        st.subheader("데이터 수집 · 정제")
        st.markdown("GDELT GKG(BigQuery) 기반 글로벌 뉴스 데이터를 수집하고, 이벤트 단위로 전처리를 수행하여 Custom GPR 생성에 활용하였다.")
        st.divider()

        st.markdown("### A. 뉴스 기사 수 분석 (Raw Data Overview)")
        
        left,right=st.columns([1,1.4])

        with left:
            st.metric("수집된 뉴스 기사 수","약 734만 건")
            st.metric("분석 이벤트 수","6개")
            st.metric("분석 기간","2019–2026")

            st.markdown("<div style='height:15px'></div>",unsafe_allow_html=True)

            st.info(
                "• 러-우 전쟁 이벤트에서 가장 큰 뉴스 기사량 증가가 확인되었으며,\n\n"
                "• 지정학 이벤트 직후 글로벌 뉴스 보도가 집중되는 패턴을 확인함"
            )

        with right:
            img=load_image("FIGURES/01-3_russia_ukraine_article_count.png")
            if img:
                st.image(
                    img,
                    caption="러시아-우크라이나 전쟁 기간 기사량 급증",
                    use_container_width=True
                )
        st.divider()
        st.markdown("### B. 이벤트별 기사량 변화 (Event Distribution)")
        with st.expander("이벤트별 뉴스 보도량 분포 그래프 전체 보기 (클릭하여 펼치기)", expanded=False):
            imgs_raw = [
                ("FIGURES/01-1_hormuz_article_count.png", "호르무즈 위기"),
                ("FIGURES/01-2_soleimani_article_count.png", "솔레이마니 암살"),
                ("FIGURES/01-3_russia_ukraine_article_count.png", "러시아-우크라이나 전쟁"),
                ("FIGURES/01-4_israel_hamas_article_count.png", "이란-하마스 전쟁"),
                ("FIGURES/01-5_israel_iran_article_count.png", "이스라엘-이란 충돌"),
                ("FIGURES/01-6_us_israel_iran_article_count.png", "미국-이스라엘-이란 위기")
            ]
            col1, col2 = st.columns(2)
            with col1:
                st.image(load_uniform_canvas_image(imgs_raw[0][0]), use_column_width=True)
                st.caption(imgs_raw[0][1])
                st.image(load_uniform_canvas_image(imgs_raw[2][0]), use_column_width=True)
                st.caption(imgs_raw[2][1])
                st.image(load_uniform_canvas_image(imgs_raw[4][0]), use_column_width=True)
                st.caption(imgs_raw[4][1])
            with col2:
                st.image(load_uniform_canvas_image(imgs_raw[1][0]), use_column_width=True)
                st.caption(imgs_raw[1][1])
                st.image(load_uniform_canvas_image(imgs_raw[3][0]), use_column_width=True)
                st.caption(imgs_raw[3][1])
                st.image(load_uniform_canvas_image(imgs_raw[5][0]), use_column_width=True)
                st.caption(imgs_raw[5][1])

        st.divider()
        st.markdown("### C. 데이터 정제 및 필터링 (Cleaning Process)")
        col1,col2=st.columns([0.9,1.3])

        with col1:
            st.markdown("#### 전처리 절차")

            st.markdown("""
            <div style="text-align:center;padding:12px;border:2px solid #d9d9d9;border-radius:20px;background:#f8f9fa;">
            Raw Query
            </div>
            <div style="text-align:center;font-size:28px;">↓</div>

            <div style="text-align:center;padding:12px;border:2px solid #d9d9d9;border-radius:20px;background:#f8f9fa;">
            URL 중복 제거
            </div>
            <div style="text-align:center;font-size:28px;">↓</div>

            <div style="text-align:center;padding:12px;border:2px solid #d9d9d9;border-radius:20px;background:#f8f9fa;">
            tone 결측치 제거
            </div>
            <div style="text-align:center;font-size:28px;">↓</div>

            <div style="text-align:center;padding:12px;border:2px solid #d9d9d9;border-radius:20px;background:#f8f9fa;">
            이상값 제거<br>(|tone_score| > 20)
            </div>
            <div style="text-align:center;font-size:28px;">↓</div>

            <div style="text-align:center;padding:12px;border:2px solid #d9d9d9;border-radius:20px;background:#f8f9fa;">
            GEO_THEMES 기반<br>지정학 필터링
            </div>
            <div style="text-align:center;font-size:28px;">↓</div>

            <div style="text-align:center;padding:12px;border:2px solid #d9d9d9;border-radius:20px;background:#f8f9fa;">
            Daily Aggregation
            </div>
            <div style="text-align:center;font-size:28px;">↓</div>

            <div style="text-align:center;padding:12px;border:2px solid #d9d9d9;border-radius:20px;background:#e8f4ff;">
            최소 기사 수 조건 적용<br>(일 5건 이상)
            </div>
            """,unsafe_allow_html=True)

        with col2:
            st.markdown("#### Before vs After")
            img=load_image("FIGURES/02-1_hormuz_preprocessed.png")
            if img: st.image(img,caption="전처리 이후 기사량 및 tone 분포",width=650)
        st.success("• 전처리 과정에서 이상치 및 노이즈가 제거되었으나 전체 기사량 추세는 크게 변하지 않았으며, 주요 이벤트 반응 패턴이 안정적으로 유지됨.")

    with tab2:
        st.subheader("Custom GPR 설계 및 검증")
        st.markdown("뉴스 감성(tone)과 기사량(volume)을 조합하여 F1~F5 형태의 Custom GPR 공식을 설계하고 비교 분석하였다.")
        st.divider()

        st.markdown("### A. 후보 수식 모델링 및 통계적 특성 비교")

        formula_df=pd.DataFrame({
            "모델":["F1","F2","F3","F4","F5"],
            "설계 방식":["Tone Mean","Polarity Weighted","Tone × log(N)","Negative Ratio","28D EWMA"],
            "설명":["평균 tone 기반 감성 지표","polarity 가중 평균","tone과 상대 기사량 결합","부정 기사 비율 기반","F2 시계열 평활화 적용"]
        })

        st.dataframe(formula_df,use_container_width=True,hide_index=True)

        st.info("F3 수식 구조: Custom GPR(F3) = − mean_tone × log(1 + N / N_mean)")
        st.divider()
        st.markdown("### B. 공식 GPR과의 상관관계 검증")
        img = load_image("FIGURES/03_correlation_heatmap.png")
        if img:
            st.image(img, caption="공식 GPR vs Custom GPR 상관관계 히트맵", use_column_width=True)

        st.info(
            "**F3 공식 최종 선정 근거**\n\n"
            "- **공식 GPR 지수와의 정합성**: Pearson 상관계수 **r = 0.41**로 후보군 중 가장 높은 일치도를 기록함.\n"
            "- **왜곡 방지 메커니즘**: 위기 발발 시 뉴스 보도량이 기하급수적으로 폭증하는 현상(Volume Shock)에 의해 전체 시계열 독립변수가 왜곡되는 현상을 로그 스케일 가중치를 적용하여 방지함."
        )

        st.divider()
        st.markdown("### C. 시계열 및 이벤트 윈도우 반응 비교")
        # ---------------
        # summary_df 안의 값 수정 필요
        # ---------------
        summary_df=pd.DataFrame({
            "Event":["Russia-Ukraine","Israel-Hamas","Hormuz","Soleimani","US-Israel-Iran"],
            "공식 GPR 반응":["급등","급등","상승","급등","급등"],
            "Custom GPR(F3)":["유사","유사","유사","유사","유사"],
            "판정":["매우 높음","매우 높음","높음","매우 높음","매우 높음"]
        })
        st.dataframe(summary_df,use_container_width=True,hide_index=True)

        left,right=st.columns(2)

        with left:
            img_ts=load_image("FIGURES/05_gpr_timeseries.png")
            if img_ts:
                st.image(img_ts,caption="Figure 5. 후보 모델(F1~F5) 시계열 비교",use_container_width=True)

        with right:
            img_ev=load_image("FIGURES/07_event_window.png")
            if img_ev:
                st.image(img_ev,caption="Figure 7. 공식 GPR vs Custom GPR(F3) 이벤트 반응 비교",use_container_width=True)

        st.success(
            "• F3는 다수의 지정학 이벤트에서 공식 GPR 지수와 유사한 방향성과 반응 강도를 보였으며, "
            "이벤트 발생 직후 위험 인식 상승 구간을 안정적으로 포착하였다."
        )
    with tab3:
        st.subheader("금융시장 통합 데이터 구축")
        st.divider()
        st.markdown("### A. 금융시장 데이터 수집 대상")
        market_df = pd.DataFrame({
            "자산": ["Bitcoin", "Gold", "TLT", "DXY", "S&P500", "NASDAQ"],
            "Ticker": ["BTC-USD", "GC=F", "TLT", "DX-Y.NYB", "^GSPC", "^IXIC"],
            "역할": ["위험자산 검증 대상", "전통 안전자산 benchmark", "장기채 proxy", "달러 강세 proxy", "미국 주식시장 benchmark", "기술주 시장 benchmark"]
        })
        st.dataframe(market_df, use_container_width=True, hide_index=True)

        st.divider()
        st.markdown("### B. 로그수익률 변환 및 거래일 보정 논리")

        c1,a1,c2,a2,c3,a3,c4,a4,c5=st.columns([2.8,0.5,2.8,0.5,2.8,0.5,2.8,0.5,2.8])

        with c1:
            st.markdown("""
            <div style="height:120px;border:2px solid #d9d9d9;border-radius:50%;display:flex;align-items:center;justify-content:center;text-align:center;font-size:20px;">
            Raw Price
            </div>
            """,unsafe_allow_html=True)

        with a1:
            st.markdown("<div style='text-align:center;font-size:42px;padding-top:35px;font-weight:bold;'>→</div>",unsafe_allow_html=True)

        with c2:
            st.markdown("""
            <div style="height:120px;border:2px solid #d9d9d9;border-radius:50%;display:flex;align-items:center;justify-content:center;text-align:center;font-size:20px;">
            Log Return<br>Conversion

            </div>
            """,unsafe_allow_html=True)

        with a2:
            st.markdown("<div style='text-align:center;font-size:42px;padding-top:35px;font-weight:bold;'>→</div>",unsafe_allow_html=True)

        with c3:
            st.markdown("""
            <div style="height:120px;border:2px solid #d9d9d9;border-radius:50%;display:flex;align-items:center;justify-content:center;text-align:center;font-size:20px;">
            Trading Day<br>Alignment
            </div>
            """,unsafe_allow_html=True)

        with a3:
            st.markdown("<div style='text-align:center;font-size:42px;padding-top:35px;font-weight:bold;'>→</div>",unsafe_allow_html=True)

        with c4:
            st.markdown("""
            <div style="height:120px;border:2px solid #d9d9d9;border-radius:50%;display:flex;align-items:center;justify-content:center;text-align:center;font-size:20px;">
            Missing Value<br>Imputation
            </div>
            """,unsafe_allow_html=True)

        with a4:
            st.markdown("<div style='text-align:center;font-size:42px;padding-top:35px;font-weight:bold;'>→</div>",unsafe_allow_html=True)

        with c5:
            st.markdown("""
            <div style="height:120px;border:2px solid #4CAF50;border-radius:50%;display:flex;align-items:center;justify-content:center;text-align:center;font-size:20px;font-weight:600;background:#f3fff3;">
            Master<br>Dataset
            </div>
            """,unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        st.info(
            "거래일 불일치 통제: 주말 및 휴일에도 24시간 거래가 지속되는 BTC 시계열과 전통 자산 시장의 휴장일 시차를 보정하기 위해, "
            "비거래일 동안 누적된 BTC 수익률을 전통 시장 개장일(월요일 등) 수익률로 누적 합산(Summation) 정렬하여 편향을 통제함."
        )

        st.divider()
        st.markdown("### C. 최종 통합 데이터셋(Master Dataset) 개요")
        master_path = ROOT / "DataPipeline" / "processed_data" / "final" / "master_data.csv"
        if master_path.exists():
            master_df = pd.read_csv(master_path)
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Rows (관측치)", f"{len(master_df):,}")
            col2.metric("Columns (변수)", master_df.shape[1])
            col3.metric("Events (이벤트 수)", 6)
            col4.metric("Assets (대상 자산)", 6)
            with st.expander("master_data.csv Sample Data Preview", expanded=False):
                st.dataframe(master_df.head(10), use_container_width=True, hide_index=True)

def render_eda() -> None:
    st.header("EDA — 탐색적 데이터 분석")

    st.markdown("""
    <div style="background:#FDFBFF;border-left:6px solid #7C3AED;padding:18px 22px;border-radius:8px;margin-bottom:20px;">
        <p style="font-size:17px;font-weight:700;color:#4C1D95;margin:0 0 6px 0;">분석 배경 및 목적 — 통계적 모형 도입의 정당성 확보</p>
        <p style="font-size:15px;color:#1f2937;margin:0;">
        본격적인 계량 회귀 분석에 앞서 수집된 시계열 데이터의 기초 분포를 검토한다.
        금융 시계열 특유의 <b>정규성 왜곡(Fat-tail) 및 변동성 군집(Volatility Clustering)</b> 현상이 포착되어야
        일반 OLS 모형 대신 분위수 회귀 및 GARCH 계열 모형을 도입하는 통계적 당위성이 확립된다.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("## A. 시계열 추세 및 이벤트 가격 반응")

    c1,c2,c3=st.columns(3)
    with c1: st.metric("분석 자산","6개")
    with c2: st.metric("분석 이벤트","6개")
    with c3: st.metric("분석 기간","2019-07-01 ~ 2026-03-24")

    with st.expander("📈 전체 기간 자산 가격 추이", expanded=False):
        img=load_image("eda/result_csv_png/plot1_price_trend.png")
        if img: st.image(img,caption="전체 기간 자산 가격 추이",use_container_width=True)
        st.info("• BTC, 금, 원유, 주식시장 등 주요 자산의 장기 가격 흐름과 구조적 추세를 비교")

    with st.expander("📊 이벤트별 정규화 가격 비교 및 이동평균선 추세 분석", expanded=False):

        left,right=st.columns(2)

        with left:
            st.markdown("#### 이벤트별 정규화 가격 비교")
            img=load_image("eda/result_csv_png/plot2_event_price.png")
            if img: st.image(img,caption="이벤트 구간별 정규화 가격 흐름",use_container_width=True)
            st.success("• 지정학 이벤트 발생 이후 자산별 반응 강도와 회복 속도의 차이를 확인")

        with right:
            st.markdown("#### 이동평균선(MA20·MA60) 추세 분석")
            img=load_image("eda/result_csv_png/plot3_moving_average.png")
            if img: st.image(img,caption="자산별 이동평균선 추이",use_container_width=True)
            st.info("• 단기(MA20)와 장기(MA60) 추세 비교를 통해 주요 변곡점 및 추세 지속성을 확인")
    
    st.divider()

    st.markdown("## B. 수익률 분포 특성 및 변동성 분석")

    returns=load_csv("eda/result_csv_png/returns.csv")

    if returns is not None and "BTC" in returns.columns:
        c1,c2,c3=st.columns(3)
        with c1: st.metric("BTC 평균 수익률",f"{returns['BTC'].mean():.4f}")
        with c2: st.metric("BTC 변동성",f"{returns['BTC'].std():.4f}")
        with c3: st.metric("관측치 수",f"{len(returns):,}")


    left,right=st.columns([1,1.1])

    with left:
        st.markdown("#### 수익률 분포")
        img=load_image("eda/result_csv_png/plot4_returns_dist.png")
        if img: st.image(img,caption="자산별 수익률 분포",use_container_width=True)
        st.success(
        "• BTC 수익률은 정규분포를 따르지 않으며 두꺼운 꼬리(Fat-Tail)와 높은 변동성을 보임"
    )
        if returns is not None:
            st.markdown("#### 기술통계 요약")
            st.dataframe(
                returns.describe().round(4),
                use_container_width=True,
                height=350
            )

    with right:
        st.markdown("#### BTC 일별 변동폭")
        img=load_image("eda/result_csv_png/plot5_btc_highlow.png")
        if img: st.image(
            img,
            caption="BTC High-Low 변동폭",
            use_container_width=True
        )

  

    st.divider()

    st.markdown("## C. 상관관계 구조 변화 및 위험 동조화 분석")

    with st.expander("📊 전체 기간 및 전쟁 전후 상관관계 비교", expanded=False):

        img=load_image("eda/result_csv_png/plot6_corr_heatmap.png")
        if img:
            st.image(
                img,
                caption="전체 기간 · 전쟁 전 · 전쟁 중 상관관계 비교",
                use_container_width=True
            )

        st.info(
            "• 전쟁 국면에서 BTC와 주식시장(S&P500·NASDAQ)의 상관관계가 상승하며 위험 동조화 현상이 강화됨"
        )

    with st.expander("📊 지정학 이벤트별 ±60일 상관관계 변화", expanded=False):

        img=load_image("eda/result_csv_png/plot7_event_heatmap.png")
        if img:
            st.image(
                img,
                caption="이벤트별 ±60일 상관관계 비교",
                use_container_width=True
            )

        st.info(
            "• 이벤트별 차이는 존재하지만 대부분의 위기 국면에서 BTC-주식시장 상관성이 확대되는 경향을 확인"
        )

    with st.expander("📈 BTC 롤링 상관관계 (30일 기준)", expanded=False):

        img=load_image("eda/result_csv_png/plot8_rolling_corr.png")
        if img:
            st.image(
                img,
                caption="BTC vs 주요 안전자산 롤링 상관관계",
                use_container_width=True
            )

        st.info(
            "• BTC는 주식시장과 지속적인 양(+)의 상관관계를 보이며 전통적 안전자산과의 안정적 동행은 제한적으로 나타남"
        )

    st.success(
        "• 종합적으로 BTC는 위기 국면에서 위험자산과의 동조화가 강화되어 완전한 안전자산으로 보기 어려운 특성을 보임"
    )

def render_event_study() -> None:
    st.header("Event Study — Safe Haven Validation")
    st.markdown("""
        <div style="background:#F8FAFF; border-left:6px solid #2563EB; padding:18px 22px; border-radius:8px; margin-bottom:20px;">
            <p style="font-size:17px; font-weight:700; color:#1E40AF; margin:0 0 6px 0;">분석 배경 및 목적 — C1 평균적 초과수익률 검증</p>
            <p style="font-size:15px; color:#1f2937; margin:0;">지정학적 위기 충격이 금융 시장에 가해진 당일과 직후, 시장 참여자들이 비트코인을 가치 저장 수단으로 인식하여 자금을 유입시켰는지 검증한다. MacKinlay(1997) 방법론을 적용하여 예측치를 상회하는 <b>누적 비정상 수익률(CAR)</b>을 도출하고, 다중비교 보정(BH-FDR)을 거쳐 평균적 관점의 <b>Baur &amp; Lucey(2010) C1 안전자산 조건</b>을 검정한다.</p>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("BTC Positive CAR", "5 / 6")
    col2.metric("BTC Stat. Significant", "0 / 6")
    col3.metric("Gold Safe Haven Pass", "1 Event")
    col4.metric("BH-FDR Significant", "0")
    st.divider()

    st.markdown("## A. Baur & Lucey (2010) 기준 자산 분류 매트릭스")
    event = load_csv("EventStudy/result_csv_png/event_study_car_bh.csv")
    if event is not None:
        classify_df = event.copy()
        classify_df["event_label"] = classify_df["event"].map(EVENT_LABEL).fillna(classify_df["event"])

        def classify(row):
            p = row.get("p_norm", np.nan)
            car = row.get("CAR", np.nan)
            if pd.isna(car): return "—"
            if car > 0 and p < 0.05: return "🟢 Safe Haven"
            elif car > 0: return "🟡 Diversifier"
            elif car < 0 and p < 0.05: return "🔴 Risky Asset"
            else: return "⚪ Neutral"

        classify_df["classification"] = classify_df.apply(classify, axis=1)
        pivot = classify_df.pivot_table(index="event_label", columns="asset", values="classification", aggfunc="first")
        st.dataframe(pivot, use_container_width=True)

    st.divider()
    st.markdown("## B. 이벤트 창(±17일) 내 누적 비정상 수익률 추이")
    tab1, tab2 = st.tabs(["CAR 시계열 추이 (정적)", "자산별 CAR 비교 (인터랙티브)"])
    with tab1:
        img_ts = load_image("EventStudy/result_csv_png/event_study_CAR_timeseries.png")
        if img_ts: st.image(img_ts, caption="이벤트별 CAR 누적 추이", width=1000)
    with tab2:
        if event is not None:
            assets = sorted(event["asset"].dropna().unique())
            default_assets = ["BTC", "Gold"] if "BTC" in assets else assets[:2]
            selected_assets = st.multiselect("분석 자산 필터링", assets, default=default_assets)

            sub = event[event["asset"].isin(selected_assets)].copy()
            sub["event_label"] = sub["event"].map(EVENT_LABEL).fillna(sub["event"])

            fig = px.bar(sub, x="event_label", y="CAR", color="asset", barmode="group",
                        color_discrete_map=ASSET_COLORS, title="Event-wise CAR Comparison")
            fig.add_hline(y=0, line_color="white", line_width=1)
            fig.update_layout(height=500, xaxis_title="지정학 이벤트", yaxis_title="Cumulative Abnormal Return")
            st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.markdown("## C. 통계적 강건성 및 Placebo 검정")
    with st.expander("📊 BH-FDR 다중검정 보정 결과", expanded=False):
        if event is not None:
            sub=event.copy()
            sub["event_label"]=sub["event"].map(EVENT_LABEL).fillna(sub["event"])

            keep=[
                c for c in [
                    "event_label",
                    "asset",
                    "CAR",
                    "t_stat",
                    "p_norm",
                    "p_boot",
                    "p_norm_bh",
                    "sig_bh"
                ]
                if c in sub.columns
            ]

            st.dataframe(
                sub[keep].round(4),
                use_container_width=True,
                hide_index=True
            )

        st.info(
            "• Gold의 Israel-Iran 이벤트(p=0.040)를 제외하면 모든 이벤트가 통계적으로 비유의하였으며, "
            "BH-FDR 다중검정 보정 후에는 전체 검정이 비유의(p_bh=0.849)로 판정됨"
        )
    

    with st.expander("🎲 Placebo 검정 결과", expanded=False):

        placebo=load_csv(
            "EventStudy/result_csv_png/event_study_placebo.csv"
        )

        if placebo is not None:

            placebo["event_label"]=placebo["event_name"].map(
                EVENT_LABEL
            ).fillna(placebo["event_name"])

            placebo=placebo.dropna(
                subset=["real_CAR","percentile_of_real"]
            )

            left,right=st.columns(2)

            with left:

                st.markdown("##### 실제 CAR")

                df_car=placebo.sort_values("real_CAR").copy()

                df_car["색상"]=df_car["real_CAR"].apply(
                    lambda x:
                    "#C62828" if x < -0.30 else
                    "#EF5350" if x < 0 else
                    "#90CAF9" if x < 0.20 else
                    "#42A5F5" if x < 0.35 else
                    "#1565C0"
                )

                fig_car=px.bar(
                    df_car,
                    x="real_CAR",
                    y="event_label",
                    orientation="h",
                    text="real_CAR"
                )

                fig_car.update_traces(
                    marker_color=df_car["색상"],
                    texttemplate="%{text:.3f}",
                    textposition="outside"
                )

                fig_car.update_layout(
                    height=350,
                    showlegend=False,
                    xaxis_title="실제 CAR",
                    yaxis_title="",
                    margin=dict(l=0,r=0,t=10,b=0)
                )

                st.plotly_chart(
                    fig_car,
                    use_container_width=True
                )

            with right:

                st.markdown("##### 랜덤 이벤트 대비 특이성")

                df_pct=placebo.sort_values(
                    "percentile_of_real"
                ).copy()

                fig_pct=px.bar(
                    df_pct,
                    x="percentile_of_real",
                    y="event_label",
                    orientation="h",
                    text="percentile_of_real",
                    color="percentile_of_real",
                    color_continuous_scale="Blues"
                )

                fig_pct.update_traces(
                    texttemplate="%{text:.1%}",
                    textposition="outside"
                )

                fig_pct.update_layout(
                    height=350,
                    coloraxis_showscale=False,
                    xaxis_title="Percentile",
                    yaxis_title="",
                    margin=dict(l=0,r=0,t=10,b=0)
                )

                fig_pct.add_vline(
                    x=0.95,
                    line_dash="dash",
                    line_color="red",
                    annotation_text="95% 기준",
                    annotation_position="top"
                )

                st.plotly_chart(
                    fig_pct,
                    use_container_width=True
                )

        st.info(
            "• 솔레이마니 암살(93%)과 이스라엘-하마스 전쟁(94%)은 플라시보 분포 상위 구간에 위치했으나, 95% 유의수준을 충족하지 못해 우연적 발생 가능성을 완전히 배제할 수 없었다."
        )
    st.markdown(""" <div style="background:#EFF6FF; border-left:6px solid #2563EB; padding:18px 22px; border-radius:8px; margin-top:20px;"> <p style="font-size:18px; font-weight:700; color:#1E40AF; margin:0 0 8px 0;">C1 이벤트 스터디 판정 요약</p> <p style="font-size:14px; color:#374151; margin:0;">BTC는 5개 이벤트 중 4개에서 양(+)의 CAR을 기록했으나 전 이벤트에서 통계적 유의성을 확보하지 못하였다. "
        "Gold 역시 Israel-Iran 이벤트에서만 일시적 Safe Haven 특성이 관찰되었으나 BH 보정 후 비유의로 판정되었다. "
        "따라서 C1(Event Study) 기준에서 BTC의 안전자산 성격은 확인되지 않았으며, 보다 강건한 검증을 위해 <b>C2 분위수 회귀 분석</b>으로 검증을 심화합니다.</p> </div> """, unsafe_allow_html=True)

def render_quantile() -> None:
    st.header("분위수 회귀 — Quantile Regression")
    st.markdown("""
        <div style="background:#FFFBF5; border-left:6px solid #EA580C; padding:18px 22px; border-radius:8px; margin-bottom:20px;">
            <p style="font-size:17px; font-weight:700; color:#92400E; margin:0 0 6px 0;">분석 배경 및 목적 — C2 조건 기반 극단 하락 국면 추적</p>
            <p style="font-size:15px; color:#1f2937; margin:0;">전체 기간의 평균치에 의존하는 OLS나 이벤트 스터디(C1)는 자산 시장 대폭락 시기에 작동하는 비선형적 자산 동조화 현상을 차단한다. 비트코인이 진정한 Safe Haven 자산이라면 주식시장이 가장 강력하게 붕괴하는 하위 분위수 영역<b>(τ ≤ 0.10)에서 주식과 디커플링되거나 음(-)의 상관관계(β &lt; 0)</b>를 입증해야 한다. 이를 Koenker &amp; Bassett(1978) 모형으로 추정한다.</p>
        </div>
    """, unsafe_allow_html=True)

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Safe Haven Pass", "1 / 6")
    k2.metric("Risky Asset Behavior", "5 / 6")
    k3.metric("SP500 Beta > 0", "10 / 10")
    k4.metric("Gold Beta Co-move", "10 / 10")
    k5.metric("GPR Direct Effect", "Stat. Non-Sig")
    st.divider()

    st.markdown("## A. 구조적 분위수 회귀 방정식 및 추정 수식")
    st.latex(r"Q_{\tau}(R_{\text{BTC}, t} | X_t) = \alpha_{\tau} + \beta_{\tau} R_{\text{SP500}, t} + \gamma_{\tau} \text{Custom\_GPR}_t + \delta_{\tau} (R_{\text{SP500}, t} \times \text{Custom\_GPR}_t)")
    st.caption("수식 설명: 주식 폭락기(저분위수 τ) 영역에서 주식 베타인 β_τ가 음(-)이거나 통계적으로 비유의해야 안전자산으로 성립됨. δ_τ 상호작용 계수는 지정학 위험 고조 시 자산 동조화가 가속되는지 측정함.")

    st.markdown("## B. 조건부 분위수별 계수 추정 경로 (Beta Path Analysis)")
    beta_csv = load_csv("quantile/result_csv_png/quantreg_beta_path.csv")
    if beta_csv is not None:
        st.line_chart(beta_csv.set_index("tau")[["beta"]])

    with st.expander("상세 구조 시각화 플롯 확인 (기본 모델 vs 상호작용항 포함 모델)", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            img = load_image("quantile/result_csv_png/quantreg_beta_path.png")
            if img: st.image(img, caption="기본 분위수 베타 경로")
        with col2:
            img = load_image("quantile/result_csv_png/quantreg_beta_path_ia.png")
            if img: st.image(img, caption="상호작용항 포함 베타 경로")

    st.divider()
    st.markdown("## C. 지정학 리스크 효과 및 이벤트별 연계 검증")
    with st.expander("GPR 직접 효과 경로 및 이벤트별 판정 히트맵 (기본 vs 상호작용 모델)", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            img = load_image("quantile/result_csv_png/quantreg_gamma_path.png")
            if img: st.image(img, caption="GPR 독자 영향력(Gamma) 경로")
            img = load_image("quantile/result_csv_png/quantreg_heatmap.png")
            if img: st.image(img, caption="기본 모형 판정 히트맵")
        with col2:
            img = load_image("quantile/result_csv_png/quantreg_gamma_path_ia.png")
            if img: st.image(img, caption="상호작용 GPR 영향력 경로")
            img = load_image("quantile/result_csv_png/quantreg_heatmap_ia.png")
            if img: st.image(img, caption="상호작용항 포함 판정 히트맵")

    st.divider()
    st.markdown("## D. GPR 상호작용 효과 및 강건성 검정 (Robustness)")
    ia_df = load_csv("quantile/result_csv_png/quantreg_results_ia.csv")
    if ia_df is not None:
        with st.expander("상호작용항 모델 파라미터 세부 추정치 확인", expanded=False):
            st.dataframe(ia_df, use_container_width=True, hide_index=True)

    with st.expander("외생변수 변형 및 표본 통제 기반 강건성 검정 데이터 표", expanded=False):
        tab1, tab2, tab3 = st.tabs(["GPR 변수 제외 대체", "Leave-One-Out 표본 추출 통제", "Min-Max 스케일 변환 보정"])
        with tab1:
            robust_iv = load_csv("quantile/result_csv_png/robust_iv.csv")
            if robust_iv is not None: st.dataframe(robust_iv, use_container_width=True)
        with tab2:
            robust_loo = load_csv("quantile/result_csv_png/robust_loo.csv")
            if robust_loo is not None: st.dataframe(robust_loo, use_container_width=True)
        with tab3:
            robust_mm = load_csv("quantile/result_csv_png/robust_mm.csv")
            if robust_mm is not None: st.dataframe(robust_mm, use_container_width=True)

    st.markdown("""
        <div style="background:#FFF7ED; border-left:6px solid #EA580C; padding:18px 22px; border-radius:8px; margin-top:20px;">
            <p style="font-size:18px; font-weight:700; color:#92400E; margin:0 0 8px 0;">C2 분위수 회귀 판정 요약</p>
            <p style="font-size:14px; color:#374151; margin:0;">초기 2019년 호르무즈 위기 국면을 제외하고, 5개 대형 지정학 위기 국면에서 하방 분위수(τ ≤ 0.10)로 진입할수록 BTC의 주식 베타(β_τ)는 강력한 양(+)의 값으로 급증했습니다. 시장 폭락기 분산 능력을 보는 <b>C2 조건을 5/6 확률로 실패</b>하여 위험자산(Risky Asset)에 부합함을 계량적으로 입증했습니다. 수익률 방향(C1, C2) 분석을 넘어 변동성 전이 계수를 측정하고자 <b>C3 GARCH-X</b> 검증으로 이행합니다.</p>
        </div>
    """, unsafe_allow_html=True)

def render_garch() -> None:
    st.header("GARCH-X & EGARCH Robustness")
    st.markdown("""
        <div style="background:#F0FDF4; border-left:6px solid #16A34A; padding:18px 22px; border-radius:8px; margin-bottom:20px;">
            <p style="font-size:17px; font-weight:700; color:#14532D; margin:0 0 6px 0;">분석 배경 및 목적 — C3 변동성 전이 및 리스크 독립성 검증</p>
            <p style="font-size:15px; color:#1f2937; margin:0;">수익률의 방향 분석(C1, C2) 결과 비트코인은 위험자산 동조화를 보였다. C3 단계는 자산의 분산(Variance), 즉 위험의 절대적 크기 차원에서 분석을 수행한다. 진정한 안전자산은 전쟁 리스크(GPR)가 스파이크를 쳐도 자산 시스템 자체의 조건부 변동성이 자극받지 않고 독립적이어야 한다(γ 비유의). 외생적 위험(Custom GPR)과 자산 내부의 과열·공포 심리 변수를 조건부 분산식에 결합하여 영향력을 최종 분리한다.</p>
        </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("최적 변동성 모델", "Model3 (EGARCH)")
    c2.metric("Lowest AIC Score", "9578.71")
    c3.metric("Persistence (α + β)", "0.996")
    c4.metric("지배적 내생 변수", "Fear & Greed")
    c5.metric("GPR 변동성 효과", "비유의 (Non-Sig)")
    st.divider()

    st.markdown("### 계량 모델 공식 (Specification)")
    st.markdown("**1. 평균 방정식 (Mean Equation)**")
    st.latex(r"R_{\text{BTC}, t} = \mu + \varepsilon_t, \quad \varepsilon_t \sim \text{ged}(0, h_t)")
    st.markdown("**2. 조건부 분산 방정식 (Model3: EGARCH Variance Equation)**")
    st.latex(r"\ln(h_t) = \omega + \alpha \left( \left| \frac{\varepsilon_{t-1}}{\sqrt{h_{t-1}}} \right| - E\left| \frac{\varepsilon_{t-1}}{\sqrt{h_{t-1}}} \right| \right) + \beta \ln(h_{t-1}) + \gamma_1 \mathrm{VIX}_{t-1} + \gamma_2 \mathrm{FearGreed}_{t-1}")
    st.caption("수식 통제: 독립변수들의 동시성 결합으로 인한 편향 및 내생성 문제를 차단하기 위해 외생 제어변수인 VIX와 Fear&Greed 지수를 모두 1시차 전일 변수(t-1) 체제로 통일하여 모형의 엄밀성을 확보함.")

    st.divider()
    st.markdown("## A. GARCH 추정 조건부 변동성 추세 시계열")
    img = load_image("garch/result_csv_png/garch_conditional_vol.png")
    if img: st.image(img, caption="시간 가변적 BTC 조건부 변동성 σ(t) 추정 경로", use_column_width=True)

    event_vol = load_csv("garch/result_csv_png/garch_event_volatility.csv")
    if event_vol is not None:
        fig = px.bar(event_vol, x="event", y="max_volatility", color="model", barmode="group", title="이벤트 구간별 BTC 최대 조건부 변동성 폭 대비")
        st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.markdown("## B. 정보손실 기준 모델 적합도 비교 수치")
    col1, col2 = st.columns([1.4, 1])
    with col1:
        img = load_image("garch/result_csv_png/garch_model_comparison.png")
        if img: st.image(img, caption="정보손실 계수(AIC/BIC) 기준 모델 비교", use_column_width=True)
    with col2:
        ranking = load_csv("garch/result_csv_png/garch_model_ranking.csv")
        if ranking is not None:
            top3 = ranking.head(3)
            st.metric("최적 모델 (Lowest AIC)", top3.iloc[0]["model"])
            st.metric("차석 모델", top3.iloc[1]["model"])
            st.metric("삼석 모델", top3.iloc[2]["model"])

    st.divider()
    st.markdown("## C. 외생 요인별 영향력 계수 파라미터 분석")
    col1, col2 = st.columns(2)
    with col1:
        img = load_image("garch/result_csv_png/garch_gamma_coefficients.png")
        if img: st.image(img, caption="외생 변수별 Gamma 계수 신뢰구간 플롯", use_column_width=True)
    with col2:
        gamma = load_csv("garch/result_csv_png/garch_gamma_long.csv")
        if gamma is not None and "coef" in gamma.columns:
            fig = px.scatter(gamma, x="coef", y="var", color="model", size=np.abs(gamma["coef"]),
                            hover_data=["pvalue"], title="Interactive Gamma Effect 및 P-value 분포")
            fig.add_vline(x=0, line_dash="dash")
            st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.markdown("## D. 변동성 지속성 및 비대칭 강건성 검정 (EGARCH)")
    persist = load_csv("garch/result_csv_png/garch_persistence.csv")
    if persist is not None:
        fig = px.bar(persist, x="model", y="alpha_plus_beta", color="alpha_plus_beta", title="변동성 지속성 강도 (Persistence: α + β)")
        fig.add_hline(y=1, line_dash="dash", line_color="red")
        st.plotly_chart(fig, use_container_width=True)

    with st.expander("EGARCH 비대칭 정보 반응 및 다차원 통합 검정 구조 트리맵 확인", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            img = load_image("garch/result_csv_png/egarch_model_aic_bic.png")
            if img: st.image(img, use_column_width=True)
        with col2:
            img = load_image("garch/result_csv_png/egarch_cond_vol_comparison.png")
            if img: st.image(img, use_column_width=True)
        with col3:
            img = load_image("garch/result_csv_png/egarch_gpr_coef_compare.png")
            if img: st.image(img, use_column_width=True)

        integrated = load_csv("garch/result_csv_png/garch_egarch_integrated_summary.csv")
        if integrated is not None:
            fig = px.treemap(integrated, path=["section", "model"], values="AIC", color="AIC", title="연구 모형 강건성 다단계 구조 맵")
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
        <div style="background:#F0FDF4; border-left:6px solid #16A34A; padding:18px 22px; border-radius:8px; margin-top:20px;">
            <p style="font-size:18px; font-weight:700; color:#14532D; margin:0 0 8px 0;">C3 GARCH-X 판정 요약</p>
            <p style="font-size:14px; color:#374151; margin:0;">변동성 분석 결과 외부적인 지정학 충격 변수인 Custom GPR 지수는 비트코인의 고유 조건부 분산을 확대하는 데 통계적 영향력이 전무(γ 비유의)했습니다. 비트코인의 리스크 확산을 지배하는 핵심 독립변수는 내부 투자자들의 과열 및 공포 상태인 내생 심리 변수(Fear &amp; Greed)임이 확인되어, 외부 위기 자극에 변동성이 흔들리지 않는 독립적 구조 자산이라는 <b>C3 조건을 최종 충족</b>했습니다.</p>
        </div>
    """, unsafe_allow_html=True)

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
        key="nav_section",
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
