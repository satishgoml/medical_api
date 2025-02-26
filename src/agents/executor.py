from langchain import hub
from langchain_openai import ChatOpenAI
import sys
sys.path.append("")

from langgraph.prebuilt import create_react_agent
from src.tools.retriever import retriever_tool
from src.settings import settings
from src.agents.config import AgentNames, AGENT_PROMPTS, DEFAULT_AGENT_PROMPT

tools = [retriever_tool]

# Choose the LLM that will drive the agent
llm = ChatOpenAI(model=settings.default_model)

def get_executor_for_agent(agent_type=None):
    """
    Creates an executor agent with the appropriate system prompt for the given agent type
    
    Args:
        agent_type (AgentNames, optional): The type of medical specialist. Defaults to None.
        
    Returns:
        Agent: A ReAct agent with the specialized prompt
    """
    # Get the appropriate prompt based on agent type
    if agent_type and agent_type in AGENT_PROMPTS:
        prompt = AGENT_PROMPTS[agent_type]
    else:
        prompt = DEFAULT_AGENT_PROMPT
    
    
    # Create and return the agent
    return create_react_agent(llm, tools, prompt=prompt)

# Create a default executor
executor = get_executor_for_agent()

async def main():
    from dotenv import load_dotenv
    load_dotenv()
    config = {"recursion_limit": 50}
    inputs = {"messages": [("user", "What is the patient's history?")]}
    async for event in executor.astream(inputs, config=config):
        for k, v in event.items():
            if k != "__end__":
                print(v)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())