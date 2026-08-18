import argparse
import asyncio
import logging
from typing import List

from .base_scraper import BaseScraper, ScrapeResult

logger = logging.getLogger(__name__)

class WorldBankScraper(BaseScraper):
    """
    World Bank Scraper — fetches macro-economic indicators for India.
    No API key needed (completely free open REST API).
    """

    SOURCE_NAME = "worldbank"
    BASE_URL = "https://api.worldbank.org/v2/country/IND/indicator"

    INDICATORS = {
        "PA.NUS.PPP": "ppp_factor",
        "FP.CPI.TOTL.ZG": "cpi_inflation_pct",
        "NY.GDP.PCAP.KD.ZG": "gdp_growth_pct",
        "SL.UEM.TOTL.ZS": "unemployment_pct",
    }

    async def scrape(self) -> List[ScrapeResult]:
        """
        Scrape macro indicators from World Bank API.
        """
        results = []
        for indicator, field_name in self.INDICATORS.items():
            url = f"{self.BASE_URL}/{indicator}?format=json&per_page=1"
            logger.info(f"Fetching {field_name} from {url}")
            try:
                response = await self.get(url)
                data = response.json()
                
                # The World Bank JSON response is typically a 2-element array
                # where index 1 contains the actual data records.
                if len(data) > 1 and data[1]:
                    latest_data = data[1][0]
                    val = latest_data.get("value")
                    if val is not None:
                        val = float(val)
                        unit = "pct" if "pct" in field_name else "lcu_per_usd"
                        results.append(ScrapeResult(
                            program_id="india_macro",
                            field_name=field_name,
                            raw_value=str(val),
                            parsed_value=val,
                            unit=unit,
                            source_url=url,
                        ))
                    else:
                        logger.warning(f"No valid data value found for {indicator}")
            except Exception as e:
                logger.error(f"Error fetching World Bank indicator {indicator}: {e}")

        return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="WorldBank API Scraper")
    parser.add_argument("--dry-run", action="store_true", help="Print results instead of saving to DB")
    args = parser.parse_args()

    async def main():
        if args.dry_run:
            # Setting up basic logging for dry run
            logging.basicConfig(level=logging.INFO)
            logger.info("Starting WorldBank Scraper in dry-run mode...")
            # We mock the DB dependency by passing None, since persist_results won't be called.
            async with WorldBankScraper(db=None, run_id="dry_run") as scraper:
                results = await scraper.scrape()
                for result in results:
                    print(result)
        else:
            print("Please run this scraper through the main Airflow pipeline or specify --dry-run")

    asyncio.run(main())
