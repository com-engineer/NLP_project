# ============================================================================
# EXPERIMENT 7 MODULE - Prompt Engineering for your existing app
# Add this to a new file: models/prompt_engineer.py
# ============================================================================

class PromptEngineer:
    """Handles prompt generation for different complexity levels"""

    def __init__(self):
        pass

    def create_basic_prompt(self, resume_text, job_description, similarity_score):
        """Generate basic prompt for simple comparison"""
        prompt = f"""
Compare this resume to the job description and provide a matching score.

Resume Summary: {resume_text[:500]}...
Job Description Summary: {job_description[:500]}...

Semantic Similarity Score: {similarity_score:.2%}

Please provide:
- Overall match assessment
- Key observations
"""
        return prompt

    def create_advanced_prompt(self, resume_text, job_description, similarity_score, skills_data):
        """Generate advanced structured prompt"""
        prompt = f"""
You are an intelligent recruitment assistant. Analyze the candidate's resume against the job description.

JOB DESCRIPTION:
{job_description}

CANDIDATE RESUME:
{resume_text}

SEMANTIC MATCH SCORE: {similarity_score:.2%}
SKILLS FOUND: {', '.join(skills_data.get('resume_skills', [])[:10])}
REQUIRED SKILLS: {', '.join(skills_data.get('jd_skills', [])[:10])}

Please provide:
1. Overall matching assessment (Excellent/Good/Fair/Poor)
2. Key strengths that align with the job requirements
3. Missing skills or qualifications
4. Top 3 recommended online courses or certifications to bridge skill gaps
5. Specific suggestions to improve the resume for this role

Provide your analysis in a structured, professional manner.
"""
        return prompt

    def create_contextual_prompt(self, resume_text, job_description, similarity_score, 
                                 skills_data, gap_analysis):
        """Generate contextual domain-aware prompt"""
        prompt = f"""
As a career counselor and recruitment expert, analyze this candidate-job match:

TARGET ROLE: {job_description.split('\n')[0][:100]}
MATCH SCORE: {similarity_score:.2%}

CANDIDATE PROFILE:
{resume_text[:800]}

FULL JOB REQUIREMENTS:
{job_description}

SKILLS ANALYSIS:
- Matching Skills: {', '.join(gap_analysis.get('matching_skills', [])[:10])}
- Missing Skills: {', '.join(gap_analysis.get('missing_skills', [])[:10])}
- Extra Skills: {', '.join(gap_analysis.get('extra_skills', [])[:5])}

Please provide a detailed assessment:

1. MATCH ANALYSIS:
   - What makes this candidate suitable for this role?
   - Calculate a weighted score considering: skills (40%), experience (30%), education (20%), achievements (10%)

2. GAP ANALYSIS:
   - Critical missing skills
   - Nice-to-have missing qualifications
   - Experience gaps

3. ACTIONABLE RECOMMENDATIONS:
   - Top 5 specific online courses (with platform names like Coursera, Udemy, etc.)
   - Suggested certifications
   - Project ideas to demonstrate missing skills

4. RESUME OPTIMIZATION:
   - Keywords to add
   - Sections to strengthen
   - Format improvements

Provide concrete, actionable guidance tailored to this specific job opportunity.
"""
        return prompt

    def get_prompt_comparison(self):
        """Return comparison data for different prompt types"""
        return {
            "Prompt Type": ["Basic", "Advanced", "Contextual"],
            "Complexity": ["Low", "Medium", "High"],
            "Detail Level": ["Minimal", "Moderate", "Comprehensive"],
            "Context Awareness": ["None", "Moderate", "High"],
            "Actionability": ["Low", "High", "Very High"],
            "Best For": [
                "Quick screening",
                "Detailed evaluation",
                "Personalized guidance"
            ]
        }
