import json
import re
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, ValidationError

class InterviewAnswerEvaluation(BaseModel):
    score: float = Field(..., ge=0, le=100, description="Overall answer score from 0 to 100")
    technical_accuracy: float = Field(..., ge=0, le=100, description="Technical correctness score")
    completeness: float = Field(..., ge=0, le=100, description="Depth and coverage score")
    feedback: str = Field(..., description="Actionable constructive coaching critique")
    strengths: List[str] = Field(default_factory=list, description="Key strengths identified in the answer")
    missing_concepts: List[str] = Field(default_factory=list, description="Technical gaps or missed architecture points")
    model_answer: str = Field(..., description="Gold-standard senior engineer response")

class PracticeQuestionEvaluation(BaseModel):
    score: float = Field(..., ge=0, le=100)
    feedback: str
    strengths: List[str] = Field(default_factory=list)
    missing_concepts: List[str] = Field(default_factory=list)

class ProjectSpec(BaseModel):
    name: str
    description: str
    tech_stack: List[str]

class ResourceItem(BaseModel):
    title: str
    type: str
    link: str

class MilestoneSpec(BaseModel):
    phase_number: int
    title: str
    duration: str
    objectives: List[str]
    recommended_projects: List[ProjectSpec] = Field(default_factory=list)
    learning_resources: List[ResourceItem] = Field(default_factory=list)

class CareerRoadmapPlan(BaseModel):
    overview: str
    key_focus_areas: List[str]
    milestones: List[MilestoneSpec]

def extract_and_validate_json(raw_text: str, schema_cls: Any) -> Any:
    """
    Extracts JSON from an LLM response string and validates it against a Pydantic model.
    Handles markdown backticks, prefix conversational text, and missing keys.
    """
    if not raw_text or not raw_text.strip():
        raise ValueError("Model output was completely empty")

    cleaned = raw_text.strip()
    # Strip markdown ```json ... ``` blocks
    if "```json" in cleaned:
        parts = cleaned.split("```json")
        if len(parts) > 1:
            cleaned = parts[1].split("```")[0].strip()
    elif "```" in cleaned:
        parts = cleaned.split("```")
        if len(parts) > 1:
            cleaned = parts[1].strip()

    # Search for first { to last }
    json_match = re.search(r'\{.*\}', cleaned, re.DOTALL)
    if not json_match:
        raise ValueError("No JSON object structure found in response text")

    json_str = json_match.group(0)

    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        # Simple cleanup attempt (fix trailing commas)
        fixed_json = re.sub(r',\s*([\]}])', r'\1', json_str)
        try:
            data = json.loads(fixed_json)
        except Exception:
            raise ValueError(f"Malformed JSON from AI model: {str(e)}")

    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object, got {type(data).__name__}")

    # Validate with Pydantic
    try:
        validated = schema_cls.model_validate(data)
        return validated
    except ValidationError as ve:
        raise ValueError(f"Schema validation failed: {ve.errors()}")
