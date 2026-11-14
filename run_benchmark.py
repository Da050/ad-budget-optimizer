"""Main entry point.
Usage:
    python run_benchmark.py                       # 10K, 100K, 1M, 10M
    python run_benchmark.py --sizes 10000 100000  # custom sizes
"""
import argparse
import os
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from src.data_generator import generate
from src.engines import run_mapreduce, run_pandas, run_spark
from src.recommender import recommend

ENGINES = [("pandas", run_pandas), ("mapreduce", run_mapreduce), ("spark", run_spark)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sizes", type=int, nargs="+",
                    default=[10_000, 100_000, 1_000_000, 10_000_000])
    ap.add_argument("--budget", type=float, default=1_000_000)
    ap.add_argument("--skip", nargs="*", default=[], choices=["pandas", "mapreduce", "spark"])
    args = ap.parse_args()

    os.makedirs("data", exist_ok=True)
    os.makedirs("results", exist_ok=True)

    rows, last = [], None
    warmed = False
    for n in args.sizes:
        path = f"data/ads_{n}.parquet"
        print(f"\n=== {n:,} rows: generating data ===")
        generate(n).to_parquet(path, index=False)
        row = {"rows": n}
        for name, fn in ENGINES:
            if name in args.skip:
                continue
            if name == "spark" and not warmed:
                fn(path)            # JVM startup ko timing se bahar rakhne ke liye warm-up
                warmed = True
            t0 = time.perf_counter()
            res = fn(path)
            row[name] = round(time.perf_counter() - t0, 3)
            last = res
        print(row)
        rows.append(row)

    bench = pd.DataFrame(rows)
    bench.to_csv("results/benchmark.csv", index=False)
    print("\n=== BENCHMARK (seconds) ===")
    print(bench.to_string(index=False))

    last.round(4).to_csv("results/platform_metrics.csv")
    print("\n=== PLATFORM METRICS ===")
    print(last[["CTR", "CPC", "CPA", "CVR", "ROAS"]].round(3))

    rec = recommend(last, budget=args.budget)
    rec.to_csv("results/recommendation.csv")
    print(f"\n=== BUDGET RECOMMENDATION (Rs. {args.budget:,.0f}) ===")
    print(rec)

    # Charts
    ax = bench.set_index("rows").plot(marker="o", logx=True, figsize=(7, 4))
    ax.set_ylabel("Time (seconds)"); ax.set_xlabel("Rows"); ax.grid(True)
    ax.set_title("Pandas vs MapReduce vs Spark")
    plt.tight_layout(); plt.savefig("results/benchmark.png", dpi=150); plt.close()

    ax = rec["share_pct"].plot.bar(figsize=(7, 4), color="#4C78A8")
    ax.set_ylabel("Budget share (%)"); ax.set_title("Recommended budget split")
    plt.xticks(rotation=0); plt.tight_layout()
    plt.savefig("results/recommendation.png", dpi=150); plt.close()
    print("\nSaved: results/benchmark.csv, platform_metrics.csv, recommendation.csv, *.png")


if __name__ == "__main__":
    main()
