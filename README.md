# FairDecision AI  
## A Fairness-Aware Explainable Hiring Intelligence System for Auditable Candidate Evaluation

**FairDecision AI** is an end-to-end research-driven hiring intelligence platform designed to evaluate candidates not only on job fit, but also on fairness sensitivity, bias exposure, and decision transparency.

Traditional hiring systems often optimize for relevance and ranking, but they rarely explain **why** a candidate was selected, **which non-merit variables influenced the result**, or **how the recommendation changes when contextual factors are altered**.

FairDecision AI addresses this gap by integrating:

- structured resume intelligence  
- job description understanding  
- weighted candidate-job scoring  
- fairness auditing  
- bias signal exposure  
- counterfactual simulation  
- explainable recommendation generation  

The system transforms candidate evaluation from a black-box scoring process into an **auditable decision framework**.

---

# Core Research Objective

The central research objective of FairDecision AI is:

> **To investigate whether AI-assisted hiring systems can separate merit-based candidate evaluation from fairness-sensitive contextual influence, while preserving interpretability and reproducibility.**

Rather than treating hiring as pure matching, the project introduces a dual-layer evaluation architecture:

## Layer 1: Merit Evaluation
Measures candidate suitability through objective hiring signals.

## Layer 2: Fairness Evaluation
Surfaces contextual variables that may introduce unintended bias.

This makes every recommendation testable rather than opaque.

---

# Research Problem Statement

Many automated hiring systems suffer from three critical limitations:

- They prioritize similarity matching without fairness auditing.
- They hide intermediate decision signals.
- They cannot explain score sensitivity when contextual variables change.

As a result, users often cannot determine:

- whether a lower score came from actual skill mismatch,
- whether non-merit factors influenced ranking,
- whether a decision remains stable under controlled variable changes.

FairDecision AI directly addresses these limitations by creating a structured fairness-aware evaluation pipeline.

---

# Research Hypothesis

The project is built around the following hypothesis:

> **Candidate-job fit signals and fairness-sensitive signals can be modeled independently, audited explicitly, and recombined into an explainable hiring recommendation.**

---

# Primary Research Questions

## 1. Fit vs Fairness Separation
Can candidate-job compatibility be decomposed into:

- merit-based fit signals  
- fairness-sensitive contextual signals  

without losing evaluation clarity?

## 2. Auditable Bias Detection
Can contextual factors such as:

- geographic location  
- college tier  
- employment gaps  

be surfaced as measurable audit indicators?

## 3. Counterfactual Stability
If only one contextual variable changes, does the recommendation remain stable?

## 4. Explainability
Can hiring recommendations be translated into plain-language explanations while remaining grounded in score logic?

---

# Why This Is a Research System (Not Just an App)

FairDecision AI qualifies as a research system because it contains:

- a formal problem definition  
- explicit measurable variables  
- testable scoring assumptions  
- controlled experiments  
- repeatable evaluation cases  
- interpretable outputs  

This moves the project beyond application engineering into experimental AI system design.

---

# Research Methodology

## Phase 1 — Data Ingestion

Input documents include:

- candidate resumes (PDF / DOCX)
- job descriptions (PDF / DOCX)

The system extracts raw textual content for downstream analysis.

## Phase 2 — Structured Information Extraction

The extraction layer converts unstructured documents into machine-readable fields.

### Resume Extraction
Produces:

- skills  
- education  
- work history  
- certifications  
- location  
- timeline gaps  

### Job Description Extraction
Produces:

- required skills  
- preferred skills  
- minimum experience  
- education expectations  
- role priority signals  

## Phase 3 — Candidate Scoring Engine

A weighted scoring engine computes merit-based compatibility.

### Sub-scores include:

- Skill Match Score  
- Experience Score  
- Education Score  
- Aggregate Match Score  

## Phase 4 — Bias Audit Engine

The fairness audit layer identifies contextual variables that may influence hiring outcomes.

### Current audit dimensions:

- Location Sensitivity  
- College Tier Sensitivity  
- Employment Gap Sensitivity  

## Phase 5 — Fairness Score Generation

A fairness score estimates how much contextual influence appears in the evaluation.

## Phase 6 — Counterfactual Simulation Engine

The simulator changes exactly one contextual variable while keeping all others constant.

Examples:

- same candidate, different city  
- same candidate, different college tier  
- same candidate, no employment gap  

Then it measures:

- score delta  
- fairness delta  
- recommendation shift  

## Phase 7 — Explanation Layer

The explanation engine converts evaluation results into human-readable audit language.

---

# System Architecture

## Backend Architecture

- FastAPI  
- MongoDB  
- LM Studio  
- scoring engine  
- fairness engine  
- counterfactual engine  
- cache layer  

## Frontend Architecture

- React  
- Vite  
- Tailwind CSS  
- React Router  

### Frontend Modules

- Upload Interface  
- Processing Pipeline View  
- Results Dashboard  
- Bias Audit Panel  
- Counterfactual Simulator  
- Explanation Panel  

---

# Technical Stack Summary

| Layer | Technology |
|------|------------|
| Frontend | React, Vite, Tailwind CSS |
| Backend | FastAPI, Pydantic |
| Database | MongoDB |
| AI Runtime | LM Studio |
| Parsing | PyPDF2, python-docx |
| Demo Generation | reportlab |

---

# Evaluation Framework

## Controlled Candidate Profiles

Create profiles where only one variable changes:

- same skills, different city  
- same skills, different college  
- same skills, employment gap variation  

Then record:

- score changes  
- fairness changes  
- recommendation stability  

---

# Success Metrics

## Functional Success

- parse documents correctly  
- generate stable scores  
- produce explanations  

## Research Success

- detect fairness-sensitive variables  
- expose decision instability  
- reproduce identical results under repeated runs  

---

# Limitations

Current limitations include:

- rule-based fairness assumptions  
- heuristic college mapping  
- simplified timeline interpretation  
- non-causal bias inference  

Therefore:

> This system is a research prototype for fairness exposure, not a legal compliance engine.

---

# Future Work

- Add causal fairness methods  
- Benchmark against public hiring datasets  
- Introduce experiment tracking  
- Compare multiple fairness weighting models  
- Add protected-variable stress testing  
- Evaluate explanation consistency across models  

---

# Final Summary

> FairDecision AI demonstrates that hiring intelligence can move beyond ranking toward auditable reasoning.

It asks a critical research question:

> Can an AI hiring system show not only who matches a role, but also where fairness-sensitive variables may alter that decision?

That is the scientific contribution of this work.
