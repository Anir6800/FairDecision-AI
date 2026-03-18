# FairDecision AI

FairDecision AI is a research project on fairness-aware hiring evaluation.  
It combines resume parsing, job-description parsing, candidate scoring, bias auditing, counterfactual simulation, and natural-language explanations into one end-to-end system.

The core idea is simple:
- do not score only for fit
- also detect where non-merit factors may influence the decision
- make the final recommendation auditable, explainable, and testable

## Research Project Focus

This project studies how AI-assisted hiring systems can be made more transparent and fair.

The research problem is:
- traditional resume-screening systems optimize only for matching
- they often do not expose bias signals clearly
- they rarely show how a decision changes if a sensitive or contextual variable changes

FairDecision AI addresses that by adding:
- structured resume and JD extraction
- weighted candidate-job matching
- bias factor detection
- fairness scoring
- counterfactual simulation
- explanation generation for audit review

## Research Questions

This project is designed to explore questions such as:

1. Can a candidate-job scoring system be separated into fit signals and fairness signals?
2. Can location, college tier, and employment gaps be surfaced as auditable risk factors?
3. Can counterfactual simulation show whether the system reacts differently when only one sensitive/contextual factor changes?
4. Can a hiring recommendation be explained in plain English without hiding the underlying score logic?

## What Counts As Research Here

This is not only an app-building project. It is a research system because it includes:
- a defined problem statement
- explicit hypotheses about fairness and bias
- measurable outputs
- repeatable test cases
- demo scenarios
- evaluation criteria for whether the approach works

In practice, the research work is:
- define fairness-related variables
- formalize scoring and bias rules
- test the rules with controlled candidate profiles
- compare original and counterfactual outcomes
- observe whether the system exposes unfair influence clearly

## Research Methodology

The project follows this pipeline:

1. Data ingestion
   - upload resume and job description files
   - extract text from PDF or DOCX

2. Information extraction
   - parse resume into structured candidate data
   - parse job description into structured hiring requirements

3. Candidate evaluation
   - calculate skill score
   - calculate experience score
   - calculate education score
   - calculate aggregate match score

4. Bias audit
   - detect location-related influence
   - detect college-tier-related influence
   - detect employment-gap-related influence
   - calculate fairness score

5. Counterfactual analysis
   - change one variable at a time
   - compare score delta and fairness delta

6. Explanation generation
   - generate a readable audit explanation
   - cache results for repeat access

## System Features

### Backend
- FastAPI API server
- MongoDB storage for candidates, JDs, and evaluations
- LM Studio integration for structured extraction and explanation generation
- scoring engine
- bias detection engine
- counterfactual simulator
- explanation caching

### Frontend
- upload interface for resume and JD
- processing pipeline screen
- results dashboard with gauges and sub-scores
- bias audit panel
- counterfactual simulator
- explanation panel

## Tech Stack

- Frontend: React, Vite, Tailwind CSS, React Router
- Backend: FastAPI, Pydantic
- Database: MongoDB
- Local AI runtime: LM Studio
- File parsing: PyPDF2, python-docx
- Demo PDF generation: reportlab

## Project Structure

```text
FairDecision AI/
├── backend/
│   ├── app/
│   │   ├── routes/
│   │   ├── services/
│   │   ├── models/
│   │   └── main.py
│   ├── demo_data/
│   ├── test_*.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   ├── components/
│   │   └── pages/
│   └── package.json
└── README.md
```

## How To Run The Project

### 1. Start MongoDB

If you are using Docker:

```bash
docker-compose up -d
```

### 2. Start LM Studio

You must run LM Studio locally and load a model.

Suggested usage:
- start LM Studio server
- expose OpenAI-compatible API
- use the configured model for resume parsing, JD parsing, and explanation generation

Default backend expectation:
- URL: `http://localhost:1234/v1`

### 3. Run Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 4. Run Frontend

```bash
cd frontend
npm install
npm run dev
```

## How To Use The System

1. Open the frontend in the browser
2. Upload a resume and a job description
3. Wait for processing to complete
4. Review:
   - match score
   - fairness score
   - recommendation
   - sub-scores
5. Open the bias audit page
6. Run counterfactual simulations
7. Open the explanation page

## Demo Data

Demo PDFs can be generated from:

```bash
cd backend
python demo_data/generate_demo_data.py
```

Generated files:
- `resume_A.pdf`
- `resume_B.pdf`
- `resume_C.pdf`
- `JD_senior_dev.pdf`

## Testing

### Unit and Integration Tests

```bash
cd backend
python -m unittest backend/test_bias_detector.py backend/test_counterfactual.py backend/test_scorer.py backend/test_candidate_flow.py backend/test_resume_parser.py -v
```

### End-to-End Demo Test

```bash
cd backend
python test_e2e.py
```

This test:
- uploads `resume_B.pdf`
- uploads `JD_senior_dev.pdf`
- runs evaluation
- validates bias flags
- validates counterfactual effects

## How To Do The Research Properly

If this project is part of your academic or portfolio research, the right way to present it is:

1. Define the problem clearly
   - hiring AI often rewards fit without auditing fairness

2. Define the variables
   - skill match
   - experience
   - education
   - location
   - college tier
   - employment gaps

3. Explain your scoring rules
   - weighted fit score
   - bias factor influence
   - fairness score

4. Create controlled candidate profiles
   - same skills, different city
   - same skills, different college tier
   - same skills, with and without employment gap

5. Run counterfactual comparisons
   - observe score delta
   - observe fairness delta

6. Record outcomes
   - which variables changed the decision
   - whether the change was merit-based or fairness-sensitive

7. Discuss limitations
   - rule-based bias signals are simplified
   - LLM extraction quality depends on model behavior
   - real hiring fairness is broader than these three factors

## How To Succeed With This Project

To make this project strong as a research submission, portfolio project, or thesis prototype:

### Be clear about contribution
- this project is not a generic ATS
- its value is fairness auditing plus explainability plus counterfactual simulation

### Show repeatable evidence
- use demo PDFs
- run test suites
- show before/after counterfactual outputs
- keep results reproducible

### Be honest about limitations
- this is a prototype fairness evaluation framework
- not a legal compliance engine
- not a production hiring policy replacement

### Present both engineering and research value
- engineering: full-stack system, APIs, frontend, DB, local AI integration
- research: fairness metrics, interpretable scoring, auditable outputs

## Success Criteria

This project is successful if it can consistently do the following:

- parse resumes and JDs into structured data
- evaluate candidate-job fit with transparent sub-scores
- detect at least some non-merit bias indicators
- expose those indicators clearly in the UI
- show meaningful counterfactual changes
- produce an explanation that is readable and grounded in the evaluation
- pass repeatable tests and demo scenarios

## Limitations

Current limitations include:
- fairness is modeled with hand-designed rules, not learned causal inference
- gap detection and location normalization are simplified
- explanation quality depends on LM Studio model behavior
- college-tier mapping is heuristic
- bias scores are research signals, not formal proof of discrimination

## Future Work

Possible next steps:
- add more protected or contextual factors carefully and ethically
- improve city normalization and geography handling
- improve employment timeline modeling for overlapping jobs
- add benchmark datasets
- compare different weighting strategies
- add formal experiment tracking
- add browser automation tests for the full frontend flow

## Final Summary

FairDecision AI is a fairness-aware hiring research system.  
It tries to answer an important question:

Can we build an AI hiring workflow that not only scores candidates, but also shows where bias may influence the outcome, explains the reasoning, and lets us test what would happen if a sensitive factor changed?

That is the research value of this project.
