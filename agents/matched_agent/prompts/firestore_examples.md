# Matched Agent Examples

This document provides examples of how the matched agent uses the Firestore query tool to analyze candidate-job matches.

## Example 1: Fetching Candidate and Job Documents

```
<tool_call name="query_firestore">
{
  "collection": "candidates",
  "filter_dict": {"__name__": "candidate_123"}
}
</tool_call>
```

This fetches a specific candidate document by ID. The response includes:
- Complete candidate profile data
- Resume information (skills, experience, education)
- Contact details and preferences
- Application history and status

```
<tool_call name="query_firestore">
{
  "collection": "jobs", 
  "filter_dict": {"__name__": "job_456"}
}
</tool_call>
```

This fetches a specific job posting by ID, including:
- Job title, description, and requirements
- Company information and culture
- Salary range and benefits
- Application process and timeline

## Example 2: Skills-Based Matching

```
<tool_call name="query_firestore">
{
  "collection": "candidates",
  "filter_dict": {
    "skills": {"array-contains-any": ["python", "machine learning", "tensorflow"]},
    "status": "active"
  },
  "projection": ["skills", "experience_years", "education", "salary_expectation"],
  "limit": 10
}
</tool_call>
```

This query finds active candidates with relevant technical skills for a data science role, returning only the fields needed for skills analysis.

## Example 3: Experience Level Filtering

```
<tool_call name="query_firestore">
{
  "collection": "candidates",
  "filter_dict": {
    "experience_years": {">=": 3},
    "experience_years": {"<=": 7},
    "location": "San Francisco"
  },
  "order_by": "experience_years",
  "order_direction": "DESCENDING"
}
</tool_call>
```

This finds mid-level candidates in a specific location, ordered by experience level.

## Example 4: Company Culture Matching

```
<tool_call name="query_firestore">
{
  "collection": "jobs",
  "filter_dict": {
    "company_size": {">=": 100},
    "remote_work": true,
    "industry": "technology"
  },
  "projection": ["company_culture", "benefits", "work_environment", "team_structure"]
}
</tool_call>
```

This searches for jobs that match a candidate's preference for larger tech companies with remote work options.

## Example 5: Historical Interview Feedback

```
<tool_call name="query_firestore">
{
  "collection": "interview_feedback",
  "filter_dict": {
    "candidate_id": "candidate_123"
  },
  "projection": ["feedback_score", "technical_assessment", "communication_skills", "cultural_fit"],
  "order_by": "interview_date",
  "order_direction": "DESCENDING",
  "limit": 5
}
</tool_call>
```

This retrieves recent interview feedback for a candidate to understand their strengths and areas for improvement.

## Example 6: Salary Benchmarking

```
<tool_call name="query_firestore">
{
  "collection": "jobs",
  "filter_dict": {
    "job_title": {"==": "Senior Software Engineer"},
    "location": "San Francisco",
    "salary_range.min": {">=": 120000}
  },
  "projection": ["salary_range", "benefits_value", "equity_options"],
  "order_by": "salary_range.max",
  "order_direction": "DESCENDING"
}
</tool_call>
```

This helps analyze market rates for similar positions to assess salary compatibility.

## Example 7: Complete Match Analysis Workflow

```python
# Step 1: Get match context
match_context = retrieve_match_context("match_789")

# Step 2: Analyze skills alignment
candidate_skills = match_context["candidate"]["data"]["skills"]
required_skills = match_context["job"]["data"]["required_skills"]

# Step 3: Query for similar successful matches
<tool_call name="query_firestore">
{
  "collection": "matches",
  "filter_dict": {
    "status": "hired",
    "job_category": "software_engineering",
    "candidate_skills": {"array-contains-any": candidate_skills}
  },
  "projection": ["compatibility_score", "success_factors", "interview_feedback"],
  "limit": 10
}
</tool_call>

# Step 4: Generate comprehensive analysis
```

This workflow demonstrates how to build a complete matching analysis using multiple Firestore queries to gather context and benchmarking data.

## Best Practices

1. **Use projection** to limit data transfer and improve performance
2. **Apply filters** to narrow down results to relevant documents
3. **Leverage ordering** to get the most relevant or recent documents first
4. **Set limits** to avoid overwhelming responses, especially for large collections
5. **Handle missing data** gracefully in your analysis logic
6. **Use compound queries** for complex matching scenarios

## Error Handling

The query_firestore tool includes automatic retry logic and error handling. If a query fails:

1. The tool will retry up to 3 times with exponential backoff
2. Detailed error messages are logged for debugging
3. The agent should handle null or empty results gracefully
4. Consider fallback strategies for critical data retrieval

## Performance Considerations

1. **Index your queries** - ensure Firestore has composite indexes for complex filters
2. **Use pagination** for large result sets (implement cursor-based pagination)
3. **Cache frequent queries** where appropriate
4. **Monitor query costs** and optimize for efficiency
5. **Consider document size** and projection to minimize data transfer