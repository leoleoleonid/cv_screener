from pathlib import Path
from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class CandidateProfile(BaseModel):
    """Normalized candidate profile used across generators and renderers."""

    model_config = ConfigDict(arbitrary_types_allowed=True, validate_assignment=True)

    name: str
    title: str
    summary: str
    contact: Dict[str, object]
    experience: List[Dict[str, object]]
    education: List[Dict[str, object]]
    skills: List[str]
    languages: List[str]
    gender: Optional[str] = None
    photo_path: Optional[Path] = Field(default=None, exclude=True)
