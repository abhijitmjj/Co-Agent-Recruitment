# Firestore Query Examples for Matched Agent

This document provides examples of how to use the Firestore query tools within the matched agent.

## Basic Document Retrieval

### Fetching a candidate by ID
```
<tool_call name="get_document_by_id">
{"collection": "candidates", "document_id": "candidate_123"}
</tool_call>
```

### Fetching a job by ID
```
<tool_call name="get_document_by_id">
{"collection": "jobs", "document_id": "job_456"}
</tool_call>
```

### Getting both candidate and job for matching
```
<tool_call name="retrieve_match_context">
{"candidate_id": "candidate_123", "job_id": "job_456"}
</tool_call>
```

## Filtering and Querying

### Find candidates with specific skills
```
<tool_call name="query_firestore">
{
  "collection": "candidates",
  "filter_dict": {"skills": {"array-contains": "Python"}},
  "projection": ["name", "skills", "experience", "location"]
}
</tool_call>
```

### Find candidates with multiple skill requirements
```
<tool_call name="query_firestore">
{
  "collection": "candidates", 
  "filter_dict": {"skills": {"array-contains-any": ["Python", "JavaScript", "React"]}},
  "projection": ["name", "skills", "experience"]
}
</tool_call>
```

### Find jobs within salary range
```
<tool_call name="query_firestore">
{
  "collection": "jobs",
  "filter_dict": {"salary": {">=": 50000, "<=": 100000}},
  "projection": ["title", "company", "salary", "requirements"],
  "limit": 10,
  "order_by": "salary",
  "order_direction": "desc"
}
</tool_call>
```

### Find active candidates interested in specific role types
```
<tool_call name="query_firestore">
{
  "collection": "candidates",
  "filter_dict": {
    "status": "interested",
    "preferred_roles": {"array-contains": "Software Engineer"}
  },
  "projection": ["name", "skills", "experience", "preferred_roles", "location"]
}
</tool_call>
```

## Complex Matching Scenarios

### Find candidates matching job requirements
For a job requiring Python and 3+ years experience:

```
<tool_call name="query_firestore">
{
  "collection": "candidates",
  "filter_dict": {
    "skills": {"array-contains": "Python"},
    "years_experience": {">=": 3},
    "status": "active"
  },
  "projection": ["name", "skills", "years_experience", "location", "salary_expectation"]
}
</tool_call>
```

### Find similar jobs for a candidate
For a candidate with specific skills and salary expectations:

```
<tool_call name="query_firestore">
{
  "collection": "jobs",
  "filter_dict": {
    "required_skills": {"array-contains-any": ["Python", "Django", "PostgreSQL"]},
    "salary": {">=": 75000},
    "location": "Remote"
  },
  "projection": ["title", "company", "required_skills", "salary", "location", "description"]
}
</tool_call>
```

## Creating Match Analysis

### Save match analysis to Firestore
```
<tool_call name="create_document">
{
  "collection": "matches",
  "document_id": "match_candidate123_job456",
  "data": {
    "candidate_id": "candidate_123",
    "job_id": "job_456", 
    "compatibility_score": 85,
    "skill_match_percentage": 90,
    "salary_compatibility": true,
    "location_match": "remote_ok",
    "analysis": {
      "strengths": ["Strong Python skills", "Relevant experience", "Salary aligned"],
      "concerns": ["Limited React experience", "No AWS certification"],
      "recommendation": "Strong match - recommend interview"
    },
    "analyzed_at": "2024-01-15T10:30:00Z",
    "analyzed_by": "matched_agent"
  }
}
</tool_call>
```

## Compound Queries for Advanced Matching

### Find best candidates for multiple jobs
```
<tool_call name="query_firestore">
{
  "collection": "candidates",
  "filter_dict": {
    "skills": {"array-contains-any": ["Python", "Java", "JavaScript"]},
    "years_experience": {">=": 2},
    "availability": "immediate"
  },
  "limit": 20,
  "order_by": "years_experience", 
  "order_direction": "desc"
}
</tool_call>
```

### Get past interview feedback for candidates
```
<tool_call name="query_firestore">
{
  "collection": "interviews",
  "filter_dict": {"candidate_id": "candidate_123"},
  "projection": ["interviewer", "feedback", "score", "date", "stage"]
}
</tool_call>
```

## Tips for Effective Matching

1. **Always retrieve both candidate and job data** before making compatibility assessments
2. **Use projection** to limit data transfer and focus on relevant fields
3. **Consider multiple factors**: skills, experience, salary, location, culture fit
4. **Save analysis results** to build a knowledge base for future matches
5. **Use array-contains-any** for flexible skill matching
6. **Order results** by relevance (experience, salary, etc.)
7. **Set reasonable limits** to avoid overwhelming responses