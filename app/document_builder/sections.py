# Contains one class or function per domain.
from abc import ABC, abstractmethod
from typing import Any

from app.document_builder.models import DocumentSection


class SectionBuilder(ABC):
    """Converts one raw report section (a dict or list of dicts) into a
    single human-readable DocumentSection. Implementations own all
    knowledge of that section's shape and units.
    """

    @abstractmethod
    def build(self, raw_section: Any) -> DocumentSection | None:
        """Return None if the section is missing/empty — the caller
        skips it rather than producing an empty section.
        """
        raise NotImplementedError