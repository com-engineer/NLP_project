# Complete Resume Ranking Web Application with Experiments 7, 8, 9
# Two-sided platform: Company view for bulk ranking + User view for individual assessment

import streamlit as st
import pandas as pd
import numpy as np
import io
import re
import os
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Import your existing classes from the models folder
from models.file_handler import ResumeFileHandler
from models.text_processor import TextPreprocessor
from models.semantic_analyzer import SemanticAnalyzer
from models.ranking_system import ResumeRankingSystem

# NEW IMPORTS for Experiments 7, 8, 9 (Using Gemini versions)
from models.prompt_engineer import PromptEngineer
from models.mcq_generator import MCQGenerator
from models.chatbot_rag import RAGChatbot

import json

# ================================
# ENHANCED CLASSES FOR UI FEATURES
# ================================

class SkillGapAnalyzer:
    """Analyzes skill gaps and provides improvement suggestions"""
    
    def __init__(self):
        # Comprehensive skill database with categories
        self.skill_database = {
            'programming': ['python', 'java', 'javascript', 'c++', 'c#', 'php', 'ruby', 'go', 'rust', 'scala'],
            'web_development': ['html', 'css', 'react', 'angular', 'vue', 'nodejs', 'express', 'django', 'flask'],
            'databases': ['sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'cassandra'],
            'cloud': ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'jenkins'],
            'data_science': ['pandas', 'numpy', 'matplotlib', 'seaborn', 'scikit-learn', 'tensorflow', 'pytorch'],
            'machine_learning': ['machine learning', 'deep learning', 'nlp', 'computer vision', 'neural networks'],
            'tools': ['git', 'linux', 'jira', 'confluence', 'postman', 'swagger', 'tableau', 'power bi']
        }
        
        # Course recommendations for skills
        self.course_recommendations = {
            'python': ['Python for Everybody - Coursera', 'Complete Python Bootcamp - Udemy'],
            'machine learning': ['Machine Learning - Andrew Ng', 'Hands-On Machine Learning - Udemy'],
            'aws': ['AWS Solutions Architect - A Cloud Guru', 'AWS Certified Developer - Udemy'],
            'react': ['React Complete Guide - Udemy', 'React Fundamentals - Pluralsight'],
            'sql': ['SQL for Data Science - Coursera', 'The Complete SQL Bootcamp - Udemy']
        }
    
    def analyze_skill_gaps(self, resume_skills, jd_skills):
        """Analyze gaps between resume and job requirements"""
        resume_skills_lower = [skill.lower() for skill in resume_skills]
        jd_skills_lower = [skill.lower() for skill in jd_skills]
        
        missing_skills = [skill for skill in jd_skills_lower if skill not in resume_skills_lower]
        matching_skills = [skill for skill in jd_skills_lower if skill in resume_skills_lower]
        extra_skills = [skill for skill in resume_skills_lower if skill not in jd_skills_lower]
        
        return {
            'missing_skills': missing_skills,
            'matching_skills': matching_skills,
            'extra_skills': extra_skills,
            'match_percentage': len(matching_skills) / len(jd_skills_lower) * 100 if jd_skills_lower else 0
        }
    
    def get_improvement_suggestions(self, missing_skills):
        """Generate improvement suggestions for missing skills"""
        suggestions = []
        for skill in missing_skills:
            skill_lower = skill.lower()
            category = None
            
            for cat, skills in self.skill_database.items():
                if skill_lower in skills:
                    category = cat
                    break
            
            courses = self.course_recommendations.get(skill_lower, [f"Search for '{skill}' courses on Coursera/Udemy"])
            
            suggestion = {
                'skill': skill,
                'category': category or 'general',
                'priority': 'High' if skill_lower in ['python', 'java', 'sql', 'machine learning'] else 'Medium',
                'courses': courses,
                'learning_path': self.get_learning_path(skill_lower, category)
            }
            suggestions.append(suggestion)
        
        return suggestions
    
    def get_learning_path(self, skill, category):
        """Generate learning path for a skill"""
        paths = {
            'python': ['Basic Python syntax', 'Data structures', 'OOP concepts', 'Libraries (pandas, numpy)', 'Practice projects'],
            'machine learning': ['Statistics basics', 'Python/R programming', 'ML algorithms', 'Scikit-learn', 'Real projects'],
            'react': ['JavaScript ES6+', 'React fundamentals', 'State management', 'Hooks', 'Build projects'],
            'aws': ['Cloud concepts', 'Core AWS services', 'Hands-on labs', 'Certification prep', 'Practice exams']
        }
        return paths.get(skill, ['Research fundamentals', 'Online courses', 'Hands-on practice', 'Build projects'])


# ================================
# MAIN APPLICATION
# ================================


def main():
    """Main Streamlit application"""
    
    # Page configuration
    st.set_page_config(
        page_title="Resume Ranking Application",
        page_icon="📄",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Title and description
    st.title("📄 Resume Ranking & Analysis System")
    st.markdown("**Two-sided platform:** Company view for bulk ranking + User view for individual assessment")
    
    # Sidebar for navigation and API key
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Key input
        gemini_api_key = st.text_input("Enter Gemini API Key", type="password", help="Required for AI-powered features")
        
        st.markdown("---")
        st.header("📋 Navigation")
        
        # View selection
        view_mode = st.radio(
            "Select View",
            ["🏢 Company View (Bulk Ranking)", "👤 User View (Individual Assessment)"]
        )
        
        st.markdown("---")
        st.info("💡 **Tip:** Upload your resume and job description to get started!")
    
    # Initialize session state
    if 'processed_data' not in st.session_state:
        st.session_state.processed_data = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Initialize core systems
    ranking_system = ResumeRankingSystem()
    skill_analyzer = SkillGapAnalyzer()
    
    # Initialize AI-powered systems (only if API key provided)
    prompt_engineer = None
    mcq_generator = None
    rag_chatbot = None
    
    if gemini_api_key:
        prompt_engineer = PromptEngineer(gemini_api_key)
        mcq_generator = MCQGenerator(gemini_api_key)
        rag_chatbot = RAGChatbot(gemini_api_key)
    
    # ================================
    # COMPANY VIEW - BULK RANKING
    # ================================
    if "Company View" in view_mode:
        st.header("🏢 Company View - Bulk Resume Ranking")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Upload Resumes")
            uploaded_files = st.file_uploader(
                "Upload multiple resumes (PDF, DOCX, TXT)",
                type=['pdf', 'docx', 'txt'],
                accept_multiple_files=True
            )
        
        with col2:
            st.subheader("Job Description")
            job_description = st.text_area(
                "Paste job description",
                height=200,
                placeholder="Enter the job description here..."
            )
        
        if uploaded_files and job_description:
            if st.button("🔍 Analyze & Rank Resumes", type="primary"):
                with st.spinner("Processing resumes..."):
                    processed_resumes = []
                    
                    for uploaded_file in uploaded_files:
                        file_extension = os.path.splitext(uploaded_file.name)[1]
                        file_content = uploaded_file.read()
                        
                        result = ranking_system.process_single_resume(
                            file_content=file_content,
                            file_extension=file_extension
                        )
                        
                        if result['success']:
                            result['filename'] = uploaded_file.name
                            processed_resumes.append(result)
                    
                    if processed_resumes:
                        preprocessor = TextPreprocessor()
                        jd_processed = preprocessor.preprocess_text(job_description)
                        
                        analyzer = SemanticAnalyzer()
                        
                        for resume in processed_resumes:
                            similarity = analyzer.calculate_similarity(
                                resume['processed_text'],
                                jd_processed
                            )
                            resume['similarity_score'] = similarity
                        
                        processed_resumes.sort(key=lambda x: x['similarity_score'], reverse=True)
                        
                        for i, resume in enumerate(processed_resumes):
                            resume['rank'] = i + 1
                        
                        st.session_state.processed_data = processed_resumes
                        st.success(f"✅ Processed {len(processed_resumes)} resumes successfully!")
        
        if st.session_state.processed_data:
            st.markdown("---")
            st.subheader("📊 Ranking Results")
            
            df_data = []
            for resume in st.session_state.processed_data:
                df_data.append({
                    'Rank': resume['rank'],
                    'Filename': resume['filename'],
                    'Match Score': f"{resume['similarity_score']:.2%}",
                    'Skills Found': len(resume['skills']),
                    'Email': resume['email'][0] if resume['email'] else 'N/A'
                })
            
            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True)
            
            st.subheader("📈 Visualizations")
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.bar(
                    df,
                    x='Rank',
                    y=[float(score.strip('%'))/100 for score in df['Match Score']],
                    title="Similarity Scores by Rank",
                    labels={'y': 'Match Score', 'x': 'Rank'}
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                match_levels = []
                for resume in st.session_state.processed_data:
                    score = resume['similarity_score']
                    if score > 0.7:
                        match_levels.append("Excellent")
                    elif score > 0.5:
                        match_levels.append("Good")
                    elif score > 0.3:
                        match_levels.append("Fair")
                    else:
                        match_levels.append("Poor")
                
                fig = px.pie(
                    names=match_levels,
                    title="Match Level Distribution"
                )
                st.plotly_chart(fig, use_container_width=True)
    
    # ================================
    # USER VIEW - INDIVIDUAL ASSESSMENT
    # ================================
    else:
        st.header("👤 User View - Individual Resume Assessment")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("📄 Upload Your Resume")
            uploaded_resume = st.file_uploader(
                "Upload your resume",
                type=['pdf', 'docx', 'txt']
            )
        
        with col2:
            st.subheader("💼 Target Job Description")
            job_description = st.text_area(
                "Paste the job description",
                height=200,
                placeholder="Enter the job description you're targeting..."
            )
        
        if uploaded_resume and job_description:
            if st.button("🎯 Analyze My Resume", type="primary"):
                with st.spinner("Analyzing your resume..."):
                    file_extension = os.path.splitext(uploaded_resume.name)[1]
                    file_content = uploaded_resume.read()
                    
                    result = ranking_system.process_single_resume(
                        file_content=file_content,
                        file_extension=file_extension
                    )
                    
                    if result['success']:
                        preprocessor = TextPreprocessor()
                        jd_processed = preprocessor.preprocess_text(job_description)
                        
                        analyzer = SemanticAnalyzer()
                        similarity = analyzer.calculate_similarity(
                            result['processed_text'],
                            jd_processed
                        )
                        
                        result['similarity_score'] = similarity
                        result['job_description'] = job_description
                        
                        st.session_state.user_analysis = result
                        st.success("✅ Analysis complete!")
        
        if 'user_analysis' in st.session_state:
            result = st.session_state.user_analysis
            
            st.markdown("---")
            
            st.subheader("📊 Your Match Score")
            score = result['similarity_score']
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Match Score", f"{score:.1%}")
            with col2:
                if score > 0.7:
                    st.metric("Match Level", "Excellent ⭐")
                elif score > 0.5:
                    st.metric("Match Level", "Good 👍")
                elif score > 0.3:
                    st.metric("Match Level", "Fair 👌")
                else:
                    st.metric("Match Level", "Needs Work 📝")
            with col3:
                st.metric("Skills Found", len(result['skills']))
            
            st.markdown("---")
            st.subheader("🎯 Skills Analysis")
            
            preprocessor = TextPreprocessor()
            jd_skills = preprocessor.extract_skills(job_description)
            resume_skills = result['skills']
            
            skill_gap = skill_analyzer.analyze_skill_gaps(resume_skills, jd_skills)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**✅ Matching Skills**")
                if skill_gap['matching_skills']:
                    for skill in skill_gap['matching_skills']:
                        st.success(f"✓ {skill}")
                else:
                    st.info("No matching skills found")
            
            with col2:
                st.markdown("**❌ Missing Skills**")
                if skill_gap['missing_skills']:
                    for skill in skill_gap['missing_skills']:
                        st.error(f"✗ {skill}")
                else:
                    st.success("All required skills present!")
            
            with col3:
                st.markdown("**➕ Additional Skills**")
                if skill_gap['extra_skills']:
                    for skill in skill_gap['extra_skills'][:5]:
                        st.info(f"+ {skill}")
            
            if gemini_api_key and prompt_engineer:
                st.markdown("---")
                st.subheader("🤖 AI-Powered Insights")
                
                tabs = st.tabs(["📝 Detailed Analysis", "❓ Interview Questions", "📚 Skill Recommendations", "💬 AI Chatbot"])
                
                with tabs[0]:
                    if st.button("Generate Detailed Analysis"):
                        with st.spinner("Generating analysis..."):
                            analysis_result = prompt_engineer.generate_detailed_analysis(
                                result['raw_text'],
                                job_description,
                                score
                            )
                            if analysis_result['success']:
                                st.markdown(analysis_result['analysis'])
                            else:
                                st.error(f"Error: {analysis_result['error']}")
                
                with tabs[1]:
                    if st.button("Generate Interview Questions"):
                        with st.spinner("Generating questions..."):
                            # Reinitialize preprocessor here as well for safety
                            preprocessor = TextPreprocessor()
                            questions_result = prompt_engineer.generate_interview_questions(
                                result['raw_text'],
                                job_description
                            )
                            if questions_result['success']:
                                st.markdown(questions_result['questions'])
                            else:
                                st.error(f"Error: {questions_result['error']}")
                
                with tabs[2]:
                    if st.button("Get Skill Recommendations"):
                        with st.spinner("Generating recommendations..."):
                            rec_result = prompt_engineer.generate_skill_recommendations(
                                result['raw_text'],
                                job_description
                            )
                            if rec_result['success']:
                                st.markdown(rec_result['recommendations'])
                            else:
                                st.error(f"Error: {rec_result['error']}")
                
                with tabs[3]:
                    st.markdown("**Ask questions about your resume match:**")
                    
                    if 'chatbot_initialized' not in st.session_state:
                        rag_chatbot.create_vectorstore(result['raw_text'], job_description)
                        rag_chatbot.initialize_qa_chain(score)
                        st.session_state.chatbot_initialized = True
                    
                    user_question = st.text_input("Your question:")
                    if user_question:
                        with st.spinner("Thinking..."):
                            response = rag_chatbot.get_response(user_question)
                            if response['success']:
                                st.markdown(f"**Answer:** {response['answer']}")
                                st.session_state.chat_history.append({
                                    'role': 'user',
                                    'content': user_question
                                })
                                st.session_state.chat_history.append({
                                    'role': 'assistant',
                                    'content': response['answer']
                                })
                            else:
                                st.error(f"Error: {response['error']}")
                    
                    if st.session_state.chat_history:
                        st.markdown("---")
                        st.markdown("**Chat History:**")
                        for msg in st.session_state.chat_history[-6:]:
                            if msg['role'] == 'user':
                                st.info(f"**You:** {msg['content']}")
                            else:
                                st.success(f"**AI:** {msg['content']}")
            else:
                st.warning("⚠️ Enter a Gemini API key in the sidebar to unlock AI-powered features!")


if __name__ == '__main__':
    main()
