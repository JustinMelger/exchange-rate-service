from __future__ import annotations
from typing import Any, Mapping, Sequence
from google.cloud import bigquery
from google.oauth2 import service_account


class BigQueryClient:
    def __init__(
        self,
        *,
        credential_file: str,
        project_id: str,
        dataset: str,
        staging_table: str,
        prod_table: str,
    ):
        """Initialize a BigQuery client wrapper.

        Args:
            credential_file (str): Path to the service-account JSON.
            project_id (str): GCP project ID.
            dataset (str): BigQuery dataset name.
            staging_table (str): Fully qualified name of the staging table.
            prod_table (str): Fully qualified name of the production table.
        """

        self.project_id = project_id
        self.dataset = dataset
        self.staging_table = staging_table
        self.prod_table = prod_table
        credentials = service_account.Credentials.from_service_account_file(credential_file)
        self.client = bigquery.Client(credentials=credentials, project=self.project_id)

    def insert_rows(
        self,
        table_name: str,
        rows: Sequence[Mapping[str, Any]],
    ) -> int:
        """Insert JSON rows into the specified table.

        Args:
            table_name (str): Target table name.
            rows (Sequence[Mapping[str, Any]]): Row payloads to insert.

        Returns:
            int: Number of rows successfully inserted.

        Raises:
            RuntimeError: If BigQuery reports insert errors.
        """
        if not rows:
            return 0

        table_ref = f"{self.project_id}.{self.dataset}.{table_name}"
        errors = self.client.insert_rows_json(table_ref, rows)
        if errors:
            raise RuntimeError(f"BigQuery insert failed: {errors}")
        return len(rows)

    def execute_query(
        self,
        query: str,
    ) -> bigquery.table.RowIterator:
        """Run a SQL query and wait for completion.

        Args:
            query (str): SQL statement to execute.

        Returns:
            bigquery.table.RowIterator: Iterator over the resulting rows.
        """
        job = self.client.query(query)
        return job.result()

    def insert_into_staging(self, rows: Sequence[Mapping[str, Any]]) -> int:
        """Insert rows directly into the configured staging table.

        Args:
            rows (Sequence[Mapping[str, Any]]): Row payloads to insert.

        Returns:
            int: Number of rows successfully inserted.
        """
        return self.insert_rows(self.staging_table, rows)
