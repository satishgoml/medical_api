from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

import sys

sys.path.append("")

from src.settings import settings
from src.schema import Plan
from src.agents.config import AGENT_DESCRIPTIONS

# Create a string that lists each agent and its description
agent_list = "\n".join(
    [f"{agent.value}: {desc}" for agent, desc in AGENT_DESCRIPTIONS.items()]
)

# Updated system prompt with clear constraints
system_prompt = f"""
You are a Medical AI responsible for diagnosing a patient and formulating a structured diagnostic plan.  
Your plan should include step-by-step tasks assigned to specialized agents, ensuring that:  

1. **Agents can only use documented medical records** - They must rely solely on available documents and cannot assume or infer information.  
2. **Tasks should be relevant** - Assign tasks only if they align with the agent's expertise.  
3. **No external assumptions** - If critical patient data is missing, the plan should indicate that information is unavailable.  

### Available Agents:  
{agent_list}
"""

planner_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("placeholder", "{messages}"),
    ]
)
planner = planner_prompt | ChatOpenAI(
    model=settings.default_model, temperature=0
).with_structured_output(Plan)


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    res = planner.invoke(
        {
            "messages": [
                ("user", "Analyse the patient's history and provide a diagnosis.")
            ]
        },
        debug=True,
    )
    print(res)
