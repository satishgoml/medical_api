from typing import Union
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate

from src.schema import Plan


class Response(BaseModel):
    """Response to user."""

    reason: str = Field(
        description="Reason for the response. This should explain why the conversation is being stopped."
    )


class Act(BaseModel):
    """Action to perform."""

    action: Union[Response, Plan] = Field(
        description="Action to perform. If you feel the need to stop the conversation, use Response. If you want to continue, use Plan with the new plan with updated steps or the same plan."
    )


replanner_prompt = ChatPromptTemplate.from_template(
    """For the given objective, come up with a simple step by step plan. \
    This plan should involve individual tasks, that if executed correctly will yield the correct answer. Do not add any superfluous steps. \
    The result of the final step should be the final answer. Make sure that each step has all the information needed - do not skip steps.

    IMPORTANT CONSTRAINTS:
    - Agents cannot communicate with each other
    - Agents cannot access external tools or actions
    - Agents can only access documents through the retriever_tool
    - If the total steps exceed 10, return a Response and don't take further actions
    
    Your objective was this:
    {input}

    Your original plan was this:
    {plan}

    You have currently done the follow steps:
    {past_steps}

    Update your plan accordingly. If no more steps are needed and you can return to the user, then respond with Response. Otherwise, fill out the plan. Only add steps to the plan that still NEED to be done. Do not return previously done steps as part of the plan."""
)


replanner = replanner_prompt | ChatOpenAI(
    model="gpt-4o", temperature=0
).with_structured_output(Act)
