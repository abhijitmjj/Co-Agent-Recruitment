# Candidate-Job Match Analysis Prompts

This document provides detailed prompts and examples for the matched agent to perform comprehensive candidate-job matching analysis.

## Core Analysis Framework

When analyzing a candidate-job match, consider these key dimensions:

### 1. Technical Skills Assessment
- **Hard Skills**: Programming languages, frameworks, tools
- **Soft Skills**: Communication, leadership, problem-solving
- **Domain Knowledge**: Industry-specific expertise
- **Certifications**: Professional credentials and training

### 2. Experience Evaluation
- **Years of Experience**: Total and relevant experience
- **Role Progression**: Career advancement and growth
- **Project Complexity**: Scale and impact of previous work
- **Team Leadership**: Management and mentoring experience

### 3. Cultural Fit Analysis
- **Company Values**: Alignment with organizational culture
- **Work Style**: Remote vs. office, collaboration preferences
- **Team Dynamics**: Compatibility with existing team members
- **Growth Mindset**: Learning attitude and adaptability

### 4. Compensation Compatibility
- **Salary Expectations**: Candidate's financial requirements
- **Market Rate**: Industry standard for the role
- **Benefits Package**: Total compensation beyond base salary
- **Negotiation Flexibility**: Room for adjustment

## Sample Analysis Prompts

### Comprehensive Match Analysis

```
Given the candidate profile and job requirements, perform a comprehensive matching analysis:

1. First, retrieve the candidate document:
   <tool_call name="query_firestore">
   {"collection": "candidates", "filter_dict": {"__name__": "{candidate_id}"}}
   </tool_call>

2. Then, retrieve the job posting:
   <tool_call name="query_firestore">
   {"collection": "jobs", "filter_dict": {"__name__": "{job_id}"}}
   </tool_call>

3. Analyze skills alignment:
   - Compare candidate skills with job requirements
   - Identify matching skills and skill gaps
   - Assess transferable skills and learning potential
   - Rate technical competency fit (0-100)

4. Evaluate experience compatibility:
   - Compare years of experience with job requirements
   - Assess relevance of previous roles and projects
   - Consider career progression and growth trajectory
   - Rate experience fit (0-100)

5. Assess cultural fit:
   - Compare candidate values with company culture
   - Evaluate work style preferences
   - Consider team dynamics and collaboration style
   - Rate cultural alignment (0-100)

6. Analyze compensation compatibility:
   - Compare salary expectations with job offering
   - Consider total compensation package
   - Assess negotiation potential and flexibility
   - Rate compensation fit (0-100)

7. Generate overall compatibility score (0-100) and detailed rationale
```

### Skills-Focused Analysis

```
Perform a detailed skills analysis for this candidate-job match:

1. Retrieve candidate skills data:
   <tool_call name="query_firestore">
   {
     "collection": "candidates", 
     "filter_dict": {"__name__": "{candidate_id}"},
     "projection": ["skills", "certifications", "education", "projects"]
   }
   </tool_call>

2. Get job requirements:
   <tool_call name="query_firestore">
   {
     "collection": "jobs",
     "filter_dict": {"__name__": "{job_id}"},
     "projection": ["required_skills", "nice_to_have_skills", "technical_requirements"]
   }
   </tool_call>

3. Analyze skill alignment:
   - Calculate percentage of required skills possessed
   - Identify critical missing skills
   - Assess learning curve for missing skills
   - Evaluate skill proficiency levels
   - Consider skill relevance and recency

4. Provide skill development recommendations:
   - Suggest training programs for skill gaps
   - Recommend certification paths
   - Identify mentorship opportunities
   - Estimate time to proficiency
```

### Experience-Based Matching

```
Analyze experience compatibility between candidate and job requirements:

1. Get candidate experience data:
   <tool_call name="query_firestore">
   {
     "collection": "candidates",
     "filter_dict": {"__name__": "{candidate_id}"},
     "projection": ["work_history", "projects", "achievements", "leadership_experience"]
   }
   </tool_call>

2. Retrieve job experience requirements:
   <tool_call name="query_firestore">
   {
     "collection": "jobs",
     "filter_dict": {"__name__": "{job_id}"},
     "projection": ["experience_requirements", "seniority_level", "leadership_requirements"]
   }
   </tool_call>

3. Compare and analyze:
   - Years of relevant experience vs. requirements
   - Industry experience alignment
   - Project complexity and scale
   - Leadership and team management experience
   - Career progression and growth pattern

4. Assess growth potential:
   - Readiness for increased responsibility
   - Learning agility and adaptability
   - Mentoring and development needs
```

### Cultural Fit Assessment

```
Evaluate cultural compatibility between candidate and company:

1. Get candidate cultural preferences:
   <tool_call name="query_firestore">
   {
     "collection": "candidates",
     "filter_dict": {"__name__": "{candidate_id}"},
     "projection": ["work_preferences", "values", "personality_traits", "communication_style"]
   }
   </tool_call>

2. Retrieve company culture information:
   <tool_call name="query_firestore">
   {
     "collection": "companies",
     "filter_dict": {"__name__": "{company_id}"},
     "projection": ["culture_values", "work_environment", "team_structure", "communication_style"]
   }
   </tool_call>

3. Analyze cultural alignment:
   - Values compatibility assessment
   - Work style preferences match
   - Communication style alignment
   - Team collaboration preferences
   - Company size and structure fit

4. Identify potential cultural challenges:
   - Areas of misalignment
   - Adaptation requirements
   - Integration strategies
   - Long-term cultural fit sustainability
```

### Benchmarking and Market Analysis

```
Perform market benchmarking for this candidate-job match:

1. Find similar successful matches:
   <tool_call name="query_firestore">
   {
     "collection": "matches",
     "filter_dict": {
       "status": "hired",
       "job_category": "{job_category}",
       "candidate_experience_level": "{experience_level}"
     },
     "projection": ["compatibility_score", "success_factors", "challenges"],
     "limit": 10
   }
   </tool_call>

2. Analyze salary benchmarks:
   <tool_call name="query_firestore">
   {
     "collection": "jobs",
     "filter_dict": {
       "title": "{job_title}",
       "location": "{location}",
       "company_size": "{company_size_range}"
     },
     "projection": ["salary_range", "benefits", "equity"],
     "order_by": "salary_range.max",
     "limit": 20
   }
   </tool_call>

3. Compare with market standards:
   - Salary competitiveness analysis
   - Benefits package comparison
   - Success factor identification
   - Risk assessment based on similar matches
```

## Decision-Making Framework

### Scoring Methodology

1. **Technical Skills (30%)**
   - Required skills coverage: 0-100
   - Skill proficiency depth: 0-100
   - Learning potential: 0-100

2. **Experience (25%)**
   - Years of experience fit: 0-100
   - Relevant experience quality: 0-100
   - Leadership experience: 0-100

3. **Cultural Fit (25%)**
   - Values alignment: 0-100
   - Work style compatibility: 0-100
   - Team integration potential: 0-100

4. **Compensation (20%)**
   - Salary expectation match: 0-100
   - Benefits satisfaction: 0-100
   - Long-term retention potential: 0-100

### Recommendation Thresholds

- **Excellent Match (85-100)**: Strongly recommend, high success probability
- **Good Match (70-84)**: Recommend with minor reservations
- **Fair Match (55-69)**: Consider with significant development plan
- **Poor Match (40-54)**: Not recommended, major gaps
- **No Match (0-39)**: Do not proceed, fundamental incompatibility

### Risk Assessment

Consider these risk factors in your analysis:
- **Skill Gap Risk**: Time and cost to bridge missing skills
- **Experience Gap Risk**: Ability to handle job complexity
- **Cultural Risk**: Likelihood of cultural misalignment
- **Retention Risk**: Long-term job satisfaction and retention
- **Performance Risk**: Ability to meet job expectations

## Output Format

Always structure your analysis with:

1. **Executive Summary**: Brief compatibility assessment
2. **Detailed Scores**: Numerical ratings for each dimension
3. **Strengths**: Key positive factors supporting the match
4. **Concerns**: Potential issues or gaps to address
5. **Recommendations**: Specific next steps for each stakeholder
6. **Risk Mitigation**: Strategies to address identified risks
7. **Timeline**: Suggested evaluation and onboarding timeline