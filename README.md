# Dynamic Agent Staffing Optimization (DADS5250 Hackathon)

Decide how many support agents each of 22 countries needs in each month of 2026, and build a GenAI
application (LangChain / LangGraph) that explains and explores the plan.

## Team & ownership

| Role | Owner | Folder |
|---|---|---|
| 1. Data & Forecast | _name_ | `model/clean.py`, `model/forecast.py` |
| 2. Simulation & Optimization | _name_ | `model/simulate.py`, `model/optimize.py` |
| 3. GenAI App | _name_ | `app/` |
| 4. Analysis, Report & Integration | _name_ | `analysis/`, `report/` |

## Setup

```bash
git clone https://github.com/JahnaviSam/staffing-hackathon.git
cd staffing-hackathon
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # then add your own API key; never commit .env
```

Download `DADS5250_Hackathon_Google_Data.xlsx` (Northeastern sign-in) into `data/raw/`.
**The data file is git-ignored; do not commit it.**

Run the pipeline:

```bash
python -m model.clean       # -> data/processed/daily_eligible.csv
python -m model.forecast    # -> data/processed/forecast.csv
python -m model.optimize    # -> data/processed/plan.csv
streamlit run app/ui.py
```

## Agreed assumptions (fill in at kickoff; change only by team agreement)

| # | Question | Decision |
|---|---|---|
| A1 | Uplift % applies to annual budget or only the 60-day support window? | _TBD_ |
| A2 | 920 rows dated 2025-02-29: remap to Feb 28, Mar 1, or drop? | Default in code: Feb 28 |
| A3 | Eligible means budget **strictly greater than** country threshold | Yes (problem says "exceeds") |
| A4 | Pool and agent caseloads are empty on 1 Jan 2026 | Yes (problem statement) |
| A5 | Jan 2026 headcount = Existing_Agent_Count, all available in January | _TBD_ |
| A6 | Hire decided in month m-1 becomes available in month m; paid during ramp month | _TBD_ |
| A7 | Fire: notice given in month m-1, agent paid through notice, + 40% annual salary | _TBD_ |
| A8 | Expected uplift = 13.5% (from the given distribution) | Yes |
| A9 | LLM provider / model | _TBD_ |

## Interfaces (contracts between roles)

### `data/processed/forecast.csv` (Role 1 → Role 2)

| column | type | meaning |
|---|---|---|
| `country` | str | country name as in the workbook |
| `month` | int 1–12 | month of 2026 |
| `daily_eligible_base` | float | expected eligible sign-ups per day |
| `daily_eligible_low` | float | low scenario |
| `daily_eligible_high` | float | high scenario |
| `avg_eligible_budget` | float | mean projected annual budget of eligible advertisers, USD |

### `model.simulate.run_plan(...)` (Role 2 → Roles 3 & 4)

```python
run_plan(
    country: str,
    headcount: list[int],          # 12 values: agents AVAILABLE each month of 2026
    scenario: str = "base",        # "base" | "low" | "high"
    stochastic: bool = False,      # False = expected values; True = Poisson arrivals
    seed: int | None = None,
) -> dict  # keys: country, scenario, total_cost, total_revenue, net_value,
           #       served, abandoned, avg_wait_days, utilization, hires, fires,
           #       monthly (list of 12 dicts with the same metrics per month)
```

### `model.optimize.optimize_country(country, scenario="base") -> list[int]`
Returns the recommended 12-month headcount.

## Git workflow

- `main` is protected: changes go in through pull requests with 1 approval.
- Branch names: `data/...`, `model/...`, `app/...`, `analysis/...`.
- Before opening a PR: `git pull origin main` and make sure the pipeline still runs.
- Put logic in `.py` files; notebooks are for exploration only, one per person
  (e.g. `analysis/p4_sensitivity.ipynb`). Run `nbstripout --install` once.
- Write `Closes #<issue>` in PR descriptions.

## Ground rules for the GenAI app

The LLM never does arithmetic. Every number it reports must come from a tool call to
`model/` functions.
