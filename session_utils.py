#!/usr/bin/env python3
"""
Session utilities for Co-Agent-Recruitment
Provides easy access to session information for debugging and monitoring
"""

import asyncio
from typing import Dict, Any, Optional
from co_agent_recruitment.agent import root_agent
from google.adk.runners import InMemoryRunner
from google.adk.sessions import Session


class SessionManager:
    """Utility class to manage and inspect sessions"""

    def __init__(self, app_name: str = "co_agent_recruitment"):
        self.app_name = app_name
        self.runner: Optional[InMemoryRunner] = None

    def get_runner(self) -> InMemoryRunner:
        """Get or create the runner instance"""
        if self.runner is None:
            self.runner = InMemoryRunner(agent=root_agent, app_name=self.app_name)
        return self.runner

    async def create_session(self, user_id: str) -> Session:
        """Create a new session for a user"""
        runner = self.get_runner()
        return await runner.session_service.create_session(
            app_name=self.app_name, user_id=user_id
        )

    async def get_session_info(
        self, user_id: str, session_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get detailed session information"""
        runner = self.get_runner()
        session = await runner.session_service.get_session(
            app_name=self.app_name, user_id=user_id, session_id=session_id
        )

        if not session:
            return None

        return {
            "session_id": session.id,
            "user_id": session.user_id,
            "app_name": session.app_name,
            "interaction_count": session.state.get("interaction_count", 0),
            "conversation_started": session.state.get("conversation_started"),
            "last_interaction_start": session.state.get("last_interaction_start"),
            "last_interaction_end": session.state.get("last_interaction_end"),
            "last_operation_status": session.state.get("last_operation_status"),
            "all_state_keys": list(session.state.keys()),
            "full_state": dict(session.state),
        }

    async def list_user_sessions(self, user_id: str) -> Dict[str, Any]:
        """List all sessions for a user"""
        runner = self.get_runner()
        sessions_response = await runner.session_service.list_sessions(
            app_name=self.app_name, user_id=user_id
        )

        sessions_info = []
        for session in sessions_response.sessions:
            sessions_info.append(
                {
                    "session_id": session.id,
                    "interaction_count": session.state.get("interaction_count", 0),
                    "conversation_started": session.state.get("conversation_started"),
                    "last_operation_status": session.state.get("last_operation_status"),
                }
            )

        return {
            "user_id": user_id,
            "total_sessions": len(sessions_info),
            "sessions": sessions_info,
        }

    async def print_session_summary(self, user_id: str, session_id: str):
        """Print a formatted summary of session information"""
        info = await self.get_session_info(user_id, session_id)

        if not info:
            print(f"❌ Session {session_id} not found for user {user_id}")
            return

        print("📊 Session Summary")
        print(f"   Session ID: {info['session_id']}")
        print(f"   User ID: {info['user_id']}")
        print(f"   Interactions: {info['interaction_count']}")
        print(f"   Started: {info['conversation_started']}")
        print(f"   Last Status: {info['last_operation_status']}")
        print(f"   State Keys: {info['all_state_keys']}")


# Global session manager instance
session_manager = SessionManager()


# Convenience functions
async def get_session_info(user_id: str, session_id: str) -> Optional[Dict[str, Any]]:
    """Get session information for a user and session"""
    return await session_manager.get_session_info(user_id, session_id)


async def list_user_sessions(user_id: str) -> Dict[str, Any]:
    """List all sessions for a user"""
    return await session_manager.list_user_sessions(user_id)


async def print_session_summary(user_id: str, session_id: str):
    """Print session summary"""
    await session_manager.print_session_summary(user_id, session_id)


async def create_new_session(user_id: str) -> Session:
    """Create a new session"""
    return await session_manager.create_session(user_id)


# Example usage
if __name__ == "__main__":

    async def demo():
        # Create a session
        session = await create_new_session("example_user")
        print(f"Created session: {session.id}")

        # Get session info
        info = await get_session_info("example_user", session.id)
        print(f"Session info: {info}")

        # List user sessions
        sessions = await list_user_sessions("example_user")
        print(f"User sessions: {sessions}")

    asyncio.run(demo())
