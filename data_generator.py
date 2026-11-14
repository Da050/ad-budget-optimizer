"""Simulated digital-advertising data generator."""
import numpy as np
import pandas as pd

PLATFORMS = ["Facebook", "Instagram", "Google", "TikTok", "YouTube"]

# Har platform ke hidden characteristics (simulation assumptions)
#             CTR     CPC(Rs)  CVR     AOV(Rs)
PROFILE = {
    "Facebook":  (0.015, 28, 0.030, 4500),
    "Instagram": (0.020, 32, 0.035, 4800),
    "Google":    (0.030, 40, 0.060, 5200),
    "TikTok":    (0.025, 18, 0.015, 3200),
    "YouTube":   (0.010, 22, 0.020, 4000),
}

CITIES = ["Lahore", "Karachi", "Islamabad", "Faisalabad", "Multan"]
DEVICES = ["mobile", "desktop", "tablet"]
CAMPAIGNS = [f"camp_{i:02d}" for i in range(50)]


def generate(n: int, seed: int = 42) -> pd.DataFrame:
    """Generate n ad-performance records."""
    rng = np.random.default_rng(seed)

    p_idx = rng.integers(0, len(PLATFORMS), n)
    ctr = np.array([PROFILE[p][0] for p in PLATFORMS])[p_idx]
    cpc = np.array([PROFILE[p][1] for p in PLATFORMS])[p_idx]
    cvr = np.array([PROFILE[p][2] for p in PLATFORMS])[p_idx]
    aov = np.array([PROFILE[p][3] for p in PLATFORMS])[p_idx]

    impressions = rng.integers(1_000, 50_000, n)
    clicks = rng.binomial(impressions, np.clip(ctr * rng.uniform(0.7, 1.3, n), 0, 1))
    spend = clicks * cpc * rng.uniform(0.8, 1.2, n)
    conversions = rng.binomial(clicks, np.clip(cvr * rng.uniform(0.7, 1.3, n), 0, 1))
    revenue = conversions * aov * rng.uniform(0.8, 1.2, n)

    def cat(values, probs=None):
        codes = rng.choice(len(values), n, p=probs)
        return pd.Categorical.from_codes(codes, categories=values)

    return pd.DataFrame({
        "date": pd.Timestamp("2025-01-01") + pd.to_timedelta(rng.integers(0, 365, n), unit="D"),
        "campaign": cat(CAMPAIGNS),
        "platform": pd.Categorical.from_codes(p_idx, categories=PLATFORMS),
        "impressions": impressions,
        "clicks": clicks,
        "spend": spend.round(2),
        "conversions": conversions,
        "revenue": revenue.round(2),
        "age": rng.integers(18, 55, n),
        "gender": cat(["M", "F"]),
        "city": cat(CITIES),
        "device": cat(DEVICES, [0.70, 0.25, 0.05]),
    })
