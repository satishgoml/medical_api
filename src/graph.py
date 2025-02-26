import sys

sys.path.append("")

from src.schema import Plan, PlanExecute, CompletedTask
from src.agents.planner import planner
from src.agents.executor import get_executor_for_agent
from langgraph.graph import StateGraph, START, END
from src.agents.replanner import replanner, Response
from src.agents.report_generator import report_generator


async def execute_step(state: PlanExecute):
    plan = state["plan"]
    task = plan.steps[0]
    task_formatted = f"""Execute:  {task.task}."""

    # Create specialized executor based on the agent type in the task
    specialized_executor = get_executor_for_agent(task.agent)

    agent_response = await specialized_executor.ainvoke(
        {"messages": [("user", state["intial_diagnosis"]), ("user", task_formatted)]}
    )

    agent_response = agent_response["messages"][-1].content

    # Create a CompletedTask from the current task and response
    completed_task = CompletedTask(
        task=task.task, agent=task.agent, result=agent_response
    )

    return {
        "past_steps": [completed_task],
        "response": {"agent_name": task.agent.value, "response": agent_response},
    }


async def replan(state: PlanExecute):
    # Get replanner's decision with full context
    response = await replanner.ainvoke(
        {
            "input": state["input"],
            "plan": [step.model_dump() for step in state["plan"].steps],
            "past_steps": [step.model_dump() for step in state["past_steps"]],
        }
    )

    if isinstance(response.action, Response):
        print(response.model_dump())
        # If it's a response, we're done - return empty plan to trigger end
        return {"plan": Plan(steps=[]), "stop_reason": response.action.reason}
    elif isinstance(response.action, Plan): 
        # If it's a new plan, update the plan
        return {"plan": response.action}
    else:
        print(response.model_dump())
        raise ValueError("Unexpected action type")
    

async def generate_report(state: PlanExecute):
    message = await report_generator.ainvoke(
        {
            "initial_diagnosis": state["intial_diagnosis"],
            "past_steps": state["past_steps"],
            "stop_reason": state["stop_reason"],
        }
    )
    final_report = message.content
    return {"response": final_report}


async def general_diagnosis(state: PlanExecute):
    general_executor = get_executor_for_agent()
    messages = await general_executor.ainvoke({"messages": [("user", state["input"])]})
    intial_diagnosis = messages["messages"][-1].content
    return {"intial_diagnosis": intial_diagnosis}


async def plan_step(state: PlanExecute):
    plan_response = await planner.ainvoke(
        {"messages": [("user", state["intial_diagnosis"])]}
    )

    return {"plan": plan_response}


def should_end(state: PlanExecute):
    if len(state["plan"].steps) == 0:
        return "final_report"
    else:
        return "execute_step"




workflow = StateGraph(PlanExecute)


workflow.add_node("general_diagnosis", general_diagnosis)
workflow.add_node("plan_step", plan_step)
workflow.add_node("execute_step", execute_step)
workflow.add_node("replan", replan)
workflow.add_node("final_report", generate_report)

workflow.add_edge(START, "general_diagnosis")
workflow.add_edge("general_diagnosis", "plan_step")
workflow.add_edge("plan_step", "execute_step")
workflow.add_edge("execute_step", "replan")

workflow.add_conditional_edges(
    "replan", should_end, {"final_report": "final_report", "execute_step": "execute_step"}
)

workflow.add_edge("final_report", END)


medical_workflow = workflow.compile()


async def main():
    config = {"recursion_limit": 50}
    inputs = {"input": "The patient is feeling unwell and has a history of diabetes"}
    async for event in medical_workflow.astream(inputs, config=config):
        for k, v in event.items():
            print("Key:", k)
            if k != "__end__":
                print(k)
            else:
                print("End of workflow")

            if k == "execute_step":
                print(v)
            elif k == "final_report":
                print("Final Medical Report:")
                print(v.get("response", "No report generated"))


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
