# Vertex AI Agent Engine Deployment Guide

This guide explains how to deploy the Co-Agent Recruitment system to Google Cloud's Vertex AI Agent Engine for production use.

## Overview

The Co-Agent Recruitment system can be deployed to Vertex AI Agent Engine, which provides:

- Scalable, managed infrastructure for AI agents
- Built-in session management
- Event streaming capabilities
- Production-ready API endpoints
- Automatic scaling and load balancing

## Prerequisites

### 1. Google Cloud Setup

- Google Cloud Project with billing enabled
- Vertex AI API enabled
- Agent Engine API enabled
- Cloud Storage bucket for staging artifacts
- Appropriate IAM permissions

### 2. Environment Configuration

Create a `.env` file with the following variables:

```bash
# Use custom variable names to avoid conflicts with Vertex AI Agent Engine
PROJECT_ID=your-google-cloud-project-id
BUCKET_NAME=your-staging-bucket-name
BUCKET_LOCATION=us-central1
MODEL_NAME=gemini-1.5-pro
FIRESTORE_DATABASE_ID=(default)

# IMPORTANT: Avoid these reserved environment variables:
# - GOOGLE_CLOUD_PROJECT
# - GOOGLE_CLOUD_QUOTA_PROJECT
# - GOOGLE_CLOUD_LOCATION
# - PORT
# - K_SERVICE
# - K_REVISION
# - K_CONFIGURATION
# - GOOGLE_APPLICATION_CREDENTIALS
# - Any variables with GOOGLE_CLOUD_AGENT_ENGINE prefix
```

### 3. Python Dependencies

Install required packages:

```bash
pip install google-cloud-aiplatform[adk,agent_engines]
pip install google-adk>=1.2.1
pip install google-genai>=1.20.0
```

## Deployment Process

### Option 1: Full Deployment with Testing

```python
import asyncio
from co_agent_recruitment.vertexAI_engine import deploy_co_agent_recruitment

async def main():
    result = await deploy_co_agent_recruitment()
    if result["success"]:
        print(f"Deployment successful! Resource: {result['resource_name']}")
    else:
        print(f"Deployment failed: {result['error']}")

asyncio.run(main())
```

### Option 2: Quick Deployment

```python
import asyncio
from co_agent_recruitment.vertexAI_engine import quick_deploy

async def main():
    remote_app = await quick_deploy()
    if remote_app:
        print(f"Quick deployment successful: {remote_app.resource_name}")

asyncio.run(main())
```

### Option 3: Command Line Deployment

```bash
# Full deployment with testing
python co_agent_recruitment/vertexAI_engine.py

# Quick deployment
python co_agent_recruitment/vertexAI_engine.py quick

# Get client configuration
python co_agent_recruitment/vertexAI_engine.py client
```

## Testing the Deployment

### Local Testing

Before deploying to Vertex AI, test the agent locally:

```bash
python co_agent_recruitment/test_deployment.py
```

This will run:

- Agent creation tests
- Local functionality tests
- Environment configuration checks

### Production Testing

After deployment, test the remote agent:

```python
from co_agent_recruitment.vertexAI_engine import VertexAIAgentEngineDeployer

async def test_remote():
    deployer = VertexAIAgentEngineDeployer()
    # Deploy agent
    remote_app = await deployer.deploy_agent()
    # Test deployed agent
    results = await deployer.test_deployed_agent(remote_app)
    print(results)
```

## Using the Deployed Agent

### API Endpoints

Once deployed, your agent will be available via REST API endpoints:

```
Base URL: https://{location}-aiplatform.googleapis.com/v1/projects/{project}/locations/{location}/reasoningEngines/{resource_id}

Endpoints:
- POST :createSession - Create a new session
- POST :streamQuery - Send queries and get streaming responses
- GET :listSessions - List all sessions
- DELETE :deleteSession - Delete a session
```

### Example API Usage

```python
import requests
from google.auth import default

# Get credentials
credentials, project = default()

# Create session
session_response = requests.post(
    f"https://us-central1-aiplatform.googleapis.com/v1/projects/{project}/locations/us-central1/reasoningEngines/{resource_id}:createSession",
    headers={"Authorization": f"Bearer {credentials.token}"},
    json={"user_id": "user123"}
)

session_id = session_response.json()["session"]["id"]

# Send query
query_response = requests.post(
    f"https://us-central1-aiplatform.googleapis.com/v1/projects/{project}/locations/us-central1/reasoningEngines/{resource_id}:streamQuery",
    headers={"Authorization": f"Bearer {credentials.token}"},
    json={
        "user_id": "user123",
        "session_id": session_id,
        "message": "Parse this resume: [resume content]"
    }
)
```

### Python Client Example

```python
from google.cloud import aiplatform
from google.auth import default

# Initialize client
credentials, project = default()
client = aiplatform.gapic.ReasoningEngineServiceClient(credentials=credentials)

# Create session
session = client.create_session(
    parent=f"projects/{project}/locations/us-central1/reasoningEngines/{resource_id}",
    session={"user_id": "user123"}
)

# Stream query
for response in client.stream_query(
    reasoning_engine=f"projects/{project}/locations/us-central1/reasoningEngines/{resource_id}",
    user_id="user123",
    session_id=session.id,
    message="Analyze this job posting: [job content]"
):
    print(response)
```

## Agent Capabilities

The deployed agent provides the following functionality:

### 1. Resume Parsing

- Extract personal information (name, contact details)
- Parse work experience and employment history
- Identify skills and competencies
- Extract education background
- Return structured JSON data

### 2. Job Posting Analysis

- Extract job requirements and qualifications
- Identify key responsibilities
- Parse company information
- Analyze required skills and experience levels
- Return structured job data

### 3. Candidate Matching

- Calculate compatibility scores between resumes and job postings
- Provide detailed matching insights
- Identify skill gaps and strengths
- Generate recommendation reports

### 4. Session Management

- Maintain conversation context across interactions
- Store session state in Firestore
- Support multiple concurrent users
- Automatic session cleanup

## Architecture

### Components

```
┌─────────────────────────────────────────┐
│           Vertex AI Agent Engine        │
├─────────────────────────────────────────┤
│  ┌─────────────────────────────────────┐ │
│  │     Orchestrator Agent              │ │
│  │  ┌─────────────────────────────────┐ │ │
│  │  │  Resume Parser Sub-Agent        │ │ │
│  │  └─────────────────────────────────┘ │ │
│  │  ┌─────────────────────────────────┐ │ │
│  │  │  Job Posting Sub-Agent          │ │ │
│  │  └─────────────────────────────────┘ │ │
│  │  ┌─────────────────────────────────┐ │ │
│  │  │  Matcher Sub-Agent              │ │ │
│  │  └─────────────────────────────────┘ │ │
│  └─────────────────────────────────────┘ │
├─────────────────────────────────────────┤
│           Session Management            │
│         (Firestore Backend)             │
├─────────────────────────────────────────┤
│            Event Publishing             │
│          (Pub/Sub Integration)          │
└─────────────────────────────────────────┘
```

### Data Flow

1. Client sends request to Agent Engine API
2. Orchestrator agent receives and routes the request
3. Appropriate sub-agent processes the content
4. Results are aggregated and returned
5. Session state is persisted to Firestore
6. Events are published to Pub/Sub (if configured)

## Configuration Options

### Deployment Configuration

```python
deployer = VertexAIAgentEngineDeployer(
    project_id="your-project",
    location="us-central1",  # or your preferred region
    staging_bucket="your-bucket"
)

# Custom requirements
custom_requirements = [
    "google-cloud-aiplatform[adk,agent_engines]",
    "your-custom-package>=1.0.0"
]

# Deploy with custom settings
remote_app = await deployer.deploy_agent(
    display_name="Custom Agent Name",
    description="Custom description",
    requirements=custom_requirements
)
```

### Agent Configuration

```python
# Customize the agent before deployment
agent = deployer.create_deployment_agent()
agent.instruction = "Custom instructions for your use case"
agent.model = "gemini-1.5-pro"  # or your preferred model

# Deploy customized agent
remote_app = await deployer.deploy_agent(agent)
```

## Monitoring and Logging

### Cloud Logging

Agent logs are automatically sent to Cloud Logging:

```bash
# View logs in Cloud Console or via CLI
gcloud logging read "resource.type=vertex_ai_reasoning_engine"
```

### Metrics and Monitoring

Monitor your deployed agent using Cloud Monitoring:

- Request latency
- Error rates
- Session counts
- Resource utilization

### Tracing

Enable distributed tracing for debugging:

```python
app = reasoning_engines.AdkApp(
    agent=agent,
    enable_tracing=True,  # Enables Cloud Trace integration
)
```

## Troubleshooting

### Common Issues

1. **Deployment Fails with Permission Error**
   - Ensure your service account has the required IAM roles:
     - Vertex AI User
     - Storage Object Admin
     - Firestore User

2. **Agent Returns Empty Responses**
   - Check agent instructions and model configuration
   - Verify sub-agents are properly configured
   - Review Cloud Logging for error messages

3. **Session Management Issues**
   - Verify Firestore database is accessible
   - Check FIRESTORE_DATABASE_ID environment variable
   - Ensure proper authentication

4. **High Latency**
   - Consider using a different region closer to your users
   - Optimize agent instructions for efficiency
   - Review model selection (some models are faster than others)

### Debug Mode

Enable debug logging for troubleshooting:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Deploy with debug information
result = await deploy_co_agent_recruitment()
```

## Cost Optimization

### Tips for Reducing Costs

1. **Choose the right model**: Balance performance vs. cost
2. **Optimize instructions**: Shorter, clearer instructions reduce token usage
3. **Use session management**: Avoid redundant context in each request
4. **Monitor usage**: Set up billing alerts and quotas
5. **Clean up unused deployments**: Delete test deployments when done

### Estimated Costs

- Agent Engine hosting: ~$0.10-0.50 per hour (depending on usage)
- Model inference: Variable based on token usage
- Storage: ~$0.02 per GB per month for staging artifacts
- Firestore: ~$0.18 per 100K operations

## Security Considerations

### Authentication

- Use service account keys or Application Default Credentials
- Implement proper IAM roles and permissions
- Consider using Workload Identity for GKE deployments

### Data Privacy

- All data is processed within your Google Cloud project
- Session data is stored in your Firestore database
- No data is shared with external services

### Network Security

- Agent Engine endpoints use HTTPS encryption
- Consider VPC Service Controls for additional isolation
- Implement API rate limiting if needed

## Support and Resources

### Documentation

- [Vertex AI Agent Engine Documentation](https://cloud.google.com/vertex-ai/docs/agent-engine)
- [Google ADK Documentation](https://github.com/google/adk-python)
- [Vertex AI Python SDK](https://cloud.google.com/python/docs/reference/aiplatform/latest)

### Getting Help

- Google Cloud Support (for paid support plans)
- Stack Overflow with tags: `google-cloud-vertex-ai`, `google-adk`
- GitHub Issues for ADK-specific problems

### Best Practices

- Test locally before deploying to production
- Use version control for agent configurations
- Implement proper error handling and retry logic
- Monitor performance and costs regularly
- Keep dependencies up to date


## ✅ Deployment Status: RESOLVED

### Issues Fixed

1. **Event Loop Errors** ✅ **RESOLVED**
   - **Issue**: "Event loop is closed" errors during Firestore session operations
   - **Root Cause**: Vertex AI Agent Engine has its own session management and doesn't need Firestore
   - **Solution**: Created separate `vertex_orchestrator_agent` without Firestore dependencies

2. **Agent Parent-Child Conflicts** ✅ **RESOLVED**
   - **Issue**: Sub-agents already had parent agents and couldn't be reused
   - **Root Cause**: Attempting to reuse existing agent instances with different parents
   - **Solution**: Create new instances of sub-agents specifically for Vertex AI deployment

3. **Async/Sync Compatibility** ✅ **RESOLVED**
   - **Issue**: Mixed async/sync operations causing runtime errors
   - **Root Cause**: Vertex AI deployment environment handles sessions differently
   - **Solution**: Simplified testing approach using native Vertex AI session management

### Architecture Summary

The Co-Agent Recruitment system now has a **dual architecture**:

- **Local Development**: Uses `root_agent` with Firestore session management
- **Vertex AI Deployment**: Uses `vertex_orchestrator_agent` with native Vertex AI sessions

### Successful Test Results

```
✅ Local testing completed successfully!
✅ Resume parsing: 7 events processed
✅ Job posting analysis: 17 events processed
✅ No Firestore session errors
✅ No event loop conflicts
```

### Key Files

- [`vertex_agent.py`](vertex_agent.py) - Vertex AI optimized agent without Firestore
- [`vertexAI_engine.py`](vertexAI_engine.py) - Updated deployment engine
- [`deploy.py`](deploy.py) - CLI deployment script with test modes

The system is now ready for production deployment to Vertex AI Agent Engine! 🚀
