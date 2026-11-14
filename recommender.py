"""Marketing Budget Recommendation Engine."""
import pandas as pd

from .metrics import SUM_COLS, add_metrics


def recommend(metrics: pd.DataFrame, budget: float = 1_000_000,
              min_share: float = 0.05, max_share: float = 0.45) -> pd.DataFrame:
    """ROAS-weighted allocation.
    - Jis platform ka ROAS zyada, usko zyada budget.
    - min/max caps: ek platform par saara paisa nahi (diminishing returns guard)
      aur kisi ko bilkul zero nahi (testing/brand reach).
    """
    share = metrics["ROAS"] / metrics["ROAS"].sum()
    for _ in range(10):                      # cap lagane ke baad re-normalize
        share = share.clip(min_share, max_share)
        share = share / share.sum()
    out = pd.DataFrame({
        "ROAS": metrics["ROAS"].round(2),
        "CPA": metrics["CPA"].round(0),
        "share_pct": (share * 100).round(1),
        "budget_rs": (share * budget).round(0),
    })
    out["expected_revenue_rs"] = (out["budget_rs"] * metrics["ROAS"]).round(0)
    return out.sort_values("share_pct", ascending=False)


def recommend_by_segment(df: pd.DataFrame, segment: str, **kw) -> dict:
    """Segment-wise (jaise device ya city) alag recommendation."""
    result = {}
    for seg, part in df.groupby(segment, observed=True):
        g = part.groupby("platform", observed=True)[SUM_COLS].sum()
        result[seg] = recommend(add_metrics(g), **kw)
    return result
