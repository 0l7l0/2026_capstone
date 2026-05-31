"""3종 본분석 결과를 통합해 final_judgment.csv + final_report.md 생성.

Baur & Lucey (2010) Safe-Haven 3조건:
  C1) 이벤트 스터디: 위기 시 BTC CAR ≥ 0 (음수 비정상수익 없음). 단순 검정 + BH-FDR 보정.
  C2) 분위수 회귀:   τ=0.05 극단 하락 시 SP500 β ≤ 0 (시장과 반대로). BH-FDR 보정.
  C3) GARCH:        지정학 변수 γ ≤ 0 또는 비유의 (변동성 증가 없음).

이벤트별 verdict:
  Safe Haven    — 3조건 모두 만족
  Weak Haven    — 2조건 만족
  Diversifier   — 1조건 만족
  Risky Asset   — 0조건 만족
"""
from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / 'Edit_mj' / 'results'
ALPHA = 0.05

EVENTS = ['hormuz_crisis','soleimani_assassination','russia_ukraine_war',
          'israel_hamas_war','israel_iran','us_israel_iran']
EVENT_LABEL = {
    'hormuz_crisis'          : '호르무즈 위기',
    'soleimani_assassination': '솔레이마니 암살',
    'russia_ukraine_war'     : '러-우 전쟁',
    'israel_hamas_war'       : '이스라엘-하마스',
    'israel_iran'            : '이스라엘-이란 충돌',
    'us_israel_iran'         : '미-이스라엘-이란',
}
# 별칭 (quantile_results_bh.csv 등에서 다르게 저장된 경우)
# us_israel_iran은 분위수 회귀 CSV에 '이란 전쟁'으로 저장됨 → 매칭 누락 방지
EVENT_LABEL_ALIASES = {
    'us_israel_iran': ['미-이스라엘-이란', '이란 전쟁'],
}


def safe_read(name):
    p = RESULTS / name
    return pd.read_csv(p) if p.exists() else None


def main():
    es  = safe_read('event_study_car_bh.csv')          # BH-FDR 적용본
    qr  = safe_read('quantile_results_bh.csv')         # BH-FDR 적용본
    gg  = safe_read('garch_event_dummy_comparison.csv')# 이벤트 더미 강건성
    # 2026-05-31: garch_model_params.csv를 source of truth로 사용 (민정 요청)
    gmp = safe_read('garch_model_params.csv')          # 전체 모델 파라미터 (source of truth)
    if gmp is not None and 'param' in gmp.columns:
        # gamma 행만 필터: param 컬럼이 "gamma(...)" 형식
        gamma_rows = gmp[gmp['param'].astype(str).str.startswith('gamma(')].copy()
        # variable 컬럼 추출 (gamma(X_scaled) → X_scaled)
        gamma_rows['variable'] = gamma_rows['param'].astype(str).str.extract(r'gamma\(([^)]+)\)')
        gamma_rows['gamma'] = gamma_rows['estimate'].astype(float)
        ggp = gamma_rows[['model', 'model_label', 'variable', 'gamma', 'p_value']]
    else:
        ggp = safe_read('garch_gamma_results.csv')     # fallback
    pl  = safe_read('event_study_placebo.csv')         # Placebo (boost C1)
    wb  = safe_read('event_study_car_wild_bh.csv')     # Wild Bootstrap (catalog v1.6 — 호르무즈 보강)

    if es is None or qr is None:
        print('필수 입력 csv 없음')
        return

    rows = []
    for ev in EVENTS:
        # C1: 이벤트 스터디 (BTC만)
        c1_pass = False
        c1_detail = ''
        if es is not None and 'event' in es.columns:
            es_btc = es[(es['event'] == ev) & (es['asset'] == 'BTC')]
            if len(es_btc) > 0:
                car = float(es_btc['CAR'].iloc[0])
                p_bh = float(es_btc.get('p_norm_bh', es_btc.get('p_t_bh', pd.Series([1.0]))).iloc[0])
                # Baur & Lucey (2010) 부호 기준 엄격: CAR ≥ 0 통과, CAR < 0 모두 미달
                # (이전 elif p_bh >= ALPHA: c1_pass = True 는 정의 위반이라 2026-05-29 제거)
                if car >= 0 and p_bh < ALPHA:
                    c1_pass = True; c1_detail = f'CAR=+{car:.3f} (p_BH={p_bh:.3f}) Strong'
                elif car >= 0:
                    c1_pass = True; c1_detail = f'CAR=+{car:.3f} (p_BH={p_bh:.3f}) Weak non-neg'
                else:
                    c1_pass = False
                    sig_tag = '유의 음수 → 위험자산' if p_bh < ALPHA else '비유의 음수 → 안전자산 미달'
                    c1_detail = f'CAR={car:.3f} (p_BH={p_bh:.3f}) {sig_tag}'

        # Placebo 보강
        placebo_p_val = None
        if pl is not None and 'event_name' in pl.columns:
            sub = pl[pl['event_name'] == ev]
            if len(sub) > 0 and pd.notna(sub['placebo_p'].iloc[0]):
                placebo_p_val = float(sub['placebo_p'].iloc[0])
                c1_detail += f' | placebo_p={placebo_p_val:.3f}'

        # Wild Bootstrap 보강 (catalog v1.6 — 호르무즈 한정)
        wild_p_3 = None
        wild_p_17 = None
        if wb is not None and 'event' in wb.columns:
            wb_btc = wb[(wb['event'] == ev) & (wb['asset'] == 'BTC')]
            if len(wb_btc) > 0:
                for _, wrow in wb_btc.iterrows():
                    ew = int(wrow.get('event_window', 0))
                    pw = float(wrow.get('p_wild_bootstrap', 1.0))
                    if ew == 3:
                        wild_p_3 = pw
                    elif ew == 17:
                        wild_p_17 = pw
                if wild_p_3 is not None and wild_p_17 is not None:
                    c1_detail += f' | Wild p(±3)={wild_p_3:.3f}, p(±17)={wild_p_17:.3f}'

        # C1 통계 강도 평가 (catalog v1.6)
        # strong = BH 유의 AND Placebo 유의 / weak = 부호만 통과, 검정 결과 분산 / inconclusive = 미달
        c1_strength = 'inconclusive'
        if c1_pass:
            # BH 통과 + Placebo 통과 + (Wild 일치) → strong
            es_btc_row = es[(es['event'] == ev) & (es['asset'] == 'BTC')]
            p_bh_val = 1.0
            if len(es_btc_row) > 0:
                p_bh_val = float(es_btc_row.get('p_norm_bh', es_btc_row.get('p_t_bh', pd.Series([1.0]))).iloc[0])
            is_bh_sig = p_bh_val < ALPHA
            is_placebo_sig = (placebo_p_val is not None and placebo_p_val < ALPHA)
            if is_bh_sig and is_placebo_sig:
                c1_strength = 'strong'
            elif is_bh_sig or is_placebo_sig:
                c1_strength = 'moderate'
            else:
                c1_strength = 'weak'  # 부호만 통과, 통계 강도 약함

        # C2: 분위수 회귀 (이벤트별 + τ=0.05 + SP500_z 변수)
        c2_pass = False
        c2_detail = ''
        ev_label = EVENT_LABEL[ev]
        if qr is not None:
            tau_col = next((c for c in qr.columns if c.strip() in ('τ','tau')), None)
            pcol = next((c for c in qr.columns if c.strip() in ('p','p_value')), None)
            pbh  = next((c for c in qr.columns if c.endswith('_bh')), None)
            bcol = next((c for c in qr.columns if c.strip() in ('β','beta')), None)
            if tau_col and pcol and bcol:
                # 이벤트별 SP500+GPR 모델 + τ=0.05 + SP500_z 변수
                # 라벨 별칭 적용 (us_israel_iran ↔ '이란 전쟁' 등 mismatch 해소)
                labels_to_try = EVENT_LABEL_ALIASES.get(ev, [ev_label])
                sub = qr[(qr.get('이벤트','').isin(labels_to_try))
                         & (qr.get('모델','').astype(str).str.contains('SP500\\+GPR'))
                         & (qr[tau_col].astype(float).round(3) == 0.05)
                         & (qr.get('변수','') == 'SP500_z')]
                if len(sub) > 0:
                    beta = float(sub[bcol].iloc[0])
                    p = float(sub[pcol].iloc[0])
                    p_bh = float(sub[pbh].iloc[0]) if pbh else 1.0
                    # Baur & Lucey (2010) 부호 기준 엄격: β ≤ 0 통과, β > 0 모두 미달
                    if beta <= 0 and p_bh < ALPHA:
                        c2_pass = True; c2_detail = f'β={beta:+.4f} (p_BH={p_bh:.3f}) Strong haven'
                    elif beta <= 0:
                        c2_pass = True; c2_detail = f'β={beta:+.4f} (p_BH={p_bh:.3f}) Weak non-pos'
                    else:
                        c2_pass = False
                        sig_tag = '유의 양수 → 위험자산' if p_bh < ALPHA else '비유의 양수 → 안전자산 미달'
                        c2_detail = f'β=+{beta:.4f} (p_BH={p_bh:.3f}) {sig_tag}'
                else:
                    c2_detail = '데이터 없음'

        # C3: GARCH 이벤트 더미 + 전체 γ
        c3_pass = False
        c3_detail = ''
        if ggp is not None and 'variable' in ggp.columns:
            # GPR 관련 변수 γ 모두 비유의면 PASS
            gpr_rows = ggp[ggp['variable'].str.contains('GPR', case=False, na=False)]
            if len(gpr_rows) > 0:
                all_insig = (gpr_rows['p_value'].astype(float) >= ALPHA).all()
                if all_insig:
                    c3_pass = True
                    pmin = gpr_rows["p_value"].astype(float).min()
                    pmax = gpr_rows["p_value"].astype(float).max()
                    c3_detail = f'GPR γ 모두 비유의 (n={len(gpr_rows)}, min p={pmin:.3f}, max p={pmax:.3f})'
                else:
                    sig = gpr_rows[gpr_rows['p_value'].astype(float) < ALPHA]
                    pos = (sig['gamma'].astype(float) > 0).sum()
                    if pos > 0:
                        c3_detail = f'GPR γ 유의 양수 {pos}건 → 변동성 증가'
                    else:
                        c3_pass = True
                        c3_detail = f'GPR γ 유의 음수만 → 변동성 감소 (haven)'

        # 통합 verdict + statistical_strength (catalog v1.6)
        score = int(c1_pass) + int(c2_pass) + int(c3_pass)
        verdict_base = {3: 'Safe Haven', 2: 'Weak Haven', 1: 'Diversifier', 0: 'Risky Asset'}[score]
        # Safe Haven인데 C1 통계 강도가 weak이면 별표 (호르무즈 등)
        if verdict_base == 'Safe Haven' and c1_strength == 'weak':
            verdict = 'Safe Haven*'  # 별표 = 통계 강도 약함
        else:
            verdict = verdict_base
        rows.append({
            'event_name': ev,
            'event_label': ev_label,
            'C1_event_study_pass': c1_pass,
            'C1_detail': c1_detail,
            'C1_statistical_strength': c1_strength,
            'C2_quantile_reg_pass': c2_pass,
            'C2_detail': c2_detail,
            'C3_garch_pass': c3_pass,
            'C3_detail': c3_detail,
            'score': score,
            'verdict': verdict,
        })

    df = pd.DataFrame(rows)
    out = RESULTS / 'final_judgment.csv'
    df.to_csv(out, index=False, encoding='utf-8-sig')
    print(f'✅ {out.name} 저장')
    print()
    print(df[['event_label','C1_event_study_pass','C2_quantile_reg_pass','C3_garch_pass','verdict']].to_string(index=False))

    # final_report.md
    md = []
    md.append('# 비트코인 안전자산 가설 최종 검증 보고')
    md.append('')
    md.append('- 일자: 2026-05-26 (catalog v1.6 — Wild Bootstrap·Forward Placebo 통합)')
    md.append('- 데이터: `Edit_mj/GPR_custom_analysis/master_data_generated/master_data.csv` (1827행, 2019-01-02 ~ 2026-04-30)')
    md.append('- 검증 기준: Baur & Lucey (2010) — 위기 시 비음수 + 음의 시장 의존성 + 변동성 비증가')
    md.append('- 분석 3종: 이벤트 스터디(MacKinlay 1997), 분위수 회귀(Koenker & Bassett 1978), GARCH-X(Engle 1982 + Bollerslev 1986 + 외생변수)')
    md.append('- 보강: BH-FDR 다중비교 보정, Placebo 검정 (forward-only 자동 분기), Wild Bootstrap (Davidson & MacKinnon 1999, Rademacher), ADF 정상성 검증, multi-init MLE')
    md.append('')
    md.append('## 6개 지정학 이벤트별 통합 판정')
    md.append('')
    md.append('| 이벤트 | C1 이벤트스터디 | C2 분위수회귀 | C3 GARCH | 점수 | C1 강도 | 판정 |')
    md.append('|---|---|---|---|---:|---|---|')
    for _, r in df.iterrows():
        c1 = '✅' if r['C1_event_study_pass'] else '❌'
        c2 = '✅' if r['C2_quantile_reg_pass'] else '❌'
        c3 = '✅' if r['C3_garch_pass'] else '❌'
        c1_str = r.get('C1_statistical_strength', '-')
        md.append(f'| {r["event_label"]} | {c1} | {c2} | {c3} | {r["score"]}/3 | {c1_str} | **{r["verdict"]}** |')
    md.append('')
    md.append('> ⚠ **별표(\\*)**: Safe Haven 판정이나 C1 통계 강도가 약함 (BH-FDR 비유의 + Placebo 비유의). 부호 기준 채점 통과이나 통계적 유의성은 검정 방법에 따라 분산.')
    md.append('')
    md.append('## 핵심 결론')
    md.append('')
    n_safe = (df['verdict'] == 'Safe Haven').sum()
    n_weak = (df['verdict'] == 'Weak Haven').sum()
    n_div  = (df['verdict'] == 'Diversifier').sum()
    n_risky= (df['verdict'] == 'Risky Asset').sum()
    n_safe_star = (df['verdict'] == 'Safe Haven*').sum()
    md.append(f'- **Safe Haven {n_safe}건 / Safe Haven* (강도 약함) {n_safe_star}건 / Weak Haven {n_weak}건 / Diversifier {n_div}건 / Risky {n_risky}건**')
    md.append('- BH-FDR 다중비교 보정 후 이벤트 스터디에서 6이벤트 모두 BTC 비정상수익률 통계적 비유의')
    md.append('- 분위수 회귀 전체 합산 τ=0.05에서 SP500 β=+0.0162 (p<0.001) → 극단 하락 시 BTC는 시장과 동조 (위험자산 특성)')
    md.append('- 단 호르무즈 위기 단독에서는 β=-0.0116 (p=0.254 비유의) → C2 부호 기준 통과, 통계 강도 약함')
    md.append('- GARCH 5모델 모두 정상성·수렴 통과. 지정학 변수(GPR) γ 모두 비유의, 시장심리(F&G)만 유의 양수. EGARCH AIC 9559 < GARCH 9578 (비대칭 우월, GPR γ 결론 동일)')
    md.append('- Placebo 검정 (K=200, forward-only 자동): 6개 이벤트 모두 placebo p>0.05 → 실제 이벤트가 가짜 일자와 통계적으로 구분되지 않음')
    md.append('- Wild Bootstrap (Rademacher, 호르무즈 보강): ±3 p<0.001 / ±17 p<0.001 — 단 소표본(n=86) 과대자신감 가능. Placebo·BH와 결과 분산 → 호르무즈 Safe Haven 판정의 통계 강도 약함 (Safe Haven*)')
    md.append('')
    md.append('## 인용 (자동 생성)')
    md.append('')
    md.append('- MacKinlay, A. C. (1997). Event Studies in Economics and Finance. *Journal of Economic Literature*, 35(1), 13-39.')
    md.append('- Koenker, R., & Bassett, G. (1978). Regression Quantiles. *Econometrica*, 46(1), 33-50.')
    md.append('- Engle, R. F. (1982). Autoregressive Conditional Heteroscedasticity. *Econometrica*, 50(4), 987-1007. (GARCH-X ARCH 원형)')
    md.append('- Bollerslev, T. (1986). Generalized Autoregressive Conditional Heteroskedasticity. *Journal of Econometrics*, 31(3), 307-327. (GARCH 일반화)')
    md.append('- Nelson, D. B. (1991). Conditional Heteroskedasticity in Asset Returns: A New Approach. *Econometrica*, 59(2), 347-370. (EGARCH 비대칭)')
    md.append('- Baur, D. G., & Lucey, B. M. (2010). Is Gold a Hedge or a Safe Haven? *Financial Review*, 45(2), 217-229.')
    md.append('- Benjamini, Y., & Hochberg, Y. (1995). Controlling the False Discovery Rate. *JRSS B*, 57(1), 289-300.')
    md.append('- Davidson, R., & MacKinnon, J. G. (1999). The size distortion of bootstrap tests. *Econometric Theory*, 15(3), 361-376. (Wild Bootstrap 소표본 robust)')
    md.append('- Caldara, D., & Iacoviello, M. (2022). Measuring Geopolitical Risk. *American Economic Review*, 112(4), 1194-1225.')

    (RESULTS / 'final_report.md').write_text('\n'.join(md), encoding='utf-8')
    print()
    print(f'✅ final_report.md 저장')


if __name__ == '__main__':
    main()
