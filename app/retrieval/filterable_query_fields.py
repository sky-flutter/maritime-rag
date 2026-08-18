


from dataclasses import dataclass


@dataclass(frozen=True)
class FilterableField:
    key: str
    source_json_key: str
    description: str



FILTERABLE_METADATA_FIELDS : list[FilterableField] = [
    FilterableField(key='imo', source_json_key='IMO', description="The vessel's IMO number, a 7-digit identifier."),
    FilterableField(key='voyage_nr', source_json_key='VOYAGE_NR', description="The voyage number."),
    FilterableField(key='report_type', source_json_key='REPORT_TYPE', description="Report types, e.g. AT_SEA, IN_PORT, ARRIVAL, DEPARTURE."),
    FilterableField(key='vessel_condition', source_json_key='VESSEL_CONDITION', description="Vessel condition, e.g. Laden, Ballast."),
    FilterableField("destination_port", "DESTINATION_PORT", "The report's destination port."),
]

DATETIME_KEY = 'datetime_gmt'
DATETIME_SOURCE_JSON_KEY = 'DATETIME_GMT'

SECTION_FIELD_KEY = 'section'
KNOWN_SECTIONS = ['report_header', 'weather', 'navigation', 'consumption', 'forob', 'main_engine']