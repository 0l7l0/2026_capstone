from pathlib import Path
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import warnings

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[1]

EVENT_LABEL = {
    "hormuz_crisis":          "호르무즈 위기",
    "soleimani_assassination": "솔레이마니 암살",
    "russia_ukraine_war":      "러-우 전쟁",
    "israel_hamas_war":        "이스라엘-하마스",
    "israel_iran":             "이스라엘-이란",
    "us_israel_iran":          "미-이스라엘-이란",
}
EVENT_DATE = {
    "hormuz_crisis":          "2019-06-13",
    "soleimani_assassination": "2020-01-03",
    "russia_ukraine_war":      "2022-02-24",
    "israel_hamas_war":        "2023-10-07",
    "israel_iran":             "2024-04-14",
    "us_israel_iran":          "2026-02-28",
}
ASSET_COLORS = {
    "BTC": "#F7931A", "Gold": "#FFD700",
    "SP500": "#1976D2", "NASDAQ": "#7B1FA2",
    "TLT": "#388E3C", "DXY": "#E64A19",
}
VERDICT_COLOR = {
    "Safe Haven": "#2E7D32",
    "Weak Haven": "#F9A825",
    "Risky Asset": "#C62828",
}


@st.cache_data
def load_csv(rel: str) -> pd.DataFrame | None:
    p = ROOT / rel
    return pd.read_csv(p) if p.exists() else None


def load_img(rel: str) -> str | None:
    p = ROOT / rel
    return str(p) if p.exists() else None


def section(title: str, color: str = "#2563EB") -> None:
    """섹션 제목 렌더링"""
    st.markdown(
        f"<h3 style='margin:0 0 4px;color:{color};'>{title}</h3>"
        f"<hr style='margin:0 0 16px;border:none;border-top:2px solid {color};opacity:.25;'>",
        unsafe_allow_html=True,
    )


def kpi(cols, items: list[tuple[str, str]]) -> None:
    """(레이블, 값) 리스트를 metric 카드로 렌더링"""
    for col, (label, val) in zip(cols, items):
        col.metric(label, val)


def verdict_badge(v: str) -> str:
    c = VERDICT_COLOR.get(v, "#888")
    return (
        f"<span style='background:{c};color:white;padding:3px 10px;"
        f"border-radius:6px;font-size:12px;font-weight:700;'>{v}</span>"
    )


# ──────────────────────────────────────────────
# 탭 1 — 통합 판정
# ──────────────────────────────────────────────
def tab_overview() -> None:

    st.markdown("""
    <div style="padding:20px 0 10px;">
        <p style="font-size:13px;color:#6B7280;margin:0;">비트코인은 안전자산인가?</p>
        <h2 style="font-size:28px;font-weight:800;margin:4px 0 8px;color:#111827;">
            BTC는 전쟁보다 시장 심리에 더 민감하게 반응했습니다
        </h2>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    final = pd.read_csv(ROOT / "validationfinal/final_judgment.csv")
    verdict_counts = final["verdict"].value_counts()
    safe_cnt = int(verdict_counts.get("Safe Haven*", 0))
    weak_cnt = int(verdict_counts.get("Weak Haven", 0))
    div_cnt = int(verdict_counts.get("Diversifier", 0))
    overall = verdict_counts.idxmax()

    if overall == "Safe Haven*":
        verdict_color, verdict_border = "#2563EB", "#93C5FD"
    elif overall == "Weak Haven":
        verdict_color, verdict_border = "#16A34A", "#86EFAC"
    else:
        verdict_color, verdict_border = "#DC2626", "#FCA5A5"

    st.markdown("""
    <style>
    .metric-card{background:white;border-radius:18px;padding:18px 20px;min-height:130px;box-shadow:0 2px 10px rgba(0,0,0,0.05);}
    .metric-card.blue{border:1.8px solid #93C5FD;}
    .metric-card.green{border:1.8px solid #86EFAC;}
    .metric-card.red{border:1.8px solid #FCA5A5;}
    .metric-title{font-size:24px;font-weight:700;margin-bottom:12px;}
    .metric-value{font-size:32px;font-weight:900;line-height:1.1;margin-bottom:10px;}
    .metric-desc{font-size:14px;font-weight:500;}
    </style>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(f"""<div class="metric-card" style="border:1.8px solid {verdict_border};"><div class="metric-title" style="color:{verdict_color};">최종 판정</div><div class="metric-value" style="color:{verdict_color};">{overall}</div><div class="metric-desc" style="color:{verdict_color};">가장 빈번한 이벤트 판정</div></div>""", unsafe_allow_html=True)

    with c2:
        st.markdown(f"""<div class="metric-card blue"><div class="metric-title" style="color:#2563EB;">Safe Haven*</div><div class="metric-value" style="color:#2563EB;">{safe_cnt}</div><div class="metric-desc" style="color:#2563EB;">3조건 모두 충족</div></div>""", unsafe_allow_html=True)

    with c3:
        st.markdown(f"""<div class="metric-card green"><div class="metric-title" style="color:#16A34A;">Weak Haven</div><div class="metric-value" style="color:#16A34A;">{weak_cnt}</div><div class="metric-desc" style="color:#16A34A;">일부 조건 충족</div></div>""", unsafe_allow_html=True)

    with c4:
        st.markdown(f"""<div class="metric-card red"><div class="metric-title" style="color:#DC2626;">Diversifier</div><div class="metric-value" style="color:#DC2626;">{div_cnt}</div><div class="metric-desc" style="color:#DC2626;">안전자산 조건 미충족</div></div>""", unsafe_allow_html=True)

    st.divider()
    section("BTC vs Gold vs S&P500 — 누적 로그 수익률")
    returns = load_csv("DataPipeline/processed_data/market_returns.csv")
    if returns is not None:
        returns["date"] = pd.to_datetime(returns["date"])
        fig = go.Figure()
        for asset, color in [("BTC", "#F7931A"), ("Gold", "#FFD700"), ("SP500", "#1E88E5")]:
            cum = np.log1p(returns[asset]).cumsum()
            fig.add_trace(go.Scatter(
                x=returns["date"], y=cum, name=asset,
                line=dict(width=2.5, color=color),
                hovertemplate="<b>%{fullData.name}</b><br>%{x|%Y-%m-%d}<br>%{y:.3f}<extra></extra>",
            ))
        for key, date in EVENT_DATE.items():
            fig.add_vline(x=pd.to_datetime(date), line_dash="dot",
                          line_color="red", opacity=0.5)
            fig.add_annotation(
                x=pd.to_datetime(date), y=returns["BTC"].apply(np.log1p).cumsum().max(),
                text=EVENT_LABEL[key], showarrow=False,
                textangle=-90, font=dict(size=9, color="red"), yshift=6,
            )
        fig.update_layout(
            template="plotly_dark", height=420,
            hovermode="x unified",
            legend=dict(orientation="h", y=1.08, x=1, xanchor="right"),
            xaxis_title="", yaxis_title="누적 로그 수익률",
            margin=dict(l=10, r=10, t=20, b=10),
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("market_returns.csv 파일을 확인해주세요.")

    st.divider()

    VERDICT_COLOR = {
        "Safe Haven*": "#2563EB",
        "Weak Haven": "#16A34A",
        "Diversifier": "#DC2626",
    }

    section("이벤트별 통합 평가 매트릭스")

    if final is not None:

        def icon(v):
            return "✅" if v else "❌"

        df = pd.DataFrame({
            "이벤트": final["event_label"],
            "C1 이벤트 스터디": final["C1_event_study_pass"].apply(icon),
            "C2 분위수 회귀": final["C2_quantile_reg_pass"].apply(icon),
            "C3 GARCH": final["C3_garch_pass"].apply(icon),
            "최종 판정": final["verdict"],
        })

        styled = df.style.map(
            lambda x: (
                f"background-color:{VERDICT_COLOR.get(x,'#444')};"
                "color:white;"
                "font-weight:bold;"
            ),
            subset=["최종 판정"],
        )

        st.dataframe(
            styled,
            use_container_width=True,
            hide_index=True,
        )

        st.caption(
            "✅ Safe-Haven 방향 특성 확인  |  ❌ 해당 조건 미충족"
        )

    else:
        st.info("final_judgment.csv 파일을 확인해주세요.")
    st.divider()

    st.info("""
    **최종 결론**

    📈 이벤트 스터디(C1): 6개 이벤트 중 4건에서 양(+) CAR 관측

    📉 분위수 회귀(C2): 하방 극단 구간에서 5개 이벤트가 주식시장과 동조화

    ⚡ GARCH(C3): GPR 계수는 전 모델에서 비유의 → BTC 변동성 설명력 제한

    🎯 종합적으로 BTC는 Safe Haven으로 보기 어렵고,
    본 연구에서는 **Weak Haven(조건부 안전자산)** 성격이 가장 우세하게 나타남
    """)


# ──────────────────────────────────────────────
# 탭 2 — GPR 파이프라인
# ──────────────────────────────────────────────
def tab_gpr() -> None:
    section("Custom GPR 파이프라인 개요", "#6B7280")
    st.markdown("""
    > 기존 Caldara & Iacoviello GPR은 **월 단위** 집계 → 단기 이벤트 창(±17 거래일) 분석 불가  
    > GDELT GKG 빅데이터를 활용해 **일별 Custom GPR** 자체 구축
    """)

    st.markdown("""
    <style>
    [data-testid="stMetricLabel"] {
        font-size: 25px !important;
        font-weight: 800 !important;
    }

    [data-testid="stMetricValue"] {
        font-size: 32px !important;
        font-weight: 700 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    corr = pd.read_csv(
        "./DataPipeline/processed_data/final/gpr_correlation_summary.csv"
    )

    event_cnt = corr["event"].nunique()

    f3 = corr[corr["formula"] == "F3_z"]

    gpr_r = f3["pearson_r"].mean()

    c1.metric("수집 기사 수", "약 734만 건")
    c2.metric("분석 이벤트", f"{event_cnt}개")
    c3.metric("공식 GPR 상관", f"r = {gpr_r:.2f}")

    st.divider()

    t1, t2, t3 = st.tabs(["① 수집 · 정제", "② GPR 공식 설계", "③ 금융 통합 데이터"])

    with t1:
        section("전처리 흐름 & 정제 결과", "#6B7280")
        col1, col2 = st.columns([1, 1])
 
        with col1:
            steps = [
                    ("#EFF6FF", "#BFDBFE", "1️⃣ URL 중복 제거"),
                    ("#F0FDF4", "#BBF7D0", "2️⃣ Tone 결측치 제거"),
                    ("#FEF2F2", "#FECACA", "3️⃣ Tone 이상값 제거 (|Tone| ≤ 20)"),
                    ("#FFF7ED", "#FED7AA", "4️⃣ GEO_THEMES 기반 지정학 필터링"),
                    ("#F5F3FF", "#DDD6FE", "5️⃣ 일별 기사 수 집계"),
                    ("#ECFEFF", "#A5F3FC", "6️⃣ 최소 기사 수 조건 (일 5건 이상)")
                ]

            inner = ""
            for i, (bg, border, label) in enumerate(steps):
                inner += (
                    f"<div style='width:500px;"
                    f"padding:18px 24px;border-radius:12px;"
                    f"background:{bg};border:1.5px solid {border};"
                    f"text-align:center;font-weight:700;font-size:15px;"
                    f"box-shadow:0 2px 8px rgba(0,0,0,0.06);'>"
                    f"{label}</div>"
                )
                if i < len(steps) - 1:
                    inner += (
                        "<div style='font-size:26px;color:#9CA3AF;"
                        "line-height:1.8;'>↓</div>"
                    )
            st.markdown(
                "<div style='"
                "display:flex;flex-direction:column;"
                "align-items:center;justify-content:center;"
                "gap:2px;padding:16px 0;'>"
                + inner +
                "</div>",
                unsafe_allow_html=True,
            )
 
        with col2:
            img = load_img("FIGURES/02-1_hormuz_preprocessed.png")
            if img:
                st.markdown(
                    "<div style='display:flex;flex-direction:column;"
                    "align-items:center;justify-content:center;height:100%;padding:16px 0;'>",
                    unsafe_allow_html=True,
                )
                if img: 
                    st.image( img, width=600, caption="전처리 전후 기사량·Tone 분포 비교" )
                st.markdown("</div>", unsafe_allow_html=True)
 

        st.success(
            "✅ 전처리 이후에도 Tone 분포와 기사량 구조가 안정적으로 유지되어 이벤트 분석에 적합한 데이터 품질을 확보"
        )
  
    with t2:
        section("후보 공식 비교 및 F3 채택 근거", "#6B7280")

        formula_df = pd.DataFrame({
            "모델": ["F1", "F2", "F3 ✅", "F4", "F5"],
            "설계 방식": ["Tone Mean", "Polarity Weighted", "Tone × Relative Volume", "Negative Ratio", "28D EWMA"],
            "설명": [
                    "평균 Tone 기반 감성지수",
                    "Polarity 가중 감성지수",
                    "Tone과 상대 보도량을 결합한 최종 채택 GPR",
                    "부정 기사 비중 기반 지수",
                    "F2의 28일 EWMA 평활화"
                ],
        })
        st.dataframe(formula_df, use_container_width=True, hide_index=True)
        st.latex(r"\mathrm{Custom\,GPR}_{F3} = -\overline{\mathrm{tone}} \times \log\!\left(1 + \frac{N}{\bar{N}}\right)")
        st.caption("음(−)의 Tone과 상대 기사량을 결합한 GPR 지수. 위기 보도 증가 시 상승하며, 로그 스케일로 기사량 급증의 영향을 완화")

        img_heatmap = load_img("FIGURES/03_correlation_heatmap.png")
        gpr_m = f3["pearson_r"].max()
        if img_heatmap:
            _, c_mid, _ = st.columns([0.5, 9, 0.5])
            with c_mid:
                st.image(img_heatmap,
                         caption=f"공식 GPR vs Custom GPR 상관관계 히트맵 (F3: r={gpr_m:.2f} 최고)",
                         use_container_width=True)
 
        st.divider()
 
        with st.expander("📊 공식 GPR vs Custom GPR(F3) 이벤트 윈도우 반응 비교", expanded=True):
            img_window = load_img("FIGURES/07_event_window.png")
            if img_window:
                _, c_mid2, _ = st.columns([1, 8, 1])
                with c_mid2:
                    st.image(img_window,
                             caption="이벤트별 공식 GPR vs Custom GPR(F3) 반응 비교",
                             use_container_width=True)

    with t3:
        section("Master Dataset 구성", "#6B7280")

        market_df = pd.DataFrame({
                "자산": ["Bitcoin",
                    "Gold",
                    "TLT",
                    "DXY",
                    "S&P500",
                    "NASDAQ",
                    "VIX"
                ],
                "Ticker": [
                    "BTC-USD",
                    "GC=F",
                    "TLT",
                    "DX-Y.NYB",
                    "^GSPC",
                    "^IXIC",
                    "^VIX"
                ],
                "역할": [
                    "Safe Haven 검증 대상",
                    "전통 안전자산 Benchmark",
                    "미국 장기국채 ETF Proxy",
                    "달러 강세 Proxy",
                    "미국 주식시장 Benchmark",
                    "기술주 중심 주식시장 Benchmark",
                    "시장 공포·변동성 지표"
                ],
            })
        st.dataframe(market_df, use_container_width=True, hide_index=True)

        st.info(
            "**거래일 정렬(Trading-Day Alignment)**: BTC의 주말 수익률은 "
            "다음 거래일에 누적 반영하여 주식·채권·달러 지수와 동일한 거래일 기준으로 정렬"
        )

        master_path = ROOT / "DataPipeline/processed_data/final/master_data.csv"

        if master_path.exists():
            master_df = pd.read_csv(master_path)

            asset_cols = [
                "BTC", "Gold", "TLT",
                "DXY", "SP500", "NASDAQ"
            ]

            indicator_cols = [
                "VIX"
            ]

            asset_cnt = sum(col in master_df.columns for col in asset_cols)
            indicator_cnt = sum(col in master_df.columns for col in indicator_cols)

            c1, c2, c3, c4 = st.columns(4)

            c1.metric("관측치", f"{len(master_df):,}")
            c2.metric("데이터 컬럼", master_df.shape[1])
            c3.metric("비교 자산", asset_cnt)
            c4.metric("시장 지표", indicator_cnt)
            with st.expander("Master Dataset 샘플 미리보기"):
                st.dataframe(master_df.head(10), use_container_width=True, hide_index=True)


# ──────────────────────────────────────────────
# 탭 3 — EDA
# ──────────────────────────────────────────────
def tab_eda() -> None:
    section("탐색적 데이터 분석 (EDA)", "#7C3AED")
    st.caption("통계 모형 도입의 정당성 확보 — Fat-tail·변동성 군집 확인")

    # ── 기초 수치 ──
    returns = load_csv("EDA/result_csv_png/returns.csv")
    if returns is not None and "BTC" in returns.columns:
        c1, c2, c3 = st.columns(3)
        c1.metric("BTC 평균 수익률", f"{returns['BTC'].mean():.4f}")
        c2.metric("BTC 일별 변동성", f"{returns['BTC'].std():.4f}")
        c3.metric("관측치 수", f"{len(returns):,}")

    st.divider()

    t1, t2, t3 = st.tabs(["① 수익률 분포", "② 상관관계 변화", "③ 기술통계"])

    with t1:
        section("수익률 분포 & 변동폭", "#7C3AED")
 
        img_dist = load_img("EDA/result_csv_png/plot4_returns_dist.png")
        if img_dist:
            _, c_mid, _ = st.columns([0.5, 9, 0.5])
            with c_mid:
                st.image(img_dist,
                         caption="자산별 수익률 분포 — Fat-Tail 확인",
                         use_container_width=True)
 
        st.divider()
 
        with st.expander("📊 BTC 일별 High-Low 변동폭", expanded=True):
            img_hl = load_img("EDA/result_csv_png/plot5_btc_highlow.png")
            if img_hl:
                _, c_mid2, _ = st.columns([1, 8, 1])
                with c_mid2:
                    st.image(img_hl,
                             caption="BTC 일별 High-Low 변동폭",
                             use_container_width=True)
 
        st.success("✅ BTC 수익률은 높은 첨도(Fat Tail)와 변동성 군집(Volatility Clustering)을 보여 정규성 가정을 만족하지 않으며, 이에 따라 GARCH 계열 모형을 적용하였다.")

    with t2:
        section("전쟁 전후 상관관계 구조 변화", "#7C3AED")
 
        img_corr = load_img("EDA/result_csv_png/plot6_corr_heatmap.png")
        if img_corr:
            _, c_mid, _ = st.columns([0.5, 9, 0.5])
            with c_mid:
                st.image(img_corr,
                         caption="전체 기간 대비 전쟁 국면 상관관계 비교",
                         use_container_width=True)
 
        st.divider()
 
        with st.expander("📊 BTC 30일 롤링 상관관계", expanded=True):
            img_roll = load_img("EDA/result_csv_png/plot8_rolling_corr.png")
            if img_roll:
                _, c_mid2, _ = st.columns([1, 8, 1])
                with c_mid2:
                    st.image(img_roll,
                             caption="BTC vs 주요 자산 30일 롤링 상관관계",
                             use_container_width=True)
 
        st.warning("전쟁 기간 동안 BTC는 주식시장과의 상관성이 증가하여 Safe Haven 특성이 약화되는 모습을 보임")

    with t3:
        section("기술통계 요약", "#7C3AED")
        if returns is not None:
            st.dataframe(returns.describe().round(4), use_container_width=True)
        else:
            st.info("returns.csv 파일을 확인해주세요.")


# ──────────────────────────────────────────────
# 탭 4 — 이벤트 스터디
# ──────────────────────────────────────────────
def tab_event_study() -> None:
    section("이벤트 스터디 — C1 평균적 초과수익률 검증", "#2563EB")
    st.caption("MacKinlay(1997) CAR/CSAR · BH-FDR 다중비교 보정 · Placebo 검정")

    event = pd.read_csv(ROOT / "validationfinal/event_study_car_bh.csv")
    placebo = pd.read_csv(ROOT / "validationfinal/event_study_placebo.csv")

    btc = event[event["asset"] == "BTC"].copy()

    btc_total = len(btc)

    positive_car = (btc["CAR"] > 0).sum()

    strong_safe = (
        (btc["CAR"] > 0) &
        (btc["sig_bh"] == True)
    ).sum()

    bh_sig = btc["sig_bh"].sum()

    placebo_sig = (
        placebo["placebo_p"] < 0.05
    ).sum()

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("양(+) CAR 이벤트", f"{positive_car} / {btc_total}")
    c2.metric("Strong Safe Haven", f"{strong_safe} / {btc_total}")
    c3.metric("BH-FDR 유의", f"{bh_sig} / {btc_total}")
    c4.metric("Placebo 유의", f"{placebo_sig} / {len(placebo)}")
    st.divider()

    t1, t2, t3 = st.tabs(["① CAR 추이", "② 자산별 CAR 비교", "③ 강건성 검정"])

    with t1:
        img = load_img("EventStudy/result_csv_png/event_study_CAR_timeseries.png")
        if img:
            _, c_mid2, _ = st.columns([2, 6, 2])
            with c_mid2:
                st.image(img, caption="이벤트별 CAR 누적 추이 (±17 거래일)", use_container_width=True)
        else:
            st.info("이미지 파일을 확인해주세요.")

    with t2:
        if event is not None:
            event["event_label"] = event["event"].map(EVENT_LABEL).fillna(event["event"])
            assets = sorted(event["asset"].dropna().unique())
            default = [a for a in ["BTC", "Gold"] if a in assets] or assets[:2]
            selected = st.multiselect("자산 필터", assets, default=default)
            sub = event[event["asset"].isin(selected)]
            fig = px.bar(
                sub, x="event_label", y="CAR", color="asset", barmode="group",
                color_discrete_map=ASSET_COLORS,
                labels={"event_label": "이벤트", "CAR": "CAR"},
            )
            fig.add_hline(y=0, line_color="white", line_width=1)
            fig.update_layout(height=420, template="plotly_dark",
                              margin=dict(l=10, r=10, t=20, b=10))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("event_study_car_bh.csv 파일을 확인해주세요.")

    with t3:
        col1, col2 = st.columns(2)
        with col1:
            section("BH-FDR 보정 결과", "#2563EB")
            if event is not None:
                event["event_label"] = event["event"].map(EVENT_LABEL).fillna(event["event"])
                keep = [c for c in ["event_label", "asset", "CAR", "p_norm", "p_norm_bh", "sig_bh"]
                        if c in event.columns]
                st.dataframe(event[keep].round(4), use_container_width=True, hide_index=True)
        with col2:
            section("Placebo 검정 결과", "#2563EB")
            if placebo is not None:
                placebo["event_label"] = (
                    placebo["event_name"].map(EVENT_LABEL).fillna(placebo["event_name"])
                )
                placebo = placebo.dropna(subset=["real_CAR", "percentile_of_real"])
                fig = px.bar(
                    placebo.sort_values("percentile_of_real"),
                    x="percentile_of_real", y="event_label", orientation="h",
                    color="percentile_of_real", color_continuous_scale="Blues",
                    text="percentile_of_real",
                    labels={"percentile_of_real": "Percentile", "event_label": ""},
                )
                fig.update_traces(texttemplate="%{text:.0%}", textposition="outside")
                fig.add_vline(x=0.95, line_dash="dash", line_color="red",
                              annotation_text="p=0.05", annotation_position="top")
                fig.update_layout(height=320, template="plotly_dark",
                                  coloraxis_showscale=False,
                                  margin=dict(l=10, r=10, t=10, b=10))
                st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
    <div style="background:#EFF6FF;border-left:5px solid #2563EB;padding:14px 18px;border-radius:6px;margin-top:8px;">
        <b>C1 판정:</b> BTC는 6개 이벤트 중 4개에서 양(+) CAR를 기록했으나,
        BH-FDR 보정 후 모든 이벤트가 비유의로 나타났다.
        따라서 전쟁 충격 시 일관된 초과수익을 제공한다는 통계적 증거는 확인되지 않았다.
    </div>
    """, unsafe_allow_html=True)


# ──────────────────────────────────────────────
# 탭 5 — 분위수 회귀
# ──────────────────────────────────────────────
def tab_quantile() -> None:
    section("분위수 회귀 — C2 극단 하락 구간 Safe Haven 검증", "#EA580C")
    st.caption("Koenker & Bassett(1978) · τ≤0.10 영역 β_τ < 0 조건 · GPR 상호작용항")

    qr = pd.read_csv(ROOT / "Quantile/result_csv_png/quantreg_results.csv")

    low_tau = qr[(qr["scope"] == "이벤트별") & (qr["tau"] <= 0.10)].copy()

    event_results = []

    for ev in sorted(low_tau["event"].unique()):
        tmp = low_tau[low_tau["event"] == ev]

        safe = ((tmp["beta_sp500"] < 0) & (tmp["p_beta"] < 0.05)).any()
        risky = ((tmp["beta_sp500"] > 0) & (tmp["p_beta"] < 0.05)).any()

        if safe:
            label = "Safe Haven"
        elif risky:
            label = "Risky Asset"
        else:
            label = "Insignificant"

        event_results.append({"event": ev, "label": label})

    event_results = pd.DataFrame(event_results)

    safe_cnt = event_results["label"].eq("Safe Haven").sum()
    risky_cnt = event_results["label"].eq("Risky Asset").sum()
    total_event = len(event_results)

    positive_beta_events = []

    for ev in low_tau["event"].unique():
        tmp = low_tau[low_tau["event"] == ev]

        if ((tmp["beta_sp500"] > 0) & (tmp["p_beta"] < 0.05)).any():
            positive_beta_events.append(ev)

    beta_msg = "전 이벤트" if len(positive_beta_events) == total_event else f"{len(positive_beta_events)} / {total_event}"

    gpr_sig = (low_tau["p_gamma"] < 0.05).sum()
    gpr_msg = "비유의" if gpr_sig == 0 else f"{gpr_sig}건 유의"

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Safe Haven 이벤트", f"{safe_cnt} / {total_event}")
    c2.metric("위험자산 동조화", f"{risky_cnt} / {total_event}")
    c3.metric("주요 설명 변수", "SP500")
    c4.metric("GPR 직접 효과", gpr_msg)

    st.divider()
    st.latex(
        r"Q_\tau(R_{\mathrm{BTC},t}|X_t) = "
        r"\alpha_\tau + \beta_\tau R_{\mathrm{SP500},t} + "
        r"\gamma_\tau \mathrm{GPR}_t + "
        r"\delta_\tau (R_{\mathrm{SP500},t} \times \mathrm{GPR}_t)"
    )
    st.caption("τ 하락 시 β_τ 음(−) 또는 비유의여야 Safe Haven 성립")
    st.divider()

    t1, t2, t3 = st.tabs(["① Beta 경로 분석", "② 판정 히트맵", "③ 강건성 검정"])

    with t1:
        col1, col2 = st.columns(2)
        with col1:
            img = load_img("Quantile/result_csv_png/quantreg_beta_path.png")
            if img:
                st.image(img, caption="기본 모델 분위수 β 경로", use_container_width=True)
        with col2:
            img = load_img("Quantile/result_csv_png/quantreg_beta_path_ia.png")
            if img:
                st.image(img, caption="상호작용항 포함 β 경로", use_container_width=True)
        beta_csv = load_csv("Quantile/result_csv_png/quantreg_beta_path.csv")
        if beta_csv is not None and "tau" in beta_csv.columns and "beta" in beta_csv.columns:
            fig = px.line(beta_csv, x="tau", y="beta",
                          labels={"tau": "분위수 τ", "beta": "β (SP500 계수)"},
                          title="τ↓ → β 급증 확인")
            fig.add_hline(y=0, line_dash="dash", line_color="red")
            fig.update_layout(height=280, template="plotly_dark",
                              margin=dict(l=10, r=10, t=30, b=10))
            st.plotly_chart(fig, use_container_width=True)

    with t2:
        col1, col2 = st.columns(2)
        with col1:
            img = load_img("Quantile/result_csv_png/quantreg_heatmap.png")
            if img:
                st.image(img, caption="기본 모형 판정 히트맵", use_container_width=True)
        with col2:
            img = load_img("Quantile/result_csv_png/quantreg_heatmap_ia.png")
            if img:
                st.image(img, caption="상호작용항 포함 판정 히트맵", use_container_width=True)

    with t3:
        t3a, t3b, t3c = st.tabs(["GPR 변수 제외", "Leave-One-Out", "Min-Max 변환"])
        csvs = [
            ("Quantile/result_csv_png/robust_iv.csv",  t3a),
            ("Quantile/result_csv_png/robust_loo.csv", t3b),
            ("Quantile/result_csv_png/robust_mm.csv",  t3c),
        ]
        for path, tab in csvs:
            with tab:
                df = load_csv(path)
                if df is not None:
                    st.dataframe(df, use_container_width=True, hide_index=True)
                else:
                    st.info(f"{path} 파일을 확인해주세요.")

    st.markdown("""
    <div style="background:#FFF7ED;border-left:5px solid #EA580C;padding:14px 18px;border-radius:6px;margin-top:8px;">
        <b>C2 판정: 하방 극단 구간에서 BTC는 주식시장과 동조화되는 경향을 보여 6개 이벤트 중 5개에서 Safe Haven 기준을 충족하지 못함
    </div>
    """, unsafe_allow_html=True)


# ──────────────────────────────────────────────
# 탭 6 — GARCH
# ──────────────────────────────────────────────
def tab_garch() -> None:
    section("GARCH-X & EGARCH — C3 변동성 전이 검증", "#16A34A")
    st.caption("조건부 분산식에 Custom GPR + VIX + Fear&Greed 결합 · AIC/BIC 모델 선정")

    comp = pd.read_csv(ROOT / "GARCH/result_csv_png/garch_model_comparison.csv")
    persist = pd.read_csv(ROOT / "GARCH/result_csv_png/garch_persistence.csv")
    gamma = pd.read_csv(ROOT / "GARCH/result_csv_png/garch_gamma_results.csv")

    best_row = comp.loc[comp["AIC"].idxmin()]
    best_model = best_row["모델"]
    best_name = best_row["설명"]
    best_aic = best_row["AIC"]

    persist_row = persist.loc[persist["model"] == best_model]
    ab = persist_row["alpha_plus_beta"].iloc[0] if len(persist_row) else np.nan

    gpr_rows = gamma[gamma["variable"].str.contains("GPR", case=False, na=False)]
    gpr_sig = (gpr_rows["p_value"] < 0.05).any()
    gpr_msg = "유의" if gpr_sig else "비유의"

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("최적 모델", best_name)
    c2.metric("Lowest AIC", f"{best_aic:,.2f}")
    c3.metric("Persistence (α+β)", f"{ab:.3f}")
    c4.metric("GPR 변동성 효과", gpr_msg)

    st.divider()

    st.markdown("**조건부 분산 방정식 — GARCH(Model 3)**")

    st.latex(
        r"h_t = \omega + \alpha \varepsilon_{t-1}^{2}"
        r" + \beta h_{t-1}"
        r" + \gamma_1 \mathrm{VIX}_{t-1}"
        r" + \gamma_2 \mathrm{FearGreed}_{t-1}"
    )

    st.latex(
        r"\frac{\varepsilon_t}{\sqrt{h_t}} \sim t(\nu)"
    )
    st.caption("α+β≈0.995 → BTC 변동성 충격이 장기간 지속되는 Near-IGARCH 구조")
    st.divider()

    t1, t2, t3 = st.tabs(["① 조건부 변동성", "② 모델 적합도 비교", "③ 외생 효과 (γ)"])

    with t1:

        img = load_img("GARCH/result_csv_png/garch_conditional_vol.png")
        if img:
            _, c_mid, _ = st.columns([2, 6, 2])
            with c_mid:
                st.image(img, caption="BTC 조건부 변동성 σ(t) 추정 경로", use_container_width=True)
        event_vol = load_csv("GARCH/result_csv_png/garch_event_volatility.csv")
        if event_vol is not None:
            fig = px.bar(
                event_vol, x="event", y="max_volatility",
                color="model", barmode="group",
                labels={"event": "이벤트", "max_volatility": "최대 조건부 변동성"},
            )
            fig.update_layout(height=420, template="plotly_dark",
                              margin=dict(l=10, r=10, t=20, b=10))
            st.plotly_chart(fig, use_container_width=True)

    with t2:
        col1, col2 = st.columns([1.5, 1])
        with col1:
            img = load_img("GARCH/result_csv_png/garch_model_comparison.png")
            if img:
                st.image(img, caption="AIC/BIC 기준 모델 비교", use_container_width=True)
        with col2:
            ranking = load_csv("GARCH/result_csv_png/garch_model_ranking.csv")
            if ranking is not None:
                top3 = ranking.head(3)
                for rank, (_, row) in enumerate(top3.iterrows(), 1):
                    st.metric(f"{rank}위 모델", row["model"])
            persist = load_csv("GARCH/result_csv_png/garch_persistence.csv")
            if persist is not None:
                fig = px.bar(persist, x="model", y="alpha_plus_beta",
                             color="alpha_plus_beta",
                             labels={"alpha_plus_beta": "α + β"},
                             title="변동성 지속성 (α+β)")
                fig.add_hline(y=1, line_dash="dash", line_color="red",
                              annotation_text="1.0 한계")
                fig.update_layout(height=260, template="plotly_dark",
                                  showlegend=False,
                                  margin=dict(l=10, r=10, t=30, b=10))
                st.plotly_chart(fig, use_container_width=True)

    with t3:
        col1, col2 = st.columns(2)
        with col1:
            img = load_img("GARCH/result_csv_png/garch_gamma_coefficients.png")
            if img:
                st.image(img, caption="외생 변수 γ 계수 신뢰구간", use_container_width=True)
        with col2:
            gamma = load_csv("GARCH/result_csv_png/garch_gamma_long.csv")
            if gamma is not None and "coef" in gamma.columns:
                fig = px.scatter(
                    gamma, x="coef", y="var", color="model",
                    size=np.abs(gamma["coef"]),
                    hover_data=["pvalue"],
                    labels={"coef": "γ 계수", "var": "변수"},
                    title="γ 분포 및 p-value",
                )
                fig.add_vline(x=0, line_dash="dash")
                fig.update_layout(height=320, template="plotly_dark",
                                  margin=dict(l=10, r=10, t=30, b=10))
                st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
        <div style="background:#F0FDF4;border-left:5px solid #16A34A;padding:14px 18px;border-radius:6px;margin-top:8px;">
            <b>C3 판정:</b> GPR 및 Custom GPR 변수는 모든 GARCH 모형에서 γ 계수가 <b>비유의</b>.
            반면 Fear &amp; Greed는 반복적으로 유의하여 BTC 변동성은 지정학 리스크보다 시장심리에 더 민감하게 반응함
        </div>
        """, unsafe_allow_html=True)


# ──────────────────────────────────────────────
# 메인
# ──────────────────────────────────────────────
def run() -> None:
    st.set_page_config(
        page_title="BTC 안전자산 가설 검증",
        page_icon="₿",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    st.markdown("""
    <style>
        .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
        [data-testid="stMetricValue"] { font-size: 1.15rem !important; }
        [data-testid="stMetricLabel"] { font-size: 0.78rem !important; }
        div[data-testid="stTabs"] button { font-size: 0.85rem; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown(
        """
        <h1 style="font-size:38px;font-weight:800;margin-bottom:2px;">
            ₿ BTC 안전자산 가설 검증 대시보드
        </h1>
        <p style="font-size:18px;color:#6B7280;margin-top:4px;margin-bottom:0;">
            2019–2026 | 6개 지정학 이벤트 | Event Study × Quantile Reg × GARCH
        </p>
        """,
        unsafe_allow_html=True,
    )
    st.divider()


    tabs = st.tabs([
        "📊 통합 판정",
        "🗞️ GPR 파이프라인",
        "🔍 EDA",
        "📈 이벤트 스터디",
        "📉 분위수 회귀",
        "⚡ GARCH",
    ])

    with tabs[0]: tab_overview()
    with tabs[1]: tab_gpr()
    with tabs[2]: tab_eda()
    with tabs[3]: tab_event_study()
    with tabs[4]: tab_quantile()
    with tabs[5]: tab_garch()

    st.divider()
    st.caption("2026 캡스톤 | BTC 안전자산 가설 검증 · Weak Haven 판정")


if __name__ == "__main__": 
    run()
