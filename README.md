# Do free downloads turn into customers?

An analysis of my own music production business. I've sold beat licences online since 2018 and, like most producers, give beats away as free downloads to grow an email list. This project joins my sales export with my email list export to test whether that trade pays off.

**[Read the case study →](https://nikitakotadia.github.io/music-business-analysis/)**

## Findings

| | |
|---|---|
| **1 in 62** | free downloaders later bought a paid beat (1.6%) |
| **37 days** | median time from free download to first purchase; over half took more than a month |
| **5×** | buyers on the email list are five times as likely to buy again (11.5% vs 2.2%) |
| **1 in 20 → 1 in 5** | share of new buyers who joined the list first, peak years against 2024 onwards, as sales slowed |

**Recommendation:** fix the sync between the store and the email list, follow up with free downloaders for a year rather than a week, send new releases to past buyers first, and test the follow-up against a random holdout group.

## Keeping the business private

The raw exports contain customer names and emails, and the cleaned tables contain revenue, so no data is in this repository. Account-specific details (file layouts, account names, platform labels) live in a private settings file, so the code stays generic. Every query returns a rate, a share, a median or an index: never a count of customers, orders, subscribers or beats, and never revenue. Shares based on small groups are rounded so the numbers behind them can't be worked out. Customer emails are replaced with salted SHA-256 hashes before any analysis.

## The data

| Source | Covers |
|---|---|
| Sales export | Every order, January 2020 to September 2026, with items and collaborator payment splits |
| Email list export | Current subscribers, with opt-in time, source and tags |

## Cleaning problems solved

- **Block layout.** Each order is one row plus extra rows for additional beats and for each collaborator's share. Parsed line by line into `orders`, `order_items` and `payment_splits`.
- **Broken columns.** Beat titles containing commas spilled into the next field; detected by field count and rejoined.
- **Revenue splits.** Most beats sold were co-produced, so the sale price isn't what I earned. Splits are kept per party, with every collaborator anonymised.
- **Time zones.** Joining the files showed most buyers apparently subscribing exactly 4 or 5 hours before buying: the offset between US Eastern time and UTC. The email platform appears to record Eastern time without saying so. Aligned, those buyers joined the list at checkout, and without the fix the conversion rate would have been several times too high.

## Repository

```
notebooks/
  01_load_and_clean.ipynb   parse, clean and pseudonymise both exports; build the SQLite database
  02_sql_analysis.ipynb     run every query in sql/ and save results for the site
sql/
  00_views.sql              shared views: paid_items, paid_orders, buyers, buyer_paths
  01 to 09                  one file per question
docs/
  index.html                the case study page (GitHub Pages)
  build_site.py             builds index.html from results.json and the SQL files
  results.json              query results: rates, shares, medians and indexes only
data/                       local only, excluded by .gitignore
```

## Reproduce

With the two exports saved in `data/raw/` as `sales_export.csv` and `email_list_export.csv`, and a private `data/work/source_config.json` describing their account-specific labels:

```bash
pip install pandas jupyter
jupyter nbconvert --to notebook --execute --inplace notebooks/01_load_and_clean.ipynb
jupyter nbconvert --to notebook --execute --inplace notebooks/02_sql_analysis.ipynb
python docs/build_site.py
```

## Limits

- **A gap in 2025.** Almost nobody joined the list during 2025, against steady sign-ups in every other year. The most likely cause is that the automatic sync between the store and the email list stopped for most of that year, so downloaders and buyers from that period are missing from the list.
- The audience export holds current subscribers only, so buyers who unsubscribed count as never subscribed.
- A free download is visible only through its tag and the subscriber's first join date.
- Contacts imported from a spreadsheet in 2021 have their upload date as their join date and are excluded from timing questions.
- All findings are correlations. The holdout test in the recommendations is how to establish cause.

**Tools:** Python, pandas, SQLite, SQL (CTEs, window functions, views), HTML/CSS.

Nikita Kotadia · [LinkedIn](https://www.linkedin.com/in/nikitakotadia/)
