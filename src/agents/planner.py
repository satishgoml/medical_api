from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

import sys

sys.path.append("")
from src.schema import Plan

planner_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            You are a Medical tasked with diagnosing a patient, come up with a simple step by step plan. \
            This plan should involve individual tasks performed by different specialized agents, that if executed correctly will yield the correct answer. Do not add any superfluous steps. \
            The result of the final step should be the final answer. Make sure that each step has all the information needed - do not skip steps.""",
        ),
        ("placeholder", "{messages}"),
    ]
)
planner = planner_prompt | ChatOpenAI(
    model="gpt-4o", temperature=0
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
