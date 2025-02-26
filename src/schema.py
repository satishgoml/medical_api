import operator
from typing import Annotated, List
from typing_extensions import TypedDict
from pydantic import BaseModel, Field

from src.agents.config import AgentNames


class Task(BaseModel):
    """Task to be executed"""
    task: str = Field(description="Tasks to be executed")
    agent: AgentNames = Field(description="Agent to execute the task")

class CompletedTask(Task):
    result: str = Field(description="Result of task")

class Plan(BaseModel):
    """Plan to follow in future"""
    steps: List[Task] = Field(description="Steps to follow")

class PlanExecute(TypedDict):
    input: str
    plan: Plan
    past_steps: Annotated[List[CompletedTask], operator.add]
    response: str
    intial_diagnosis: str
    stop_reason: str




