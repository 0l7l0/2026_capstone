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


@st.cache_data
def load_csv(path: str):
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


def render_main():

    st.title("₿ BTC Safe-Haven Dashboard")
    st.caption("2019–2024 지정학 이벤트 기반 BTC 안전자산 가설 검증")

    st.subheader("Executive Summary")

    col1, col2 = st.columns([1, 2])

    with col1:

        st.metric("Final Verdict", "Risk Asset")
        st.metric("Best Custom GPR", "F3")

    with col2:

        img = load_image("FIGURES/Figure 06_official_vs_ours.png")

        if img:
            st.image(
                img,
                caption="BTC vs Gold Cumulative Return",
                use_column_width=True
            )

    st.divider()

    st.subheader("Quick Stats")

    col1, col2, col3 = st.columns(3)

    col1.metric("Most Impactful Event", "Russia-Ukraine")
    col2.metric("BTC Annualized Vol.", "62.6%")
    col3.metric("Event Count", "6")

    timeline_df = pd.DataFrame({
        "Event": list(EVENT_LABEL.values()),
        "Date": list(EVENT_DATE.values())
    })

    fig = px.timeline(
        timeline_df,
        x_start="Date",
        x_end="Date",
        y="Event",
        color="Event"
    )

    fig.update_layout(
        height=350,
        title="Geopolitical Event Timeline"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.info(
        """
        분석 기간(2019–2024) 동안 BTC는 Gold와 다른 움직임을 보였으며,
        Safe Haven보다 Risk Asset 특성에 가까운 것으로 나타났다.
        """
    )


def render_event_overview():

    st.header("Event Overview")

    st.markdown(
        """
        주요 지정학 이벤트의 배경과 이벤트 발생 전후 시장 반응 흐름을 시각적으로 정리하였다.
        """
    )

    selected_event = st.selectbox(
        "Event Selection",
        list(EVENT_LABEL.keys()),
        format_func=lambda x: EVENT_LABEL[x]
    )

    st.info(
        f"""
        선택 이벤트: {EVENT_LABEL[selected_event]}
        
        Event Date: {EVENT_DATE[selected_event]}
        """
    )

    col1, col2 = st.columns(2)

    with col1:

        img1 = load_image("경로 변경")

        if img1:
            st.image(
                img1,
                caption="Event Price Flow",
                use_column_width=True
            )

    with col2:

        img2 = load_image("경로 변경")

        if img2:
            st.image(
                img2,
                caption="Return Distribution",
                use_column_width=True
            )

    img3 = load_image("경로 변경")

    if img3:
        st.image(
            img3,
            caption="Rolling Correlation",
            use_column_width=True
        )

    st.divider()

    st.subheader("Key Findings")

    st.info(
        """
        - 이벤트 구간에서 BTC와 SP500 간 동조화 경향이 강화됨
        - BTC 변동성은 Gold 대비 현저히 높게 나타남
        - 위기 구간에서 자산 간 상관관계 구조 변화 확인
        """
    )


def render_safe_haven_analysis():

    st.header("Safe-Haven Analysis")

    st.markdown(
        """
        본 섹션에서는 Event Study와 Quantile Regression을 통해
        BTC의 Safe Haven 특성을 정량적으로 검증한다.
        """
    )

    st.info(
        """
        본 분석에서는 F3 기반 Custom GPR을 지정학 리스크 변수로 활용하였다.
        
        자세한 GPR 생성 과정 및 공식 GPR 비교는
        Risk Index 섹션에서 확인할 수 있다.
        """
    )

    tab1, tab2 = st.tabs(
        ["Event Study", "Quantile Regression"]
    )

    with tab1:

        st.subheader("Event Study")

        img1 = load_image("경로 변경")

        if img1:
            st.image(
                img1,
                caption="CAR Comparison",
                use_column_width=True
            )

        event = load_csv(
            "event_study/result_csv_png/event_study_car_bh.csv"
        )

        if event is not None:

            fig = px.bar(
                event,
                x="event",
                y="CAR",
                color="asset",
                barmode="group",
                color_discrete_map=ASSET_COLORS
            )

            fig.add_hline(
                y=0,
                line_color="black"
            )

            fig.update_layout(
                title="CAR by Event",
                xaxis_title="Event",
                yaxis_title="CAR"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        st.info(
            """
            - BTC CAR은 대부분 이벤트에서 통계적으로 유의하지 않음
            - BH-FDR 보정 이후 Safe Haven 조건 충족 실패
            - Event Study 단독으로는 안전자산 판정 어려움
            """
        )

    with tab2:

        st.subheader("Quantile Regression")

        col1, col2 = st.columns(2)

        with col1:

            img2 = load_image(
                "quantile/result_csv_png/quantreg_beta_path.png"
            )

            if img2:
                st.image(
                    img2,
                    caption="Quantile Beta Path",
                    use_column_width=True
                )

        with col2:

            img3 = load_image("경로 변경")

            if img3:
                st.image(
                    img3,
                    caption="Tail Dependence Heatmap",
                    use_column_width=True
                )

        quantile = load_csv(
            "quantile/result_csv_png/quantile_results_bh.csv"
        )

        if quantile is not None:

            st.dataframe(
                quantile.round(5),
                use_container_width=True,
                hide_index=True
            )

        st.info(
            """
            - 극단 하락 분위수에서 BTC-SP500 양(+)의 동조화 강화
            - β 계수가 음(-)으로 전환되지 않음
            - BTC는 Safe Haven보다 Risk Asset 특성에 가까움
            """
        )


def render_risk_index():

    st.header("Risk Index — Custom GPR")

    st.markdown(
        """
        GDELT 뉴스 데이터를 기반으로 생성한 Custom GPR(F1~F5)와
        공식 GPR 지수를 비교하였다.
        """
    )

    col1, col2 = st.columns(2)

    with col1:

        img1 = load_image("경로 변경")

        if img1:
            st.image(
                img1,
                caption="Correlation Heatmap",
                use_column_width=True
            )

    with col2:

        img2 = load_image("경로 변경")

        if img2:
            st.image(
                img2,
                caption="Scatter Matrix",
                use_column_width=True
            )

    img3 = load_image("경로 변경")

    if img3:
        st.image(
            img3,
            caption="Custom GPR Time Series",
            use_column_width=True
        )

    img4 = load_image("경로 변경")

    if img4:
        st.image(
            img4,
            caption="Official vs Custom GPR",
            use_column_width=True
        )

    st.divider()

    st.subheader("Key Findings")

    st.info(
        """
        - F3 공식이 공식 GPR과 가장 높은 상관관계를 기록
        - 보도량과 tone 결합 방식이 지정학 리스크 반영에 가장 효과적
        - 공식 GPR과 유사한 시계열 패턴 확인
        """
    )


def render_volatility():

    st.header("Volatility — GARCH-X")

    st.markdown(
        """
        GARCH-X 및 EGARCH 모형을 활용하여
        BTC 변동성 구조와 외생변수 영향을 분석하였다.
        """
    )

    tab1, tab2 = st.tabs(
        ["Model Comparison", "Conditional Volatility"]
    )

    with tab1:

        col1, col2 = st.columns(2)

        with col1:

            img1 = load_image(
                "garch/result_csv_png/garch_model_comparison.png"
            )

            if img1:
                st.image(
                    img1,
                    caption="GARCH Model Comparison",
                    use_column_width=True
                )

        with col2:

            img2 = load_image("경로 변경")

            if img2:
                st.image(
                    img2,
                    caption="Gamma Coefficient Comparison",
                    use_column_width=True
                )

    with tab2:

        img3 = load_image(
            "garch/result_csv_png/garch_conditional_vol.png"
        )

        if img3:
            st.image(
                img3,
                caption="Conditional Volatility",
                use_column_width=True
            )

        img4 = load_image(
            "garch/result_csv_png/egarch_cond_vol_comparison.png"
        )

        if img4:
            st.image(
                img4,
                caption="GARCH vs EGARCH",
                use_column_width=True
            )

    st.divider()

    st.subheader("Key Findings")

    st.info(
        """
        - BTC 변동성은 지정학 리스크보다 시장 심리 변수 영향이 큼
        - Fear & Greed 변수는 반복적으로 유의하게 나타남
        - α+β 값이 높아 충격 지속성이 강하게 유지됨
        """
    )


def render_data():

    st.header("Data")

    tab1, tab2 = st.tabs(
        ["Raw Data", "Processed Data"]
    )

    with tab1:

        st.subheader("Raw Data")

        st.markdown(
            """
            - GDELT GKG Raw News
            - Event-level News Dataset
            - Financial Market Raw Data
            """
        )

        img1 = load_image("경로 변경")

        if img1:
            st.image(
                img1,
                caption="Raw Data Structure",
                use_column_width=True
            )

    with tab2:

        st.subheader("Processed Data")

        master = load_csv(
            "DataPipeline/processed_data/final/master_data.csv"
        )

        if master is None:

            st.error(
                "master_data.csv 경로 확인 필요"
            )

        else:

            st.caption(
                f"{len(master)} rows × {len(master.columns)} columns"
            )

            st.dataframe(
                master.head(100),
                use_container_width=True,
                hide_index=True
            )

        st.markdown(
            """
            ### Processed Outputs

            - Custom GPR(F1~F5)
            - market_returns.csv
            - master_data.csv
            """
        )



def run():

    st.set_page_config(
        page_title="BTC Safe-Haven Dashboard",
        page_icon="₿",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.sidebar.title("Navigation")

    section = st.sidebar.radio(
        "Section",
        [
            "Main",
            "Event Overview",
            "Safe-Haven Analysis",
            "Risk Index",
            "Volatility",
            "Data",
        ],
    )

    st.sidebar.divider()

    st.sidebar.markdown("### Geopolitical Events")

    for key, label in EVENT_LABEL.items():

        st.sidebar.caption(
            f"• {label} ({EVENT_DATE[key]})"
        )

    if section == "Main":
        render_main()

    elif section == "Event Overview":
        render_event_overview()

    elif section == "Safe-Haven Analysis":
        render_safe_haven_analysis()

    elif section == "Risk Index":
        render_risk_index()

    elif section == "Volatility":
        render_volatility()

    else:
        render_data()

    st.divider()

    st.caption(
        "2026 Capstone Project | BTC Safe-Haven Hypothesis"
    )


if __name__ == "__main__":
    run()