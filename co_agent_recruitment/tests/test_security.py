"""Tests for secure agent functionality."""

import pytest
import asyncio
from unittest.mock import patch, AsyncMock, MagicMock
from co_agent_recruitment.agent import (
    sanitize_input, 
    parse_resume, 
    get_model_name,
    PersonalDetails,
    Link
)


class TestInputSanitization:
    """Test input sanitization functionality."""
    
    def test_sanitize_input_removes_scripts(self):
        """Test that script tags are removed."""
        malicious_input = "John Doe <script>alert('xss')</script> Software Engineer"
        result = sanitize_input(malicious_input)
        assert "<script>" not in result
        assert "alert" not in result
        assert "John Doe" in result
        assert "Software Engineer" in result
    
    def test_sanitize_input_removes_javascript_urls(self):
        """Test that javascript: URLs are removed."""
        malicious_input = "Contact: javascript:alert('xss') or email@example.com"
        result = sanitize_input(malicious_input)
        assert "javascript:" not in result
        assert "email@example.com" in result
    
    def test_sanitize_input_removes_event_handlers(self):
        """Test that event handlers are removed."""
        malicious_input = "John onclick=alert(1) Doe"
        result = sanitize_input(malicious_input)
        assert "onclick=" not in result
        assert "John" in result
        assert "Doe" in result
    
    def test_sanitize_input_size_limit(self):
        """Test that oversized input is rejected."""
        large_input = "A" * 60000  # Exceeds 50KB limit
        with pytest.raises(ValueError, match="Input text too large"):
            sanitize_input(large_input)
    
    def test_sanitize_input_invalid_types(self):
        """Test that invalid input types are rejected."""
        with pytest.raises(ValueError, match="Invalid input"):
            sanitize_input(None)
        
        with pytest.raises(ValueError, match="Invalid input"):
            sanitize_input("")
        
        with pytest.raises(ValueError, match="Invalid input"):
            sanitize_input(123)


class TestValidation:
    """Test pydantic model validation."""
    
    def test_personal_details_validation(self):
        """Test PersonalDetails validation."""
        # Test valid data
        valid_data = {
            "full_name": "John Doe",
            "email": "john@example.com"
        }
        details = PersonalDetails(**valid_data)
        assert details.full_name == "John Doe"
        assert details.email == "john@example.com"
        
        # Test invalid email
        with pytest.raises(ValueError):
            PersonalDetails(full_name="John Doe", email="invalid-email")
        
        # Test script injection in name
        with pytest.raises(ValueError):
            PersonalDetails(full_name="<script>alert('xss')</script>", email="john@example.com")
    
    def test_link_validation(self):
        """Test Link URL validation."""
        # Test valid URL
        valid_link = Link(type="LinkedIn", url="https://linkedin.com/in/johndoe")
        assert valid_link.url == "https://linkedin.com/in/johndoe"
        
        # Test invalid URL (no protocol)
        with pytest.raises(ValueError):
            Link(type="LinkedIn", url="linkedin.com/in/johndoe")
        
        # Test oversized URL
        with pytest.raises(ValueError):
            Link(type="LinkedIn", url="https://" + "a" * 2000 + ".com")


class TestConfiguration:
    """Test configuration and environment handling."""
    
    def test_get_model_name_default(self):
        """Test default model name."""
        with patch.dict('os.environ', {}, clear=True):
            model = get_model_name()
            assert model == 'gemini-2.5-flash-preview-05-20'
    
    def test_get_model_name_from_env(self):
        """Test model name from environment."""
        with patch.dict('os.environ', {'GEMINI_MODEL': 'custom-model-name'}):
            model = get_model_name()
            assert model == 'custom-model-name'


class TestResumeParsingErrors:
    """Test error handling in resume parsing."""
    
    @pytest.mark.asyncio
    async def test_parse_resume_sanitizes_input(self):
        """Test that parse_resume sanitizes input."""
        with patch('co_agent_recruitment.agent.PydanticAgent') as mock_agent_class:
            # This is the mock for the PydanticAgent class.
            # When PydanticAgent() is called, it will return mock_agent_instance.
            mock_agent_instance = AsyncMock(name="PydanticAgent_instance_mock")
            mock_agent_class.return_value = mock_agent_instance

            # This is the synchronous object that `await agent.run(...)` should yield.
            sync_run_result = MagicMock(name="run_result_sync_mock")
            sync_run_result.output.model_dump.return_value = {"test": "data"}

            # Explicitly set the 'run' attribute of mock_agent_instance to be an AsyncMock.
            # This AsyncMock, when awaited, will return sync_run_result.
            mock_agent_instance.run = AsyncMock(return_value=sync_run_result, name="run_method_async_mock")
            
            malicious_resume = "John Doe <script>alert('xss')</script> Software Engineer"
            # Inside parse_resume:
            # 1. agent = PydanticAgent(...) becomes agent = mock_agent_instance
            # 2. result = await agent.run(...) becomes result = await mock_agent_instance.run(...)
            #    Since mock_agent_instance.run is an AsyncMock returning sync_run_result,
            #    `result` becomes `sync_run_result`.
            # 3. return result.output.model_dump() becomes return sync_run_result.output.model_dump()
            #    This is a synchronous call on a MagicMock, returning {"test": "data"}.
            parsed_output = await parse_resume(malicious_resume)
            
            assert parsed_output == {"test": "data"}

            # Check that the agent's run method was called with sanitized input
            called_args = mock_agent_instance.run.call_args
            sanitized_input_arg = called_args[0][0]
            assert "<script>" not in sanitized_input_arg
            assert "alert" not in sanitized_input_arg
        
        await asyncio.sleep(0)  # Allow event loop to process pending tasks
    
    @pytest.mark.asyncio
    async def test_parse_resume_handles_exceptions(self):
        """Test that parse_resume handles exceptions gracefully."""
        with patch('co_agent_recruitment.agent.PydanticAgent') as mock_agent_class:
            mock_agent_class.side_effect = Exception("AI service error")
            
            with pytest.raises(Exception, match="Failed to parse resume"):
                await parse_resume("Valid resume text")


if __name__ == "__main__":
    pytest.main([__file__])