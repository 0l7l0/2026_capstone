from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


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
    st.header("최종 통합 판정 (Baur & Lucey 2010 3조건)")
    st.markdown(
        "**판정 기준**: 이벤트 스터디(C1) · 분위수 회귀(C2) · GARCH(C3) 세 조건을 통합하여 "
        "Safe Haven 여부를 판별합니다. 3/3 통과 시 Safe Haven, 2/3은 Weak Haven입니다."
    )

    # Hero 차트
    hero = load_image("dashboard/result_csv_png/main_btc_gold_compare.png")
    if hero:
        st.image(hero, caption="BTC vs Gold vs SP500 — 이벤트 구간 누적 로그 수익률", use_column_width=True)

    st.divider()

    final = load_csv("dashboard/result_csv_png/final_judgment.csv")
    if final is None:
        st.error("final_judgment.csv 없음")
        return

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Safe Haven", int((final["verdict"] == "Safe Haven").sum()), help="3/3 통과")
    col2.metric("Weak Haven", int((final["verdict"] == "Weak Haven").sum()), help="2/3 통과")
    col3.metric("Diversifier", int((final["verdict"] == "Diversifier").sum()), help="1/3 통과")
    col4.metric("Risky Asset", int((final["verdict"] == "Risky Asset").sum()), help="0/3 통과")

    st.divider()
    st.subheader("이벤트 × 조건 매트릭스")
    cond_cols = ["C1_event_study_pass", "C2_quantile_reg_pass", "C3_garch_pass"]
    mat = final[cond_cols].astype(int).values
    fig = go.Figure(
        data=go.Heatmap(
            z=mat,
            x=["C1 이벤트 스터디", "C2 분위수 회귀 (τ=0.05)", "C3 GARCH (GPR γ)"],
            y=final["event_label"].tolist(),
            text=[[("Pass" if v else "Fail") for v in row] for row in mat],
            texttemplate="%{text}",
            colorscale=[[0, "#C62828"], [1, "#2E7D32"]],
            showscale=False,
        )
    )
    fig.update_layout(height=380, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("이벤트별 상세")
    display = final[["event_label", "C1_detail", "C2_detail", "C3_detail", "score", "verdict"]].copy()
    display.columns = ["이벤트", "C1 (이벤트 스터디)", "C2 (분위수 회귀)", "C3 (GARCH)", "점수", "판정"]
    st.dataframe(
        display.style.map(color_verdict, subset=["판정"]),
        use_container_width=True,
        hide_index=True,
    )

    st.divider()
    st.subheader("핵심 결론")
    st.info(
        "- **BTC는 안전자산이 아니다** — 6개 이벤트 중 5개에서 분위수 회귀 조건(C2) 미통과\n"
        "- **위기 시 동조화 강화** — SP500-BTC 동조화가 극단 하락(τ=0.01)에서 평상시(τ=0.50) 대비 2.2배 증가\n"
        "- **GPR 상승이 오히려 동조화를 강화** — 상호작용항 δ=+0.005 (p=0.037), Safe Haven 조건과 반대\n"
        "- **BTC 변동성을 설명하는 건 GPR이 아닌 시장 심리(Fear&Greed)** — γ=+0.157 (p=0.038)"
    )

    report = ROOT / "MD" / "final_report.md"
    if report.exists():
        st.divider()
        with st.expander("final_report.md (전체)", expanded=False):
            st.markdown(report.read_text(encoding="utf-8"))


# ────────────────────────────────────────────────────────────
# 2. GPR 데이터파이프라인
# ────────────────────────────────────────────────────────────
def render_gpr_pipeline() -> None:
    st.header("GPR 데이터파이프라인 — 자체 지정학 리스크 지수 구축")
    st.markdown(
        "**방법**: GDELT GKG(BigQuery)에서 6개 이벤트 구간 뉴스 기사를 수집하여 "
        "F3 공식 `(tone × log(N))`으로 자체 GPR 지수를 구축하고, "
        "Caldara & Iacoviello (2022) 공식 GPR 지수와 교차 검증합니다."
    )

    tab1, tab2, tab3 = st.tabs(["기사 수 · 전처리", "GPR 분석", "이벤트 구간"])

    with tab1:
        st.subheader("이벤트별 기사 수 (원본)")
        col1, col2 = st.columns(2)
        imgs_raw = [
            ("FIGURES/01-1_hormuz_soleimani_article_count.png", "호르무즈·솔레이마니"),
            ("FIGURES/01-2_russia_ukraine_article_count.png", "러-우 전쟁"),
            ("FIGURES/01-3_israel_hamas_iran_article_count.png", "이스라엘-하마스·이란"),
            ("FIGURES/01-4_us_israel_iran_article_count.png", "미-이스라엘-이란"),
        ]
        for i, (path, cap) in enumerate(imgs_raw):
            with (col1 if i % 2 == 0 else col2):
                img = load_image(path)
                if img:
                    st.image(img, caption=cap, use_column_width=True)

        st.subheader("전처리 후")
        col1, col2 = st.columns(2)
        imgs_pre = [
            ("FIGURES/02-1_hormuz_soleimani_preprocessed.png", "호르무즈·솔레이마니 (전처리)"),
            ("FIGURES/02-2_russia_ukraine_preprocessed.png", "러-우 전쟁 (전처리)"),
            ("FIGURES/02-3_israel_hamas_iran_preprocessed.png", "이스라엘-하마스·이란 (전처리)"),
            ("FIGURES/02-4_us_israel_iran_preprocessed.png", "미-이스라엘-이란 (전처리)"),
        ]
        for i, (path, cap) in enumerate(imgs_pre):
            with (col1 if i % 2 == 0 else col2):
                img = load_image(path)
                if img:
                    st.image(img, caption=cap, use_column_width=True)

    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            img = load_image("FIGURES/03_correlation_heatmap.png")
            if img:
                st.image(img, caption="GPR 변수 간 상관관계 히트맵", use_column_width=True)
        with col2:
            img = load_image("FIGURES/04_scatter_matrix.png")
            if img:
                st.image(img, caption="GPR 산점도 행렬", use_column_width=True)

        img = load_image("FIGURES/05_gpr_timeseries.png")
        if img:
            st.image(img, caption="자체 GPR 지수 시계열", use_column_width=True)

        img = load_image("FIGURES/06_official_vs_ours.png")
        if img:
            st.image(img, caption="공식 GPR vs 자체 GPR 비교 (Caldara & Iacoviello 2022)", use_column_width=True)

    with tab3:
        img = load_image("FIGURES/07_event_window.png")
        if img:
            st.image(img, caption="이벤트 구간 정의", use_column_width=True)

    st.divider()
    st.subheader("GPR 파이프라인 핵심")
    st.info(
        "- **F3 공식**: `GPR_custom = mean_tone × log(기사 수)` — 감성과 볼륨을 동시에 반영\n"
        "- **공식 GPR과 높은 상관관계** 확인 → 자체 지수의 대리변수 타당성 검증\n"
        "- **6개 이벤트 구간** 각각 독립적으로 수집·전처리하여 병합"
    )


# ────────────────────────────────────────────────────────────
# 3. EDA
# ────────────────────────────────────────────────────────────
def render_eda() -> None:
    st.header("EDA — 탐색적 데이터 분석")
    st.markdown(
        "**분석 범위**: 6개 지정학 이벤트 구간 자산별 수익률 분포·상관관계·변동성 구조 확인. "
        "ARCH-LM 검정으로 GARCH 모형 적용의 정당성을 확보하였습니다."
    )

    tab1, tab2, tab3 = st.tabs(["가격 추이", "수익률 분포", "상관관계·변동성"])

    with tab1:
        for path, cap in [
            ("eda/result_csv_png/plot1_price_trend.png", "자산별 가격 추이 (정규화)"),
            ("eda/result_csv_png/plot2_event_price.png", "이벤트 구간별 가격 흐름"),
            ("eda/result_csv_png/plot3_moving_average.png", "이동평균선"),
            ("eda/result_csv_png/plot5_btc_highlow.png", "BTC 고점·저점 분석"),
        ]:
            img = load_image(path)
            if img:
                st.image(img, caption=cap, use_column_width=True)

    with tab2:
        img = load_image("eda/result_csv_png/plot4_returns_dist.png")
        if img:
            st.image(img, caption="자산별 수익률 분포 (fat-tail 확인)", use_column_width=True)
        returns = load_csv("eda/result_csv_png/returns.csv")
        if returns is not None:
            st.subheader("수익률 기술통계")
            st.dataframe(returns.describe().round(4), use_container_width=True)

    with tab3:
        col1, col2 = st.columns(2)
        with col1:
            img = load_image("eda/result_csv_png/plot6_corr_heatmap.png")
            if img:
                st.image(img, caption="자산 간 상관관계 히트맵", use_column_width=True)
        with col2:
            img = load_image("eda/result_csv_png/plot7_event_heatmap.png")
            if img:
                st.image(img, caption="이벤트별 상관관계 히트맵", use_column_width=True)
        img = load_image("eda/result_csv_png/plot8_rolling_corr.png")
        if img:
            st.image(img, caption="BTC-SP500 롤링 상관관계", use_column_width=True)

    st.divider()
    st.subheader("EDA 핵심 발견")
    st.info(
        "- **BTC 연환산 변동성 62.6%** — Gold(12.3%)·SP500(21.4%) 대비 압도적으로 높아 Safe Haven 판정에 불리하게 작용\n"
        "- **전 자산 ARCH 효과 유의** — Ljung-Box·ARCH-LM 검정 통과 → GARCH 모형 적용 정당화\n"
        "- **미-이스라엘-이란 기간 BTC-SP500 상관관계 +0.21** — 위기 시 동조화 경향 사전 확인"
    )


# ────────────────────────────────────────────────────────────
# 4. 이벤트 스터디
# ────────────────────────────────────────────────────────────
def render_event_study() -> None:
    st.header("이벤트 스터디 — MacKinlay 1997 (±17일, Bootstrap, BH-FDR + Placebo)")
    st.markdown(
        "**방법**: 이벤트 창(±17 거래일) 내 누적 비정상 수익률(CAR)을 산출하고 "
        "t-test·블록 부트스트랩으로 검정합니다. "
        "CAR > 0 & p < 0.05 이면 Safe Haven, BH 다중검정 보정으로 허위 양성을 통제합니다."
    )

    # CAR 시각화 (PNG + 인터랙티브)
    tab1, tab2, tab3 = st.tabs(["CAR 시각화", "검정 결과 표", "Placebo 검정"])

    with tab1:
        img_bar = load_image("event_study/result_csv_png/event_study_CAR_bar_final.png")
        if img_bar:
            st.image(img_bar, caption="이벤트별 CAR 막대그래프 (유의성 표시)", use_column_width=True)
        img_ts = load_image("event_study/result_csv_png/event_study_CAR_timeseries.png")
        if img_ts:
            st.image(img_ts, caption="이벤트별 CAR 시계열", use_column_width=True)

        # 인터랙티브 bar
        event = load_csv("event_study/result_csv_png/event_study_car_bh.csv")
        if event is not None:
            st.subheader("인터랙티브 CAR 비교")
            assets = sorted(event["asset"].dropna().unique())
            default_assets = ["BTC", "Gold"] if "BTC" in assets else assets[:2]
            selected_assets = st.multiselect("자산 선택", assets, default=default_assets)
            sub = event[event["asset"].isin(selected_assets)].copy()
            sub["event_label"] = sub["event"].map(EVENT_LABEL).fillna(sub["event"])
            fig = px.bar(
                sub, x="event_label", y="CAR", color="asset",
                color_discrete_map=ASSET_COLORS, barmode="group",
                title="이벤트별 CAR (±17일)",
            )
            fig.add_hline(y=0, line_color="white", line_width=1)
            fig.update_layout(xaxis_title="이벤트", yaxis_title="Cumulative Abnormal Return")
            st.plotly_chart(fig, use_container_width=True)

    with tab2:
        event = load_csv("event_study/result_csv_png/event_study_car_bh.csv")
        if event is not None:
            sub = event.copy()
            sub["event_label"] = sub["event"].map(EVENT_LABEL).fillna(sub["event"])
            keep = ["event_label", "asset", "CAR", "t_stat", "p_norm", "p_boot"]
            if "p_norm_bh" in sub.columns:
                keep.append("p_norm_bh")
            if "sig_bh" in sub.columns:
                keep.append("sig_bh")
            keep = [c for c in keep if c in sub.columns]
            st.dataframe(sub[keep].round(4), use_container_width=True, hide_index=True)

    with tab3:
        placebo = load_csv("event_study/result_csv_png/event_study_placebo.csv")
        if placebo is not None:
            placebo["event_label"] = placebo["event_name"].map(EVENT_LABEL).fillna(placebo["event_name"])
            keep_p = ["event_label", "real_CAR", "placebo_mean_CAR",
                      "placebo_std_CAR", "percentile_of_real", "placebo_p", "n_placebo"]
            st.dataframe(
                placebo[[c for c in keep_p if c in placebo.columns]].round(4),
                use_container_width=True, hide_index=True,
            )
            st.caption("placebo_p > 0.05 → 실제 이벤트가 가짜 일자와 통계적으로 구분되지 않음")

    st.divider()
    st.subheader("이벤트 스터디 핵심 발견")
    st.info(
        "- **BTC CAR은 5개 이벤트에서 양수이지만 전부 통계적 비유의** — 연 62.6% 고유 변동성이 유의성 확보를 방해\n"
        "- **BH 다중검정 보정 후 30개 검정 전체 비유의** — Gold/이스라엘-이란 Safe Haven(p=0.040)도 보정 후 기각\n"
        "- **결론**: 이벤트 스터디 단독으로 BTC 안전자산 여부 판별 불가 → 분위수 회귀·GARCH 추가 분석 필요"
    )


# ────────────────────────────────────────────────────────────
# 5. 분위수 회귀
# ────────────────────────────────────────────────────────────
def render_quantile() -> None:
    st.header("분위수 회귀 — Koenker & Bassett 1978 (HAC SE, BH-FDR)")
    st.markdown(
        "**방법**: 주식 시장 극단 하락 구간(τ ≤ 0.10)에서 BTC-자산 간 β 계수를 추정합니다. "
        "β < 0 & p < 0.05이면 Safe Haven. HAC(Newey-West) 표준오차로 시계열 이분산·자기상관을 보정합니다."
    )

    tab1, tab2 = st.tabs(["β 경로 차트", "결과 테이블"])

    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            img = load_image("quantile/result_csv_png/quantreg_beta_path.png")
            if img:
                st.image(img, caption="SP500·Gold β 계수 분위별 경로", use_column_width=True)
        with col2:
            img = load_image("quantile/result_csv_png/quantreg_gamma_path.png")
            if img:
                st.image(img, caption="GPR γ 계수 분위별 경로", use_column_width=True)
        img = load_image("quantile/result_csv_png/quantreg_heatmap.png")
        if img:
            st.image(img, caption="이벤트 × 분위수 β 히트맵", use_column_width=True)

    with tab2:
        quantile = load_csv("quantile/result_csv_png/quantile_results_bh.csv")
        if quantile is None:
            st.error("quantile_results_bh.csv 없음")
            return

        tau_col = next((c for c in quantile.columns if c.strip() in ("τ", "tau")), "τ")
        beta_col = next((c for c in quantile.columns if c.strip() in ("β", "beta")), "β")

        col1, col2 = st.columns(2)
        tau_vals = sorted(quantile[tau_col].astype(float).unique())
        selected_taus = col1.multiselect(
            "τ 선택", [f"{t:.3f}" for t in tau_vals], default=["0.050", "0.100", "0.500"],
        )
        sub = quantile[
            quantile[tau_col].astype(float).round(3).isin([round(float(t), 3) for t in selected_taus])
        ].copy()

        if "변수" in sub.columns:
            variables = sorted(sub["변수"].dropna().unique())
            default_vars = [v for v in ["SP500_z", "Gold_z", "GPR_custom_z"] if v in variables]
            selected_vars = col2.multiselect("변수", variables, default=default_vars)
            sub = sub[sub["변수"].isin(selected_vars)]

        if beta_col in sub.columns and "이벤트" in sub.columns:
            fig = px.scatter(
                sub, x=tau_col, y=beta_col, color="이벤트",
                symbol="변수" if "변수" in sub.columns else None,
                hover_data=["모델"] if "모델" in sub.columns else None,
                title="β 계수 (이벤트별 × τ별 × 변수별)",
            )
            fig.add_hline(y=0, line_color="white", line_width=1, line_dash="dash")
            st.plotly_chart(fig, use_container_width=True)

        st.dataframe(sub.round(5), use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("분위수 회귀 핵심 발견")
    st.info(
        "- **전 이벤트·전 위기 분위수에서 β > 0** — BTC는 주식 폭락 시 함께 하락하는 위험자산\n"
        "- **극단 하락(τ=0.01)에서 동조화가 평상시(τ=0.50) 대비 2.2배 강화** — Safe Haven과 정반대 패턴\n"
        "- **GPR 상승 시 동조화 강화** — 상호작용항 δ=+0.005 (p=0.037), 안전자산 성격 완화 없음\n"
        "- **4종 강건성 검정(GPR제거·LOO·Min-Max·블록부트스트랩) 모두에서 결론 유지**"
    )


# ────────────────────────────────────────────────────────────
# 6. GARCH
# ────────────────────────────────────────────────────────────
def render_garch() -> None:
    st.header("GARCH-X — Student-t MLE, multi-init, ADF·EGARCH")
    st.markdown(
        "**방법**: 외생변수(GPR·VIX·Fear&Greed)를 분산식에 포함한 GARCH-X를 Student-t MLE로 추정합니다. "
        "γ > 0 & p < 0.05이면 해당 변수가 BTC 변동성을 증폭시키는 위험자산 특성을 의미합니다."
    )

    tab1, tab2, tab3 = st.tabs(["모델 비교", "γ 계수 분석", "EGARCH 강건성"])

    with tab1:
        img = load_image("garch/result_csv_png/garch_model_comparison.png")
        if img:
            st.image(img, caption="모델별 AIC·BIC 비교", use_column_width=True)
        comparison = load_csv("garch/result_csv_png/garch_model_comparison.csv")
        if comparison is not None:
            st.subheader("5개 모델 비교 (AIC/BIC, α+β, 수렴)")
            st.dataframe(comparison, use_container_width=True, hide_index=True)
        adf = load_csv("garch/result_csv_png/adf_test.csv")
        if adf is not None:
            with st.expander("ADF 정상성 검증 (사전)"):
                st.dataframe(adf.round(6), use_container_width=True, hide_index=True)

    with tab2:
        img = load_image("garch/result_csv_png/garch_gamma_coefficients.png")
        if img:
            st.image(img, caption="γ 계수 방향·크기 비교", use_column_width=True)
        gamma = load_csv("garch/result_csv_png/garch_gamma_results.csv")
        if gamma is not None:
            st.subheader("외생변수 γ 계수")
            st.dataframe(gamma.round(4), use_container_width=True, hide_index=True)
        img = load_image("garch/result_csv_png/garch_conditional_vol.png")
        if img:
            st.image(img, caption="조건부 변동성 σ(t) 시계열", use_column_width=True)

    with tab3:
        col1, col2 = st.columns(2)
        with col1:
            img = load_image("garch/result_csv_png/egarch_model_aic_bic.png")
            if img:
                st.image(img, caption="EGARCH 모델 AIC·BIC", use_column_width=True)
        with col2:
            img = load_image("garch/result_csv_png/egarch_cond_vol_comparison.png")
            if img:
                st.image(img, caption="GARCH·EGARCH 조건부 변동성 비교", use_column_width=True)
        img = load_image("garch/result_csv_png/egarch_gpr_coef_compare.png")
        if img:
            st.image(img, caption="GPR 계수 GARCH·EGARCH 비교", use_column_width=True)
        egarch = load_csv("garch/result_csv_png/egarch_model_comparison.csv")
        if egarch is not None:
            st.subheader("EGARCH 모델 비교")
            st.dataframe(egarch, use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("GARCH 핵심 발견")
    st.info(
        "- **GPR은 전 모델에서 통계적 비유의** — BTC 변동성이 지정학 리스크에 반응하지 않음 → C3 조건 통과\n"
        "- **fear_greed_lag1이 반복 유의** — GARCH(p=0.038)·EGARCH(p=0.017~0.019) 모두 유의\n"
        "- **α+β ≈ 0.996 (near-IGARCH)** — 충격 지속성이 매우 강함, BTC 변동성의 구조적 특성\n"
        "- **Model3 (VIX + Fear&Greed)** AIC 기준 최적 모델 (AIC=9578.71)"
    )


# ────────────────────────────────────────────────────────────
# 7. 원 데이터
# ────────────────────────────────────────────────────────────
def render_raw_data() -> None:
    st.header("원 데이터")

    master = load_csv("datapipeline/master_data/master_data.csv")
    if master is None:
        st.error("master_data.csv 없음 — datapipeline/master_data/master_data.csv 경로 확인")
        return

    master["date"] = pd.to_datetime(master["date"])
    st.caption(
        f"기간: {master['date'].min().date()} ~ {master['date'].max().date()} "
        f"· {len(master):,}행 · {len(master.columns)}개 컬럼"
    )

    # 컬럼 구성 표
    col_desc = {
        "date": "거래일", "event_name": "이벤트 구간 레이블", "event_date": "이벤트 기준일",
        "BTC": "BTC 로그 수익률", "Gold": "금 로그 수익률", "SP500": "S&P500 로그 수익률",
        "NASDAQ": "NASDAQ 로그 수익률", "TLT": "미 장기채 ETF 로그 수익률",
        "DXY": "달러 인덱스 로그 수익률", "VIX": "변동성 지수",
        "fear_greed": "CNN Fear&Greed 지수", "fear_greed_lag1": "전일 Fear&Greed (시차 1일)",
        "GPR_custom": "자체 GPR 지수 (F3_raw)", "GPR": "Caldara & Iacoviello 공식 GPR",
        "GPR_zscore": "공식 GPR Z-score",
    }
    desc_df = pd.DataFrame([
        {"컬럼": c, "설명": col_desc.get(c, "")} for c in master.columns
    ])
    with st.expander("컬럼 구성 (19개)", expanded=False):
        st.dataframe(desc_df, use_container_width=True, hide_index=True)

    # BTC·Gold·SP500 누적 수익률 (이벤트별 색상)
    tab1, tab2 = st.tabs(["누적 수익률", "데이터 미리보기"])

    with tab1:
        fig = go.Figure()
        for asset, color in [("BTC", "#F7931A"), ("Gold", "#FFD700"), ("SP500", "#1976D2")]:
            if asset in master.columns:
                for event_key in EVENT_LABEL:
                    sub = master[master["event_name"] == event_key].sort_values("date")
                    if not sub.empty:
                        fig.add_trace(go.Scatter(
                            x=sub["date"],
                            y=sub[asset].cumsum(),
                            name=f"{asset} / {EVENT_LABEL[event_key]}",
                            mode="lines",
                            line=dict(color=color, width=1.5),
                            legendgroup=asset,
                            showlegend=(event_key == "hormuz_crisis"),
                        ))
        fig.update_layout(
            title="이벤트별 BTC·Gold·SP500 누적 로그 수익률",
            xaxis_title="Date", yaxis_title="Cumulative log return",
            legend_title="자산",
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.dataframe(master.head(100), use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("검증 스크립트")
    verification_files = sorted((ROOT / "verification").glob("*.py"))
    if verification_files:
        st.dataframe(
            pd.DataFrame({"파일명": [p.name for p in verification_files]}),
            use_container_width=True, hide_index=True,
        )
    else:
        st.caption("verification 폴더 없음")


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
        ["통합 판정", "GPR 데이터파이프라인", "EDA", "이벤트 스터디", "분위수 회귀", "GARCH", "원 데이터"],
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
    elif section == "GARCH":
        render_garch()
    else:
        render_raw_data()

    st.divider()
    st.caption("2026 캡스톤 | BTC 안전자산 가설 검증")
