import os
import json

from dotenv import load_dotenv
from openai import OpenAI

from app.models import (
    LessonBlueprint,
    Quiz,
    LessonResources,
    Worksheet,
    ReadingMaterial,
    AlignmentReport
)

from app.utils import parse_json_response


load_dotenv()


client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)


def check_alignment(
    blueprint: LessonBlueprint,
    quiz: Quiz | None = None,
    lesson_resources: LessonResources | None = None,
    worksheet: Worksheet | None = None,
    reading: ReadingMaterial | None = None
) -> AlignmentReport:

    materials = {}

    if quiz is not None:
        materials["quiz"] = quiz.model_dump()

    if lesson_resources is not None:
        materials["lesson_resources"] = (
            lesson_resources.model_dump()
        )

    if worksheet is not None:
        materials["worksheet"] = (
            worksheet.model_dump()
        )

    if reading is not None:
        materials["reading"] = (
            reading.model_dump()
        )


    prompt = f"""
You are an instructional alignment and quality checker.

Your job is to evaluate whether a generated instructional package
is coherent, aligned, realistic, and appropriate for the lesson blueprint.

Do NOT redesign the lesson.

Do NOT prefer one teaching style over another.

Do NOT report minor stylistic differences.

Only report meaningful instructional or content problems.


LESSON BLUEPRINT:

{json.dumps(
    blueprint.model_dump(),
    indent=2
)}


GENERATED MATERIALS:

{json.dumps(
    materials,
    indent=2
)}


Evaluate the package using the rules below.


==================================================
1. BLUEPRINT SCOPE
==================================================

All generated materials should stay within the concepts,
skills, learning objective, and assessment targets
defined by the lesson blueprint.

Report an issue when a material introduces a substantial
new concept or skill that students were not expected to learn.

Do NOT report harmless examples, vocabulary support,
background context, or reasonable instructional scaffolds.


==================================================
2. TAUGHT → PRACTICED → ASSESSED ALIGNMENT
==================================================

Important assessed skills should normally be taught
or supported before students are expected to demonstrate them.

Check whether:

- important concepts are taught,
- students have opportunities to practice them,
- assessments measure the intended learning objective.

Do not require every small detail to appear in every material.


==================================================
3. SEMANTIC AND IMPLICIT COVERAGE
==================================================

Judge coverage by meaning, not exact word matching.

A concept may be covered even if different wording is used.

For example:

"using inverse operations"

may be represented by:

"subtract 5 from both sides"
or
"divide both sides by 3."

Do not report missing coverage simply because the exact
blueprint wording is absent.


==================================================
4. ACTUAL TASK DEMANDS
==================================================

Evaluate what students are actually required to DO.

Do not judge alignment only from headings or labels.

For example:

If an objective requires students to explain reasoning,
but the assessment only asks students to recognize a definition,
that may be an alignment problem.

If an objective requires analysis using evidence,
the assessment should include meaningful evidence-based analysis,
not only questions about what evidence is.


==================================================
5. MISSING COVERAGE
==================================================

Report a problem when an important learning target
is substantially absent from instruction, practice,
or assessment.

Focus on important instructional gaps.

Do not report trivial omissions.


==================================================
6. CROSS-MATERIAL CONSISTENCY
==================================================

Check whether the blueprint, lesson resources,
worksheet, quiz, and reading agree with one another.

Report contradictions such as:

- different definitions of the same concept,
- conflicting answers,
- inconsistent procedures,
- materials teaching substantially different content,
- an assessment expecting something different
  from the instructional materials.


==================================================
7. LESSON SEQUENCE ↔ LESSON RESOURCES
==================================================

If lesson_resources are present, they must directly support
the existing lesson_sequence.

Check that:

- there is exactly one resource section for each lesson step,
- sections are in the same order,
- the time matches the corresponding lesson step,
- the activity matches the corresponding lesson step,
- resources directly help carry out that activity,
- no lesson stage is omitted,
- no new lesson stage is invented.

The short "step" label does NOT need to exactly match
the activity wording.

Judge the actual time, activity, and resources.

Do NOT report a mismatch when only the short label differs.


==================================================
8. AVOID FALSE POSITIVES
==================================================

Be conservative.

Do NOT report an issue just because:

- wording is different,
- examples differ,
- one material provides more detail,
- teaching approaches vary,
- an activity is challenging but still realistic,
- a concept is represented implicitly.

Only report issues that would meaningfully affect
instructional quality, correctness, or alignment.


==================================================
9. TIME FEASIBILITY
==================================================

Check whether each lesson step can realistically be completed
within its assigned time.

Consider:

- grade level,
- task complexity,
- amount of reading,
- amount of writing,
- number of questions,
- collaboration requirements,
- transitions,
- number of sub-tasks,
- required student sharing or presentations.

Report a time-feasibility issue only when a lesson step
is clearly overloaded for the available time.

Do NOT require exact minute-by-minute estimates.

Do NOT report an issue simply because a lesson is ambitious.

Examples of possible overload:

- reading a full short story,
  completing detailed analysis,
  finding multiple quotations,
  and discussing results within 15 minutes;

- analyzing many sources,
  completing a long worksheet,
  and presenting findings within a very short block.

A well-scaffolded jigsaw or shortened excerpt may make
an otherwise large task realistic.

==================================================
10. SOURCE INTEGRITY
==================================================

Apply this check ONLY when generated materials claim to use
real external sources, quotations, historical documents,
articles, studies, speeches, letters, laws, publications,
or other source-based content.

Be conservative.

Do NOT report a source-integrity issue merely because a full
academic citation is not provided.

Do NOT flag ordinary references to well-known books, songs,
musical works, artworks, historical documents, laws, treaties,
speeches, or other established works simply because complete
publication or archive information is missing.


A. SUFFICIENT SOURCE IDENTIFICATION

A source may be sufficiently identified when the material gives
enough information to clearly distinguish it from AI-created text.

Examples of sufficient identification may include:

- title + date
- author + title
- issuing body + document title
- publication name + date
- clearly named historical document + date

For example:

"Treaty of Paris, 1783"

or

"Declaration of Independence, 1776"

should generally be considered sufficiently identified for normal
classroom use.

Do NOT require:

- archive URLs
- page numbers
- publisher information
- signatories
- full MLA/APA/Chicago citations
- database identifiers

unless the lesson specifically teaches formal citation skills.


B. DIRECT QUOTATIONS AND AUTHENTIC EXCERPTS

If material is presented as a direct quotation or authentic excerpt
from a real source, there should be enough identifying context to make
clear what source is being quoted.

Report an issue when a passage is presented as authentic but is so
vaguely identified that it cannot reasonably be distinguished from
AI-created text.

Example of a meaningful risk:

"A Loyalist letter, 1783:
'I lost my farm and fled to Canada...'"

If no author, title, source name, or other identifying information
is provided, this may be too vague to safely present as an authentic
quotation.

Do NOT automatically report an issue when the quoted source is a
well-known document and is clearly identified by title and date.


C. AI-CREATED, ADAPTED, OR SIMULATED TEXT

AI-created classroom passages are allowed.

If text is not confirmed to be an authentic quotation or excerpt,
it should be clearly labeled as one of the following when appropriate:

- "Adapted practice passage"
- "Simplified practice passage"
- "Simulated source"
- "Teacher-created practice passage"

Do NOT report the use of simulated or teacher-created material by itself
as a source-integrity problem when it is clearly labeled.

However, if the lesson objective specifically requires students to
analyze authentic primary sources, check whether students still receive
a meaningful opportunity to work with authentic sources somewhere in
the lesson package.

If all source-analysis practice is simulated despite an objective that
explicitly requires authentic primary-source analysis, report this as
an ALIGNMENT problem, not as fabrication.


D. FABRICATED SPECIFICITY

Report a source-integrity issue when the material appears to invent
specific identifying details or presents uncertain information as
verified fact.

Do not invent or falsely attribute:

- authors
- publication names
- document titles
- dates
- quotations
- studies
- organizations
- URLs
- archive references
- citations

If a source cannot be confidently identified, the safer approach is to:

- describe the type of source,
- provide search keywords,
- recommend that the teacher select a verified source,
- or clearly label the passage as simulated or adapted.


E. WELL-KNOWN WORKS AND MEDIA

Do NOT flag references to real works merely because no full citation
is given.

Examples include:

- named musical compositions
- novels
- plays
- poems
- famous speeches
- historical documents
- laws
- treaties
- artworks
- films

For example:

"Clair de Lune by Debussy"

or

"Treaty of Paris, 1783"

is normally acceptable for instructional use without a formal citation.

However, do flag a quotation supposedly taken from such a work when
the quotation appears invented, insufficiently identified, or presented
as exact text without reasonable source support.


F. EXTERNAL LINKS AND SEARCH DIRECTIONS

Do NOT require direct URLs.

Search keywords, source names, archive names, or repository suggestions
are acceptable.

Do NOT report an issue merely because the teacher must retrieve the
actual source separately.

For example:

"Use a verified excerpt from the Declaration of Independence from the
National Archives"

is acceptable.

Only report a problem if the lesson depends on a source that is too vague
to locate or if the missing source prevents the activity from being
meaningfully carried out.

NO EXTERNAL FACT-CHECKING

You do not have access to an external historical,
literary, scientific, legal, or citation database.

Do NOT claim that a quotation, date, attribution,
historical wording, document text, author, or citation
is factually incorrect based only on your own background knowledge.

Do NOT compare generated source text against what you believe
the original source "actually says" unless a trusted reference text
is explicitly included in the provided lesson materials.

For example, do NOT report:

"The real Stamp Act says X rather than Y."

unless the authentic reference text needed to establish that
difference is included in the materials being evaluated.

Instead, only evaluate source integrity using evidence available
inside the provided package.

You MAY report internal problems such as:

- a passage is labeled "simulated" but later called authentic,
- a teacher-created passage is classified as a primary source,
- an answer claims evidence appears in an excerpt when it does not,
- a quotation is presented as authentic but has insufficient
  identifying information,
- two generated materials contradict each other about the same source.

If external verification would be required to establish a problem,
do NOT report that problem.

G. AVOID FALSE POSITIVES

Do NOT report a source-integrity issue merely because:

- a source is not formally cited,
- a URL is missing,
- a historical document excerpt is short,
- a famous source is identified only by title and date,
- a teacher must retrieve the full source separately,
- a simulated source is clearly labeled,
- a resource recommends search keywords,
- an instructional summary paraphrases historical content.

Only report source-integrity issues when there is a meaningful risk that:

- AI-created text is being presented as authentic,
- a quotation is insufficiently identified,
- specific source details appear fabricated,
- or the material could mislead students about the authenticity
  of the source.


H. REPORTING STYLE

When reporting a source-integrity issue:

- Do NOT claim a source is definitely fake unless the provided material
  clearly proves that.
- Prefer language such as:
  "insufficiently identified,"
  "not verifiable from the provided material,"
  "presented as authentic without enough source context,"
  or
  "should be labeled as adapted or simulated."

- Include specific evidence from the material.

- Avoid duplicate source-integrity issues.
  If several examples reflect the same underlying problem,
  combine them into one issue with multiple evidence items.

==================================================
11. ASSESSMENT SEMANTIC CONSISTENCY
==================================================

Check whether each assessment task is internally consistent.

This applies to quiz questions, worksheet problems,
exit tickets, and other assessment tasks.

Check that:

- the question stem matches the skill or concept being tested,
- the expected or correct answer actually answers the question,
- the assigned concept label matches what the question tests,
- terminology is used consistently with the lesson,
- the question does not describe one concept
  while the answer demonstrates another.

Example:

If a science question asks for an INDIRECT effect,
but the correct answer describes the immediate predator
losing its prey, that is a semantic inconsistency
because the answer describes a DIRECT effect.

Also check whether the assessment measures the level
of performance required by the learning objective.

Example:

Objective:
"Analyze theme using textual evidence."

Weak assessment:
"What is textual evidence?"

Better assessment:
Students examine a passage and select or explain evidence
that supports a theme.

Do NOT require every quiz question to measure the full objective.

The assessment as a whole should meaningfully measure
the intended learning.


==================================================
OUTPUT RULES
==================================================

Return ONLY valid JSON.

Use this exact structure:

{{
  "passed": true,
  "issues": []
}}

If problems exist:

{{
  "passed": false,
  "issues": [
    {{
      "concept": "short name of the affected concept",
      "issue": "clear explanation of the instructional problem",
      "affected_materials": [
        "quiz"
      ],
      "evidence": [
        "specific evidence showing the problem"
      ]
    }}
  ]
}}


IMPORTANT:

- Every reported issue must contain specific evidence.
- Name only the materials actually affected.
- Do not invent problems.
- Do not produce recommendations unrelated to the identified issue.
- Prefer a small number of meaningful issues
  over many minor observations.
"""


    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )


    content = response.choices[0].message.content

    data = parse_json_response(content)

    return AlignmentReport(**data)