"""Search for the best 12-month headcount for each country."""
from model.simulate import forecast, run_plan


def net_value(country, plan, scenario="base"):
    """Revenue minus cost for the whole year."""
    m = run_plan(country, plan, scenario)
    return m["revenue"].sum() - m["cost"].sum()


def make_plan(base, q4):
    """base agents for Jan-Sep, q4 agents for Oct-Dec."""
    return [base] * 9 + [q4] * 3


def optimize_country(country, scenario="base"):
    """Grid search over (base, q4); returns the best 12-month plan."""
    fc = forecast[forecast["country"] == country]
    peak = int((fc["daily_eligible_base"] * 6).max())
    high = int(peak * 1.2) + 1
    step = max(1, peak // 30)

    # Round 1: coarse search
    best = None
    for base in range(0, high, step):
        for q4 in range(base, high, step):
            v = net_value(country, make_plan(base, q4), scenario)
            if best is None or v > best[0]:
                best = (v, base, q4)

    # Round 2: fine search around the best
    _, b0, q0 = best
    for base in range(max(0, b0 - step), b0 + step + 1):
        for q4 in range(max(base, q0 - step), q0 + step + 1):
            v = net_value(country, make_plan(base, q4), scenario)
            if v > best[0]:
                best = (v, base, q4)

    return make_plan(best[1], best[2])
