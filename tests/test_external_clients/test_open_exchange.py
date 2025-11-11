from app.external_clients.open_exchange import OpenExchangeClient


def _build_client() -> OpenExchangeClient:
    return OpenExchangeClient(
        base_url="https://example.com",
        api_key="dummy",
        symbols="USD,GBP",
    )


def test_convert_to_euro_base_produces_expected_values():
    """Converts USD base to EUR base while keeping precision."""
    client = _build_client()
    euro_rate = 1.2
    rates = {"USD": 1.0, "GBP": 0.8, "JPY": 110.0, "EUR": 1.0}

    result = client.convert_to_euro_base(euro_rate, rates)

    assert result == {
        "USD": round(1.0 / euro_rate, 5),
        "GBP": round(0.8 / euro_rate, 5),
        "JPY": round(110.0 / euro_rate, 5),
        "EUR": round(1.0 / euro_rate, 5),
    }


def test_convert_to_euro_base_skips_none_values():
    """Drops currencies with null rates to avoid division errors."""
    client = _build_client()
    euro_rate = 1.0
    rates = {"USD": 1.0, "NULL": None}

    result = client.convert_to_euro_base(euro_rate, rates)

    assert "NULL" not in result
    assert result["USD"] == 1.0
