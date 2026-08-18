"""
REAL-DATA SCRAPER ARCHITECTURE — What actually works vs. what's blocked
=======================================================================

After live testing (2026-08-06), here is the verified status of every source:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 SOURCE 1: World Bank API — ✅ FULLY WORKING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
URL: https://api.worldbank.org/v2/country/IND/indicator/{id}?format=json
Status: Returns live JSON, no auth needed.
PPP 2025: 20.09 (LCU per international $)  ← verified live
Scraper: worldbank_scraper.py  ← COMPLETE, PRODUCTION READY

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 SOURCE 2: NIRF Rankings — ⚠️ JS-RENDERED + PDF NOT AVAILABLE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
nirfindia.org — returns 10-byte "Not Found" for ranking HTML pages.
The PDF endpoint also returns "Not Found".
NIRF uses JavaScript to render their ranking tables (Nuxt/Vue).

Solution: Use NIRF data from two alternative free sources:
  A. NIRF data is re-published on data.gov.in (Open Government Data)
     https://data.gov.in/catalog/nirf-rankings
     → CSV download, fully authentic
  B. Wikipedia NIRF ranking pages are HTML-scraped successfully
  C. Hardcode the top-100 verified from the official 2024 PDF
     (published at: https://nirfindia.org/nirfpdfcdn/2024/pdf/ — but CDN varies)

Scraper: nirf_scraper.py → use data.gov.in CSV endpoint

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 SOURCE 3: AmbitionBox — ⚠️ NUXT SSR, API NEEDS SESSION COOKIES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
HTML page loads (153KB) but salary data is in Nuxt SSR JS state.
The salary API (/api/v2/salaries) requires OPTIONS preflight (browser only).

Solution: 
  A. Parse the window.__NUXT__ JavaScript state from the HTML page
     using regex extraction (no JS engine needed for the state object)
  B. Alternative: scrape their public salary pages HTML — salary numbers
     ARE present in the DOM but inside React/Nuxt components rendered
     with specific class names.
  C. Use PayScale India (payscale.com/research/IN) as AmbitionBox backup
     — it's standard HTML, no JS rendering.

Scraper: ambitionbox_scraper.py → upgraded to parse __NUXT__ state

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 SOURCE 4: Naukri.com — ❌ RECAPTCHA on API, ✅ HTML SEARCH PAGES WORK
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Their JSON API requires appid/systemid AND recaptcha in production.
However, their search RESULT PAGES are plain HTML.

Solution:
  Use https://www.naukri.com/{role}-jobs?experience={X} HTML pages
  Parse: number of results (job demand), listed salary ranges from job cards.
  This is the SAME data shown on the website, just parsed from HTML.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 SOURCE 5: Reddit (PRAW) — ✅ WORKS WITH FREE APP CREDENTIALS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Requires: REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET (free signup)
Subreddits: r/india, r/cscareerquestions, r/IndiaInvestments,
            r/iitbombay, r/iitk, r/CAIndia, r/medicalschool
PRAW rate limit: 60 req/min (free, generous)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 SOURCE 6: Internshala — ✅ HTML LISTINGS WORK
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Listing pages return 525KB of HTML with 62+ stipend elements.
Pattern confirmed: use div.individual_internship containers.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 SOURCE 7: data.gov.in — ✅ OPEN GOVERNMENT API (FREE, NO KEY)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
API: https://api.data.gov.in/resource/{resource_id}?api-key=579b...
The site offers a shared anonymous key: 579b464db66ec23bdd000001cdd3946e
Contains: NIRF data, PLFS data, employment stats, college info
Use as primary source for NIRF (official data re-published here).

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 SOURCE 8: PayScale India — ✅ STANDARD HTML
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
https://www.payscale.com/research/IN/Job=Software_Engineer/Salary
Standard HTML page, salary ranges in structured elements.
Use as AmbitionBox fallback for salary data.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 ENV VARS REQUIRED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
REDDIT_CLIENT_ID       (free — reddit.com/prefs/apps → create app → script)
REDDIT_CLIENT_SECRET   (free — same as above)
REDDIT_USER_AGENT      IndiaLens/1.0 by u/<your_username>

All other sources need NO credentials.

DATAGOV_API_KEY = "579b464db66ec23bdd000001cdd3946e"  # shared public key
"""
