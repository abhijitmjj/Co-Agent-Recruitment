# Example: Using the Firestore Query Tool

This example demonstrates how the Firestore Query Tool would be used in practice by the matched agent.

## Scenario: Analyzing a Candidate-Job Match

```python
from co_agent_recruitment.tools.firestore_query import (
    retrieve_match_context,
    query_firestore,
    create_document
)

# 1. Retrieve match context
match_context = retrieve_match_context("candidate_12345", "job_67890")
candidate = match_context["candidate"]
job = match_context["job"]

print(f"Analyzing match between {candidate['name']} and {job['title']} at {job['company']}")

# 2. Analyze skills compatibility
candidate_skills = set(candidate.get("skills", []))
required_skills = set(job.get("required_skills", []))
preferred_skills = set(job.get("preferred_skills", []))

skill_matches = candidate_skills & required_skills
skill_gaps = required_skills - candidate_skills
bonus_skills = candidate_skills & preferred_skills

print(f"Skills match: {len(skill_matches)}/{len(required_skills)} required skills")
print(f"Matching skills: {list(skill_matches)}")
print(f"Skill gaps: {list(skill_gaps)}")
print(f"Bonus skills: {list(bonus_skills)}")

# 3. Find similar candidates for comparison
similar_candidates = query_firestore(
    "candidates",
    {
        "skills": {"array-contains-any": list(required_skills)[:3]},  # Top 3 required skills
        "years_experience": {">=": max(0, candidate.get("years_experience", 0) - 2)},
        "status": "active"
    },
    projection=["name", "skills", "years_experience", "salary_expectation"],
    limit=5
)

print(f"Found {len(similar_candidates)} similar candidates for comparison")

# 4. Analyze salary compatibility
candidate_salary = candidate.get("salary_expectation", 0)
job_salary = job.get("salary", 0)
salary_diff_pct = abs(candidate_salary - job_salary) / max(job_salary, 1) * 100

# 5. Calculate compatibility score
skill_score = (len(skill_matches) / max(len(required_skills), 1)) * 100
experience_score = min(100, (candidate.get("years_experience", 0) / max(job.get("required_experience", 1), 1)) * 100)
salary_score = 90 if salary_diff_pct <= 20 else 60
overall_score = (skill_score * 0.4 + experience_score * 0.3 + salary_score * 0.3)

# 6. Save analysis results
analysis_result = {
    "candidate_id": candidate["id"],
    "job_id": job["id"],
    "overall_score": round(overall_score),
    "component_scores": {
        "skills": round(skill_score),
        "experience": round(experience_score),
        "salary": round(salary_score)
    },
    "analysis": {
        "skill_matches": list(skill_matches),
        "skill_gaps": list(skill_gaps),
        "bonus_skills": list(bonus_skills),
        "salary_difference_pct": round(salary_diff_pct, 1)
    },
    "recommendation": "Strong match" if overall_score >= 75 else "Moderate match" if overall_score >= 60 else "Weak match",
    "analyzed_at": "2024-01-15T10:30:00Z"
}

# Save to Firestore
analysis_id = create_document(
    "match_analysis",
    analysis_result,
    document_id=f"analysis_{candidate['id']}_{job['id']}"
)

print(f"Analysis saved with ID: {analysis_id}")
print(f"Overall compatibility score: {overall_score:.1f}/100")
print(f"Recommendation: {analysis_result['recommendation']}")
```

## Expected Output

```
Analyzing match between John Doe and Senior Python Developer at Tech Corp
Skills match: 4/5 required skills
Matching skills: ['Python', 'Django', 'PostgreSQL', 'Git']
Skill gaps: ['AWS']
Bonus skills: ['React', 'Docker']
Found 3 similar candidates for comparison
Analysis saved with ID: analysis_candidate_12345_job_67890
Overall compatibility score: 82.0/100
Recommendation: Strong match
```

## Integration with ADK Agents

In a real ADK environment, the matched agent would call these tools automatically:

```python
# Agent receives a message like:
# "Analyze the compatibility between candidate_12345 and job_67890"

# Agent uses tools via function calls:
<tool_call name="retrieve_match_context">
{"candidate_id": "candidate_12345", "job_id": "job_67890"}
</tool_call>

# Agent processes the data and makes additional queries:
<tool_call name="query_firestore">
{
  "collection": "candidates",
  "filter_dict": {"skills": {"array-contains-any": ["Python", "Django", "PostgreSQL"]}},
  "limit": 5
}
</tool_call>

# Agent saves the analysis:
<tool_call name="create_document">
{
  "collection": "match_analysis",
  "data": {"candidate_id": "...", "overall_score": 82, "..."},
  "document_id": "analysis_candidate_12345_job_67890"
}
</tool_call>
```

This seamless integration allows the matched agent to perform sophisticated analysis while maintaining clean separation of concerns.