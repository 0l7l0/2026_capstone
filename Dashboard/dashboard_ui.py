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
    "israel_iran": "2024-04-01",
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
def load_image(path: str):
    file_path = ROOT / path
    if not file_path.exists():
        return None
    return str(file_path)


def color_verdict(value: str) -> str:
    color = VERDICT_COLOR.get(value, "#888")
    return f"background-color: {color}; color: white; font-weight: bold;"


def render_integrated_judgment() -> None:
    st.header("최종 통합 판정 (Baur & Lucey 2010 3조건)")
    st.markdown(
        """
        **판정 기준**: 이벤트 스터디(C1) · 분위수 회귀(C2) · GARCH(C3) 세 조건을 통합하여
        Safe Haven 여부를 판별합니다. 3/3 통과 시 Safe Haven, 2/3은 Weak Haven입니다.
        """
    )
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
            text=[[("Pass" if value else "Fail") for value in row] for row in mat],
            texttemplate="%{text}",
            colorscale=[[0, "#C62828"], [1, "#2E7D32"]],
            showscale=False,
        )
    )
    fig.update_layout(height=380, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("이벤트별 상세")
    display = final[
        ["event_label", "C1_detail", "C2_detail", "C3_detail", "score", "verdict"]
    ].copy()
    display.columns = ["이벤트", "C1 상세 (이벤트 스터디)", "C2 상세 (분위수 회귀)", "C3 상세 (GARCH)", "점수", "판정"]
    st.dataframe(
        display.style.map(color_verdict, subset=["판정"]),
        use_container_width=True,
        hide_index=True,
    )

    st.divider()
    st.subheader("핵심 결론")
    st.info(
        """
        - **BTC는 안전자산이 아니다** — 6개 이벤트 중 5개에서 분위수 회귀 조건(C2) 미통과
        - **위기 시 동조화 강화** — SP500-BTC 동조화가 극단 하락(τ=0.01)에서 평상시(τ=0.50) 대비 2.2배 증가
        - **GPR 상승이 오히려 동조화를 강화** — 상호작용항 δ=+0.005 (p=0.037), Safe Haven 조건과 반대
        - **BTC 변동성을 설명하는 건 GPR이 아닌 시장 심리(Fear&Greed)** — γ=+0.157 (p=0.038)
        """
    )

    report = ROOT / "MD" / "final_report.md"
    if report.exists():
        st.divider()
        with st.expander("final_report.md (전체)", expanded=False):
            st.markdown(report.read_text(encoding="utf-8"))


def render_eda() -> None:
    st.header("EDA — 탐색적 데이터 분석")
    st.markdown(
        """
        **분석 범위**: 6개 지정학 이벤트 구간 자산별 수익률 분포·상관관계·변동성 구조 확인.
        ARCH-LM 검정으로 GARCH 모형 적용의 정당성을 확보하였습니다.
        """
    )

    tab1, tab2, tab3 = st.tabs(["가격 추이", "수익률 분포", "상관관계·변동성"])

    with tab1:
        img_path = load_image("eda/result_csv_png/plot1_price_trend.png")
        if img_path:
            st.image(img_path, caption="자산별 가격 추이 (정규화)", use_column_width=True)
        img_path2 = load_image("eda/result_csv_png/plot2_event_price.png")
        if img_path2:
            st.image(img_path2, caption="이벤트 구간별 가격 흐름", use_column_width=True)
        img_path3 = load_image("eda/result_csv_png/plot3_moving_average.png")
        if img_path3:
            st.image(img_path3, caption="이동평균선", use_column_width=True)
        img_path5 = load_image("eda/result_csv_png/plot5_btc_highlow.png")
        if img_path5:
            st.image(img_path5, caption="BTC 고점·저점 분석", use_column_width=True)

    with tab2:
        img_path4 = load_image("eda/result_csv_png/plot4_returns_dist.png")
        if img_path4:
            st.image(img_path4, caption="자산별 수익률 분포 (fat-tail 확인)", use_column_width=True)

        returns = load_csv("eda/result_csv_png/returns.csv")
        if returns is not None:
            st.subheader("수익률 기술통계")
            st.dataframe(returns.describe().round(4), use_container_width=True)

    with tab3:
        col1, col2 = st.columns(2)
        with col1:
            img6 = load_image("eda/result_csv_png/plot6_corr_heatmap.png")
            if img6:
                st.image(img6, caption="자산 간 상관관계 히트맵", use_column_width=True)
        with col2:
            img7 = load_image("eda/result_csv_png/plot7_event_heatmap.png")
            if img7:
                st.image(img7, caption="이벤트별 상관관계 히트맵", use_column_width=True)
        img8 = load_image("eda/result_csv_png/plot8_rolling_corr.png")
        if img8:
            st.image(img8, caption="BTC-SP500 롤링 상관관계", use_column_width=True)

    st.divider()
    st.subheader("EDA 핵심 발견")
    st.info(
        """
        - **BTC 연환산 변동성 62.6%** — Gold(12.3%)·SP500(21.4%) 대비 압도적으로 높아 Safe Haven 판정에 불리하게 작용
        - **전 자산 ARCH 효과 유의** — Ljung-Box·ARCH-LM 검정 통과 → GARCH 모형 적용 정당화
        - **미-이스라엘-이란 전쟁 기간 BTC-SP500 상관관계 +0.21** — 위기 시 동조화 경향 사전 확인
        """
    )


def render_event_study() -> None:
    st.header("이벤트 스터디 — MacKinlay 1997 (±17일, Bootstrap, BH-FDR + Placebo)")
    st.markdown(
        """
        **방법**: 이벤트 창(±17 거래일) 내 누적 비정상 수익률(CAR)을 산출하고 t-test·블록 부트스트랩으로 검정합니다.
        CAR > 0 & p < 0.05 이면 Safe Haven, 단 BH 다중검정 보정을 통해 허위 양성을 통제합니다.
        """
    )
    event = load_csv("event_study/result_csv_png/event_study_car_bh.csv")
    if event is None:
        st.error("event_study_car_bh.csv 없음")
        return

    assets = sorted(event["asset"].dropna().unique())
    default_assets = ["BTC"] if "BTC" in assets else assets[:1]
    selected_assets = st.multiselect("자산 선택", assets, default=default_assets)
    sub = event[event["asset"].isin(selected_assets)].copy()
    sub["event_label"] = sub["event"].map(EVENT_LABEL).fillna(sub["event"])

    fig = px.bar(
        sub,
        x="event_label",
        y="CAR",
        color="asset",
        color_discrete_map=ASSET_COLORS,
        barmode="group",
        title="이벤트별 CAR (±17일)",
    )
    fig.add_hline(y=0, line_color="black", line_width=1)
    fig.update_layout(xaxis_title="이벤트", yaxis_title="Cumulative Abnormal Return")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("CAR + 검정 결과")
    pcol = "p_norm_bh" if "p_norm_bh" in sub.columns else next(
        (col for col in ["p_t", "p_norm", "p"] if col in sub.columns),
        None,
    )
    keep = ["event_label", "asset", "CAR", "t_stat", "p_norm", "p_boot"]
    if pcol and pcol not in keep:
        keep.append(pcol)
    if "sig_bh" in sub.columns:
        keep.append("sig_bh")
    keep = [col for col in keep if col in sub.columns]
    st.dataframe(sub[keep].round(4), use_container_width=True, hide_index=True)

    placebo = load_csv("event_study/result_csv_png/event_study_placebo.csv")
    if placebo is not None:
        st.divider()
        st.subheader("Placebo 검정 (실제 vs 가짜 이벤트일 200회)")
        placebo["event_label"] = placebo["event_name"].map(EVENT_LABEL).fillna(placebo["event_name"])
        keep_placebo = [
            "event_label",
            "real_CAR",
            "placebo_mean_CAR",
            "placebo_std_CAR",
            "percentile_of_real",
            "placebo_p",
            "n_placebo",
        ]
        st.dataframe(
            placebo[[col for col in keep_placebo if col in placebo.columns]].round(4),
            use_container_width=True,
            hide_index=True,
        )
        st.caption("placebo_p > 0.05 → 실제 이벤트가 가짜 일자와 통계적으로 구분되지 않음")

    st.divider()
    st.subheader("이벤트 스터디 핵심 발견")
    st.info(
        """
        - **BTC CAR은 5개 이벤트에서 양수이지만 전부 통계적 비유의** — BTC 고유 변동성(연 62.6%)이 유의성 확보를 방해
        - **BH 다중검정 보정 후 30개 검정 전체 비유의** — Gold/이스라엘-이란 Safe Haven(p=0.040)도 보정 후 기각
        - **결론**: 이벤트 스터디만으로 BTC 안전자산 여부를 판별하기 어려움 → 분위수 회귀·GARCH 추가 분석 필요
        """
    )


def render_quantile() -> None:
    st.header("분위수 회귀 — Koenker & Bassett 1978 (HAC SE, BH-FDR)")
    st.markdown(
        """
        **방법**: 주식 시장 극단 하락 구간(τ ≤ 0.10)에서 BTC-자산 간 β 계수를 추정합니다.
        β < 0 & p < 0.05이면 Safe Haven. HAC(Newey-West) 표준오차로 시계열 이분산·자기상관을 보정합니다.
        """
    )

    tab1, tab2 = st.tabs(["β 경로 차트", "결과 테이블"])

    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            img = load_image("quantile/result_csv_png/quantreg_beta_path.png")
            if img:
                st.image(img, caption="SP500·Gold β 계수 분위별 경로", use_column_width=True)
        with col2:
            img2 = load_image("quantile/result_csv_png/quantreg_gamma_path.png")
            if img2:
                st.image(img2, caption="GPR γ 계수 분위별 경로", use_column_width=True)
        img3 = load_image("quantile/result_csv_png/quantreg_heatmap.png")
        if img3:
            st.image(img3, caption="이벤트 × 분위수 β 히트맵", use_column_width=True)

    with tab2:
        quantile = load_csv("quantile/result_csv_png/quantile_results_bh.csv")
        if quantile is None:
            st.error("quantile_results_bh.csv 없음")
            return

        col1, col2 = st.columns(2)
        tau_col = next((col for col in quantile.columns if col.strip() in ("τ", "tau")), "τ")
        beta_col = next((col for col in quantile.columns if col.strip() in ("β", "beta")), "β")

        tau_vals = sorted(quantile[tau_col].astype(float).unique())
        selected_taus = col1.multiselect(
            "τ 선택",
            [f"{tau:.3f}" for tau in tau_vals],
            default=["0.050", "0.100", "0.500"],
        )
        sub = quantile[
            quantile[tau_col].astype(float).round(3).isin([round(float(tau), 3) for tau in selected_taus])
        ].copy()

        if "변수" in sub.columns:
            variables = sorted(sub["변수"].dropna().unique())
            default_vars = [var for var in ["SP500_z", "Gold_z", "GPR_custom_z"] if var in variables]
            selected_vars = col2.multiselect("변수", variables, default=default_vars)
            sub = sub[sub["변수"].isin(selected_vars)]

        if beta_col in sub.columns and "이벤트" in sub.columns:
            fig = px.scatter(
                sub,
                x=tau_col,
                y=beta_col,
                color="이벤트",
                symbol="변수" if "변수" in sub.columns else None,
                hover_data=["모델"] if "모델" in sub.columns else None,
                title="β 계수 (이벤트별 × τ별 × 변수별)",
            )
            fig.add_hline(y=0, line_color="black", line_width=1, line_dash="dash")
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("결과 표 (선택 τ)")
        st.dataframe(sub.round(5), use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("분위수 회귀 핵심 발견")
    st.info(
        """
        - **전 이벤트·전 위기 분위수에서 β > 0** — BTC는 주식 폭락 시 함께 하락하는 위험자산
        - **극단 하락(τ=0.01)에서 동조화가 평상시(τ=0.50) 대비 2.2배 강화** — Safe Haven과 정반대 패턴
        - **GPR 상승 시 동조화 강화** — 상호작용항 δ=+0.005 (p=0.037), 안전자산 성격 완화 없음
        - **4종 강건성 검정(GPR제거·LOO·Min-Max·블록부트스트랩) 모두에서 결론 유지**
        """
    )


def render_garch() -> None:
    st.header("GARCH-X — Student-t MLE, multi-init, ADF·EGARCH")
    st.markdown(
        """
        **방법**: 외생변수(GPR·VIX·Fear&Greed)를 분산식에 포함한 GARCH-X를 Student-t MLE로 추정합니다.
        γ > 0 & p < 0.05이면 해당 변수가 BTC 변동성을 증폭시키는 위험자산 특성을 의미합니다.
        """
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
        img2 = load_image("garch/result_csv_png/garch_gamma_coefficients.png")
        if img2:
            st.image(img2, caption="γ 계수 방향·크기 비교", use_column_width=True)
        gamma = load_csv("garch/result_csv_png/garch_gamma_results.csv")
        if gamma is not None:
            st.subheader("외생변수 γ 계수")
            st.dataframe(gamma.round(4), use_container_width=True, hide_index=True)
        img3 = load_image("garch/result_csv_png/garch_conditional_vol.png")
        if img3:
            st.image(img3, caption="조건부 변동성 σ(t) 시계열", use_column_width=True)

    with tab3:
        col1, col2 = st.columns(2)
        with col1:
            img4 = load_image("garch/result_csv_png/egarch_model_aic_bic.png")
            if img4:
                st.image(img4, caption="EGARCH 모델 AIC·BIC", use_column_width=True)
        with col2:
            img5 = load_image("garch/result_csv_png/egarch_cond_vol_comparison.png")
            if img5:
                st.image(img5, caption="GARCH·EGARCH 조건부 변동성 비교", use_column_width=True)
        img6 = load_image("garch/result_csv_png/egarch_gpr_coef_compare.png")
        if img6:
            st.image(img6, caption="GPR 계수 GARCH·EGARCH 비교", use_column_width=True)
        egarch = load_csv("garch/result_csv_png/egarch_model_comparison.csv")
        if egarch is not None:
            st.subheader("EGARCH 모델 비교")
            st.dataframe(egarch, use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("GARCH 핵심 발견")
    st.info(
        """
        - **GPR은 전 모델에서 통계적 비유의** — BTC 변동성이 지정학 리스크에 반응하지 않음 → C3 조건 통과
        - **fear_greed_lag1이 반복 유의** — GARCH(p=0.038)·EGARCH(p=0.017~0.019) 모두 유의, BTC 변동성의 핵심 설명 변수
        - **α+β ≈ 0.996 (near-IGARCH)** — 충격 지속성이 매우 강함, BTC 변동성의 구조적 특성
        - **Model3 (VIX + Fear&Greed)** AIC 기준 최적 모델 (AIC=9578.71)
        """
    )


def render_raw_data() -> None:
    st.header("원 데이터")
    st.subheader("master_data")
    master = load_csv("datapipeline/master_data/master_data.csv")
    if master is None:
        st.error("master_data.csv 없음 — datapipeline/master_data/master_data.csv 경로 확인")
        return

    master["date"] = pd.to_datetime(master["date"])
    st.caption(f"기간: {master['date'].min().date()} ~ {master['date'].max().date()} · {len(master)}행 · {len(master.columns)}개 컬럼")

    fig = go.Figure()
    for event_key in EVENT_LABEL:
        sub = master[master["event_name"] == event_key].sort_values("date")
        if not sub.empty:
            fig.add_trace(
                go.Scatter(
                    x=sub["date"],
                    y=sub["BTC"].cumsum(),
                    name=EVENT_LABEL[event_key],
                    mode="lines",
                )
            )
    fig.update_layout(title="이벤트별 BTC 누적 로그 수익률", xaxis_title="Date", yaxis_title="Cumulative log return")
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("데이터 미리보기 (상위 100행)"):
        st.dataframe(master.head(100), use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("검증 스크립트")
    verification_files = sorted((ROOT / "verification").glob("*.py"))
    if verification_files:
        st.dataframe(
            pd.DataFrame({"file": [path.name for path in verification_files]}),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.caption("verification 폴더 없음")


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
        ["통합 판정", "EDA", "이벤트 스터디", "분위수 회귀", "GARCH", "원 데이터"],
    )
    st.sidebar.divider()
    st.sidebar.markdown("**6개 이벤트**")
    for key, label in EVENT_LABEL.items():
        st.sidebar.caption(f"• {label} ({EVENT_DATE[key]})")

    if section == "통합 판정":
        render_integrated_judgment()
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
