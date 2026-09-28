from app.blueprint import build_blueprint
from app.graph import graph
from app.resources import generate_lesson_resources


blueprint = build_blueprint(
    grade=7,
    subject="Social Studies",
    objective="Students will explain the causes and effects of the American Revolution.",
    class_length=55
)
resources = generate_lesson_resources(blueprint)

print("\n=== LESSON RESOURCES ===")
print(
    resources.model_dump_json(
        indent=2
    )
)

print("\n=== CHECK ===")

print(
    "Lesson steps:",
    len(blueprint.lesson_sequence)
)

print(
    "Resource sections:",
    len(resources.sections)
)

for lesson_step, resource_section in zip(
    blueprint.lesson_sequence,
    resources.sections
):
    print()

    print(
        "PLAN:",
        lesson_step.time,
        "-",
        lesson_step.activity
    )

    print(
        "RESOURCE:",
        resource_section.time,
        "-",
        resource_section.activity
    )

    print(
        "MATCH:",
        lesson_step.time == resource_section.time
        and lesson_step.activity == resource_section.activity
    )



