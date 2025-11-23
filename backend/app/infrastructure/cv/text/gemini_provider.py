import json
import logging
from typing import Dict, List, Optional

from google import genai
from google.genai import types as genai_types

from app.domain.cv.interfaces import CVTextGenerator
from app.domain.cv.models import CandidateProfile
from app.infrastructure.cv.text.mock_provider import MockCVTextGenerator


class GeminiCVTextGenerator(CVTextGenerator):
    def __init__(
        self,
        api_key: str,
        model_name: str,
        fallback: Optional[CVTextGenerator] = None,
    ) -> None:
        self._client = genai.Client(api_key=api_key) if api_key and model_name else None
        self._model_name = model_name
        self._fallback = fallback or MockCVTextGenerator()
        self._logger = logging.getLogger(__name__)

    def generate(self) -> CandidateProfile:
        if not self._client or not self._model_name:
            self._logger.info("GeminiCVTextGenerator falling back to mock implementation.")
            return self._fallback.generate()

        config = genai_types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=self._get_schema(),
        )

        try:
            response = self._client.models.generate_content(
                model=self._model_name,
                contents=self._prompt(),
                config=config,
            )

            payload = self._extract_json(response)
            if payload:
                return self._profile_from_payload(payload)
        except Exception:
            self._logger.exception("Gemini text generation failed, falling back to mock.")
        return self._fallback.generate()

    def _profile_from_payload(self, payload: Dict[str, object]) -> CandidateProfile:
        def _ensure_list(value: object) -> List:
            if isinstance(value, list):
                return value
            if value is None:
                return []
            return [value]

        contact = payload.get("contact") if isinstance(payload.get("contact"), dict) else {}
        experience = [item for item in _ensure_list(payload.get("experience")) if isinstance(item, dict)]
        education = [item for item in _ensure_list(payload.get("education")) if isinstance(item, dict)]
        skills = [str(skill) for skill in _ensure_list(payload.get("skills"))]
        languages = [str(lang) for lang in _ensure_list(payload.get("languages"))]

        return CandidateProfile(
            name=str(payload.get("name", "Jordan Doe")),
            title=str(payload.get("title", "AI Specialist")),
            summary=str(
                payload.get(
                    "summary",
                    "Seasoned professional experienced in AI product delivery.",
                )
            ),
            contact={
                "email": str(contact.get("email", "jordan.doe@example.com")),
                "phone": str(contact.get("phone", "+1 (555) 000-0000")),
                "location": str(contact.get("location", "Remote")),
            },
            experience=experience or [
                {
                    "company": "NovaTech Labs",
                    "role": "AI Specialist",
                    "duration": "2020 - Present",
                    "achievements": "Delivered automation with measurable business outcomes.",
                }
            ],
            education=education or [
                {
                    "institution": "Metropolitan Institute of Technology",
                    "degree": "MSc Computer Science",
                    "graduation_year": 2018,
                }
            ],
            skills=skills or ["Python", "Prompt Engineering"],
            languages=languages or ["English"],
        )

    def _prompt(self) -> str:
        return (
            "You are a CV-writing assistant. Produce a single JSON object "
            "containing all the details for a skilled professional candidate."
        )

    def _get_schema(self) -> genai_types.Schema:
        return genai_types.Schema(
            type=genai_types.Type.OBJECT,
            properties={
                "name": genai_types.Schema(type=genai_types.Type.STRING),
                "title": genai_types.Schema(type=genai_types.Type.STRING),
                "summary": genai_types.Schema(type=genai_types.Type.STRING),
                "contact": genai_types.Schema(
                    type=genai_types.Type.OBJECT,
                    properties={
                        "email": genai_types.Schema(type=genai_types.Type.STRING),
                        "phone": genai_types.Schema(type=genai_types.Type.STRING),
                        "location": genai_types.Schema(type=genai_types.Type.STRING),
                    },
                ),
                "experience": genai_types.Schema(
                    type=genai_types.Type.ARRAY,
                    items=genai_types.Schema(
                        type=genai_types.Type.OBJECT,
                        properties={
                            "company": genai_types.Schema(type=genai_types.Type.STRING),
                            "role": genai_types.Schema(type=genai_types.Type.STRING),
                            "duration": genai_types.Schema(type=genai_types.Type.STRING),
                            "achievements": genai_types.Schema(type=genai_types.Type.STRING),
                        },
                    ),
                ),
                "education": genai_types.Schema(
                    type=genai_types.Type.ARRAY,
                    items=genai_types.Schema(
                        type=genai_types.Type.OBJECT,
                        properties={
                            "institution": genai_types.Schema(type=genai_types.Type.STRING),
                            "degree": genai_types.Schema(type=genai_types.Type.STRING),
                            "graduation_year": genai_types.Schema(type=genai_types.Type.INTEGER),
                        },
                    ),
                ),
                "skills": genai_types.Schema(
                    type=genai_types.Type.ARRAY,
                    items=genai_types.Schema(type=genai_types.Type.STRING),
                ),
                "languages": genai_types.Schema(
                    type=genai_types.Type.ARRAY,
                    items=genai_types.Schema(type=genai_types.Type.STRING),
                ),
            },
        )

    def _extract_json(self, response) -> Optional[Dict[str, object]]:
        if hasattr(response, "text") and response.text:
            try:
                return json.loads(response.text)
            except json.JSONDecodeError:
                self._logger.error("Gemini returned INVALID JSON *even with schema*. Raw text: %s", response.text)
                return None
        return None
