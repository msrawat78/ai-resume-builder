"""
Resume data models using dataclasses for structured resume representation.
"""

from dataclasses import dataclass, field
from typing import List, Optional
import json


@dataclass
class ExperienceEntry:
    """Represents a single work experience entry."""
    company: str = ""
    title: str = ""
    start_date: str = ""
    end_date: str = ""
    location: str = ""
    bullets: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "company": self.company,
            "title": self.title,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "location": self.location,
            "bullets": self.bullets,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ExperienceEntry":
        return cls(
            company=data.get("company", ""),
            title=data.get("title", ""),
            start_date=data.get("start_date", ""),
            end_date=data.get("end_date", ""),
            location=data.get("location", ""),
            bullets=data.get("bullets", []),
        )


@dataclass
class EducationEntry:
    """Represents a single education entry."""
    institution: str = ""
    degree: str = ""
    field_of_study: str = ""
    start_date: str = ""
    end_date: str = ""
    gpa: str = ""
    honors: str = ""

    def to_dict(self) -> dict:
        return {
            "institution": self.institution,
            "degree": self.degree,
            "field_of_study": self.field_of_study,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "gpa": self.gpa,
            "honors": self.honors,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "EducationEntry":
        return cls(
            institution=data.get("institution", ""),
            degree=data.get("degree", ""),
            field_of_study=data.get("field_of_study", ""),
            start_date=data.get("start_date", ""),
            end_date=data.get("end_date", ""),
            gpa=data.get("gpa", ""),
            honors=data.get("honors", ""),
        )


@dataclass
class ResumeData:
    """
    Top-level resume data model. Holds all structured resume fields.
    All fields are optional to support partial parsing.
    """
    name: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    linkedin: str = ""
    website: str = ""
    summary: str = ""
    skills: List[str] = field(default_factory=list)
    experience: List[ExperienceEntry] = field(default_factory=list)
    education: List[EducationEntry] = field(default_factory=list)
    certifications: List[str] = field(default_factory=list)
    languages: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "location": self.location,
            "linkedin": self.linkedin,
            "website": self.website,
            "summary": self.summary,
            "skills": self.skills,
            "experience": [e.to_dict() for e in self.experience],
            "education": [ed.to_dict() for ed in self.education],
            "certifications": self.certifications,
            "languages": self.languages,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ResumeData":
        return cls(
            name=data.get("name", ""),
            email=data.get("email", ""),
            phone=data.get("phone", ""),
            location=data.get("location", ""),
            linkedin=data.get("linkedin", ""),
            website=data.get("website", ""),
            summary=data.get("summary", ""),
            skills=data.get("skills", []),
            experience=[ExperienceEntry.from_dict(e) for e in data.get("experience", [])],
            education=[EducationEntry.from_dict(ed) for ed in data.get("education", [])],
            certifications=data.get("certifications", []),
            languages=data.get("languages", []),
        )

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)

    def is_empty(self) -> bool:
        return not any([
            self.name, self.email, self.phone, self.summary,
            self.skills, self.experience, self.education
        ])
