Staffing Google Ads advertiser support in 2026

DADS5250 Hackathon Â· Team: Christian Hans, Liang Wang, Jahnavi Manugarra, Charley Li

Every eligible new Google Ads advertiser gets a support agent for their first 60 days. Our job was
to work out how many agents each of 22 countries needs in each month of 2026, and to build an AI
application that can explain that plan to the person who has to approve it.

The short answer: far fewer than Google has today. There are 6,474 agents on staff in January 2026.
We recommend 1,821 for January to September and 2,559 for October to December, when sign-ups peak.
In our model that raises 2026 net value (extra ad revenue from supported advertisers, minus staffing
cost) from $364M to $471M, while advertisers wait less than a day on average.

Two countries stand out. Vietnam is the only one that is understaffed, so it hires (59 agents now,
85 for most of the year, 118 in Q4). UAE gets no agents at all: its eligible advertisers have small
budgets, so an agent there brings in only about half of what they cost.

How it works

We built it in four steps, each feeding the next.

1. Clean the data (analysis/explore.ipynb). The workbook has 499,644 sign-ups from 2024 and
   2025. We fixed 920 rows dated 29 February 2025 (a date that doesn't exist) and kept only advertisers
   whose budget exceeds their country's threshold, leaving 212,334 eligible sign-ups.
2. Forecast 2026 (same notebook, writes `data/processed/forecast.csv). For each country and
   month we took the average number of eligible sign-ups per day across 2024 and 2025. We also made a
   low and a high version, 15% below and above, for testing.
3. Simulate and optimize (model/simulate.py, model/optimize.py). The simulator plays out 2026
   one day at a time: new advertisers join a queue, free agents pick up whoever has waited longest,
   advertisers leave after 60 days of support, and anyone who waits 60 days gives up. It adds up
   revenue and cost. The optimizer then tries around 1,150 staffing plans per country and keeps the
   one with the highest net value.
4. Pick the final plan (analysis/results.ipynb, writes data/processed/plan.csv). We stress-test
   the optimizer's plan against higher and lower demand and add a 10% safety margin (explained below).

A quick way to sanity-check any number in the plan: each advertiser stays 60 days and each agent handles
 10 at once, so a country needs roughly daily eligible sign-ups × 6 agents. Argentina gets about 2.2 
eligible sign-ups a day, so it needs about 13; the optimizer picked 14.

Decisions we made, and why

The 920 sign-ups dated 29 Feb 2025. We moved them to 28 February rather than dropping them. It
creates a one-day spike that the 60-day queue absorbs without any visible effect.

No growth trend. Eligible sign-ups changed by between -6% and +4% from 2024 to 2025 in every
country, so we didn't add one. Averaging the two years also softens June 2025, which was about 30%
lower than June 2024 in every country with no days missing, and which we couldn't explain.

Revenue from an advertiser. The brief gives a distribution of extra ad spend from agent support;
its average is 13.5% (0%×5% + 5%×15% + 10%×25% + 15%×25% + 20%×20% + 25%×10%).  We apply it to the
advertiser's annual budget. The brief could also be read as "only during the 60 days of support",
which makes each advertiser worth about a sixth as much. We tested that reading: the headcount barely
changes, but the program's net value goes negative in 2026. Google should confirm which is right.

Waiting has a cost. If waiting were free, the optimizer would happily leave people in the queue
for 50+ days. We assume each day of waiting cuts that advertiser's uplift by 1/60, so someone helped
after 30 days brings in half the value, and at 60 days they leave anyway.

Hiring and firing. A new hire is paid for a training month before they can work. Firing an agent costs
 a month of notice plus 40% of annual salary, about 48% of a year’s pay in total. 
Keeping an agent with no work costs 100%. So any agent we won’t need in 2026 is cheaper to let go in 
January; for a US agent, about $37,500 instead of $77,721.


Two headcounts per country. Sign-ups run 30% to 40 % above average in October to December in both
years, so each country gets one level for January - September and a higher one for October- December,
with the extra agents hired in September. This keeps the search small enough to try every
combination, which made the optimizer easy to check and explain. A plan that changes every month
might do slightly better.

A 10% safety margin. The optimizer's plan is tuned exactly to the forecast. When we ran it with
15% more sign-ups, waits reached 19 days in 21 of 22 countries. Being short of agents turned out to
cost about 20 times more than having a few spare, so we add 10% to every headcount. It costs about
$4M if the forecast is right and protects about $131M if demand runs high.

The language model never does arithmetic. Every number the AI reports comes from our Python
model, either through a tool call or from facts we compute before the model sees anything. We did
this because a confident but made-up figure is the worst thing an AI can produce in a staffing
decision.


The AI application

Both parts are in “analysis/ai_app.ipynb” and use OpenAI's “gpt-4o-mini” at temperature 0.

Approval memos (prompt engineering, LangChain, structured output). For each country, Python runs
the model and collects these facts: headcount now and recommended, firing cost, net value with and
without the plan, waits, and how much an agent earns compared with their salary. A LangChain chain
sends these through a prompt, and the model must answer in a fixed Pydantic format: a headline, three
reasons, two or three risks and the decision needed. Python then builds the numbers table itself and
joins it to the model's text. All 22 memos are saved to report/staffing_memos.md.


What-if agent (LangGraph, agents). You ask a question in plain English, and the agent decides
which of our functions to run:

- get_recommended_plan: how our plan for a country performs, under normal, low or high demand
- evaluate_plan: what happens with a headcount someone proposes ("What if Vietnam kept 59 agents?")
- reoptimize: what the plan should be if demand were 15% higher or lower
- all_countries_overview: the summary for all 22 countries, for rankings and totals

The agent prints every tool call it makes, so you can see where each number came from.

Running it

You need Python 3.11 or newer and an OpenAI API key for the AI part.

git clone https://github.com/JahnaviSam/staffing-hackathon.git
cd staffing-hackathon
python -m venv .venv              # on Windows, if "python" isn't found: py -m venv .venv
source .venv/Scripts/activate     # Windows Git Bash; on Mac/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env              # put your OpenAI key in .env; it is never committed
jupyter lab




Put DADS5250_Hackathon_Google_Data.xlsx (Northeastern sign-in) in data/raw/. It is git-ignored.

Then open the notebooks in analysis/ and use Run → Run All Cells, in this order:
Notebook	What it does	Writes
explore.ipynb	Cleaning, eligibility, seasonality, 2026 forecast	forecast.csv
simulator.ipynb	Where we built and tested the simulator and optimizer	countries.csv
results.ipynb	Sensitivity tests and the final plan with the 10% margin	plan.csv, plan_summary.csv, plan_unbuffered.csv, sensitivity tables
ai_app.ipynb	Approval memos and the what-if agent	report/staffing_memos.md


All outputs are already committed, so you can skip straight to ai_app.ipynb if you only want to
try the AI part. The optimizer takes about 3 minutes for all 22 countries.

What's where


analysis/           the four notebooks above
model/simulate.py   run_plan(country, headcount, scenario="base") -> 12-row table of monthly results
model/optimize.py   optimize_country(country, scenario="base") -> best 12-month headcount
data/processed/     forecast, final plan (plan.csv), plan before the margin, country facts
report/             approval memos, sensitivity tables and chart, demo slides



plan.csv is the staffing plan itself: one row per country per month with the number of agents.

What the model doesn't cover

- It uses average daily demand. Real daily sign-ups jump around a lot, so short queues on busy days
  are likely understated; the 10% margin helps with this.
- It stops on 31 December 2026, so people still waiting then and the cost of Q4 hires in 2027 aren't
  counted.
- Cutting about 4,700 roles has costs we didn't price: severance rules that differ by country, morale
  and reputation.
- The what-if agent can only test demand at - 15%, the forecast, or +15%.

Team

Person	Main area
Christian Hans	Data cleaning and forecast (explore.ipynb)
Liang Wang	Simulator and optimizer (model/, simulator.ipynb)
Jahnavi Manugarra	AI application (ai_app.ipynb)
Charley Li	Sensitivity analysis, final plan and report (results.ipynb, report/)


