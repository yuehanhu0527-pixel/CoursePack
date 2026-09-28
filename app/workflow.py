from app.quiz import generate_quiz
from app.answer_verifier import verify_quiz_answers
from app.resources import generate_lesson_resources
from app.reading import generate_reading
from app.worksheet import generate_worksheet
from app.planner import create_course_plan
from app.alignment_checker import check_alignment
from app.revision_decider import decide_revision
from app.reviser import (
    revise_quiz,
    revise_reading,
    revise_lesson_resources,
    revise_worksheet
)


def build_course_pack(blueprint):

    plan = create_course_plan(blueprint)

    results = {
        "plan": plan
    }

    for step in plan.steps:

        if step.action == "generate_quiz":
            quiz = generate_quiz(
                blueprint=blueprint,
                num_questions=3
            )

            answer_report = verify_quiz_answers(
                quiz=quiz
            )

            results["quiz"] = quiz
            results["answer_report"] = answer_report

        elif step.action == "generate_lesson_resources":
            results["lesson_resources"] = generate_lesson_resources(
                blueprint=blueprint
            )

        elif step.action == "generate_reading":
            results["reading"] = generate_reading(
                blueprint=blueprint
            )

        elif step.action == "generate_worksheet":
            results["worksheet"] = generate_worksheet(
                blueprint=blueprint,
                num_problems=4
            )
    # 第一次整体 alignment 检查
    alignment_report = check_alignment(
        blueprint=blueprint,
        quiz=results.get("quiz"),
        lesson_resources=results.get("lesson_resources"),
        reading=results.get("reading"),
        worksheet=results.get("worksheet")
    )

    results["alignment_report"] = alignment_report

    max_retries = 2
    revision_count = 0

    while (
        not alignment_report.passed
        and revision_count < max_retries
    ):

        revision_decision = decide_revision(
            alignment_report=alignment_report
        )

        results["revision_decision"] = revision_decision

        if revision_decision.action == "no_revision":
            break

        if revision_decision.action == "revise_worksheet":

            results["worksheet"] = revise_worksheet(
                blueprint=blueprint,
                worksheet=results["worksheet"],
                alignment_report=alignment_report
            )

        elif revision_decision.action == "revise_reading":

            results["reading"] = revise_reading(
                blueprint=blueprint,
                reading=results["reading"],
                alignment_report=alignment_report
            )

        elif revision_decision.action == "revise_lesson_resources":

            results["lesson_resources"] = revise_lesson_resources(
                blueprint=blueprint,
                lesson_resources=results["lesson_resources"],
                alignment_report=alignment_report
            )

        elif revision_decision.action == "revise_quiz":

            results["quiz"] = revise_quiz(
                blueprint=blueprint,
                quiz=results["quiz"],
                alignment_report=alignment_report
            )

            results["answer_report"] = verify_quiz_answers(
                quiz=results["quiz"]
            )

        else:
            break


        revision_count += 1

        alignment_report = check_alignment(
            blueprint=blueprint,
            quiz=results.get("quiz"),
            lesson_resources=results.get("lesson_resources"),
            reading=results.get("reading"),
            worksheet=results.get("worksheet")
        )

        results["alignment_report_after_revision"] = alignment_report

    results["revision_count"] = revision_count

    return results

