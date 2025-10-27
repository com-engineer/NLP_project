# ============================================================================
# EXPERIMENT 8 MODULE - MCQ Generation
# Add this to a new file: models/mcq_generator.py
# ============================================================================

from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
import json

class MCQGenerator:
    """Handles MCQ generation using LangChain and LLM"""

    def __init__(self, openai_api_key=None):
        self.api_key = openai_api_key
        self.llm = None
        if openai_api_key:
            self.initialize_llm(openai_api_key)

    def initialize_llm(self, api_key):
        """Initialize the LLM with API key"""
        self.api_key = api_key
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.7,
            openai_api_key=api_key
        )

    def generate_jd_based_mcqs(self, job_description, num_questions=5):
        """Generate MCQs based on job description"""
        if not self.llm:
            return {"error": "API key not initialized"}

        system_prompt = f"""You are an expert HR professional and assessment designer. 
Generate {num_questions} multiple-choice questions based on the following job description.

Focus on:
1. Technical skills mentioned in the job description
2. Required qualifications and experience
3. Domain knowledge relevant to the role
4. Soft skills and competencies

Each question should be:
- Relevant to the job requirements
- Clear and unambiguous
- Have 4 options with only 1 correct answer
- Include a brief explanation for the correct answer

Job Description:
{job_description}
"""

        human_prompt = f"""Generate exactly {num_questions} multiple-choice questions in JSON format with the following structure:
{{
    "questions": [
        {{
            "question_number": 1,
            "question_text": "Question here?",
            "options": [
                {{"option_id": "A", "text": "Option A"}},
                {{"option_id": "B", "text": "Option B"}},
                {{"option_id": "C", "text": "Option C"}},
                {{"option_id": "D", "text": "Option D"}}
            ],
            "correct_answer": "A",
            "explanation": "Explanation here",
            "topic": "Topic name"
        }}
    ]
}}
"""

        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_prompt)
            ]
            response = self.llm(messages)
            return {"success": True, "content": response.content}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def generate_resume_based_mcqs(self, resume_text, job_description, num_questions=5):
        """Generate interview MCQs based on resume and JD"""
        if not self.llm:
            return {"error": "API key not initialized"}

        system_prompt = f"""You are an expert technical interviewer. 
Based on the candidate's resume and the job description, generate {num_questions} 
interview-style multiple-choice questions to assess the candidate's knowledge and fit.

Candidate Resume:
{resume_text[:1500]}

Job Description:
{job_description}

Generate questions that:
1. Test understanding of technologies mentioned in the resume
2. Assess relevant experience for the target role
3. Evaluate problem-solving abilities in the job's domain
4. Check knowledge of best practices in the field
"""

        human_prompt = f"""Generate {num_questions} technical interview questions in JSON format following this structure:
{{
    "questions": [
        {{
            "question_number": 1,
            "question_text": "Question?",
            "options": [
                {{"option_id": "A", "text": "Option A"}},
                {{"option_id": "B", "text": "Option B"}},
                {{"option_id": "C", "text": "Option C"}},
                {{"option_id": "D", "text": "Option D"}}
            ],
            "correct_answer": "B",
            "explanation": "Explanation",
            "topic": "Topic"
        }}
    ]
}}
"""

        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_prompt)
            ]
            response = self.llm(messages)
            return {"success": True, "content": response.content}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def parse_mcq_response(self, response_content):
        """Parse MCQ JSON response"""
        try:
            mcqs = json.loads(response_content)
            return {"success": True, "mcqs": mcqs}
        except json.JSONDecodeError:
            return {"success": False, "raw_content": response_content}
