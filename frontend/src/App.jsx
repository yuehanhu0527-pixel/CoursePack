import { useState } from 'react'
import './App.css'


function formatLabel(text) {
  if (!text) return ''

  return text
    .replaceAll('_', ' ')
    .replace(/\b\w/g, (letter) => letter.toUpperCase())
}


function ResourceValue({ value }) {
  if (value === null || value === undefined) {
    return null
  }

  if (
    typeof value === 'string' ||
    typeof value === 'number'
  ) {
    return <span>{value}</span>
  }

  if (Array.isArray(value)) {
    return (
      <div className="nested-list">
        {value.map((item, index) => (
          <div
            key={index}
            className="nested-item"
          >
            <ResourceValue value={item} />
          </div>
        ))}
      </div>
    )
  }

  if (typeof value === 'object') {
    return (
      <div className="resource-object">
        {Object.entries(value).map(
          ([key, nestedValue]) => (
            <div
              key={key}
              className="resource-field"
            >
              <strong>
                {formatLabel(key)}:
              </strong>{' '}

              <ResourceValue
                value={nestedValue}
              />
            </div>
          )
        )}
      </div>
    )
  }

  return <span>{String(value)}</span>
}


function ResourceItem({ item }) {
  if (typeof item === 'string') {
    return (
      <div className="resource-item">
        <p>{item}</p>
      </div>
    )
  }

  if (!item || typeof item !== 'object') {
    return null
  }

  const {
    type,
    description,
    ...otherFields
  } = item

  return (
    <div className="resource-item">

      {type && (
        <div className="resource-type">
          {formatLabel(type)}
        </div>
      )}

      {description && (
        <p className="resource-description">
          {description}
        </p>
      )}

      {Object.entries(otherFields).map(
        ([key, value]) => (
          <div
            key={key}
            className="resource-extra"
          >
            <strong>
              {formatLabel(key)}
            </strong>

            <ResourceValue value={value} />
          </div>
        )
      )}

    </div>
  )
}


function App() {
  const [grade, setGrade] = useState('')
  const [subject, setSubject] = useState('')
  const [objective, setObjective] = useState('')
  const [classLength, setClassLength] = useState('')
  const [quizQuestions, setQuizQuestions] = useState('5')

  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [loadingStage, setLoadingStage] = useState('')
  const [error, setError] = useState('')
  const [exportingPdf, setExportingPdf] = useState(false)

  const [
    showWorksheetAnswers,
    setShowWorksheetAnswers
  ] = useState(false)

  const [
    showQuizAnswers,
    setShowQuizAnswers
  ] = useState(false)

  const [
    validationWarning,
    setValidationWarning
  ] = useState(null)


  async function generateCoursePack(
    subjectToUse = subject
  ) {
    setLoading(true)

    setLoadingStage(
      'Building and validating your CoursePack...'
    )

    setError('')
    setResult(null)

    setShowWorksheetAnswers(false)
    setShowQuizAnswers(false)

    try {
      const response = await fetch(
        'http://127.0.0.1:8000/coursepack',
        {
          method: 'POST',

          headers: {
            'Content-Type': 'application/json',
          },

          body: JSON.stringify({
            grade: Number(grade),
            subject: subjectToUse,
            objective: objective,
            class_length: Number(classLength),
            quiz_questions: Number(quizQuestions),
          }),
        }
      )

      if (!response.ok) {
        throw new Error(
          'Failed to generate CoursePack'
        )
      }

      const data = await response.json()

      setLoadingStage(
        'Finalizing your lesson package...'
      )

      setResult(data)

    } catch (err) {
      setError(err.message)

    } finally {
      setLoading(false)
      setLoadingStage('')
    }
  }


  async function handleSubmit() {
    setError('')
    setResult(null)
    setValidationWarning(null)

    if (
      !grade ||
      !subject ||
      !objective.trim() ||
      !classLength
    ) {
      setError(
        'Please complete all lesson fields.'
      )
      return
    }

    if (Number(classLength) <= 0) {
      setError(
        'Class length must be greater than 0.'
      )
      return
    }

    setLoading(true)

    setLoadingStage(
      'Checking lesson input...'
    )

    try {
      const validationResponse = await fetch(
        'http://127.0.0.1:8000/validate-input',
        {
          method: 'POST',

          headers: {
            'Content-Type': 'application/json',
          },

          body: JSON.stringify({
            grade: Number(grade),
            subject: subject,
            objective: objective,
          }),
        }
      )

      if (!validationResponse.ok) {
        throw new Error(
          'Failed to validate lesson input'
        )
      }

      const validationData =
        await validationResponse.json()

      if (validationData.match) {

        setLoading(false)

        await generateCoursePack(subject)

      } else {

        setValidationWarning(validationData)

        setLoading(false)
        setLoadingStage('')
      }

    } catch (err) {

      setError(err.message)

      setLoading(false)
      setLoadingStage('')
    }
  }


  async function handleExportPdf() {
    if (!result) {
      setError(
        'Generate a CoursePack before exporting.'
      )
      return
    }

    setExportingPdf(true)
    setError('')

    try {
      const response = await fetch(
        'http://127.0.0.1:8000/export-pdf',
        {
          method: 'POST',

          headers: {
            'Content-Type': 'application/json',
          },

          body: JSON.stringify(result),
        }
      )

      if (!response.ok) {
        throw new Error(
          'Failed to export PDF'
        )
      }

      const blob = await response.blob()

      const url =
        window.URL.createObjectURL(blob)

      const link =
        document.createElement('a')

      link.href = url

      link.download = 'coursepack.pdf'

      document.body.appendChild(link)

      link.click()

      link.remove()

      window.URL.revokeObjectURL(url)

    } catch (err) {

      setError(err.message)

    } finally {

      setExportingPdf(false)
    }
  }


  return (
    <div className="page-layout">

      {/* ==========================================
          SIDEBAR
      ========================================== */}

      <aside className="sidebar">

        <div className="sidebar-title">
          CoursePack
        </div>

        <a href="#top">
          Create Lesson
        </a>

        {result?.blueprint && (
          <a href="#blueprint">
            Lesson Blueprint
          </a>
        )}

        {result?.lesson_resources?.sections && (
          <a href="#resources">
            Lesson Resources
          </a>
        )}

        {result?.worksheet && (
          <a href="#worksheet">
            Worksheet
          </a>
        )}

        {result?.quiz && (
          <a href="#quiz">
            Quiz
          </a>
        )}

        {result?.reading && (
          <a href="#reading">
            Reading
          </a>
        )}

      </aside>


      {/* ==========================================
          MAIN CONTENT
      ========================================== */}

      <main
        id="top"
        className="app"
      >

        <div className="decor decor-one"></div>

        <div className="decor decor-two"></div>


        {/* ==========================================
            HEADER
        ========================================== */}

        <div className="title-row">

          <h1>
            CoursePack
          </h1>

          <span className="tag">
            AI Lesson Planner
          </span>

        </div>


        {/* ==========================================
            INPUT FORM
        ========================================== */}

        <div className="form-card">

          <select
            value={grade}
            onChange={(e) =>
              setGrade(e.target.value)
            }
          >

            <option value="">
              Select Grade
            </option>

            {Array.from(
              { length: 12 },
              (_, index) => (
                <option
                  key={index + 1}
                  value={index + 1}
                >
                  Grade {index + 1}
                </option>
              )
            )}

          </select>


          <select
            value={subject}
            onChange={(e) =>
              setSubject(e.target.value)
            }
          >

            <option value="">
              Select Subject
            </option>

            <option value="Math">
              Math
            </option>

            <option value="Science">
              Science
            </option>

            <option value="English Language Arts">
              English Language Arts
            </option>

            <option value="Social Studies">
              Social Studies
            </option>

            <option value="Computer Science">
              Computer Science
            </option>

            <option value="Art">
              Art
            </option>

            <option value="Music">
              Music
            </option>

            <option value="Health">
              Health
            </option>

            <option value="Physical Education">
              Physical Education
            </option>

            <option value="World Languages">
              World Languages
            </option>

            <option value="Economics">
              Economics
            </option>

            <option value="Psychology">
              Psychology
            </option>

            <option value="Environmental Science">
              Environmental Science
            </option>

            <option value="Engineering">
              Engineering
            </option>

          </select>


          <input
            type="text"
            placeholder="Lesson Objective"
            value={objective}
            onChange={(e) =>
              setObjective(e.target.value)
            }
          />


          <input
            type="number"
            min="1"
            placeholder="Class Length (minutes)"
            value={classLength}
            onChange={(e) =>
              setClassLength(e.target.value)
            }
          />


          <select
            value={quizQuestions}
            onChange={(e) =>
              setQuizQuestions(e.target.value)
            }
          >

            <option value="3">
              3 Quiz Questions
            </option>

            <option value="5">
              5 Quiz Questions
            </option>

            <option value="10">
              10 Quiz Questions
            </option>

          </select>


          <button
            onClick={handleSubmit}
            disabled={loading}
          >
            {
              loading
                ? 'Working...'
                : 'Generate CoursePack'
            }
          </button>


          {/* ======================================
              INPUT VALIDATION WARNING
          ====================================== */}

          {validationWarning && (

            <div className="validation-warning">

              <h3>
                Subject Check
              </h3>

              <p>
                Your lesson objective may fit{' '}

                <strong>
                  {
                    validationWarning
                      .suggested_subject
                  }
                </strong>{' '}

                better than{' '}

                <strong>
                  {subject}
                </strong>.
              </p>

              <p>
                {validationWarning.reason}
              </p>


              <div className="validation-actions">

                <button
                  className="secondary-button"
                  onClick={() => {

                    setValidationWarning(null)

                    generateCoursePack(subject)
                  }}
                >
                  Keep {subject}
                </button>


                <button
                  onClick={() => {

                    const newSubject =
                      validationWarning
                        .suggested_subject

                    setSubject(newSubject)

                    setValidationWarning(null)

                    generateCoursePack(
                      newSubject
                    )
                  }}
                >
                  Use {
                    validationWarning
                      .suggested_subject
                  }
                </button>

              </div>

            </div>

          )}


          {error && (

            <p className="error">
              {error}
            </p>

          )}

        </div>


        {/* ==========================================
            LOADING
        ========================================== */}

        {loading && (

          <div className="result-card loading-card">

            <div className="loading-spinner"></div>

            <h2>
              {
                loadingStage ||
                'Creating your CoursePack...'
              }
            </h2>

            <p>
              Please wait while CoursePack prepares
              your lesson materials.
            </p>

          </div>

        )}


        {/* ==========================================
            EXPORT PDF
        ========================================== */}

        {result && !loading && (

          <div className="export-actions">

            <button
              className="secondary-button"
              onClick={handleExportPdf}
              disabled={exportingPdf}
            >
              {
                exportingPdf
                  ? 'Exporting PDF...'
                  : 'Export PDF'
              }
            </button>

          </div>

        )}


        {/* ==========================================
            LESSON BLUEPRINT
        ========================================== */}

        {result?.blueprint && (

          <div
            id="blueprint"
            className="result-card"
          >

            <h2>
              Lesson Blueprint
            </h2>

            <p>
              <strong>Grade:</strong>{' '}
              {result.blueprint.grade}
            </p>

            <p>
              <strong>Subject:</strong>{' '}
              {result.blueprint.subject}
            </p>

            <p>
              <strong>Objective:</strong>{' '}
              {result.blueprint.objective}
            </p>

            <p>
              <strong>
                Class Length:
              </strong>{' '}

              {result.blueprint.class_length} minutes
            </p>


            <h3>
              Concepts
            </h3>

            <ul>
              {result.blueprint.concepts?.map(
                (concept, index) => (

                  <li key={index}>
                    {concept}
                  </li>

                )
              )}
            </ul>


            <h3>
              Prerequisites
            </h3>

            <ul>
              {result.blueprint.prerequisites?.map(
                (item, index) => (

                  <li key={index}>
                    {item}
                  </li>

                )
              )}
            </ul>


            <h3>
              Vocabulary
            </h3>

            <ul className="vocabulary-list">

              {result.blueprint.vocabulary?.map(
                (word, index) => (

                  <li key={index}>
                    {word}
                  </li>

                )
              )}

            </ul>


            <h3>
              Assessment Targets
            </h3>

            <ul>

              {result.blueprint
                .assessment_targets
                ?.map(
                  (target, index) => (

                    <li key={index}>
                      {target}
                    </li>

                  )
                )}

            </ul>


            <h3>
              Lesson Sequence
            </h3>

            <ul>

              {result.blueprint
                .lesson_sequence
                ?.map(
                  (step, index) => (

                    <li key={index}>

                      <strong>
                        {step.time}
                      </strong>

                      {' — '}

                      {step.activity}

                    </li>

                  )
                )}

            </ul>

          </div>

        )}


        {/* ==========================================
            LESSON RESOURCES
        ========================================== */}

        {result?.lesson_resources?.sections && (

          <div
            id="resources"
            className="result-card"
          >

            <h2>
              Lesson Resources
            </h2>


            {result.lesson_resources.sections.map(
              (section, index) => (

                <div
                  key={index}
                  className="lesson-resource-section"
                >

                  <div className="lesson-step-header">

                    <span className="lesson-step-number">
                      {index + 1}
                    </span>

                    <div>

                      <h3 className="lesson-step-title">
                        {section.step}
                      </h3>

                      <span className="lesson-step-time">
                        {section.time}
                      </span>

                    </div>

                  </div>


                  <div className="lesson-activity">

                    <strong>
                      Lesson Activity
                    </strong>

                    <p>
                      {section.activity}
                    </p>

                  </div>


                  {section.resources?.length > 0 && (

                    <div className="lesson-resources-list">

                      <strong>
                        Resources
                      </strong>


                      {section.resources.map(
                        (
                          resource,
                          resourceIndex
                        ) => (

                          <ResourceItem
                            key={resourceIndex}
                            item={resource}
                          />

                        )
                      )}

                    </div>

                  )}

                </div>

              )
            )}

          </div>

        )}


        {/* ==========================================
            WORKSHEET
        ========================================== */}

        {result?.worksheet && (

          <div
            id="worksheet"
            className="result-card"
          >

            <h2>
              Worksheet
            </h2>


            {result.worksheet.title && (

              <h3>
                {result.worksheet.title}
              </h3>

            )}


            {result.worksheet.instructions && (

              <p>

                <strong>
                  Instructions:
                </strong>{' '}

                {result.worksheet.instructions}

              </p>

            )}


            {result.worksheet.problems?.length > 0 && (

              <>

                <h3>
                  Problems
                </h3>


                {result.worksheet.problems.map(
                  (problem, index) => (

                    <div
                      key={index}
                      className="question-block"
                    >

                      <strong>
                        {index + 1}.
                      </strong>{' '}

                      <ResourceValue
                        value={problem}
                      />

                    </div>

                  )
                )}

              </>

            )}


            {result.worksheet.answer_key?.length > 0 && (

              <>

                <div
                  style={{
                    marginTop: '18px',
                    marginBottom: '10px'
                  }}
                >

                  <button
                    className="secondary-button"
                    onClick={() =>
                      setShowWorksheetAnswers(
                        !showWorksheetAnswers
                      )
                    }
                  >

                    {
                      showWorksheetAnswers
                        ? 'Hide Answer Key'
                        : 'Show Answer Key'
                    }

                  </button>

                </div>


                {showWorksheetAnswers && (

                  <>

                    <h3>
                      Answer Key
                    </h3>


                    {result.worksheet.answer_key.map(
                      (answer, index) => (

                        <div
                          key={index}
                          className="question-block"
                        >

                          <strong>
                            {index + 1}.
                          </strong>{' '}

                          <ResourceValue
                            value={answer}
                          />

                        </div>

                      )
                    )}

                  </>

                )}

              </>

            )}

          </div>

        )}


        {/* ==========================================
            QUIZ
        ========================================== */}

        {result?.quiz && (

          <div
            id="quiz"
            className="result-card"
          >

            <h2>
              Quiz
            </h2>


            {result.quiz.title && (

              <h3>
                {result.quiz.title}
              </h3>

            )}


            {result.quiz.questions?.some(
              (question) =>
                Boolean(question.correct_answer)
            ) && (

              <div
                style={{
                  marginTop: '12px',
                  marginBottom: '14px'
                }}
              >

                <button
                  className="secondary-button"
                  onClick={() =>
                    setShowQuizAnswers(
                      !showQuizAnswers
                    )
                  }
                >

                  {
                    showQuizAnswers
                      ? 'Hide Correct Answers'
                      : 'Show Correct Answers'
                  }

                </button>

              </div>

            )}


            {result.quiz.questions?.map(
              (question, index) => (

                <div
                  key={index}
                  className="question-block"
                >

                  <p>

                    <strong>
                      {index + 1}.{' '}
                      {question.question}
                    </strong>

                  </p>


                  {question.options?.length > 0 && (

                    <ul>

                      {question.options.map(
                        (
                          option,
                          optionIndex
                        ) => (

                          <li
                            key={optionIndex}
                          >
                            {option}
                          </li>

                        )
                      )}

                    </ul>

                  )}


                  {
                    showQuizAnswers &&
                    question.correct_answer && (

                      <p>

                        <strong>
                          Correct Answer:
                        </strong>{' '}

                        {question.correct_answer}

                      </p>

                    )
                  }

                </div>

              )
            )}

          </div>

        )}


        {/* ==========================================
            READING
        ========================================== */}

        {result?.reading && (

          <div
            id="reading"
            className="result-card"
          >

            <h2>
              Reading
            </h2>


            {result.reading.title && (

              <h3>
                {result.reading.title}
              </h3>

            )}


            {result.reading.introduction && (

              <p>
                {result.reading.introduction}
              </p>

            )}


            {result.reading.sections?.map(
              (section, index) => (

                <div
                  key={index}
                  className="reading-section"
                >

                  <ResourceValue
                    value={section}
                  />

                </div>

              )
            )}


            {result.reading.summary && (

              <>

                <h3>
                  Summary
                </h3>

                <p>
                  {result.reading.summary}
                </p>

              </>

            )}

          </div>

        )}

      </main>

    </div>
  )
}


export default App