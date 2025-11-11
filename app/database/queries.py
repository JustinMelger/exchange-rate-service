from __future__ import annotations


def merge_exchange_rates(
    *,
    project_id: str,
    dataset: str,
    staging_table: str,
    prod_table: str,
) -> str:
    return f"""
    MERGE `{project_id}.{dataset}.{prod_table}` AS T
    USING (
        SELECT rate_date, currency, rate_eur
        FROM `{project_id}.{dataset}.{staging_table}`
    ) AS S
    ON T.rate_date = S.rate_date AND T.currency = S.currency
    WHEN MATCHED AND T.rate_eur != S.rate_eur THEN
        UPDATE SET
            T.rate_eur = S.rate_eur,
            T.last_updated_at = CURRENT_TIMESTAMP()
    WHEN NOT MATCHED THEN
        INSERT (rate_date, currency, rate_eur, last_updated_at)
        VALUES (S.rate_date, S.currency, S.rate_eur, CURRENT_TIMESTAMP())
    """


def truncate_table(
    *,
    project_id: str,
    dataset: str,
    table_name: str,
) -> str:
    return f"TRUNCATE TABLE `{project_id}.{dataset}.{table_name}`"
