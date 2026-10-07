EQ = {"Ca": 20.04, "Mg": 12.15, "Na": 23.0, "K": 39.1,
      "HCO3": 61.0, "Cl": 35.45, "SO4": 48.03}

def to_mg_l(v, unit, ion):
    return v * EQ[ion] if unit == "meq/L" else v
