from typing import Literal
from langgraph.graph import END
import sys
sys.path.append("")

from src.schema import Plan, PlanExecute
from src.agents.planner import planner
from src.agents.replanner import Response, replanner
from src.agents.executor import executor
from src.agents.general_doctor import general_doctor
from langgraph.graph import StateGraph, START


async def execute_step(state: PlanExecute):
    plan = state["plan"]
    task = plan.steps[0]
    task_formatted = f"""Execute:  {task.task}."""
    agent_response = await executor.ainvoke(
        {"messages": [
            ("user", state["intial_diagnosis"]),
            ("user", task_formatted)]}
    )

    agent_response = agent_response["messages"][-1].content

    return {
        "past_steps": [(task, agent_response)],
        "response": {
            "agent_name": task.agent.value,
            "response": agent_response
        },
    }

async def replan(state: PlanExecute):
    # Just delete the first step index using slicing
     
    plan = state["plan"]
    
    if len(plan.steps) > 1:
        plan.steps = plan.steps[1:]
        return {"plan": plan}
    else:
        return {"plan": Plan(steps=[])}
        

async def general_diagnosis(state: PlanExecute):
    messages = await general_doctor.ainvoke({"messages": [("user", state["input"])]})
    intial_diagnosis = messages["messages"][-1].content
    return {"intial_diagnosis": intial_diagnosis}


async def plan_step(state: PlanExecute):
    plan_response = await planner.ainvoke({"messages": [("user", state["intial_diagnosis"])]})


    return {"plan": plan_response}


def should_end(state: PlanExecute):
    if len(state["plan"].steps) == 0:
        return END
    else:
        return "execute_step"
    



workflow = StateGraph(PlanExecute)


workflow.add_node("general_diagnosis", general_diagnosis)
workflow.add_node("plan_step", plan_step)
workflow.add_node("execute_step", execute_step)
workflow.add_node("replan", replan)

workflow.add_edge(START, "general_diagnosis")

workflow.add_edge("general_diagnosis", "plan_step")


workflow.add_edge("plan_step", "execute_step")
workflow.add_edge("execute_step", "replan")

workflow.add_conditional_edges(
    "replan",
    # Next, we pass in the function that will determine which node is called next.
    should_end,
    ["execute_step", END],
)


medical_workflow = workflow.compile()


async def main():
    config = {"recursion_limit": 50}
    inputs = {"input": "The patient is feeling unwell and has a history of diabetes"}
    async for event in medical_workflow.astream(inputs, config=config):
        for k, v in event.items():
            if k != "__end__":
                print(k)
            else:
                print("End of workflow")

            if k == "execute_step":
                print(v)
                

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())