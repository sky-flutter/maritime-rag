from app.repository.base import BaseRepository
from app.repository.models import Report, ReportNotFoundError
from app.repository.postgres.connection_manager import ConnectionManager
from app.repository.postgres.orm_models import ReportDocumentORM


class ReportRepository(BaseRepository[Report]):
    """Postgres-backed repository for fetching vessel reports."""

    def __init__(self, connection_manager: ConnectionManager) -> None:
        self._connection_manager = connection_manager

    def get_by_id(self, report_id: str) -> Report:
        with self._connection_manager.session_scope() as session:
            row = session.get(ReportDocumentORM, report_id)
            if row is None:
                raise ReportNotFoundError(report_id)

            return Report(
                report_id=row.report_id,
                data_source=row.data_source,
                imo=row.imo,
                report_type=row.report_type,
                raw_json=row.report_json,
                datetime_gmt=row.datetime_gmt,
                zn_updated_at=row.zn_updated_at,
            )
