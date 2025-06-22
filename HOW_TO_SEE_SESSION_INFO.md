# How to See Session Information in Co-Agent-Recruitment

## Problem Solved ✅

You mentioned "i am not seeing session information at all" - this has been fixed! Here's exactly how to see session information in your application.

## 1. Quick Demo - Session Information is Now Visible

Run this command to see session information in action:

```bash
python demo_session_info.py
```

**Output shows:**
- Session ID: `80912b38-eac8-4146-9f2e-ecd5101e7d10`
- Interaction Count: `1` → `2` (increments with each interaction)
- Conversation Started: `2025-06-18T20:09:34.247589`
- Session State Keys: `['conversation_started', 'interaction_count', 'last_interaction_start', 'result', 'last_interaction_end', 'last_interaction_completed', 'last_operation_status']`

## 2. Using Session Utils in Your Code

Import and use the session utilities:

```python
from session_utils import get_session_info, list_user_sessions, print_session_summary

# Get detailed session information
session_info = await get_session_info("user_123", "session_id_here")
print(f"Interactions: {session_info['interaction_count']}")
print(f"Started: {session_info['conversation_started']}")

# List all sessions for a user
user_sessions = await list_user_sessions("user_123")
print(f"Total sessions: {user_sessions['total_sessions']}")

# Print formatted session summary
await print_session_summary("user_123", "session_id_here")
```

## 3. Integration with Your Application

### Option A: Using InMemoryRunner (Recommended)

```python
from co_agent_recruitment.agent import root_agent
from google.adk.runners import InMemoryRunner
from google.adk.agents.run_config import RunConfig
from google.genai import types

# Create runner
runner = InMemoryRunner(agent=root_agent, app_name="co_agent_recruitment")

# Create session
session = await runner.session_service.create_session(
    app_name="co_agent_recruitment", 
    user_id="your_user_id"
)

print(f"📋 Session Created: {session.id}")

# Run agent interaction
content = types.Content(
    role="user", 
    parts=[types.Part.from_text(text="Your user input here")]
)

async for event in runner.run_async(
    user_id="your_user_id",
    session_id=session.id,  # Same session for continuity
    new_message=content,
    run_config=RunConfig(save_input_blobs_as_artifacts=False),
):
    # Process events...
    pass

# Check session state after interaction
updated_session = await runner.session_service.get_session(
    app_name="co_agent_recruitment",
    user_id="your_user_id",
    session_id=session.id
)

print(f"📊 Session State:")
print(f"   Interactions: {updated_session.state.get('interaction_count', 0)}")
print(f"   Started: {updated_session.state.get('conversation_started')}")
print(f"   Status: {updated_session.state.get('last_operation_status')}")
```

### Option B: Using Session Utils Helper

```python
from session_utils import SessionManager

# Create session manager
session_mgr = SessionManager()

# Create session
session = await session_mgr.create_session("your_user_id")

# Get session info anytime
info = await session_mgr.get_session_info("your_user_id", session.id)
print(f"Session has {info['interaction_count']} interactions")

# Print formatted summary
await session_mgr.print_session_summary("your_user_id", session.id)
```

## 4. What Session Information You Can See

The session now tracks:

| Field | Description | Example |
|-------|-------------|---------|
| `session_id` | Unique session identifier | `80912b38-eac8-4146-9f2e-ecd5101e7d10` |
| `user_id` | User identifier | `demo_user` |
| `interaction_count` | Number of interactions | `2` |
| `conversation_started` | When conversation began | `2025-06-18T20:09:34.247589` |
| `last_interaction_start` | Last interaction start time | `2025-06-18T20:09:59.123456` |
| `last_interaction_end` | Last interaction end time | `2025-06-18T20:09:59.569486` |
| `last_operation_status` | Status of last operation | `completed` |
| `full_state` | Complete session state | `{...}` |

## 5. Session Continuity Verification

**Before Fix:** New session created for each interaction
**After Fix:** Same session reused for continuing conversations

```python
# First interaction
session_id = "80912b38-eac8-4146-9f2e-ecd5101e7d10"
# interaction_count: 1

# Second interaction (SAME session_id)
session_id = "80912b38-eac8-4146-9f2e-ecd5101e7d10"  
# interaction_count: 2  ← Incremented!
```

## 6. Debugging Session Issues

If you're not seeing session information:

1. **Check if using InMemoryRunner:**
   ```python
   runner = InMemoryRunner(agent=root_agent, app_name="co_agent_recruitment")
   ```

2. **Verify session retrieval:**
   ```python
   session = await runner.session_service.get_session(
       app_name="co_agent_recruitment",
       user_id="your_user_id", 
       session_id="your_session_id"
   )
   if session:
       print(f"Session found: {session.state}")
   else:
       print("Session not found!")
   ```

3. **Use the demo script:**
   ```bash
   python demo_session_info.py
   ```

## 7. Files Created for Session Visibility

1. **`demo_session_info.py`** - Complete working example
2. **`session_utils.py`** - Utility functions for easy session access
3. **`test_session.py`** - Comprehensive session testing
4. **Updated `co_agent_recruitment/agent.py`** - Fixed session callbacks

## Summary

✅ **Session information is now fully visible**
✅ **Sessions persist across interactions** 
✅ **Interaction count increments properly**
✅ **Conversation state is tracked**
✅ **Easy-to-use utilities provided**

You can now see all session information including interaction counts, timestamps, and session state throughout your application!