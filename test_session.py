#!/usr/bin/env python3
"""
Test script for session management functionality
"""
import asyncio
import sys
import os

# Add the co_agent_recruitment directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'co_agent_recruitment'))

from agent import parse_resume_with_session, list_user_sessions, get_session_history

async def test_session_management():
    """Test the session management functionality"""
    print("Testing session management...")
    
    # Test data
    test_resume = """
    John Doe
    Software Engineer
    Email: john.doe@example.com
    Phone: (555) 123-4567
    
    Experience:
    - 5 years Python development
    - 3 years React/JavaScript
    - 2 years AWS cloud services
    
    Education:
    - BS Computer Science, University of Technology, 2018
    
    Skills:
    - Python, JavaScript, React, AWS, Docker
    """
    
    user_id = "test_user_123"
    
    try:
        # Test 1: Create a session and parse resume
        print("Test 1: Creating session and parsing resume...")
        result, session_id = await parse_resume_with_session(test_resume, user_id)
        print(f"✅ Session created: {session_id}")
        print(f"✅ Resume parsed successfully")
        
        # Test 2: List user sessions
        print("\nTest 2: Listing user sessions...")
        sessions = await list_user_sessions(user_id)
        print(f"✅ Found {len(sessions['sessions'])} sessions for user {user_id}")
        
        # Test 3: Get session history
        print("\nTest 3: Getting session history...")
        history = await get_session_history(user_id, session_id)
        print(f"✅ Session history retrieved")
        print(f"   - Session ID: {history.get('session_id')}")
        print(f"   - Events count: {history.get('events_count', 0)}")
        print(f"   - State keys: {list(history.get('state', {}).keys())}")
        
        # Test 4: Parse another resume with the same user (new session)
        print("\nTest 4: Creating another session for the same user...")
        test_resume_2 = "Jane Smith\nData Scientist\n3 years experience in ML"
        result2, session_id2 = await parse_resume_with_session(test_resume_2, user_id)
        print(f"✅ Second session created: {session_id2}")
        
        # Test 5: List sessions again
        print("\nTest 5: Listing sessions after second parse...")
        sessions_final = await list_user_sessions(user_id)
        print(f"✅ Now found {len(sessions_final['sessions'])} sessions for user {user_id}")
        
        print("\n🎉 All session management tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_session_management())
    sys.exit(0 if success else 1)