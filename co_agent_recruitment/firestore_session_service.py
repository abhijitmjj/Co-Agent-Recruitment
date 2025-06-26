"""
Firestore-based session service for the Co-Agent Recruitment system.
"""

import logging
from typing import Optional, Any
from google.cloud import firestore
from google.adk.sessions import Session, BaseSessionService
from google.adk.sessions.base_session_service import GetSessionConfig, ListSessionsResponse

logger = logging.getLogger(__name__)

class FirestoreSessionService(BaseSessionService):
    """A session service that stores session data in Firestore."""

    def __init__(self, project_id: str, collection_name: str = "sessions"):
        """Initializes the FirestoreSessionService.

        Args:
            project_id: The Google Cloud project ID.
            collection_name: The name of the Firestore collection to store sessions in.
        """
        self.db = firestore.AsyncClient(project=project_id)
        self.collection = self.db.collection(collection_name)

    async def create_session(
        self, 
        *,
        app_name: str, 
        user_id: str, 
        state: Optional[dict[str, Any]] = None,
        session_id: Optional[str] = None,
    ) -> Session:
        """Creates a new session in Firestore."""
        import uuid
        import time
        
        try:
            # Determine the session ID to use
            final_session_id = (
                session_id.strip() 
                if session_id and session_id.strip() 
                else str(uuid.uuid4())
            )
            
            session = Session(
                app_name=app_name,
                user_id=user_id,
                id=final_session_id,
                state=state or {},
                last_update_time=time.time(),
            )
            
            await self.collection.document(session.id).set(session.model_dump())
            logger.info(f"Created session {session.id} for user {user_id}")
            return session
        except Exception as e:
            logger.error(f"Error creating session: {e}")
            raise

    async def get_session(
        self, 
        *,
        app_name: str, 
        user_id: str, 
        session_id: str,
        config: Optional[GetSessionConfig] = None,
    ) -> Session | None:
        """Gets a session from Firestore."""
        try:
            doc = await self.collection.document(session_id).get()
            if doc.exists:
                data = doc.to_dict()
                if data:
                    session = Session.model_validate(data)
                    # Apply config filtering if provided
                    if config:
                        if config.num_recent_events and hasattr(session, 'events'):
                            session.events = session.events[-config.num_recent_events:]
                        if config.after_timestamp and hasattr(session, 'events'):
                            session.events = [
                                event for event in session.events
                                if getattr(event, 'timestamp', 0) >= config.after_timestamp
                            ]
                    logger.debug(f"Retrieved session {session_id} with state: {session.state}")
                    return session
        except Exception as e:
            logger.error(f"Error getting session {session_id}: {e}")
        return None

    async def list_sessions(self, *, app_name: str, user_id: str) -> ListSessionsResponse:
        """Lists all sessions for a user from Firestore."""
        try:
            query = self.collection.where("user_id", "==", user_id)
            docs = query.stream()
            
            sessions = []
            async for doc in docs:
                try:
                    data = doc.to_dict()
                    if data:
                        session = Session.model_validate(data)
                        # Clear events and state for listing to reduce payload size
                        session.events = []
                        session.state = {}
                        sessions.append(session)
                except Exception as e:
                    logger.warning(f"Error parsing session {doc.id}: {e}")
                    continue
            
            return ListSessionsResponse(sessions=sessions)
        except Exception as e:
            logger.error(f"Error listing sessions for user {user_id}: {e}")
            return ListSessionsResponse(sessions=[])

    async def update_session(self, session: Session) -> None:
        """Updates a session in Firestore."""
        try:
            await self.collection.document(session.id).set(session.model_dump())
            logger.debug(f"Updated session {session.id}")
        except Exception as e:
            logger.error(f"Error updating session {session.id}: {e}")
            raise

    async def delete_session(
        self, *, app_name: str, user_id: str, session_id: str
    ) -> None:
        """Deletes a session from Firestore."""
        try:
            await self.collection.document(session_id).delete()
            logger.info(f"Deleted session {session_id} for user {user_id}")
        except Exception as e:
            logger.error(f"Error deleting session {session_id}: {e}")
            raise
