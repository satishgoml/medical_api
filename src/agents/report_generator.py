from src.schema import PlanExecute
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI


report_prompt = ChatPromptTemplate.from_template(
    """
    Create a comprehensive medical report based on the following diagnostic process. Ensure the report is structured professionally with clear sections and prioritizes identified risks and recommendations.  

    ### **Medical Report**  

    #### **1. Initial Assessment**  
    Provide an overview of the patient's condition based on the initial diagnosis.  
    **Initial Diagnosis:** {initial_diagnosis}  

    #### **2. Diagnostic Procedures**  
    Summarize the steps taken during the diagnostic process, highlighting key observations.  
    **Steps Taken:** {past_steps}  

    #### **3. Findings & Risk Assessment**  
    Detail the findings from the diagnostic process. Identify and categorize risks by severity:  
    - **Critical Risks:** Immediate threats requiring urgent attention.  
    - **High Risks:** Significant concerns that need prompt intervention.  
    - **Moderate/Low Risks:** Issues that should be monitored or managed over time.  

    #### **4. Conclusion & Final Diagnosis**  
    Explain the reasoning behind the final diagnosis.  
    **Conclusion Reason:** {stop_reason}  

    #### **5. Priority-Based Recommendations**  
    Provide clear, actionable recommendations ranked by priority:  
    - **Critical:** Immediate actions required to mitigate severe risks.  
    - **High Priority:** Necessary steps to prevent complications.  
    - **Advisory:** Additional guidance for long-term care and monitoring.  

    Ensure clarity, conciseness, and a logical flow of information.  

    """
)

report_generator = report_prompt | ChatOpenAI(model="o3-mini")
