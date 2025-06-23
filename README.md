# Co-Agent-Recruitment Hire — Agent-to-Agent AI Recruitment Platform


## Executive Summary

Co-Agent-Recruitment Hire automates the end-to-end recruitment workflow by orchestrating specialized AI agents to parse resumes, analyze job postings, and deliver data-driven match recommendations—all while safeguarding candidate privacy. Recruiters only ever see anonymized, non-PII summaries and high-level insights; our co-agents handle personal data with the utmost care.
Built on Google’s Agent Development Kit (ADK) and leveraging event-driven agent-to-agent communication, Co-Agent-Recruitment Hire provides a scalable, modular architecture for streamlined and privacy-first hiring operations.

## Motivation

Hiring teams face several challenges:
- Manual extraction of unstructured resume and job posting data.
- Lack of real-time, structured insights for candidate–job alignment.
- Scalability bottlenecks when handling high volumes of applications.

Co-Agent-Recruitment Hire addresses these pain points by automating parsing, matching, and session management to accelerate and scale the recruitment process.

## Solution Overview

| Pillar                         | Description                                                          |
|--------------------------------|----------------------------------------------------------------------|
| **ADK Framework**              | Defines and configures AI agents for discrete parsing and matching tasks. |
| **Agent-to-Agent (Co-Agent-Recruitment)**       | Agents coordinate via Pub/Sub events and sub-agent orchestration.    |
| **Core Agents**                | Resume Parser, Job Posting Parser, Matcher, and Orchestrator.       |
| **Dataflow & Scalability**     | Stateless agents with Pub/Sub messaging, containerized for elastic scaling. |

![alt text](image.png)

## Architecture Overview

```text
   +----------+          +-------------+        +------------+
   | Company  |          | Resume      |        | Job Posting|
   | & Candidate|---+--->| Parser      |        | Parser     |
   +----------+   |      +-------------+        +------------+
                  |              \                /
                  |               \              /
                  |           +----------------------+      +--------+
                  +---------->| Orchestrator Agent   |----->| Matcher|
                              +----------------------+      +--------+
                                                  |
                                                  v
                                          +---------------+
                                          | UI & Reporting|
                                          +---------------+
```

## Agent Development Kit (ADK) Framework

Agents and orchestration are defined using Google’s ADK, which provides session management, callbacks, and modular sub-agent support.【F:co_agent_recruitment/agent.py†L99-L123】

The `OrchestratorAgentRunner` wraps the orchestrator for programmatic use and integrates session handling and event publishing.【F:co_agent_recruitment/agent_engine.py†L31-L44】

## Agent-to-Agent Communication (Co-Agent-Recruitment)

Agents emit and consume events via Google Cloud Pub/Sub using helper tools for robust message handling. This decouples services and enables asynchronous coordination.【F:co_agent_recruitment/tools/pubsub.py†L146-L168】【F:co_agent_recruitment/tools/pubsub.py†L171-L183】

## Core Features

Outlined in the project [blueprint](docs/blueprint.md):【F:docs/blueprint.md†L5-L9】
- **Company Interface:** Structured submission of job descriptions.
- **Candidate Interface:** Structured submission of resumes.
- **AI Matchmaking:** Orchestrator agent compares and matches profiles using Gemini via ADK.
- **Match Display:** Ranked match recommendations for both companies and candidates.
- **Privacy-First Workflow:** Recruiters only ever see anonymized summaries and high-level insights; all PII remains securely managed by our cooperative agents.

## Dataflow & Scalability Management

1. **Ingestion:** Resumes and job postings are submitted via REST or events.
2. **Parsing:** Dedicated agents transform unstructured text into JSON structures.
3. **Orchestration:** A master agent routes parsed data, invokes matching, and enriches responses with session info.
4. **Matching:** Compatibility scores are generated through a matcher agent.
5. **Emission:** Results are published to Pub/Sub, stored, and surfaced in the UI.

All components are stateless and containerized for horizontal scaling. Pub/Sub ensures backpressure management and elasticity under load.

```mermaid
graph TB
    subgraph "Frontend / UI Layer"
        UI[Recruiter UI<br/>Next.js App]
        API[REST API<br/>FastAPI/Express]
    end

    subgraph "Orchestration Layer"
        ORCH[Orchestrator Agent<br/>ADK Framework]
        RUNNER[OrchestratorAgentRunner<br/>Session Management]
        SESS[InMemorySessionService<br/>Session Persistence]
    end

    subgraph "Core Agents"
        RESUME[Resume Parser Agent<br/>Pydantic + Gemini]
        JOB[Job Posting Agent<br/>Pydantic + Gemini]
        MATCH[Matcher Agent<br/>Compatibility Scoring]
    end

    subgraph "Communication Layer"
        PUBSUB[Google Cloud Pub/Sub<br/>Event Bus]
        EVENTS[Event Types:<br/>• ParseResumeEvent<br/>• ParseJobPostingEvent<br/>• CompatibilityScoreEvent]
    end

    subgraph "External Services"
        VERTEX[Google Vertex AI<br/>Gemini Models]
        FIRESTORE[Google Firestore<br/>Data Storage]
        FIREBASE[Firebase Auth<br/>User Management]
        GCFUNC[Google Cloud Functions<br/>Firestore Saver]
    end

    subgraph "Agentic Tools"
        EMIT[emit_event<br/>Pub/Sub Publisher]
        RECV[receive_events<br/>Pub/Sub Consumer]
        PARSE[parse_dirty_json<br/>JSON Parser]
        SAVE[save_to_firestore<br/>Data Persistence]
    end

    %% Frontend connections
    UI --> API
    API --> RUNNER

    %% Orchestration connections
    RUNNER --> ORCH
    ORCH --> SESS
    ORCH --> RESUME
    ORCH --> JOB
    ORCH --> MATCH

    %% Agent connections
    RESUME --> VERTEX
    JOB --> VERTEX
    MATCH --> VERTEX

    %% Event publishing
    RUNNER --> EMIT
    EMIT --> PUBSUB
    PUBSUB --> EVENTS

    %% Data flow
    PUBSUB --> GCFUNC
    GCFUNC --> FIRESTORE

    %% Tool usage
    RESUME --> PARSE
    JOB --> PARSE
    MATCH --> PARSE
    GCFUNC --> SAVE

    %% External services
    UI --> FIREBASE
    FIRESTORE --> VERTEX

    %% Styling
    classDef frontend fill:#e1f5fe
    classDef orchestration fill:#f3e5f5
    classDef agents fill:#e8f5e8
    classDef communication fill:#fff3e0
    classDef external fill:#fce4ec
    classDef tools fill:#f1f8e9

    class UI,API frontend
    class ORCH,RUNNER,SESS orchestration
    class RESUME,JOB,MATCH agents
    class PUBSUB,EVENTS communication
    class VERTEX,FIRESTORE,FIREBASE,GCFUNC external
    class EMIT,RECV,PARSE,SAVE tools
```


## Event Flow

```mermaid
sequenceDiagram
    participant UI as Recruiter UI
    participant API as REST API
    participant RUNNER as OrchestratorAgentRunner
    participant ORCH as Orchestrator Agent
    participant RESUME as Resume Parser Agent
    participant JOB as Job Posting Agent
    participant MATCH as Matcher Agent
    participant PUBSUB as Google Cloud Pub/Sub
    participant FIRESTORE as Firestore Database
    participant GCFUNC as Cloud Function

    Note over UI,GCFUNC: Candidate-Job Match Flow: End-to-End

    %% Step 1: Job Collection
    UI->>+API: POST /parse-job-posting
    Note over UI,API: Recruiter submits job description
    
    API->>+RUNNER: run_async(user_id, job_posting_text)
    RUNNER->>+ORCH: Route to job_posting_agent
    
    ORCH->>+JOB: analyze_job_posting(job_text)
    Note over JOB: Gemini model extracts:<br/>• Job title, requirements<br/>• Skills, location<br/>• Company details
    JOB-->>-ORCH: Structured job posting JSON
    
    ORCH-->>-RUNNER: Job posting data + session info
    RUNNER->>PUBSUB: emit_event("ParseJobPostingEvent", payload)
    PUBSUB->>GCFUNC: Event trigger
    GCFUNC->>FIRESTORE: Save to jobs/{jobId}
    
    RUNNER-->>-API: Job posting analysis response
    API-->>-UI: Display parsed job posting

    %% Step 2: Candidate Collection  
    UI->>+API: POST /parse-resume
    Note over UI,API: Recruiter submits candidate resume
    
    API->>+RUNNER: run_async(user_id, resume_text)
    RUNNER->>+ORCH: Route to parse_resume_agent
    
    ORCH->>+RESUME: parse_resume(resume_text)
    Note over RESUME: Gemini model extracts:<br/>• Personal details<br/>• Skills, experience<br/>• Education, certifications
    RESUME-->>-ORCH: Structured resume JSON
    
    ORCH-->>-RUNNER: Resume data + session info
    RUNNER->>PUBSUB: emit_event("ParseResumeEvent", payload)
    PUBSUB->>GCFUNC: Event trigger
    GCFUNC->>FIRESTORE: Save to candidates/{candidateId}
    
    RUNNER-->>-API: Resume parsing response
    API-->>-UI: Display parsed resume

    %% Step 3: Match Creation
    UI->>+API: POST /generate-match
    Note over UI,API: Request compatibility analysis<br/>with job_id & candidate_id
    
    API->>FIRESTORE: Query job and candidate data
    FIRESTORE-->>API: Retrieved structured data
    
    API->>+RUNNER: run_async(user_id, match_request)
    RUNNER->>+ORCH: Route to matcher_agent
    
    ORCH->>+MATCH: generate_compatibility_score(resume_data, job_data)
    Note over MATCH: Gemini analyzes:<br/>• Skill alignment<br/>• Experience relevance<br/>• Qualification match
    MATCH-->>-ORCH: Compatibility score (0-100) + analysis
    
    ORCH-->>-RUNNER: Match results + session info
    RUNNER->>PUBSUB: emit_event("CompatibilityScoreEvent", payload)
    PUBSUB->>GCFUNC: Event trigger
    GCFUNC->>FIRESTORE: Save to matches/{matchId}
    
    RUNNER-->>-API: Compatibility analysis response
    API-->>-UI: Display match score & insights

    %% Step 4: Future Enhancement (Interview Scheduling)
    Note over UI,GCFUNC: Future: Interview Agent Integration
    rect rgb(240, 240, 240)
        Note over FIRESTORE: When match score > threshold
        FIRESTORE->>GCFUNC: Trigger interview_agent
        Note over GCFUNC: Would integrate with:<br/>• Calendar APIs<br/>• Email notifications<br/>• Interview scheduling
    end
```

## Getting Started

1. Clone the repository and navigate into the project root.
2. Copy environment templates and set required variables:
   ```bash
   cp .env.example .env.local
   ```
3. Start dependencies (Pub/Sub emulator, Qdrant, etc.) via Docker Compose:
   ```bash
   docker-compose up -d
   ```
4. Launch the API server:
   ```bash
   uvicorn standalone_server:app --reload
   ```
5. Install dependencies and start the NextJS frontend:
   ```bash
   bun install
   bun run dev
   ```
6. Open the UI at http://localhost:9002 and follow on-screen prompts.

## Debugging

A VS Code launch configuration has been added at `.vscode/launch.json`:

- **Debug TypeScript File**: runs and debugs the currently open `.ts` file using `ts-node`.
- **Debug JavaScript File**: runs and debugs the currently open `.js` file with Node.

Make sure to install `ts-node` as a development dependency:
```bash
npm install --save-dev ts-node
```

Select the desired configuration from the Run and Debug panel in VS Code.

## Project Structure

```
. 
├── co_agent_recruitment/          # Core ADK agents & API
├── docs/                         # Design blueprints and diagrams
├── standalone_server.py          # Lightweight JSON-focused API
├── compose.yaml                  # Docker Compose for dependencies
└── README.md                     # This document
```

## Contributing

Contributions are welcome! Please open an issue or pull request, and refer to our [contributing guidelines](CONTRIBUTING.md).

## Firestore Query Tool

The Firestore Query Tool provides agentic access to candidate profiles, job descriptions, and related documents stored in Firestore. This tool enables the `matched_agent` to fetch and analyze comprehensive matching data in real-time.

### Features

- **Flexible Querying**: Query any Firestore collection with custom filters and projections
- **Complex Filters**: Support for equality, comparison, array-contains, and array-contains-any operations
- **Document Retrieval**: Get specific documents by ID with full metadata
- **Match Context**: Higher-level helper to retrieve complete candidate-job matching context
- **Retry Logic**: Built-in exponential backoff for robust error handling
- **Performance Optimized**: Support for projection, ordering, and limits to minimize data transfer

### Environment Variables

Configure the following environment variables for Firestore access:

```bash
# Required: Google Cloud credentials
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
# OR
FIREBASE_SERVICE_ACCOUNT_KEY='{"type":"service_account",...}'

# Required: Google Cloud project ID
PROJECT_ID=your-gcp-project-id
# OR  
GCP_PROJECT=your-gcp-project-id

# Optional: For local development with emulator
FIRESTORE_EMULATOR_HOST=localhost:8080
```

### Usage Examples

#### Basic Collection Query
```python
from co_agent_recruitment.tools.firestore_query import query_firestore

# Get all active candidates
candidates = query_firestore("candidates", {"status": "active"})

# Get specific candidate by ID
candidate = query_firestore("candidates", {"__name__": "candidate_123"})
```

#### Skills-Based Matching
```python
# Find candidates with specific skills
skilled_candidates = query_firestore(
    "candidates",
    {"skills": {"array-contains-any": ["python", "javascript"]}},
    projection=["name", "skills", "experience_years"],
    limit=10
)
```

#### Job Requirements Analysis
```python
# Get recent high-paying jobs
recent_jobs = query_firestore(
    "jobs",
    {
        "salary_range.min": {">=": 120000},
        "created_at": {">=": "2024-01-01"}
    },
    order_by="created_at",
    order_direction="DESCENDING"
)
```

#### Complete Match Analysis
```python
from co_agent_recruitment.tools.firestore_query import retrieve_match_context

# Get comprehensive match context
context = retrieve_match_context("match_789")
if context["success"]:
    candidate = context["candidate"]
    job = context["job"]
    feedback = context["interview_feedback"]
    # Perform detailed matching analysis...
```

### ADK Agent Integration

The tool is designed for use with Google's Agent Development Kit (ADK). Agents can call it using the standard tool interface:

```xml
<tool_call name="query_firestore">
{
  "collection": "candidates",
  "filter_dict": {"skills": {"array-contains": "python"}},
  "projection": ["name", "skills", "location"],
  "limit": 5
}
</tool_call>
```

### Local Development with Emulator

For local development and testing, use the Firestore emulator:

```bash
# Install Firebase CLI
npm install -g firebase-tools

# Start Firestore emulator
firebase emulators:start --only=firestore

# Set environment variable
export FIRESTORE_EMULATOR_HOST=localhost:8080

# Run your application or tests
python -m pytest co_agent_recruitment/tests/test_firestore_query.py
```

### Performance Best Practices

1. **Use Projections**: Limit fields to reduce data transfer
2. **Apply Filters**: Narrow results at the database level
3. **Set Limits**: Avoid large result sets
4. **Index Queries**: Ensure Firestore has appropriate composite indexes
5. **Monitor Costs**: Track query usage and optimize for efficiency

### Error Handling

The tool includes automatic retry logic with exponential backoff:
- Maximum 3 retry attempts
- Base delay of 0.5 seconds
- Maximum delay of 10 seconds
- Comprehensive error logging

### Testing

Unit tests use mocking for fast execution:
```bash
python -m pytest co_agent_recruitment/tests/test_firestore_query.py
```

Integration tests require the Firestore emulator:
```bash
export FIRESTORE_EMULATOR_HOST=localhost:8080
python -m pytest co_agent_recruitment/tests/test_firestore_query.py -k integration
```

## License

This project is released under the [MIT License](LICENSE).
