import json
import logging
import random
from typing import Dict, List, Optional

from google import genai
from google.genai import types as genai_types

from app.models.cv import CandidateProfile
from app.services.cv_generator import CVTextGenerator


class MockCVTextGenerator(CVTextGenerator):
    """Deterministic-ish fallback profile generator used in dev and tests."""

    def __init__(self) -> None:
        self._random = random.Random()

    def generate(self) -> CandidateProfile:
        first_names = ["Avery", "Kai", "Morgan", "Sage", "River"]
        last_names = ["Singh", "Garcia", "Turner", "Patel", "Davis"]
        roles = [
            "Machine Learning Engineer",
            "Frontend Engineer",
            "Product Manager",
            "AI Researcher",
            "Security Analyst",
        ]
        locations = ["Berlin, Germany", "Austin, TX", "Toronto, Canada", "Remote"]

        name = f"{self._random.choice(first_names)} {self._random.choice(last_names)}"
        role = self._random.choice(roles)
        skills = [
            "Python",
            "TypeScript",
            "Prompt Engineering",
            "Generative AI",
            "Kubernetes",
            "LLM Fine-tuning",
        ]

        return CandidateProfile(
            name=name,
            title=role,
            summary=(
                f"{name} is a {role} with a strong record of shipping AI-powered products "
                "and mentoring cross-functional teams."
            ),
            contact={
                "email": f"{name.replace(' ', '.').lower()}@example.com",
                "phone": "+1 (555) 555-1212",
                "location": self._random.choice(locations),
            },
            experience=[
                {
                    "company": "NovaTech Labs",
                    "role": role,
                    "duration": "2021 - Present",
                    "achievements": "Leads delivery of intelligent features that increased adoption by 30%.",
                },
                {
                    "company": "Quantum Solutions",
                    "role": f"Senior {role}",
                    "duration": "2018 - 2021",
                    "achievements": "Introduced experimentation practices that cut cycle time by 20%.",
                },
            ],
            education=[
                {
                    "institution": "Metropolitan Institute of Technology",
                    "degree": "MSc Computer Science",
                    "graduation_year": 2018,
                }
            ],
            skills=skills,
            languages=["English", "German"],
        )


class GeminiCVTextGenerator(CVTextGenerator):
    """Gemini-powered profile generator with JSON schema enforcement."""

    def __init__(
        self,
        api_key: str,
        model_name: str,
        fallback: Optional[MockCVTextGenerator] = None,
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
        experience = []
        for item in _ensure_list(payload.get("experience")):
            if not isinstance(item, dict):
                continue
            clean = {key: str(value).strip() for key, value in item.items() if value}
            if clean:
                experience.append(clean)

        education = []
        for item in _ensure_list(payload.get("education")):
            if not isinstance(item, dict):
                continue
            clean = {key: str(value).strip() for key, value in item.items() if value}
            if clean:
                education.append(clean)

        skills = [
            str(skill).strip()
            for skill in _ensure_list(payload.get("skills"))
            if str(skill).strip()
        ]
        languages = [
            str(lang).strip()
            for lang in _ensure_list(payload.get("languages"))
            if str(lang).strip()
        ]

        name = str(payload.get("name") or "").strip()
        title = str(payload.get("title") or "").strip()
        summary = str(payload.get("summary") or "").strip()

        if not name or not title:
            raise ValueError("Candidate profile missing required fields.")

        return CandidateProfile(
            name=name,
            title=title,
            summary=summary,
            contact={
                "email": str(contact.get("email", "") or "").strip(),
                "phone": str(contact.get("phone", "") or "").strip(),
                "location": str(contact.get("location", "") or "").strip(),
            },
            experience=experience,
            education=education,
            skills=skills,
            languages=languages,
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
