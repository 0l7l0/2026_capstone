"""Wild Bootstrap (Davidson & MacKinnon 1999, 2010; Mammen 1993) — 호르무즈 위기 한정 보강.

이벤트 스터디 CAR p값을 Wild Bootstrap (Rademacher 가중치)으로 재계산.
본분석(Stationary Bootstrap, Politis & Romano 1994)과 비교 → 견고성 확인.

배경:
  - 호르무즈 위기(2019-06-13)는 데이터 시작(2019-01-02) 근접 → 추정창 부족 (112일, 표준 120일에서 -8일)
  - Stationary Bootstrap은 자기상관 보존이 강점이지만 소표본에서 부정확 가능
  - Wild Bootstrap은 잔차 분포 가정 최소화 → 소표본·이분산성 robust

사용:
    python3 _verifier/wild_bootstrap.py [--event hormuz_crisis] [--n-boot 5000] [--seed 42]

산출:
    Edit_mj/results/event_study_car_wild_bh.csv

인용:
    Davidson, R., & MacKinnon, J. G. (1999). The size distortion of bootstrap tests.
        Econometric Theory, 15(3), 361-376.
    Davidson, R., & MacKinnon, J. G. (2010). Wild bootstrap tests for IV regression.
        JBES, 28(1), 128-144.
    Mammen, E. (1993). Bootstrap and wild bootstrap for high dimensional linear models.
        Annals of Statistics, 21(1), 255-285.
"""
import argparse
import numpy as np
import pandas as pd
from pathlib import Path
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
RETURNS = ROOT / 'Edit_mj/GPR_custom_analysis/master_data_generated/returns.csv'
MASTER = ROOT / 'Edit_mj/GPR_custom_analysis/master_data_generated/master_data.csv'
OUT = ROOT / 'Edit_mj/results/event_study_car_wild_bh.csv'

# 본분석과 동일 파라미터
EST_END = -26       # 추정창 종료 (이벤트일 기준)
EST_START_TARGET = -120  # 추정창 시작 목표 (가능하면)
MARKET_ASSET = 'SP500'   # 시장 모델 기준
DEFAULT_ASSETS = ['BTC', 'Gold', 'TLT', 'DXY', 'NASDAQ']  # SP500은 시장이므로 제외

# 본분석 셀 [21]에서 EVENT_WINDOW=3으로 재정의되어 실제 사용. catalog 표준은 17.
# 두 윈도우 모두 실행해서 견고성 비교.
DEFAULT_WINDOWS = [3, 17]  # ±3 (본분석 실제), ±17 (catalog 표준)

EVENT_DATES = {
    'hormuz_crisis':           '2019-06-13',
    'soleimani_assassination': '2020-01-03',
    'russia_ukraine_war':      '2022-02-24',
    'israel_hamas_war':        '2023-10-07',
    'israel_iran':             '2024-04-01',
    'us_israel_iran':          '2026-02-28',
}

EVENT_LABELS = {
    'hormuz_crisis':           '호르무즈 위기',
    'soleimani_assassination': '솔레이마니 암살',
    'russia_ukraine_war':      '러-우 전쟁',
    'israel_hamas_war':        '이스라엘-하마스',
    'israel_iran':             '이스라엘-이란 충돌',
    'us_israel_iran':          '미-이스라엘-이란',
}


def market_model_residuals(asset_ret, mkt_ret):
    """OLS 시장 모델 r_i = α + β·r_m + ε 추정 → (α, β, 잔차)."""
    X = np.column_stack([np.ones(len(mkt_ret)), mkt_ret])
    coef, *_ = np.linalg.lstsq(X, asset_ret, rcond=None)
    alpha, beta = coef
    resid = asset_ret - (alpha + beta * mkt_ret)
    return alpha, beta, resid


def cmrm_mean(asset_ret):
    """Constant Mean Return Model (BTC용): μ̂ + 잔차."""
    mu = asset_ret.mean()
    resid = asset_ret - mu
    return mu, resid


def wild_bootstrap_event_study(returns_df, event_date, asset, event_window, use_cmrm=False,
                                n_boot=5000, seed=42):
    """Wild Bootstrap (Rademacher) — 단일 자산·단일 이벤트·단일 윈도우.

    Returns: dict {CAR, t_stat, p_norm, p_wild, n_est, n_event, est_window_actual}
    """
    rng = np.random.default_rng(seed)
    event_idx = returns_df.index[returns_df['date'] == event_date][0]

    # 추정창: [-120, -26] 목표, 데이터 부족 시 가능한 최대
    est_start_desired = event_idx + EST_START_TARGET
    est_end_idx = event_idx + EST_END
    est_start_idx = max(0, est_start_desired)
    n_est = est_end_idx - est_start_idx
    if n_est < 30:
        return None  # 추정 불가

    # 이벤트창: [-event_window, +event_window]
    evt_start = event_idx - event_window
    evt_end = min(len(returns_df) - 1, event_idx + event_window)
    n_evt = evt_end - evt_start + 1

    asset_full = returns_df[asset].values
    mkt_full = returns_df[MARKET_ASSET].values

    asset_est = asset_full[est_start_idx:est_end_idx]
    mkt_est = mkt_full[est_start_idx:est_end_idx]
    asset_evt = asset_full[evt_start:evt_end + 1]
    mkt_evt = mkt_full[evt_start:evt_end + 1]

    # 1. 본분석 (Market Model 또는 CMRM)
    if use_cmrm:
        mu_hat, resid_est = cmrm_mean(asset_est)
        expected_evt = np.full(n_evt, mu_hat)
    else:
        alpha_hat, beta_hat, resid_est = market_model_residuals(asset_est, mkt_est)
        expected_evt = alpha_hat + beta_hat * mkt_evt

    ar_evt = asset_evt - expected_evt
    car = ar_evt.sum()
    se_ar = resid_est.std(ddof=1)
    t_stat = car / (se_ar * np.sqrt(n_evt)) if se_ar > 0 else 0.0
    p_norm = 2 * (1 - stats.norm.cdf(abs(t_stat)))

    # 2. Wild Bootstrap (Rademacher: w ∈ {-1, +1})
    car_boot = np.empty(n_boot)
    for b in range(n_boot):
        w_est = rng.choice([-1.0, 1.0], size=n_est)
        w_evt = rng.choice([-1.0, 1.0], size=n_evt)
        resid_star_est = w_est * resid_est
        if use_cmrm:
            asset_est_star = mu_hat + resid_star_est
            mu_star, _ = cmrm_mean(asset_est_star)
            ar_star = (asset_evt - mu_star) + w_evt * 0  # 이벤트창 잔차도 wild
            # 표준 형태: AR* = (r_evt - μ*) + w_evt·(원 잔차의 신호 없음 = 0)
            # 더 정석: 이벤트창 잔차를 무관 가정 → AR* = r_evt - μ*
            car_boot[b] = (asset_evt - mu_star).sum()
        else:
            asset_est_star = alpha_hat + beta_hat * mkt_est + resid_star_est
            X_est = np.column_stack([np.ones(n_est), mkt_est])
            coef_star, *_ = np.linalg.lstsq(X_est, asset_est_star, rcond=None)
            alpha_star, beta_star = coef_star
            expected_evt_star = alpha_star + beta_star * mkt_evt
            ar_star = asset_evt - expected_evt_star
            car_boot[b] = ar_star.sum()

    # Wild p값: H0 (CAR_true = 0) 하에서 분포 비교
    # 정석: bootstrap CAR을 평균 0으로 센터링 후 |CAR_boot| >= |CAR_obs| 비율
    car_boot_centered = car_boot - car_boot.mean()
    p_wild = (np.abs(car_boot_centered) >= np.abs(car)).mean()

    return dict(
        CAR=car,
        t_stat=t_stat,
        p_norm=p_norm,
        p_wild=p_wild,
        n_est=n_est,
        n_evt=n_evt,
        est_window_actual=f'[-{est_end_idx - est_start_idx + abs(EST_END)}, {EST_END}]',
        car_boot_mean=car_boot.mean(),
        car_boot_std=car_boot.std(ddof=1),
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--event', default='hormuz_crisis',
                        help='이벤트 키 (호르무즈 단독: hormuz_crisis, 전체: all)')
    parser.add_argument('--n-boot', type=int, default=5000)
    parser.add_argument('--seed', type=int, default=42)
    args = parser.parse_args()

    returns = pd.read_csv(RETURNS)
    returns['date'] = pd.to_datetime(returns['date'])
    returns = returns.reset_index(drop=True)

    events = list(EVENT_DATES.keys()) if args.event == 'all' else [args.event]

    rows = []
    print('=' * 78)
    print(f'Wild Bootstrap (Rademacher, N_BOOT={args.n_boot}, seed={args.seed})')
    print('Davidson & MacKinnon (1999, ET 15:361-376)')
    print('=' * 78)

    for ev in events:
        ev_date = pd.Timestamp(EVENT_DATES[ev])
        ev_label = EVENT_LABELS[ev]
        if ev_date not in returns['date'].values:
            print(f'⚠ {ev} ({ev_date.date()}) 거래일 아님 — 가장 가까운 다음 거래일 탐색')
            ev_date = returns.loc[returns['date'] >= ev_date, 'date'].iloc[0]
        print(f'\n▶ {ev_label} ({ev_date.date()})')

        for ew in DEFAULT_WINDOWS:
            ew_label = f'±{ew}일'
            ew_note = '(본분석 실제)' if ew == 3 else '(catalog 표준)'
            print(f'  [이벤트창 {ew_label} {ew_note}]')
            for asset in DEFAULT_ASSETS:
                use_cmrm = (asset == 'BTC')  # BTC는 CMRM (본분석과 동일)
                res = wild_bootstrap_event_study(
                    returns, ev_date, asset, event_window=ew, use_cmrm=use_cmrm,
                    n_boot=args.n_boot, seed=args.seed + hash(asset) % 1000 + ew,
                )
                if res is None:
                    print(f'    {asset:8s}  추정창 부족 — 스킵')
                    continue
                sig_norm = res['p_norm'] < 0.05
                sig_wild = res['p_wild'] < 0.05
                print(f'    {asset:8s}  CAR={res["CAR"]:+.4f}  t={res["t_stat"]:+.3f}  '
                      f'p_norm={res["p_norm"]:.3f}  p_wild={res["p_wild"]:.3f}  '
                      f'sig_wild={"✓" if sig_wild else "✗"}  '
                      f'est={res["n_est"]}일{"(부족!)" if res["n_est"] < 90 else ""}')
                rows.append(dict(
                    event=ev,
                    event_label=ev_label,
                    event_date=ev_date.date().isoformat(),
                    asset=asset,
                    event_window=ew,
                    event_window_note=ew_note.strip('()'),
                    model='CMRM' if use_cmrm else 'MarketModel',
                    CAR=res['CAR'],
                    t_stat=res['t_stat'],
                    p_norm=res['p_norm'],
                    p_wild_bootstrap=res['p_wild'],
                    sig_norm=sig_norm,
                    sig_wild=sig_wild,
                    n_est=res['n_est'],
                    n_evt=res['n_evt'],
                    est_window_short=(res['n_est'] < 90),
                    car_boot_mean=res['car_boot_mean'],
                    car_boot_std=res['car_boot_std'],
                    n_boot=args.n_boot,
                    bootstrap_method='Wild (Rademacher)',
                    citation='Davidson & MacKinnon (1999, ET 15:361-376)',
                ))

    df = pd.DataFrame(rows)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False, encoding='utf-8-sig')
    print(f'\n✅ 저장: {OUT}')
    print(f'  {len(df)} 행, Wild sig: {df["sig_wild"].sum()}/{len(df)}')


if __name__ == '__main__':
    main()
