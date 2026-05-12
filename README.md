<p align="center">
  <img src="assets/logo.svg" alt="Asahlagi logo" width="240">
</p>

# Asahlagi

> *Asah lagi sampai paham.*

**Asahlagi** is a web-based educational tool that converts learning material into an automatic quiz, evaluates the result, then surfaces an understanding level, insight, and learning recommendation — so students can measure their grasp of a topic instead of guessing it. The name itself encodes the loop: read, asah, asah lagi, sampai paham.

> See [`BRAND.md`](BRAND.md) for the full brand identity (name, voice, copy library) and [`DESIGN.md`](DESIGN.md) for visual design tokens.

**Formal project title (academic submission)**: *Sistem Deteksi Tingkat Pemahaman Mahasiswa Berdasarkan Hasil Kuis Berbasis Data*

## Theme

**Digital Education & Skill Development** [file:42]

## Team

**Team ID:** TP-G005 — Capstone for the **Tempa** learning program [file:42]

- Audry Nabila Anastasya — Backend Quiz Generator [file:42]
- Ariq Marwan Permana — Backend Data & Analisis [file:42]
- Desta Anandhika Rajendra Maheswara — Backend Logic, Insight & Recommendation [file:42]
- Ravi Arnan Irianto — Frontend React & TypeScript [file:42]

## Background

Many students consume digital learning materials such as modules and articles but do not have a clear way to measure whether they truly understand the content. Quiz creation is also often manual and not always available, making evaluation less effective. This project addresses that gap by integrating quiz generation, result analysis, and recommendation into one simple system. [file:42]

## Main Features

- Text-based learning material input
- Automatic quiz generation
- Quiz-taking interface
- Score and time calculation
- Understanding level detection
- Automatic insight
- Learning recommendation
- Simple result chart [file:42]

## Scope

### Included
- Material input in text form
- Simple rule-based quiz generation
- Simple result analysis
- Web interface for taking quizzes and viewing results [file:42]

### Excluded
- PDF/video upload
- Complex AI/ML models as the main engine
- Authentication and complex database systems [file:42]

## Tech Stack

### Frontend
- React
- TypeScript [file:42]

### Backend
- Python [file:42]

### Libraries / Tools
- Pandas
- Scikit-learn (optional)
- GitHub
- VS Code [file:42]

## Proposed Architecture

```txt
User Input (Text Material)
        ↓
Frontend (React + TypeScript)
        ↓
Backend API (Python)
        ↓
Quiz Generator → Quiz Evaluator → Understanding Classifier
                              ↓
                    Insight & Recommendation Engine
        ↓
Result Page + Simple Chart
```

## Core User Flow

1. User pastes learning material into the application.
2. System generates quiz questions from the material.
3. User answers the quiz.
4. System calculates score and completion time.
5. System classifies understanding level.
6. System shows insight, recommendation, and chart. [file:42]

## Project Structure

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
│  │  ├─ schemas/
│  │  └─ utils/
│  ├─ tests/
│  └─ requirements.txt
│
├─ docs/
│  ├─ PRD.md
│  ├─ TASKS.md
│  └─ project-plan.md
│
└─ README.md
```

## Suggested API Endpoints

### `POST /quiz/generate`
Generate quiz questions from text material.

#### Request
```json
{
  "material_text": "Your learning material here"
}
```

#### Response
```json
{
  "quiz_id": "quiz-001",
  "questions": [
    {
      "id": 1,
      "question": "What is ...?",
      "options": ["A", "B", "C", "D"]
    }
  ]
}
```

### `POST /quiz/submit`
Submit quiz answers and return result analysis.

#### Request
```json
{
  "quiz_id": "quiz-001",
  "answers": [
    {
      "question_id": 1,
      "selected_answer": "A"
    }
  ],
  "time_taken_seconds": 120
}
```

#### Response
```json
{
  "score_percentage": 80,
  "correct_count": 4,
  "wrong_count": 1,
  "understanding_level": "High",
  "insight": "You understand the main concepts well.",
  "recommendation": "Continue to the next material or retry with a more difficult quiz.",
  "chart_data": {
    "correct": 4,
    "wrong": 1
  }
}
```

## Development Plan

### Week 1
- Finalize system design
- Setup environment
- Prepare repo structure [file:42]

### Week 2
- Implement material input
- Implement quiz generator [file:42]

### Week 3
- Implement quiz-taking flow
- Implement result processing [file:42]

### Week 4
- Implement analysis, insight, and recommendation [file:42]

### Week 5
- Integrate frontend and backend
- Testing and debugging
- Demo preparation [file:42]

## Success Criteria

The MVP is considered successful if:
- users can input text material,
- the system can generate a quiz,
- users can complete the quiz,
- the system can show score, time, understanding level, insight, and recommendation,
- the main end-to-end demo works without critical errors.

## Risks

- Project complexity becomes too high
- Development time is limited
- Lack of test data
- Weak team coordination [file:42]

## Notes

This project intentionally uses a simple and explainable approach for the MVP. The main priority is a working end-to-end educational product that can be completed realistically within the capstone timeline. [file:42]
