import vertexai
from vertexai import agent_engines

# Create an agent engine instance
agent_engine = agent_engines.create()
def get_agent_engine() -> agent_engines.AgentEngine:
    """Get the agent engine instance."""
    return agent_engine


if __name__ == "__main__":
    # Example usage of the agent engine
    print("Agent Engine created successfully.")
    print(f"Engine ID: {agent_engine.name.split('/')[-1]}")
    print(f"Engine Name: {agent_engine.name}")
    # You can add more functionality or tests here as needed.
    agent_engine.delete(force=True)
