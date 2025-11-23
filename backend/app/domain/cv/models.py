from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class CandidateProfile:
    name: str
    title: str
    summary: str
    contact: Dict[str, str]
    experience: List[Dict[str, str]]
    education: List[Dict[str, str]]
    skills: List[str]
    languages: List[str]
    photo_path: Optional[Path] = None
