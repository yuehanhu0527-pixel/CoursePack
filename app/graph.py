from typing import TypedDict, Any

from langgraph.graph import StateGraph, START, END

from app.planner import create_course_plan
from app.quiz import generate_quiz
from app.answer_verifier import verify_quiz_answers
from app.resources import generate_lesson_resources
from app.reading import generate_reading
from app.worksheet import generate_worksheet
from app.alignment_checker import check_alignment
from app.revision_decider import decide_revision

from app.reviser import (
    revise_quiz,
    revise_reading,
    revise_lesson_resources,
    revise_worksheet
)


# =========================================================
# STATE
# =========================================================

class CoursePackState(TypedDict, total=False):

    blueprint: Any
    plan: Any

    quiz: Any
    lesson_resources: Any
    reading: Any
    worksheet: Any

    answer_report: Any
    alignment_report: Any
    revision_decision: Any

    # Quiz answer correction loop
    answer_revision_count: int

    # Cross-material alignment correction loop
    alignment_revision_count: int

    # Maximum retries for each loop
    max_retries: int

    quiz_questions: int

# =========================================================
# PLANNER NODE
# =========================================================

def planner_node(state: CoursePackState):

    blueprint = state["blueprint"]

    plan = create_course_plan(blueprint)

    return {
        "plan": plan
    }


# =========================================================
# GENERATION NODE
# =========================================================

def generation_node(state: CoursePackState):

    blueprint = state["blueprint"]
    plan = state["plan"]

    updates = {}

    for step in plan.steps:

        if step.action == "generate_quiz":

            quiz = generate_quiz(
                blueprint=blueprint,
                num_questions=state.get("quiz_questions", 5)
            )

            updates["quiz"] = quiz

            updates["answer_report"] = verify_quiz_answers(
                quiz=quiz
            )

        elif step.action == "generate_lesson_resources":

            updates["lesson_resources"] = generate_lesson_resources(
                blueprint=blueprint
            )

        elif step.action == "generate_reading":

            updates["reading"] = generate_reading(
                blueprint=blueprint,
            )

        elif step.action == "generate_worksheet":

            updates["worksheet"] = generate_worksheet(
                blueprint=blueprint,
                num_problems=4
            )

    return updates


# =========================================================
# ROUTE AFTER GENERATION / ANSWER REVISION
# =========================================================

def route_after_generation(state: CoursePackState):

    answer_report = state.get("answer_report")

    # Planner may decide not to generate a quiz.
    if answer_report is None:
        return "alignment"

    # Quiz answers are correct.
    if answer_report.passed:
        return "alignment"

    answer_revision_count = state.get(
        "answer_revision_count",
        0
    )

    max_retries = state.get(
        "max_retries",
        2
    )

    # Do not revise forever.
    if answer_revision_count >= max_retries:
        return "alignment"

    return "fix_quiz"


# =========================================================
# ANSWER REVISION NODE
# =========================================================

def answer_revision_node(state: CoursePackState):

    blueprint = state["blueprint"]
    quiz = state["quiz"]
    answer_report = state["answer_report"]

    # Tell revise_quiz WHY the quiz needs revision.
    revision_context = {
        "answer_report": answer_report.model_dump()
    }

    revised_quiz = revise_quiz(
        blueprint=blueprint,
        quiz=quiz,
        revision_context=revision_context
    )

    new_answer_report = verify_quiz_answers(
        quiz=revised_quiz
    )

    return {
        "quiz": revised_quiz,
        "answer_report": new_answer_report,
        "answer_revision_count": (
            state.get("answer_revision_count", 0) + 1
        )
    }


# =========================================================
# ALIGNMENT NODE
# =========================================================

def alignment_node(state: CoursePackState):

    alignment_report = check_alignment(
        blueprint=state["blueprint"],
        quiz=state.get("quiz"),
        lesson_resources=state.get("lesson_resources"),
        reading=state.get("reading"),
        worksheet=state.get("worksheet")
    )

    print("\n=== ALIGNMENT REPORT ===")
    print(alignment_report.model_dump_json(indent=2))
    print("========================\n")

    return {
        "alignment_report": alignment_report
    }

    return {
        "alignment_report": alignment_report
    }


# =========================================================
# ROUTE AFTER ALIGNMENT
# =========================================================

def route_after_alignment(state: CoursePackState):

    alignment_report = state["alignment_report"]

    # Everything is aligned.
    if alignment_report.passed:
        return "end"

    alignment_revision_count = state.get(
        "alignment_revision_count",
        0
    )

    max_retries = state.get(
        "max_retries",
        2
    )

    # Stop if alignment has already been revised too many times.
    if alignment_revision_count >= max_retries:
        return "end"

    return "revise"


# =========================================================
# REVISION DECISION NODE
# =========================================================

def revision_decision_node(state: CoursePackState):

    alignment_report = state["alignment_report"]

    decision = decide_revision(
        alignment_report=alignment_report
    )

    return {
        "revision_decision": decision
    }


# =========================================================
# ROUTE AFTER REVISION DECISION
# =========================================================

def route_after_revision_decision(
    state: CoursePackState
):

    decision = state["revision_decision"]

    if decision.action == "no_revision":
        return "end"

    return "revise"


# =========================================================
# REVISION NODE
# =========================================================

def revision_node(state: CoursePackState):

    blueprint = state["blueprint"]
    alignment_report = state["alignment_report"]
    decision = state["revision_decision"]

    updates = {}

    # -------------------------
    # QUIZ
    # -------------------------

    if decision.action == "revise_quiz":

        revision_context = {
            "alignment_report": alignment_report.model_dump()
        }

        revised_quiz = revise_quiz(
            blueprint=blueprint,
            quiz=state["quiz"],
            revision_context=revision_context
        )

        updates["quiz"] = revised_quiz

        # Quiz changed, so its answers must be checked again.
        updates["answer_report"] = verify_quiz_answers(
            quiz=revised_quiz
        )

    # -------------------------
    # WORKSHEET
    # -------------------------

    elif decision.action == "revise_worksheet":

        updates["worksheet"] = revise_worksheet(
            blueprint=blueprint,
            worksheet=state["worksheet"],
            alignment_report=alignment_report
        )

    # -------------------------
    # READING
    # -------------------------

    elif decision.action == "revise_reading":

        updates["reading"] = revise_reading(
            blueprint=blueprint,
            reading=state["reading"],
            alignment_report=alignment_report
        )

    # -------------------------
    # LESSON RESOURCES
    # -------------------------

    elif decision.action == "revise_lesson_resources":

        updates["lesson_resources"] = revise_lesson_resources(
            blueprint=blueprint,
            lesson_resources=state["lesson_resources"],
            alignment_report=alignment_report
        )

    # Unknown action: do not pretend that a revision happened.
    else:
        return {}

    updates["alignment_revision_count"] = (
        state.get("alignment_revision_count", 0) + 1
    )

    return updates

# =========================================================
# ROUTE AFTER ALIGNMENT REVISION
# =========================================================

def route_after_revision(state: CoursePackState):

    decision = state["revision_decision"]

    # Special case:
    # If alignment revision changed the quiz,
    # make sure the new quiz answers are still correct.
    if decision.action == "revise_quiz":

        answer_report = state.get("answer_report")

        if (
            answer_report is not None
            and not answer_report.passed
        ):

            answer_revision_count = state.get(
                "answer_revision_count",
                0
            )

            max_retries = state.get(
                "max_retries",
                2
            )

            if answer_revision_count < max_retries:
                return "fix_quiz"

    return "alignment"


# =========================================================
# BUILD GRAPH
# =========================================================

builder = StateGraph(CoursePackState)

builder.add_node(
    "planner",
    planner_node
)

builder.add_node(
    "generate",
    generation_node
)

builder.add_node(
    "answer_revision",
    answer_revision_node
)

builder.add_node(
    "alignment",
    alignment_node
)

builder.add_node(
    "revision_decision",
    revision_decision_node
)

builder.add_node(
    "revision",
    revision_node
)


# =========================================================
# EDGES
# =========================================================

builder.add_edge(
    START,
    "planner"
)

builder.add_edge(
    "planner",
    "generate"
)
# After generation:
# bad quiz answers -> fix quiz
# otherwise -> alignment
builder.add_conditional_edges(
    "generate",
    route_after_generation,
    {
        "fix_quiz": "answer_revision",
        "alignment": "alignment"
    }
)

# After fixing quiz answers:
# still wrong -> fix again
# correct / retry limit -> alignment
builder.add_conditional_edges(
    "answer_revision",
    route_after_generation,
    {
        "fix_quiz": "answer_revision",
        "alignment": "alignment"
    }
)


# After alignment:
# pass -> END
# fail -> revision decision
builder.add_conditional_edges(
    "alignment",
    route_after_alignment,
    {
        "end": END,
        "revise": "revision_decision"
    }
)


# After deciding what to revise:
# no_revision -> END
# otherwise -> revision
builder.add_conditional_edges(
    "revision_decision",
    route_after_revision_decision,
    {
        "end": END,
        "revise": "revision"
    }
)


# After revising:
# if quiz answers became wrong -> answer revision
# otherwise -> alignment again
builder.add_conditional_edges(
    "revision",
    route_after_revision,
    {
        "fix_quiz": "answer_revision",
        "alignment": "alignment"
    }
)


# =========================================================
# COMPILE
# =========================================================

graph = builder.compile()
