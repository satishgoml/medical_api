from langchain import hub
from langchain_openai import ChatOpenAI
import sys
sys.path.append("")

from langgraph.prebuilt import create_react_agent
from src.tools.retriever import retriever_tool

tools = [retriever_tool]

# Choose the LLM that will drive the agent
llm = ChatOpenAI(model="gpt-4o")
prompt = f"You are a medical professional tasked with diagnosing a patient. You have access to patient's details using tool {retriever_tool.name}. Use this tool to retrieve information and provide a detailed diagnosis finally."
general_doctor = create_react_agent(llm, tools, prompt=prompt)


async def main():
    from dotenv import load_dotenv
    load_dotenv()
    config = {"recursion_limit": 50}
    inputs = {"messages": [("user", "What is the patient's history?")]}
    async for event in general_doctor.astream(inputs, config=config):
        for k, v in event.items():
            if k != "__end__":
                print(v)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())