# ============================================================================
# EXPERIMENT 7 MODULE - Prompt Engineering (GEMINI VERSION)
# ============================================================================

import google.generativeai as genai

class PromptEngineer:
    """Handles advanced prompt engineering for resume analysis using Google Gemini"""

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
                    'temperature': 0.3,  # Lower for more consistent analysis
                    'top_p': 0.95,
                    'top_k': 40,
                    'max_output_tokens': 2048,
                }
            )
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def generate_detailed_analysis(self, resume_text, job_description, similarity_score):
        """Generate comprehensive resume analysis"""
        if not self.model:
            return {"error": "API key not initialized"}

        prompt = f"""You are an expert HR analyst and career counselor. Analyze the following resume against the job description.

RESUME:
{resume_text[:2000]}

JOB DESCRIPTION:
{job_description[:2000]}

SIMILARITY SCORE: {similarity_score:.2%}

Provide a detailed analysis covering:

1. **Overall Match Assessment** (2-3 sentences)
   - How well does this candidate fit the role?

2. **Key Strengths** (3-5 bullet points)
   - What makes this candidate stand out?
   - Relevant experience and skills

3. **Areas for Improvement** (3-5 bullet points)
   - Skills or experience gaps
   - Areas where the candidate could develop

4. **Technical Skills Analysis**
   - Skills present in resume
   - Skills required but missing
   - Additional relevant skills

5. **Experience Relevance** (2-3 sentences)
   - How relevant is their work experience?
   - Years of experience vs. requirements

6. **Recommendations**
   - For the candidate: How to improve their profile
   - For the recruiter: Interview focus areas

7. **Final Verdict** (1-2 sentences)
   - Hire/Interview/Reject recommendation with reasoning

Format your response in clear sections with headers.
"""

        try:
            response = self.model.generate_content(prompt)
            return {"success": True, "analysis": response.text}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def generate_interview_questions(self, resume_text, job_description, num_questions=5):
        """Generate targeted interview questions"""
        if not self.model:
            return {"error": "API key not initialized"}

        prompt = f"""Based on the candidate's resume and job requirements, generate {num_questions} insightful interview questions.

RESUME HIGHLIGHTS:
{resume_text[:1500]}

JOB REQUIREMENTS:
{job_description[:1500]}

Generate {num_questions} interview questions that:
1. Test technical competency in required skills
2. Assess relevant experience
3. Evaluate problem-solving abilities
4. Check cultural fit
5. Explore career motivations

Format each question with:
- The question itself
- What you're trying to assess
- What a good answer might include

Number each question clearly.
"""

        try:
            response = self.model.generate_content(prompt)
            return {"success": True, "questions": response.text}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def generate_skill_recommendations(self, resume_text, job_description):
        """Generate personalized skill development recommendations"""
        if not self.model:
            return {"error": "API key not initialized"}

        prompt = f"""As a career development advisor, analyze the skill gaps between this resume and job requirements.

CANDIDATE RESUME:
{resume_text[:1500]}

TARGET JOB:
{job_description[:1500]}

Provide:

1. **Critical Missing Skills** (Must have for the role)
   - List 3-5 essential skills the candidate lacks
   - For each skill, explain why it's important

2. **Recommended Learning Path**
   - Prioritized list of skills to develop
   - Suggested timeline (3 months, 6 months, 1 year)
   - Specific resources (courses, certifications, books)

3. **Quick Wins** (Skills that can be learned fast)
   - 2-3 skills achievable in 1-2 months
   - How to demonstrate these skills

4. **Long-term Development**
   - Skills requiring deeper investment
   - Career progression path

5. **Project Ideas**
   - 2-3 practical projects to build missing skills
   - How these projects strengthen the resume

Be specific with course names and resources where possible.
"""

        try:
            response = self.model.generate_content(prompt)
            return {"success": True, "recommendations": response.text}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def generate_resume_improvement_suggestions(self, resume_text, job_description):
        """Generate specific resume improvement suggestions"""
        if not self.model:
            return {"error": "API key not initialized"}

        prompt = f"""As a professional resume writer, provide specific suggestions to improve this resume for the target job.

CURRENT RESUME:
{resume_text[:2000]}

TARGET JOB:
{job_description[:1500]}

Provide actionable advice on:

1. **Content Improvements**
   - What to add
   - What to emphasize more
   - What to remove or de-emphasize

2. **Keywords to Include**
   - List 10-15 important keywords from the job description
   - Where to naturally incorporate them

3. **Achievement Quantification**
   - Identify vague statements
   - Suggest how to add metrics and numbers

4. **Structure and Format**
   - Section organization
   - Length and readability

5. **Specific Rewrite Examples**
   - Take 2-3 bullets from the resume
   - Show "Before" and improved "After" versions

Be concrete and actionable.
"""

        try:
            response = self.model.generate_content(prompt)
            return {"success": True, "suggestions": response.text}
        except Exception as e:
            return {"success": False, "error": str(e)}