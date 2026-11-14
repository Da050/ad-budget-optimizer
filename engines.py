"""Teen processing engines: Pandas, MapReduce (map -> shuffle -> reduce), Spark.
Teeno same kaam karte hain: platform-wise sums nikalna, phir KPIs."""
from collections import defaultdict
from multiprocessing import Pool, cpu_count

import numpy as np
import pandas as pd

from .metrics import SUM_COLS, add_metrics


# ---------------- Pandas ----------------
def run_pandas(path: str) -> pd.DataFrame:
    df = pd.read_parquet(path)
    g = df.groupby("platform", observed=True)[SUM_COLS].sum()
    return add_metrics(g)


# ---------------- MapReduce ----------------
def _mapper(chunk: pd.DataFrame) -> dict:
    """MAP: har row ke liye (key=platform, value=numbers) emit + local combine."""
    out = defaultdict(lambda: [0, 0, 0.0, 0, 0.0])
    cols = [chunk[c].tolist() for c in ["platform"] + SUM_COLS]
    for p, imp, clk, sp, conv, rev in zip(*cols):
        a = out[p]
        a[0] += imp
        a[1] += clk
        a[2] += sp
        a[3] += conv
        a[4] += rev
    return dict(out)


def run_mapreduce(path: str) -> pd.DataFrame:
    df = pd.read_parquet(path, columns=["platform"] + SUM_COLS)
    df["platform"] = df["platform"].astype(str)
    workers = cpu_count()
    chunks = [df.iloc[i] for i in np.array_split(np.arange(len(df)), workers) if len(i)]
    with Pool(workers) as pool:
        mapped = pool.map(_mapper, chunks)                    # MAP phase (parallel)
    reduced = defaultdict(lambda: [0, 0, 0.0, 0, 0.0])        # SHUFFLE + REDUCE phase
    for part in mapped:
        for key, vals in part.items():
            for i in range(5):
                reduced[key][i] += vals[i]
    g = pd.DataFrame.from_dict(reduced, orient="index", columns=SUM_COLS)
    g.index.name = "platform"
    return add_metrics(g)


# ---------------- Spark ----------------
_spark = None


def get_spark():
    global _spark
    if _spark is None:
        from pyspark.sql import SparkSession
        _spark = (SparkSession.builder.master("local[*]").appName("AdOptimizer")
                  .config("spark.ui.showConsoleProgress", "false")
                  .config("spark.driver.memory", "4g")
                  .getOrCreate())
        _spark.sparkContext.setLogLevel("ERROR")
    return _spark


def run_spark(path: str) -> pd.DataFrame:
    from pyspark.sql import functions as F
    df = get_spark().read.parquet(path)
    g = df.groupBy("platform").agg(*[F.sum(c).alias(c) for c in SUM_COLS]).toPandas()
    return add_metrics(g.set_index("platform"))
