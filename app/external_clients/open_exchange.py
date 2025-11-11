from datetime import date, timedelta
import aiohttp
import asyncio
import logging
from dataclasses import dataclass


logger = logging.getLogger(__name__)


@dataclass
class ExchangeRate:
    day: str
    rates: dict[str, float]


class OpenExchangeClient:

    def __init__(self, base_url: str, api_key: str, symbols: str) -> None:

        self.base_url = base_url
        self.api_key = api_key
        self.symbols = symbols

    def convert_to_euro_base(self, euro_rate: float, rates: dict) -> dict:
        """Convert USD-based rates to EUR-based rates.

        Args:
            euro_rate (float): EUR value in the original USD-based payload.
            rates (dict): Mapping of currency codes to USD-based rates.

        Returns:
            dict: Mapping of currency codes to EUR-based rates.
        """

        converted_rates = {}
        for cur, val in rates.items():
            if val is None:
                continue
            converted_rates[cur] = round(val / euro_rate, 5)

        return converted_rates

    async def _fetch_exchange_rate(self, session: aiohttp.ClientSession, day: date) -> ExchangeRate:
        """Fetch the exchange rates for a specific day.

        Args:
            session (aiohttp.ClientSession): Shared HTTP session used for requests.
            day (date): Calendar day to fetch from Open Exchange.

        Returns:
            ExchangeRate: Exchange rate for the given day.
        """

        url = f"{self.base_url}/historical/{day.isoformat()}.json"
        params = {"app_id": self.api_key, "symbols": self.symbols}

        day_iso = day.isoformat()

        try:
            async with session.get(url, params=params) as response:
                response.raise_for_status()
                data = await response.json()
        except Exception as e:
            logger.error("Failed to gather exchange rate for %s: %s", day_iso, str(e))
            return ExchangeRate(day=day_iso, rates={})

        rates = data.get("rates", {})
        euro_rate = rates.get("EUR", None)

        if euro_rate in (None, 0):
            logger.error("EUR rate missing in OpenExchange response for %s", day_iso)
            return ExchangeRate(day=day_iso, rates={})
        rates_eur_base = self.convert_to_euro_base(euro_rate, rates)
        return ExchangeRate(day=day_iso, rates=rates_eur_base)

    async def fetch_historical_exchange_rates(self, days: int = 1) -> list[ExchangeRate]:
        """Fetch exchange rates for the most recent N days.

        Args:
            days (int): Number of consecutive days (including today) to retrieve.

        Returns:
            List[ExchangeRate]: Successful exchange rate snapshots ordered oldest to newest.
        """

        if days <= 0:
            return []

        end_date = date.today()
        start_date = end_date - timedelta(days=days - 1)
        historical_days = [start_date + timedelta(days=i) for i in range(days)]

        async with aiohttp.ClientSession() as session:
            tasks = [self._fetch_exchange_rate(session, d) for d in historical_days]
            results = await asyncio.gather(*tasks)

        return [result for result in results if result.rates]
