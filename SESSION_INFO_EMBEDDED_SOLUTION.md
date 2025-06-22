# Session Information Embedded in Orchestrator and Parsers

## ✅ Problem Solved

You requested to "just add session info in our orchestrator or parsers" - this has been successfully implemented!

## 📊 What's Now Included in All Outputs

### 1. Resume Parser Output Structure
```json
{
  "resume_data": { /* parsed resume data */ },
  "session_info": {
    "operation_type": "resume_parsing",
    "timestamp": "2025-06-18T20:17:04.742036",
    "processing_time": "completed",
    "model_used": "gemini-2.5-flash-preview-05-20"
  },
  "operation_status": "success"
}
```

### 2. Job Posting Parser Output Structure
```json
{
  "job_posting_data": { /* parsed job posting data */ },
  "session_info": {
    "operation_type": "job_posting_analysis", 
    "timestamp": "2025-06-18T20:17:08.352269",
    "processing_time": "completed",
    "model_used": "gemini-2.5-flash-preview-05-20"
  },
  "operation_status": "success"
}
```

### 3. Orchestrator Session State
The orchestrator now tracks detailed session information:
```json
{
  "session_id": "707e40da-8be1-4c0b-a50f-d32c552202fe",
  "user_id": "test_user", 
  "interaction_number": 1,
  "conversation_started": "2025-06-18T20:17:08.352658",
  "interaction_start_time": "2025-06-18T20:17:08.352666",
  "interaction_end_time": "2025-06-18T20:17:19.941958",
  "status": "completed"
}
```

## 🔧 Changes Made

### 1. Updated `parse_resume()` function
- Now returns structured output with `resume_data`, `session_info`, and `operation_status`
- Includes timestamp, operation type, model used, and processing status
- Handles errors with session information

### 2. Updated `analyze_job_posting()` function  
- Now returns structured output with `job_posting_data`, `session_info`, and `operation_status`
- Includes timestamp, operation type, model used, and processing status
- Handles validation errors and exceptions with session information

### 3. Enhanced Orchestrator Callbacks
- `orchestrator_before_callback()` now stores session info in state
- `orchestrator_after_callback()` updates session info with completion details
- Session state includes: session_id, user_id, interaction_number, timestamps

### 4. Updated Orchestrator Instructions
- Now explicitly instructs the agent to include session information in responses
- Provides example response format with session_info and orchestrator_info
- Ensures consistent session data inclusion

## 🧪 Test Results

Running `python test_session_in_output.py` shows:

**Direct Parser Calls:**
- ✅ Resume parser includes session_info with operation details
- ✅ Job posting parser includes session_info with operation details

**Orchestrator Calls:**
- ✅ Session state tracks interaction_number, timestamps, and status
- ✅ Session ID persists across interactions
- ✅ Current session info available in state

## 📋 Usage Examples

### Direct Function Usage
```python
from co_agent_recruitment.agent import parse_resume
from co_agent_recruitment.job_posting.agent import analyze_job_posting

# Resume parsing with session info
result = await parse_resume("John Doe resume text...")
print(f"Session Info: {result['session_info']}")
print(f"Status: {result['operation_status']}")

# Job posting analysis with session info  
result = await analyze_job_posting("Job posting text...")
print(f"Session Info: {result['session_info']}")
print(f"Status: {result['operation_status']}")
```

### Orchestrator Usage
```python
from google.adk.runners import InMemoryRunner

runner = InMemoryRunner(agent=root_agent, app_name="co_agent_recruitment")
session = await runner.session_service.create_session(app_name="co_agent_recruitment", user_id="user_123")

# After running the agent, check session state
updated_session = await runner.session_service.get_session(
    app_name="co_agent_recruitment",
    user_id="user_123", 
    session_id=session.id
)

session_info = updated_session.state.get('current_session_info', {})
print(f"Session ID: {session_info['session_id']}")
print(f"Interaction #: {session_info['interaction_number']}")
print(f"Status: {session_info['status']}")
```

## 🎯 Key Benefits

1. **Embedded Session Data**: All parser and orchestrator outputs now include session information
2. **Consistent Structure**: Standardized format across all functions
3. **Error Handling**: Session info included even in error responses
4. **Interaction Tracking**: Each interaction numbered and timestamped
5. **Status Monitoring**: Clear operation status in all responses

## 📁 Files Modified

1. **`co_agent_recruitment/agent.py`**:
   - Updated `parse_resume()` to include session_info
   - Enhanced orchestrator callbacks with session tracking
   - Updated orchestrator instructions for session inclusion

2. **`co_agent_recruitment/job_posting/agent.py`**:
   - Updated `analyze_job_posting()` to include session_info
   - Added error handling with session information

3. **`test_session_in_output.py`**: 
   - Comprehensive test showing session info in all outputs

Session information is now fully embedded in your orchestrator and parsers! 🎉