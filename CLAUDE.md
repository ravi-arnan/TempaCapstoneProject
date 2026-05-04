# CLAUDE.md

## Project Identity

**Project Name:** Sistem Deteksi Tingkat Pemahaman Mahasiswa Berdasarkan Hasil Kuis Berbasis Data  
**Team ID:** TP-G005  
**Theme:** Digital Education & Skill Development [file:42]

## Project Purpose

This project builds a simple educational web application that:
1. Accepts learning material in text form.
2. Generates a quiz automatically from that material.
3. Lets the user complete the quiz.
4. Analyzes quiz results.
5. Displays understanding level, insight, recommendation, and a simple chart. [file:42]

The core objective is to help students evaluate their understanding after reading learning material, because many students currently consume digital material without a clear evaluation mechanism. [file:42]

## Product Scope

### In Scope
- Text input for learning material.
- Automatic quiz generation from the material.
- Quiz-taking interface.
- Score calculation.
- Time tracking.
- Understanding level classification.
- Insight generation.
- Learning recommendation generation.
- Simple result visualization. [file:42]

### Out of Scope
- PDF upload.
- Video/audio processing.
- Complex AI/ML model as the main engine.
- RAG pipelines.
- Telegram bot.
- Authentication and complex user management.
- Complex database architecture.
- Full LMS features such as class management, assignments, or discussions. [file:42]

## Technical Direction

### Frontend
- React
- TypeScript [file:42]

### Backend
- Python [file:42]

### Data / Analysis
- Pandas for processing quiz result data. [file:42]
- Scikit-learn is optional, not required for MVP. [file:42]

### Tools
- GitHub for version control. [file:42]
- VS Code for development. [file:42]

## Architecture Principles

- Keep the system simple and modular.
- Separate concerns clearly:
  - frontend UI
  - quiz generation logic
  - result evaluation logic
  - insight/recommendation rules
- Prefer rule-based logic for MVP.
- Do not introduce unnecessary infrastructure.
- Avoid over-engineering. [file:42]

## Expected User Flow

1. User opens the application.
2. User pastes learning material as text.
3. Backend processes the text and generates quiz questions.
4. User answers the quiz.
5. Backend calculates:
   - total correct answers
   - total wrong answers
   - score
   - completion time
6. Backend classifies understanding level.
7. Frontend shows:
   - score
   - time
   - understanding level
   - insight
   - recommendation
   - chart

## MVP Feature Requirements

### 1. Material Input
- Accept plain text input.
- Reject empty input.
- Show validation if the material is too short.

### 2. Quiz Generator
- Generate simple multiple-choice questions from text.
- Each question must contain:
  - prompt
  - answer options
  - correct answer
- Keep implementation deterministic and understandable.

### 3. Quiz Session
- Show questions one by one or in a list.
- Allow selecting one answer per question.
- Record completion time.

### 4. Result Calculation
- Compute correct count, wrong count, score percentage, and time taken.

### 5. Understanding Classification
Use simple rule-based classification:
- High
- Medium
- Low

Do not use advanced ML unless explicitly requested.

### 6. Insight Engine
Generate short explanations based on user performance.

Examples:
- High score + efficient completion time -> good understanding.
- Medium score + long completion time -> partial understanding, still hesitant.
- Low score -> core concepts need review.

### 7. Recommendation Engine
Generate practical next steps:
- Review the material again.
- Focus on misunderstood sections.
- Retry the quiz.
- Summarize key points before retaking.

### 8. Result Chart
Display a simple chart such as:
- correct vs wrong answers
- score percentage

## Suggested Repository Structure

```txt
/
├─ frontend/
│  ├─ src/
│  │  ├─ components/
│  │  ├─ pages/
│  │  ├─ hooks/
│  │  ├─ services/
│  │  ├─ types/
│  │  └─ utils/
│  └─ package.json
│
├─ backend/
│  ├─ app/
│  │  ├─ main.py
│  │  ├─ routes/
│  │  ├─ services/
│  │  ├─ models/
│  │  ├─ schemas/
│  │  └─ utils/
│  ├─ tests/
│  └─ requirements.txt
│
├─ docs/
│  ├─ PRD.md
│  └─ project-plan.md
│
└─ README.md
```

## Backend Guidelines

- Use Python for quiz logic and analysis. [file:42]
- Keep APIs small and explicit.
- Prefer pure functions for scoring, classification, and recommendation rules.
- Keep business logic out of route handlers.
- Store reusable logic in `services/`.
- If persistence is needed for MVP, prefer lightweight local storage or simple file-based storage before introducing a complex database.

### Suggested backend modules
- `quiz_generator.py`
- `quiz_evaluator.py`
- `understanding_classifier.py`
- `insight_engine.py`
- `recommendation_engine.py`

## Frontend Guidelines

- Use React + TypeScript as the main UI layer. [file:42]
- Keep pages simple and task-oriented.
- Focus on usability over flashy design.
- Build around the main flow:
  - input material
  - review generated quiz
  - answer questions
  - view result and analysis

### Suggested frontend pages
- `HomePage`
- `QuizPage`
- `ResultPage`

### Suggested frontend components
- `MaterialInputForm`
- `QuizQuestionCard`
- `QuizTimer`
- `ResultSummary`
- `UnderstandingBadge`
- `InsightCard`
- `RecommendationCard`
- `ScoreChart`

## API Contract Suggestions

### POST `/quiz/generate`
Input:
```json
{
  "material_text": "..."
}
```

Output:
```json
{
  "quiz_id": "generated-id",
  "questions": [
    {
      "id": 1,
      "question": "string",
      "options": ["A", "B", "C", "D"],
      "correct_answer": "A"
    }
  ]
}
```

### POST `/quiz/submit`
Input:
```json
{
  "quiz_id": "generated-id",
  "answers": [
    {
      "question_id": 1,
      "selected_answer": "A"
    }
  ],
  "time_taken_seconds": 120
}
```

Output:
```json
{
  "score_percentage": 80,
  "correct_count": 4,
  "wrong_count": 1,
  "understanding_level": "High",
  "insight": "You understand the main points well.",
  "recommendation": "Continue to the next material or retry with harder questions.",
  "chart_data": {
    "correct": 4,
    "wrong": 1
  }
}
```

## Coding Rules

### General
- Write readable code first.
- Keep functions small and focused.
- Avoid hidden magic logic.
- Prefer explicit names over clever names.
- Add comments only where the intent is not obvious.

### TypeScript
- Use strict typing where practical.
- Avoid `any` unless absolutely necessary.
- Centralize shared types.

### Python
- Prefer simple functions and dataclasses/pydantic models when useful.
- Keep route handlers thin.
- Separate validation, transformation, and analysis logic.

## Product Rules

- The app should not pretend to be an advanced AI tutor if the logic is rule-based.
- Output must stay honest and explainable.
- Understanding classification should be deterministic and reviewable.
- Recommendations must be actionable, not generic motivational filler.
- Quiz generation should prioritize clarity and relevance over complexity.

## UX Rules

- The interface must be understandable on first use.
- The main action on each page should be obvious.
- Do not overload users with too many settings.
- Show progress during quiz completion.
- Result page must clearly separate:
  - score
  - category
  - explanation
  - recommendation

## Testing Priorities

### Must test
- Empty material input.
- Very short material input.
- Quiz generation from normal text.
- Submit flow with complete answers.
- Submit flow with some unanswered questions.
- Result classification rules.
- Insight and recommendation consistency.
- Frontend-backend integration.

### Nice to have
- Snapshot/component tests for core UI.
- Unit tests for scoring/classification services.

## Delivery Priorities

### Week 1
- Finalize requirements and system design.
- Prepare repository structure.
- Setup React frontend and Python backend environment. [file:42]

### Week 2
- Implement text input flow.
- Implement simple quiz generator. [file:42]

### Week 3
- Implement quiz-taking experience.
- Implement result storage/processing flow. [file:42]

### Week 4
- Implement analysis logic.
- Implement insight and recommendation features. [file:42]

### Week 5
- Integrate frontend and backend.
- Test, debug, and prepare final demo. [file:42]

## Team Responsibility Mapping

- **Audry Nabila Anastasya**: Backend - Quiz Generator. [file:42]
- **Ariq Marwan Permana**: Backend - Data & Analysis. [file:42]
- **Desta Anandhika Rajendra Maheswara**: Backend - Logic, Insight, Recommendation. [file:42]
- **Ravi Arnan Irianto**: Frontend - React & TypeScript integration. [file:42]

## Risk Control Rules

To avoid the risks identified in the proposal:
- Do not expand scope without team agreement.
- Do not add advanced AI components unless the MVP is complete.
- Keep weekly progress visible.
- Prioritize working end-to-end flow over adding many unfinished features.
- Use dummy/synthetic data if real evaluation data is not available. [file:42]

## Definition of Done

A task is done only if:
- the feature works in the intended flow,
- the code is readable,
- the feature is integrated with the rest of the system,
- basic validation is included,
- no critical bug blocks the main demo.

## Final Note

This repository should optimize for:
- simplicity,
- explainability,
- reliable demo flow,
- realistic completion within 4–5 weeks. [file:42]
