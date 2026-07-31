from collections import defaultdict

from app.document_builder.sections import SectionBuilder
from app.document_builder.models import DocumentSection


class ConsumptionSectionBuilder(SectionBuilder):
    """CONSUMPTION is a list of (ENGINE_TYPE, FUEL_TYPE) records that
    needs grouping by engine to read as coherent sentences, rather than
    dumping 12+ raw rows.
    """

    def build(self, raw_section: list[dict] | None) -> DocumentSection | None:
        if not raw_section:
            return None

        by_engine: dict[str, list[dict]] = defaultdict(list)
        for record in raw_section:
            by_engine[record.get("ENGINE_TYPE", "UNKNOWN")].append(record)

        sentences = []
        for engine_type, records in by_engine.items():
            fuel_parts = [
                f"{r.get('CONSUMPTION')} {r.get('UNIT', 'mt')} {r.get('FUEL_TYPE')}"
                for r in records
                if r.get("CONSUMPTION")  # skip zero-consumption rows
            ]
            if fuel_parts:
                sentences.append(
                    f"{engine_type.title()} engine consumed " + ", ".join(fuel_parts) + "."
                )
            else:
                sentences.append(f"{engine_type.title()} engine reported no fuel consumption.")

        return DocumentSection(
            name="consumption",
            content=" ".join(sentences),
            metadata={"engine_types": list(by_engine.keys())},
        )