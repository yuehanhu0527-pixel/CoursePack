from io import BytesIO

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak
)


def build_coursepack_pdf(result: dict) -> BytesIO:

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=50,
        leftMargin=50,
        topMargin=50,
        bottomMargin=50
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "CoursePackTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        spaceAfter=20
    )

    section_style = ParagraphStyle(
        "SectionTitle",
        parent=styles["Heading1"],
        spaceBefore=14,
        spaceAfter=10
    )

    subsection_style = ParagraphStyle(
        "SubsectionTitle",
        parent=styles["Heading2"],
        spaceBefore=10,
        spaceAfter=6
    )

    body_style = styles["BodyText"]

    story = []

    # -------------------------------------------------
    # TITLE
    # -------------------------------------------------

    story.append(
        Paragraph(
            "CoursePack Lesson Package",
            title_style
        )
    )

    blueprint = result.get("blueprint")

    if blueprint:
        story.append(
            Paragraph(
                f"<b>Grade:</b> {blueprint.get('grade', '')}",
                body_style
            )
        )

        story.append(
            Paragraph(
                f"<b>Subject:</b> {blueprint.get('subject', '')}",
                body_style
            )
        )

        story.append(
            Paragraph(
                f"<b>Objective:</b> {blueprint.get('objective', '')}",
                body_style
            )
        )

        story.append(
            Paragraph(
                f"<b>Class Length:</b> "
                f"{blueprint.get('class_length', '')} minutes",
                body_style
            )
        )

    story.append(Spacer(1, 16))


    # -------------------------------------------------
    # BLUEPRINT
    # -------------------------------------------------

    if blueprint:

        story.append(
            Paragraph(
                "Lesson Blueprint",
                section_style
            )
        )

        add_list(
            story,
            "Concepts",
            blueprint.get("concepts", []),
            subsection_style,
            body_style
        )

        add_list(
            story,
            "Prerequisites",
            blueprint.get("prerequisites", []),
            subsection_style,
            body_style
        )

        add_list(
            story,
            "Vocabulary",
            blueprint.get("vocabulary", []),
            subsection_style,
            body_style
        )

        add_list(
            story,
            "Assessment Targets",
            blueprint.get("assessment_targets", []),
            subsection_style,
            body_style
        )

        story.append(
            Paragraph(
                "Lesson Sequence",
                subsection_style
            )
        )

        for step in blueprint.get("lesson_sequence", []):
            story.append(
                Paragraph(
                    f"<b>{step.get('time', '')}</b> - "
                    f"{step.get('activity', '')}",
                    body_style
                )
            )

            story.append(Spacer(1, 6))


    # -------------------------------------------------
    # LESSON RESOURCES
    # -------------------------------------------------

    lesson_resources = result.get("lesson_resources")

    if lesson_resources:

        story.append(PageBreak())

        story.append(
            Paragraph(
                "Lesson Resources",
                section_style
            )
        )

        for index, section in enumerate(
            lesson_resources.get("sections", []),
            start=1
        ):

            story.append(
                Paragraph(
                    f"{index}. {section.get('step', '')}",
                    subsection_style
                )
            )

            story.append(
                Paragraph(
                    f"<b>Time:</b> {section.get('time', '')}",
                    body_style
                )
            )

            story.append(
                Paragraph(
                    f"<b>Activity:</b> "
                    f"{section.get('activity', '')}",
                    body_style
                )
            )

            story.append(Spacer(1, 6))

            for resource in section.get("resources", []):

                if isinstance(resource, dict):

                    resource_type = resource.get(
                        "type",
                        "Resource"
                    )

                    description = resource.get(
                        "description",
                        ""
                    )

                    story.append(
                        Paragraph(
                            f"<b>{resource_type}</b>",
                            body_style
                        )
                    )

                    story.append(
                        Paragraph(
                            description,
                            body_style
                        )
                    )

                else:
                    story.append(
                        Paragraph(
                            str(resource),
                            body_style
                        )
                    )

                story.append(Spacer(1, 6))


    # -------------------------------------------------
    # WORKSHEET
    # -------------------------------------------------

    worksheet = result.get("worksheet")

    if worksheet:

        story.append(PageBreak())

        story.append(
            Paragraph(
                "Worksheet",
                section_style
            )
        )

        story.append(
            Paragraph(
                worksheet.get("title", ""),
                subsection_style
            )
        )

        story.append(
            Paragraph(
                worksheet.get("instructions", ""),
                body_style
            )
        )

        story.append(Spacer(1, 10))

        for index, problem in enumerate(
            worksheet.get("problems", []),
            start=1
        ):
            story.append(
                Paragraph(
                    f"<b>{index}.</b> {problem}",
                    body_style
                )
            )
            story.append(Spacer(1, 8))

        story.append(
            Paragraph(
                "Answer Key",
                subsection_style
            )
        )

        for index, answer in enumerate(
            worksheet.get("answer_key", []),
            start=1
        ):
            story.append(
                Paragraph(
                    f"<b>{index}.</b> {answer}",
                    body_style
                )
            )
            story.append(Spacer(1, 6))


    # -------------------------------------------------
    # QUIZ
    # -------------------------------------------------

    quiz = result.get("quiz")

    if quiz:

        story.append(PageBreak())

        story.append(
            Paragraph(
                "Quiz",
                section_style
            )
        )

        story.append(
            Paragraph(
                quiz.get("title", ""),
                subsection_style
            )
        )

        for index, question in enumerate(
            quiz.get("questions", []),
            start=1
        ):

            story.append(
                Paragraph(
                    f"<b>{index}.</b> "
                    f"{question.get('question', '')}",
                    body_style
                )
            )

            for option in question.get("options", []):
                story.append(
                    Paragraph(
                        option,
                        body_style
                    )
                )

            story.append(
                Paragraph(
                    f"<b>Correct Answer:</b> "
                    f"{question.get('correct_answer', '')}",
                    body_style
                )
            )

            story.append(Spacer(1, 10))


    # -------------------------------------------------
    # READING
    # -------------------------------------------------

    reading = result.get("reading")

    if reading:

        story.append(PageBreak())

        story.append(
            Paragraph(
                "Reading",
                section_style
            )
        )

        story.append(
            Paragraph(
                reading.get("title", ""),
                subsection_style
            )
        )

        story.append(
            Paragraph(
                reading.get("introduction", ""),
                body_style
            )
        )

        story.append(Spacer(1, 10))

        for section in reading.get("sections", []):
            story.append(
                Paragraph(
                    section,
                    body_style
                )
            )

            story.append(Spacer(1, 8))

        story.append(
            Paragraph(
                "Summary",
                subsection_style
            )
        )

        story.append(
            Paragraph(
                reading.get("summary", ""),
                body_style
            )
        )


    doc.build(story)

    buffer.seek(0)

    return buffer


def add_list(
    story,
    title,
    items,
    subsection_style,
    body_style
):

    story.append(
        Paragraph(
            title,
            subsection_style
        )
    )

    for item in items:
        story.append(
            Paragraph(
                f"- {item}",
                body_style
            )
        )

        story.append(Spacer(1, 4))