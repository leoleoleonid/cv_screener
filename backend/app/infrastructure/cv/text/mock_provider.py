import random

from app.domain.cv.interfaces import CVTextGenerator
from app.domain.cv.models import CandidateProfile


class MockCVTextGenerator(CVTextGenerator):
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
