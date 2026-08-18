"""
Data Source Inventory — IndiaLens Scraping Stack
=================================================

All sources below are FREE. Organised by "needs account" status.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 NO ACCOUNT NEEDED (completely open)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1.  NIRF          https://nirfindia.org/Home
    Data: rankings, placement %, fees, student count, GO score
    Method: HTML table parse (requests + BeautifulSoup)
    Frequency: annually (published June)

2.  World Bank    https://api.worldbank.org/v2/
    Data: PPP conversion factor (PA.NUS.PPP), GDP growth
    Method: open REST JSON API, no key
    Frequency: quarterly update

3.  RBI DBIE      https://dbie.rbi.org.in/DBIE/dbie.rbi
    Data: CPI inflation, wage indices, banking stats
    Method: direct CSV download from public portal
    Frequency: monthly

4.  Internshala   https://internshala.com/internships/
    Data: stipend ranges for internships, demand by city/field
    Method: requests + BeautifulSoup (public listings)
    Frequency: weekly

5.  Shine.com     https://www.shine.com/job-search/
    Data: job postings, salary ranges, skills demand
    Method: requests + HTML parse (public search pages)
    Frequency: weekly

6.  Indeed India  https://in.indeed.com/jobs
    Data: job volume by role + city, listed salary ranges
    Method: requests + BeautifulSoup (public search results)
    Frequency: weekly

7.  PLFS / NSO    https://mospi.gov.in/web/plfs
    Data: Periodic Labour Force Survey, employment rates, wages
    Method: direct PDF/Excel download + pandas parse
    Frequency: annual (quarterly Brief)

8.  College websites (IIT, NIT, IIM placement reports)
    Data: official placement PDFs with median/highest/average salary
    Method: PDF download → pdfminer.six extract → regex parse
    Frequency: annually (April–June placement season)

9.  Glassdoor India (public pages)
    https://www.glassdoor.co.in/Salaries/
    Data: role-level salary by company/city
    Method: requests + HTML parse (public salary pages)
    Frequency: weekly

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 FREE ACCOUNT NEEDED (sign up, no credit card)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

10. Reddit PRAW   https://www.reddit.com/prefs/apps
    Data: salary mentions, placement stories, college reviews
    Key vars: REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET
    Free tier: 60 req/min, no rate cost
    Sign up: https://www.reddit.com/prefs/apps → "create app"

11. Naukri.com    https://www.naukri.com/jobapi/v3/search
    Data: job listings, salary metadata, skills demand
    Method: reverse-engineered public search API (no paid key)
    Note: uses same endpoints as their website; respectful rate limiting

12. AmbitionBox   https://www.ambitionbox.com/api/v2/salaries
    Data: salary percentiles by role × experience bucket
    Method: reverse-engineered public JSON API (no paid key)
    Note: same API as their public salary pages

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 OPTIONAL — only if you want richer data (free tiers available)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

13. LinkedIn      (ToS restricts scraping; use with care)
    Free alternative: use Reddit + AmbitionBox for alumni data

14. Serpapi        https://serpapi.com (free: 100 searches/month)
    Only needed if Google Jobs data is required.
    Avoid — Indeed India + Naukri cover the same ground.

15. Firecrawl     https://firecrawl.dev (free: 500 pages/month)
    Use as fallback for heavy JS sites (college portals).
    Key var: FIRECRAWL_API_KEY (if provided by user)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 ENV VARS NEEDED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Required (free Reddit account)
REDDIT_CLIENT_ID=your_app_id
REDDIT_CLIENT_SECRET=your_app_secret
REDDIT_USER_AGENT=IndiaLens/1.0 by u/your_username

# Optional (only needed for JS-heavy college portals)
FIRECRAWL_API_KEY=fc-...     # firecrawl.dev free tier

# Optional (only for Google Jobs data — low priority)
SERPAPI_KEY=...              # 100/month free

All other sources require NO API key.
"""

# This file is documentation only — no executable code.
