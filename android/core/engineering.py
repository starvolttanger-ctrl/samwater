import math

def water_chemistry(cations, anions, sio2, ca, mg, ph, tds, temp_c, alk, pca, palk, k):
    """cations/anions: {ion: (mg/L, poids équivalent)}"""
    cat = sum(c / e for c, e in cations.values())
    an = sum(c / e for c, e in anions.values())
    tot = cat + an
    err = 0.0 if tot == 0 else 100 * (cat - an) / tot
    tds_calc = sum(c for c, _ in cations.values()) + sum(c for c, _ in anions.values()) + sio2
    hard = 2.497 * ca + 4.118 * mg
    if min(tds, temp_c + 273.15, alk, ca) <= 0:
        raise ValueError("TDS, T absolue, alcalinité et Ca doivent être > 0")
    A = (math.log10(tds) - 1) / 10
    B = -13.12 * math.log10(temp_c + 273.15) + 34.55
    C = math.log10(ca) - 0.4
    D = math.log10(alk)
    phs = 9.3 + A + B - C - D
    return {"Cations (meq/L)": cat, "Anions (meq/L)": an,
            "Erreur balance (%)": err, "TDS calculé (mg/L)": tds_calc,
            "Dureté totale (mg/L CaCO3)": hard, "LSI": ph - phs,
            "S&DSI": ph - pca - palk - k,
            "Pression osmotique (bar)": 0.0385 * (tds / 1000) * ((temp_c + 273.15) / 298.15)}

def mineral_saturation(ca, so4, ba, sr, f, sio2, ksp_caso4, ksp_baso4, ksp_srso4, ksp_caf2, sio2_sol):
    def pct(iap, ksp):
        return 100 * iap / ksp if ksp > 0 else float("inf")
    mm = {"Ca": 40.08, "SO4": 96.06, "Ba": 137.33, "Sr": 87.62, "F": 19.0}
    iap_caso4 = (ca / mm["Ca"] / 1000) * (so4 / mm["SO4"] / 1000)
    iap_baso4 = (ba / mm["Ba"] / 1000) * (so4 / mm["SO4"] / 1000)
    iap_srso4 = (sr / mm["Sr"] / 1000) * (so4 / mm["SO4"] / 1000)
    iap_caf2 = (ca / mm["Ca"] / 1000) * (f / mm["F"] / 1000) ** 2
    return {"CaSO4 (%)": pct(iap_caso4, ksp_caso4), "BaSO4 (%)": pct(iap_baso4, ksp_baso4),
            "SrSO4 (%)": pct(iap_srso4, ksp_srso4), "CaF2 (%)": pct(iap_caf2, ksp_caf2),
            "SiO2 (%)": 100 * sio2 / sio2_sol if sio2_sol > 0 else float("inf")}

def uf(q_fil, area, p_feed, p_conc, p_fil, v_fil, v_bw, tcf):
    if min(area, tcf, v_fil) <= 0:
        raise ValueError("Surface, TCF et volume filtrat > 0 requis")
    flux = q_fil / area
    tmp = (p_feed + p_conc) / 2 - p_fil
    if tmp <= 0:
        raise ValueError("TMP doit être > 0")
    return {"Flux (LMH)": flux, "TMP (bar)": tmp,
            "Récupération (%)": 100 * (v_fil - v_bw) / v_fil,
            "Perméabilité (LMH/bar)": flux / (tmp * tcf)}

def ro_nf(q_perm, q_feed, c_perm, c_feed, p_feed, dp_stage, p_perm,
          osm_avg, osm_perm, A, B, c_memb, k_mass, y,
          q_act, ndp_init, ndp_act, tcf_init, tcf_act):
    if min(q_feed, c_feed) <= 0:
        raise ValueError("Débit et concentration d'alimentation > 0 requis")
    ndp = (p_feed - dp_stage / 2 - p_perm) - (osm_avg - osm_perm)
    jw = A * ndp
    js = B * (c_memb - c_perm)
    rej = (1 - c_perm / c_feed) * 100
    return {"Récupération (%)": 100 * q_perm / q_feed,
            "Rejet de sel (%)": rej, "Passage de sel (%)": 100 - rej,
            "NDP (bar)": ndp, "Flux d'eau Jw": jw, "Flux de sel Js": js,
            "CPF exp(Jw/k)": math.exp(jw / k_mass) if k_mass > 0 else float("inf"),
            "CPF 1+0.7Y": 1 + 0.7 * y,
            "Q perm. normalisé (ASTM D4516)": q_act * (ndp_init / ndp_act) * (tcf_init / tcf_act)}

def ion_exchange(v_water_m3, v_resin_l, eq_removed, mass_chem_g, dosage_eq_l):
    if v_resin_l <= 0:
        raise ValueError("Volume de résine > 0 requis")
    cap = eq_removed / v_resin_l
    return {"Bed Volumes (BV)": v_water_m3 * 1000 / v_resin_l,
            "Capacité opératoire (eq/L)": cap,
            "Dosage régénérant (g/L)": mass_chem_g / v_resin_l,
            "Efficacité régénération (%)": 100 * cap / dosage_eq_l if dosage_eq_l > 0 else 0}

def blending(q1, c1, q2, c2):
    if q1 + q2 <= 0:
        raise ValueError("Débit total > 0 requis")
    return {"Concentration finale": (q1 * c1 + q2 * c2) / (q1 + q2)}

def sec(power_kw, flow_m3h):
    if flow_m3h <= 0:
        raise ValueError("Débit > 0 requis")
    return {"SEC (kWh/m3)": power_kw / flow_m3h}

def chemical_dosing(q_water, dose, conc_pct, sg, alum_dose, cl_resid, contact_min):
    den = conc_pct * 10 * sg
    if den <= 0:
        raise ValueError("Concentration et densité > 0 requises")
    return {"Pompe doseuse (L/h)": q_water * dose / den,
            "Alcalinité consommée alun (mg/L CaCO3)": alum_dose * 0.5,
            "CT chlore (mg.min/L)": cl_resid * contact_min}

def media_filtration(q, a_filter, h_settled, h_expanded, a_settling):
    if min(a_filter, h_settled, a_settling) <= 0:
        raise ValueError("Surfaces et hauteur > 0 requises")
    return {"Vitesse filtration (m/h)": q / a_filter,
            "Expansion du lit (%)": 100 * (h_expanded - h_settled) / h_settled,
            "SOR (m3/m2.h)": q / a_settling}

def wastewater(q, bod5, v_aer, mlvss, mlss, ssv30, q_w, x_w, q_e, x_e, v_tank):
    if min(q, v_aer, mlvss, mlss) <= 0:
        raise ValueError("Débit, volumes, MLSS/MLVSS > 0 requis")
    out = q_w * x_w + q_e * x_e
    return {"HRT (h)": v_tank / q,
            "SRT (j)": v_aer * mlss / out if out > 0 else float("inf"),
            "F/M (1/j)": q * bod5 / (v_aer * mlvss),
            "SVI (mL/g)": ssv30 * 1000 / mlss}

def pump_hydraulics(q, h_dis_static, h_suc_static, hf, h_minor, p_dis, p_suc, sg,
                    eff_p, eff_m, eff_vfd, f, L, D, vel,
                    h_baro, h_suc_fric, h_vapor):
    if min(sg, eff_p, eff_m, eff_vfd, D) <= 0:
        raise ValueError("SG, rendements et diamètre > 0 requis")
    h_static = h_dis_static - h_suc_static
    tdh = h_static + hf + h_minor + (p_dis - p_suc) * 10.197 / sg
    pw = q * tdh * sg / 367
    return {"H statique (m)": h_static,
            "TDH (m)": tdh,
            "Perte Darcy (m)": f * (L / D) * vel ** 2 / (2 * 9.81),
            "P hydraulique (kW)": pw,
            "P arbre BHP (kW)": pw / eff_p,
            "P électrique (kW)": pw / (eff_p * eff_m * eff_vfd),
            "Rendement système (%)": 100 * eff_p * eff_m * eff_vfd,
            "NPSHA (m)": h_baro + h_suc_static - h_suc_fric - h_vapor}

def ro_pumps(ndp, osm_avg, dp_stages, p_perm_bp, q_feed, q_perm, q_conc,
             p_conc, erd_eff, eff_p, eff_m):
    if min(eff_p, eff_m) <= 0:
        raise ValueError("Rendements > 0 requis")
    p_feed = ndp + osm_avg + dp_stages + p_perm_bp
    p_no = q_feed * p_feed / (36 * eff_p * eff_m)
    p_erd = (q_perm * p_feed + q_conc * (p_feed - p_conc * erd_eff)) / (36 * eff_p * eff_m)
    return {"P alimentation requise (bar)": p_feed,
            "P HPP sans ERD (kW)": p_no,
            "P HPP avec ERD (kW)": p_erd,
            "SEC RO (kWh/m3)": p_erd / q_perm if q_perm > 0 else float("inf")}

def dosing_pumps(q_raw, dose, conc_pct, sg, q_max, stroke_pct, freq_pct,
                 vol_ml, time_s, p_line, dp_valve):
    den = conc_pct * 10 * sg
    if min(den, time_s) <= 0:
        raise ValueError("Concentration, densité et temps > 0 requis")
    return {"Q doseuse (L/h)": q_raw * dose / den,
            "Q réel course/fréq. (L/h)": q_max * stroke_pct / 100 * freq_pct / 100,
            "Q mesuré calibration (L/h)": vol_ml / time_s * 3.6,
            "P nominale min. (bar)": p_line + dp_valve + 1.5}

def instrumentation(i_ma, pv_min, pv_max, cond, k):
    return {"Valeur mesurée (4-20 mA)": pv_min + (i_ma - 4) / 16 * (pv_max - pv_min),
            "TDS depuis conductivité (mg/L)": k * cond}

def affinity(q1, h1, p1, n1, n2, d1, d2):
    if min(n1, d1) <= 0:
        raise ValueError("N1 et D1 > 0 requis")
    rn, rd = n2 / n1, d2 / d1
    return {"Q2 vitesse": q1 * rn, "H2 vitesse": h1 * rn ** 2, "P2 vitesse": p1 * rn ** 3,
            "Q2 diamètre": q1 * rd, "H2 diamètre": h1 * rd ** 2, "P2 diamètre": p1 * rd ** 3}
