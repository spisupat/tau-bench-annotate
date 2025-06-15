# This file is adapted from the Logfire MCP server.
# We were having trouble running the MCP server so we mock it by directly importing tools.
# See https://discuss.huggingface.co/t/gradioui-smolagents-mcp-event-loop-is-closed/155485

import os
import re
from datetime import UTC, datetime, timedelta
from textwrap import indent
from typing import Annotated, Any, Literal, TypedDict, cast

from logfire.experimental.query_client import LogfireQueryClient
from pydantic import AfterValidator
from smolagents import tool

HOUR = 60  # minutes
DAY = 24 * HOUR


logfire_client = LogfireQueryClient(
    os.getenv("LOGFIRE_READ_TOKEN"),
    os.getenv("LOGFIRE_BASE_URL"),
)

def validate_age(age: int) -> int:
    """Validate that the age is within acceptable bounds (positive and <= 7 days)."""
    if age <= 0:
        raise ValueError("Age must be positive")
    if age > 7 * DAY:
        raise ValueError("Age cannot be more than 7 days")
    return age


ValidatedAge = Annotated[int, AfterValidator(validate_age)]
"""We don't want to add exclusiveMaximum on the schema because it fails with some models."""

@tool
def arbitrary_query(query: str, age: ValidatedAge) -> list[Any]:
    """Run an arbitrary query on the Logfire database.

    The schema is available via the `get_logfire_records_schema` tool.

    Args:
        query: The query to run, as a SQL string.
        age: Number of minutes to look back, e.g. 30 for last 30 minutes. Maximum allowed value is 7 days.
    """
    min_timestamp = datetime.now(UTC) - timedelta(minutes=age)
    result = logfire_client.query_json_rows(query, min_timestamp=min_timestamp)
    return result["rows"]

@tool
def get_logfire_records_schema() -> str:
    """Get the records schema from Logfire.

    To perform the `arbitrary_query` tool, you can use the `schema://records` to understand the schema.
    """
    result = logfire_client.query_json_rows("SHOW COLUMNS FROM records")
    return build_schema_description(cast(list[SchemaRow], result["rows"]))


class SchemaRow(TypedDict):
    column_name: str
    data_type: str
    is_nullable: Literal["YES", "NO"]

    # These columns are less likely to be useful
    table_name: str  # could be useful if looking at both records _and_ metrics..
    table_catalog: str
    table_schema: str


def _remove_dictionary_encoding(data_type: str) -> str:
    result = re.sub(r"Dictionary\([^,]+, ([^,]+)\)", r"\1", data_type)
    return result


def build_schema_description(rows: list[SchemaRow]) -> str:
    normal_column_lines: list[str] = []
    attribute_lines: list[str] = []
    resource_attribute_lines: list[str] = []

    for row in rows:
        modifier = " IS NOT NULL" if row["is_nullable"] == "NO" else ""
        data_type = _remove_dictionary_encoding(row["data_type"])
        if row["column_name"].startswith("_lf_attributes"):
            name = row["column_name"][len("_lf_attributes/") :]
            attribute_lines.append(f"attributes->>'{name}' (type: {data_type}{modifier})")
        elif row["column_name"].startswith("_lf_otel_resource_attributes"):
            name = row["column_name"][len("_lf_otel_resource_attributes/") :]
            resource_attribute_lines.append(f"otel_resource_attributes->>'{name}' (type: {data_type}{modifier})")
        else:
            name = row["column_name"]
            normal_column_lines.append(f"{name} {data_type}{modifier}")

    normal_columns = ",\n".join(normal_column_lines)
    attributes = "\n".join([f"* {line}" for line in attribute_lines])
    resource_attributes = "\n".join([f"* {line}" for line in resource_attribute_lines])

    schema_description = f"""\
The following data was obtained by running the query "SHOW COLUMNS FROM records" in the Logfire datafusion database.
We present it here as pseudo-postgres-DDL, but this is a datafusion table.
Note that Logfire has support for special JSON querying so that you can use the `->` and `->>` operators like in Postgres, despite being a DataFusion database.

CREATE TABLE records AS (
{indent(normal_columns, "    ")}
)

Note that the `attributes` column can be interacted with like postgres JSONB.
It can have arbitrary user-specified fields, but the following fields are semantic conventions and have the specified types:
{attributes}

And for `otel_resource_attributes`:
{resource_attributes}
"""
    return schema_description

