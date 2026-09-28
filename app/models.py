from pydantic import BaseModel, Field
from typing import Any

class LessonStep(BaseModel):
    time: str
    activity: str


class LessonBlueprint(BaseModel):
    grade: int
    subject: str
    objective: str
    class_length: int
    concepts: list[str]
    prerequisites: list[str]
    vocabulary: list[str]
    lesson_sequence: list[LessonStep]
    assessment_targets: list[str]

class QuizQuestion(BaseModel):
    question:str
    options: list[str]
    correct_answer: str
    concept: str
    difficulty: str

class Quiz(BaseModel):
    title:str
    questions: list[QuizQuestion]

class AnswerVerificationResult(BaseModel):
    question_number : int
    correct: bool
    expected_answer : str
    reason: str

class AnswerVerificationReport(BaseModel):
    passed: bool
    results: list[AnswerVerificationResult]

class LessonResourceSection(BaseModel):
    step: str
    time: str
    activity: str
    resources: list[str | dict[str, Any]] = Field(default_factory=list)

class LessonResources(BaseModel):
    sections: list[LessonResourceSection]

class ReadingMaterial(BaseModel):
    title: str
    introduction: str
    sections: list[str]
    summary: str

class Worksheet(BaseModel):
    title:str
    instructions:str
    problems: list[str]
    answer_key: list[str]

class PlanStep(BaseModel):
    action:str 
    reason: str 

class CoursePlan(BaseModel):
    steps: list[PlanStep]

class AlignmentIssue(BaseModel):
    concept: str
    issue: str
    affected_materials: list[str]
    evidence: list[str]


class AlignmentReport(BaseModel):
    passed: bool
    issues: list[AlignmentIssue]

class RevisionDecision(BaseModel):
    action: str
    reason: str
