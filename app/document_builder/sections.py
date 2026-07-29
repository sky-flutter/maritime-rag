# Contains one class or function per domain.
from abc import ABC


class SectionBuilder(ABC):
    pass


class WeatherSectionBuilder(SectionBuilder):
    pass


class NavigationSectionBuilder(SectionBuilder):
    pass


class EngineSectionBuilder(SectionBuilder):
    pass


class CargoSectionBuilder(SectionBuilder):
    pass


class EventSectionBuilder(SectionBuilder):
    pass
