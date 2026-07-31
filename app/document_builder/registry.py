from app.document_builder.builders.consumption_builder import ConsumptionSectionBuilder
from app.document_builder.builders.navigation_builder import NavigationSectionBuilder
from app.document_builder.builders.reports_builder import ReportsSectionBuilder
from app.document_builder.builders.weather_builder import WeatherSectionBuilder
from app.document_builder.builders.forob_builder import ForobSectionBuilder
from app.document_builder.builders.main_engine_builder import MainEngineSectionBuilder
from app.document_builder.sections import SectionBuilder


def build_default_registry() -> dict[str, SectionBuilder]:
    """Maps raw JSON section keys to their builder. Add a new section
    type by adding one entry here — no other code changes needed.
    """
    return {
        "REPORTS": ReportsSectionBuilder(),
        "WEATHER": WeatherSectionBuilder(),
        "NAVIGATION": NavigationSectionBuilder(),
        "CONSUMPTION": ConsumptionSectionBuilder(),
        "FOROB": ForobSectionBuilder(),        # same pattern as Consumption
        "MAIN_ENGINE": MainEngineSectionBuilder(),  # same pattern as Weather
    }
