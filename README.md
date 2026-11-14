# Digital Advertising Budget Optimizer

**Course:** Big Data Analytics | **University:** University of Management & Technology (UMT)
**Author:** Dayan (Roll No. F2023376050) — *group members yahan add karo*

## Problem
Ek company Facebook, Instagram, Google, TikTok aur YouTube par ads chalati hai.
Management ka sawal: **"Agle Rs. 1 million kahan lagayein?"**

## Is project mein kya hai
1. **Simulated ad data** (10K → 100K → 1M → 10M records): date, campaign, platform, impressions, clicks, spend, conversions, revenue, age, gender, city, device.
2. **KPIs:** CTR, CPC, CPA, Conversion Rate (CVR), ROAS, profit.
3. **Big Data benchmark:** same aggregation par **Pandas vs MapReduce vs Spark** ka time comparison.
4. **Budget Recommendation Engine:** ROAS-weighted allocation with min/max caps.

## Project structure
```
ad-budget-optimizer/
├── run_benchmark.py        # main script
├── requirements.txt
├── src/
│   ├── data_generator.py   # simulated data
│   ├── metrics.py          # CTR, CPC, CPA, CVR, ROAS
│   ├── engines.py          # Pandas, MapReduce, Spark
│   └── recommender.py      # budget recommendation engine
├── results/                # benchmark.csv, recommendation.csv, charts
├── data/                   # generated parquet files (gitignored)
└── REPORT.md
```

## Setup
```bash
git clone <your-repo-url>
cd ad-budget-optimizer
python -m venv venv
venv\Scripts\activate          # Windows  (Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
```
PySpark ke liye **Java 11 ya 17** installed hona chahiye (`java -version` se check karo).

## Run
```bash
python run_benchmark.py                          # full: 10K, 100K, 1M, 10M
python run_benchmark.py --sizes 10000 100000     # chhota test
python run_benchmark.py --skip spark             # agar Java na ho
python run_benchmark.py --budget 2000000         # alag budget
```
Outputs `results/` folder mein save hote hain.

## Formulas
| KPI | Formula |
|---|---|
| CTR | clicks / impressions |
| CPC | spend / clicks |
| CPA | spend / conversions |
| CVR | conversions / clicks |
| ROAS | revenue / spend |

## Recommendation logic
`share_i = ROAS_i / sum(ROAS)`, phir har platform ko **5% se 45%** ke beech clip karke re-normalize kiya jata hai
(diminishing returns se bachne ke liye, aur kisi platform ko zero na karne ke liye).

## Results

**Benchmark** (seconds; single-core, 3 GB RAM test environment — apne machine par numbers alag aa sakte hain)

| Records | Pandas | MapReduce | Spark |
|---|---|---|---|
| 10K | 0.028 | 0.038 | 0.867 |
| 100K | 0.043 | 0.142 | 0.879 |
| 1M | 0.168 | 1.100 | 1.157 |
| 10M | 2.217 | DNF* | 4.160 |

\*10M MapReduce run test environment mein 15 minute mein complete nahi hua (limited RAM/1 core).

![Benchmark](results/benchmark.png)

**Budget recommendation for Rs. 1,000,000**

| Platform | ROAS | CPA (Rs) | Share | Budget (Rs) |
|---|---|---|---|---|
| Google | 7.80 | 667 | 32.3% | 322,721 |
| Instagram | 5.25 | 914 | 21.7% | 217,318 |
| Facebook | 4.81 | 935 | 19.9% | 199,268 |
| YouTube | 3.63 | 1,101 | 15.0% | 150,352 |
| TikTok | 2.67 | 1,200 | 11.0% | 110,341 |

Expected revenue is about 12.9% higher than an equal 20% split (under constant-ROAS assumption).

![Recommendation](results/recommendation.png)

Full write-up: see `REPORT.docx`.

## Limitations
- Data simulated hai, real campaigns ka nahi.
- Spark local machine par chala (single node), isliye cluster jitna faida nahi dikhta.
- ROAS linear maana gaya; real mein spend badhne par ROAS girta hai.

## Future work
Diminishing-returns curve fitting, segment-wise (city/device) recommendation, Streamlit dashboard.
