from dataclasses import dataclass


@dataclass
class ExchangeRate:
    day: str
    rates: dict[str, float]
    error: bool = False


class OpenExchangeClient:

    def __init__(self) -> None: ...

    def fetch_historical_exchange_rates(self) -> list[ExchangeRate]:

        dummy_exchange_rate = ExchangeRate(day="12-20-2024", rates={"EUR": 1, "USD": 0.90}, error=False)

        return [dummy_exchange_rate]
