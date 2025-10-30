# ============================================================================
# EXPERIMENT 8 MODULE - MCQ Generation (GEMINI VERSION, Simplified - No LangChain)
# ============================================================================

import google.generativeai as genai
import json

class MCQGenerator:
    """Handles MCQ generation using Google Gemini"""

    def __init__(self, gemini_api_key=None):
        self.api_key = gemini_api_key
        self.model = None
        if gemini_api_key:
            self.initialize_llm(gemini_api_key)

    def initialize_llm(self, api_key):
        """Initialize the Gemini model with API key"""
        self.api_key = api_key
        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(
                'gemini-2.0-flash-exp',
                generation_config={
                    'temperature': 0.7,
                    'top_p': 0.95,
                    'top_k': 40,
                    'max_output_tokens': 3000,
                }
            )
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def generate_jd_based_mcqs(self, job_description, num_questions=5):
        """Generate MCQs based on job description"""
        if not self.model:
            return {"error": "API key not initialized"}

        prompt = f"""You are an expert HR professional and assessment designer. 
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

Generate exactly {num_questions} multiple-choice questions in JSON format with the following structure:
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

Return ONLY the JSON, no additional text.
"""

        try:
            response = self.model.generate_content(prompt)
            return {"success": True, "content": response.text}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def generate_resume_based_mcqs(self, resume_text, job_description, num_questions=5):
        """Generate interview MCQs based on resume and JD"""
        if not self.model:
            return {"error": "API key not initialized"}

        prompt = f"""You are an expert technical interviewer. 
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

Generate {num_questions} technical interview questions in JSON format following this structure:
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

Return ONLY the JSON, no additional text.
"""

        try:
            response = self.model.generate_content(prompt)
            return {"success": True, "content": response.text}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def parse_mcq_response(self, response_content):
        """Parse MCQ JSON response"""
        try:
            # Try to extract JSON from markdown code blocks if present
            if "```json" in response_content:
                start = response_content.find("```json") + 7
                end = response_content.find("```", start)
                response_content = response_content[start:end].strip()
            elif "```" in response_content:
                start = response_content.find("```") + 3
                end = response_content.find("```", start)
                response_content = response_content[start:end].strip()

            mcqs = json.loads(response_content)
            return {"success": True, "mcqs": mcqs}
        except json.JSONDecodeError as e:
            return {"success": False, "error": str(e), "raw_content": response_content}