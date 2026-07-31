from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    """Generic repository contract. Entity-specific repositories
    (ReportRepository, etc.) inherit this so every repository in the
    app exposes the same basic shape.
    """

    @abstractmethod
    def get_by_id(self, report_id: str) -> T:
        """Fetch a single report by its ID.

        Raises:
            NotFoundError: if no entity exists with this ID.
        """
        raise NotImplementedError
