from app.document_builder.sections import SectionBuilder
from app.document_builder.models import DocumentSection


class WeatherSectionBuilder(SectionBuilder):
    """WEATHER is a list with a single snapshot record per report."""

    def build(self, raw_section: list[dict] | None) -> DocumentSection | None:
        if not raw_section:
            return None

        w = raw_section[0]
        content = (
            f"Wind force {w.get('WIND_FORCE')} from {w.get('WIND_DIRECTION')}°. "
            f"Wave height {w.get('WAVE_HEIGHT')} m, wave length {w.get('WAVE_LENGTH')} m, "
            f"wave direction {w.get('WAVE_DIRECTION')}°. "
            f"Swell height {w.get('SWELL_HEIGHT')} m. "
            f"Current speed {w.get('current')} kn from {w.get('CURRENT_DIRECTION')}°. "
            f"Water temperature {w.get('WATER_TEMPERATURE')}°C."
        )
        return DocumentSection(name="weather", content=content, metadata={})