import json

from openai import OpenAI
from datetime import datetime, timedelta
from app.retrieval.filterable_query_fields import (
    FILTERABLE_METADATA_FIELDS,
    SECTION_FIELD_KEY,
    KNOWN_SECTIONS,
)

from app.retrieval.query_analyzer import QueryAnalyzer, QueryAnalysis


def _build_extraction_schema() -> dict:
    properties = {
        field.key: {"type": ["string", "null"], "description": field.description}
        for field in FILTERABLE_METADATA_FIELDS
    }

    properties[SECTION_FIELD_KEY] = {
        "type": ["string", "null"],
        "enum": KNOWN_SECTIONS + [None],
        "description": (
            "Which report section the question is about. Map based on topic:\n"
            "- weather: wind, waves, swell, current, water temperature\n"
            "- navigation: position, course, speed, draft\n"
            "- consumption: fuel BURNED/USED by engines (asking how much was consumed)\n"
            "- forob: fuel REMAINING/LEFT on board, ROB, bunker levels remaining "
            "(asking how much is left, not how much was used)\n"
            "- main_engine: engine RPM, output, running hours\n"
            "- report_header: voyage number, destination, vessel condition, distance\n"
            "Null if the question doesn't clearly map to one section, or spans multiple."
        ),
    }

    properties["datetime_start"] = {
        "type": ["string", "null"],
        "description": "Start of the relevant date/time range, ISO 8601. Null if not applicable.",
    }
    properties["datetime_end"] = {
        "type": ["string", "null"],
        "description": "End of the relevant date/time range, ISO 8601. Null if not applicable.",
    }

    return {
        "type": "object",
        "properties": properties,
        "required": list(properties.keys()),
        "additionalProperties": False,
    }


SYSTEM_PROMPT = """You extract structured filters from questions about ship voyage reports.
Only extract a field if it is explicitly stated or unambiguously implied in the question.
Never guess or invent values. If a field isn't mentioned, return null for it.
Today's reference date, if relative dates are used, is {today}."""


EXTRACTION_SCHEMA = _build_extraction_schema()


class LLMQueryAnalyzer(QueryAnalyzer):
    def __init__(self, client: OpenAI, model: str = "gpt-4o-mini"):
        self._client = client
        self._model = model

    def _parse_iso(self, value: str | None) -> datetime | None:
        if not value:
            return None

        try:
            return datetime.fromisoformat(value)
        except ValueError:
            return None

    def analyze(self, text: str) -> QueryAnalysis:
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT.format(
                        today=datetime.utcnow().date().isoformat()
                    ),
                },
                {"role": "user", "content": text},
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "query_filters",
                    "schema": EXTRACTION_SCHEMA,
                    "strict": True,
                },
            },
        )

        extracted = json.loads(response.choices[0].message.content)

        metadata_filter = {
            field.key: extracted[field.key]
            for field in FILTERABLE_METADATA_FIELDS
            if extracted.get(field.key)
        }

        if extracted.get(SECTION_FIELD_KEY):
            metadata_filter[SECTION_FIELD_KEY] = extracted[SECTION_FIELD_KEY]

        datetime_from = self._parse_iso(extracted["datetime_start"])
        datetime_to = self._parse_iso(extracted["datetime_end"])

        if datetime_from and not datetime_to:
            datetime_to = datetime_from + timedelta(minutes=1)
            datetime_from = datetime_to - timedelta(minutes=1)

        return QueryAnalysis(
            original_text=text,
            metadata_filter=metadata_filter,
            datetime_from=datetime_from,
            datetime_to=datetime_to,
        )
