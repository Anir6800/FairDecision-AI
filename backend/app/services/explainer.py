import json
from typing import Any

from app.services.lm_client import LMStudioClient


EXPLAINER_SYSTEM_PROMPT = """You are a fair hiring consultant writing audit reports. You MUST respond with ONLY a valid JSON object with these exact keys: "summary", "positive_factors", "limiting_factors", "bias_assessment", "recommendation_reason". Each value is a string of 1-3 sentences. No markdown, no code fences, just JSON."""


def _extract_json_object(response_text: str) -> dict[str, Any]:
    response_text = response_text.strip()
    try:
        parsed = json.loads(response_text)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass

    start_index = response_text.find("{")
    if start_index == -1:
        raise ValueError("Model response did not contain a JSON object")

    depth = 0
    in_string = False
    escape = False

    for index in range(start_index, len(response_text)):
        char = response_text[index]
        if in_string:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == '"':
                in_string = False
            continue

        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                candidate = response_text[start_index : index + 1]
                parsed = json.loads(candidate)
                if isinstance(parsed, dict):
                    return parsed
                break

    raise ValueError("Unable to parse a JSON object from model response")


def _as_string(value: Any) -> str:
    return str(value).strip() if value is not None else ""


def _normalize_explanation(data: dict[str, Any]) -> dict[str, str]:
    return {
        "summary": _as_string(data.get("summary")),
        "positive_factors": _as_string(data.get("positive_factors")),
        "limiting_factors": _as_string(data.get("limiting_factors")),
        "bias_assessment": _as_string(data.get("bias_assessment")),
        "recommendation_reason": _as_string(data.get("recommendation_reason")),
    }


def _bias_summary(bias_flags: list[dict[str, Any]]) -> str:
    if not bias_flags:
        return "No bias flags identified."

    parts: list[str] = []
    for flag in bias_flags:
        if not isinstance(flag, dict):
            continue
        factor = _as_string(flag.get("factor")) or "unknown"
        severity = _as_string(flag.get("severity")) or "NONE"
        influence = _as_string(flag.get("influence_pct")) or "0"
        candidate_value = _as_string(flag.get("candidate_value")) or "unknown"
        parts.append(f"{factor}: {candidate_value}, severity {severity}, influence {influence}%")
    return "; ".join(parts) if parts else "No bias flags identified."


def _significant_bias_flags(bias_flags: list[dict[str, Any]]) -> list[dict[str, Any]]:
    significant: list[dict[str, Any]] = []
    for flag in bias_flags:
        if not isinstance(flag, dict):
            continue
        try:
            influence = float(flag.get("influence_pct", 0.0))
        except (TypeError, ValueError):
            influence = 0.0
        if influence > 0:
            significant.append(flag)
    return significant


def _factor_label(factor: str) -> str:
    mapping = {
        "location": "location",
        "college": "college background",
        "employment_gap": "employment gap history",
    }
    return mapping.get(factor, factor.replace("_", " "))


def _default_bias_assessment(bias_flags: list[dict[str, Any]]) -> str:
    significant = _significant_bias_flags(bias_flags)
    if not significant:
        return "No material bias factors were identified in the audit review."

    factors = [_factor_label(_as_string(flag.get("factor")) or "unknown") for flag in significant]
    factor_text = ", ".join(factors)
    return f"Potential bias signals were identified in {factor_text}. These factors should be reviewed as contextual risk signals rather than merit-based decision criteria."


def _ensure_bias_assessment_mentions_factors(explanation: dict[str, str], bias_flags: list[dict[str, Any]]) -> dict[str, str]:
    significant = _significant_bias_flags(bias_flags)
    if not significant:
        if not explanation["bias_assessment"]:
            explanation["bias_assessment"] = _default_bias_assessment(bias_flags)
        return explanation

    assessment = explanation["bias_assessment"].casefold()
    required_terms = [_factor_label(_as_string(flag.get("factor")) or "unknown").casefold() for flag in significant]
    if not explanation["bias_assessment"] or not all(term in assessment for term in required_terms):
        explanation["bias_assessment"] = _default_bias_assessment(bias_flags)
    return explanation


def _fill_empty_fields(explanation: dict[str, str], evaluation: dict[str, Any], candidate: dict[str, Any], jd: dict[str, Any]) -> dict[str, str]:
    if not explanation["summary"]:
        explanation["summary"] = (
            f"{_as_string(candidate.get('name')) or 'The candidate'} was evaluated for {_as_string(jd.get('title')) or 'the role'} "
            f"with an overall score of {_as_string(evaluation.get('overall_score'))}/100."
        )
    if not explanation["positive_factors"]:
        explanation["positive_factors"] = "The evaluation identified some strengths in the candidate profile, including parts of the education or experience record."
    if not explanation["limiting_factors"]:
        explanation["limiting_factors"] = "The main constraints came from the lower-scoring areas in the evaluation, especially where job alignment was weak."
    if not explanation["recommendation_reason"]:
        explanation["recommendation_reason"] = f"The recommendation reflects the overall score and the balance of strengths, gaps, and audit considerations for this role."
    if not explanation["bias_assessment"]:
        explanation["bias_assessment"] = _default_bias_assessment([])
    return explanation


def generate_explanation(evaluation, bias_flags, candidate, jd) -> dict:
    client = LMStudioClient()

    education = candidate.get("education", []) if isinstance(candidate, dict) else []
    primary_education = education[0] if education and isinstance(education[0], dict) else {}

    sub_scores = evaluation.get("sub_scores", {}) if isinstance(evaluation, dict) else {}
    aggregate = sub_scores.get("aggregate", {}) if isinstance(sub_scores, dict) else {}

    user_message = "\n".join(
        [
            f"Candidate: {_as_string(candidate.get('name'))}, Location: {_as_string(candidate.get('location'))}, Education: {_as_string(primary_education.get('degree'))} from {_as_string(primary_education.get('institution'))}",
            f"Job: {_as_string(jd.get('title'))}",
            f"Overall Score: {_as_string(evaluation.get('overall_score'))}/100",
            f"Sub-scores: Skills {_as_string(aggregate.get('skill_score'))}, Experience {_as_string(aggregate.get('experience_score'))}, Education {_as_string(aggregate.get('education_score'))}",
            f"Bias flags: {_bias_summary(bias_flags)}",
            f"Recommendation: {_as_string(evaluation.get('recommendation'))}",
        ]
    )

    response_text = client.chat(
        system_prompt=EXPLAINER_SYSTEM_PROMPT,
        user_message=user_message,
        temperature=0,
    )
    explanation = _normalize_explanation(_extract_json_object(response_text))
    explanation = _fill_empty_fields(explanation, evaluation, candidate, jd)
    return _ensure_bias_assessment_mentions_factors(explanation, bias_flags)


def is_valid_explanation(explanation: Any, bias_flags: list[dict[str, Any]]) -> bool:
    if not isinstance(explanation, dict):
        return False

    required_keys = {
        "summary",
        "positive_factors",
        "limiting_factors",
        "bias_assessment",
        "recommendation_reason",
    }
    if set(explanation.keys()) != required_keys:
        return False

    if not all(isinstance(explanation[key], str) and explanation[key].strip() for key in required_keys):
        return False

    significant = _significant_bias_flags(bias_flags)
    if not significant:
        return True

    assessment = explanation["bias_assessment"].casefold()
    required_terms = [_factor_label(_as_string(flag.get("factor")) or "unknown").casefold() for flag in significant]
    return all(term in assessment for term in required_terms)
