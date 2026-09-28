from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.blueprint import build_blueprint
from app.graph import graph
from app.input_validator import validate_subject_objective
from app.pdf_export import build_coursepack_pdf


app = FastAPI()


# ==========================================
# CORS
# ==========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================
# REQUEST MODELS
# ==========================================

class InputValidationRequest(BaseModel):
    grade: int
    subject: str
    objective: str


class CoursePackRequest(BaseModel):
    grade: int
    subject: str
    objective: str
    class_length: int = Field(gt=0)
    quiz_questions: int = 5


# ==========================================
# ROOT
# ==========================================

@app.get("/")
def root():
    return {
        "message": "CoursePack API is running"
    }


# ==========================================
# INPUT VALIDATION
# ==========================================

@app.post("/validate-input")
def validate_input(request: InputValidationRequest):

    result = validate_subject_objective(
        grade=request.grade,
        subject=request.subject,
        objective=request.objective
    )

    return result


# ==========================================
# COURSEPACK GENERATION
# ==========================================

@app.post("/coursepack")
def create_coursepack(request: CoursePackRequest):

    blueprint = build_blueprint(
        grade=request.grade,
        subject=request.subject,
        objective=request.objective,
        class_length=request.class_length
    )

    result = graph.invoke({
        "blueprint": blueprint,
        "quiz_questions": request.quiz_questions,
        "answer_revision_count": 0,
        "alignment_revision_count": 0,
        "max_retries": 2
    })

    return result


# ==========================================
# PDF EXPORT
# ==========================================

@app.post("/export-pdf")
def export_pdf(result: dict):

    pdf_buffer = build_coursepack_pdf(result)

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
                'attachment; filename="coursepack.pdf"'
        }
    )