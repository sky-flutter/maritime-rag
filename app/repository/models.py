from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Report:
    """Domain model for a single vessel report.

    Intentionally a thin wrapper — `raw_json` is handed off to the
    Document Builder layer for interpretation. This layer does not
    know or care about the internal structure of the report JSON.
    """
    report_id: str
    data_source: str
    customer_name: str
    imo: int
    report_type: str
    datetime_gmt: datetime
    raw_json: dict
    zn_updated_at: datetime


class NotFoundError(Exception):
    """Generic not-found error other repositories can reuse."""

    def __init__(self, entity_name: str, entity_id: int) -> None:
        self.entity_name = entity_name
        self.entity_id = entity_id
        super().__init__(f"{entity_name} with id={entity_id} not found")


class ReportNotFoundError(NotFoundError):
    """Raised when a report with the given ID does not exist."""

    def __init__(self, report_id: int) -> None:
        super().__init__("Report", report_id)