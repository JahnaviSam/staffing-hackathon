"""Day-by-day simulation of the waiting pool and agents for one country in 2026."""
import calendar
from pathlib import Path

import pandas as pd

# ---- Rules from the problem statement (change only by team agreement) ----
SUPPORT_DAYS = 60     # an advertiser is supported for 60 days
MAX_WAIT_DAYS = 60    # leaves the pool after waiting 60 days
CAPACITY = 10         # advertisers per agent at once
UPLIFT = 0.135        # expected uplift: 13.5% of annual budget (assumption A1)
FIRE_COST = 0.40      # firing costs 40% of annual salary

# ---- Load the data once, when this file is imported ----
DATA = Path(__file__).resolve().parents[1] / "data" / "processed"
forecast = pd.read_csv(DATA / "forecast.csv")
countries = pd.read_csv(DATA / "countries.csv").set_index("Country")
salaries = countries["Annual_Agent_Salary_USD"]
staff = countries["Existing_Agent_Count"]


def run_plan(country, headcount, scenario="base"):
    """Simulate a 12-month headcount for one country. Returns a 12-row table."""
    salary = salaries[country]
    fc = forecast[forecast["country"] == country].set_index("month")
    budget = fc["avg_eligible_budget"].iloc[0]
    start_agents = staff[country]

    pool = []
    active = []
    rows = []
    day = 0

    for month in range(1, 13):
        agents = headcount[month - 1]
        arrivals_per_day = fc.loc[month, f"daily_eligible_{scenario}"]
        n_days = calendar.monthrange(2026, month)[1]
        served = abandoned = wait_days = busy = revenue = 0.0

        for _ in range(n_days):
            active = [g for g in active if day - g[0] < SUPPORT_DAYS]

            still_waiting = []
            for g in pool:
                if day - g[0] >= MAX_WAIT_DAYS:
                    abandoned += g[1]
                else:
                    still_waiting.append(g)
            pool = still_waiting

            pool.append([day, arrivals_per_day])

            free = agents * CAPACITY - sum(g[1] for g in active)
            while free > 1e-9 and pool:
                g = pool[0]
                take = min(free, g[1])
                waited = day - g[0]
                active.append([day, take])
                served += take
                wait_days += take * waited
                revenue += take * budget * UPLIFT * (1 - waited / MAX_WAIT_DAYS)
                g[1] -= take
                free -= take
                if g[1] <= 1e-9:
                    pool.pop(0)

            busy += sum(g[1] for g in active)
            day += 1

        prev = start_agents if month == 1 else headcount[month - 2]
        hires = max(agents - prev, 0)
        fires = max(prev - agents, 0)
        cost = (agents * salary / 12
                + hires * salary / 12
                + fires * salary / 12
                + fires * FIRE_COST * salary)

        rows.append({
            "month": month, "agents": agents, "hires": hires, "fires": fires,
            "served": served, "abandoned": abandoned,
            "avg_wait_days": wait_days / served if served else 0,
            "utilization": busy / (agents * CAPACITY * n_days) if agents else 0,
            "waiting_end": sum(g[1] for g in pool),
            "revenue": revenue,
            "cost": cost,
        })

    return pd.DataFrame(rows)
