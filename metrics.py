"""Marketing KPI calculations."""
import pandas as pd

SUM_COLS = ["impressions", "clicks", "spend", "conversions", "revenue"]


def add_metrics(g: pd.DataFrame) -> pd.DataFrame:
    """Aggregated sums (per platform/campaign) se KPIs nikalta hai."""
    g = g.copy()
    g["CTR"] = g["clicks"] / g["impressions"]          # click-through rate
    g["CPC"] = g["spend"] / g["clicks"]                # cost per click
    g["CPA"] = g["spend"] / g["conversions"]           # cost per acquisition
    g["CVR"] = g["conversions"] / g["clicks"]          # conversion rate
    g["ROAS"] = g["revenue"] / g["spend"]              # return on ad spend
    g["profit"] = g["revenue"] - g["spend"]
    return g
