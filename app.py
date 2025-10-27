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

# Import your existing classes from the colab code
from models.file_handler import ResumeFileHandler
from models.text_processor import TextPreprocessor
from models.semantic_analyzer import SemanticAnalyzer
from models.ranking_system import ResumeRankingSystem

# NEW IMPORTS for Experiments 7, 8, 9
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

class CompanyDashboard:
    """Enhanced dashboard for company view"""
    
    def __init__(self, ranking_system):
        self.ranking_system = ranking_system
        self.results_history = []
    
    def process_bulk_resumes(self, uploaded_files, job_description):
        """Process multiple resumes for company ranking"""
        results = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, uploaded_file in enumerate(uploaded_files):
            status_text.text(f'Processing {uploaded_file.name}...')
            progress_bar.progress((i + 1) / len(uploaded_files))
            
            file_extension = os.path.splitext(uploaded_file.name)[1].lower()
            
            try:
                result = self.ranking_system.process_single_resume(
                    file_content=uploaded_file.read(),
                    file_extension=file_extension
                )
                
                if result['success']:
                    similarity = self.ranking_system.analyzer.calculate_similarity(
                        result['processed_text'],
                        job_description
                    )
                    
                    result.update({
                        'file_name': uploaded_file.name,
                        'similarity_score': similarity,
                        'match_level': self.ranking_system.get_match_level(similarity),
                        'processed_at': datetime.now()
                    })
                    results.append(result)
                else:
                    st.error(f"Failed to process {uploaded_file.name}: {result.get('error', 'Unknown error')}")
            except Exception as e:
                st.error(f"Error processing {uploaded_file.name}: {str(e)}")
        
        # Sort by similarity score
        results.sort(key=lambda x: x['similarity_score'], reverse=True)
        for i, result in enumerate(results):
            result['rank'] = i + 1
        
        status_text.text('Processing complete!')
        progress_bar.progress(1.0)
        
        return results

class UserAssessment:
    """Enhanced assessment for individual users"""
    
    def __init__(self, ranking_system):
        self.ranking_system = ranking_system
        self.gap_analyzer = SkillGapAnalyzer()
    
    def assess_resume(self, resume_file, job_description):
        """Comprehensive resume assessment"""
        file_extension = os.path.splitext(resume_file.name)[1].lower()
        
        result = self.ranking_system.process_single_resume(
            file_content=resume_file.read(),
            file_extension=file_extension
        )
        
        if not result['success']:
            return {'error': result['error']}
        
        similarity = self.ranking_system.analyzer.calculate_similarity(
            result['processed_text'],
            job_description
        )
        
        jd_skills = self.ranking_system.preprocessor.extract_skills(job_description)
        resume_skills = result.get('skills', [])
        
        gap_analysis = self.gap_analyzer.analyze_skill_gaps(resume_skills, jd_skills)
        suggestions = self.gap_analyzer.get_improvement_suggestions(gap_analysis['missing_skills'])
        
        assessment = {
            'similarity_score': similarity,
            'match_level': self.ranking_system.get_match_level(similarity),
            'resume_skills': resume_skills,
            'jd_skills': jd_skills,
            'gap_analysis': gap_analysis,
            'suggestions': suggestions,
            'assessment_date': datetime.now(),
            'file_name': resume_file.name
        }
        
        return assessment

# ================================
# STREAMLIT UI IMPLEMENTATION
# ================================

def main():
    """Main Streamlit application"""
    
    st.set_page_config(
        page_title="AI Resume Ranking System",
        page_icon="📄",
        layout="wide"
    )
    
    # Initialize the ranking system
    @st.cache_resource
    def load_ranking_system():
        return ResumeRankingSystem()
    
    ranking_system = load_ranking_system()
    
    # Sidebar for navigation
    st.sidebar.title("🎯 AI Resume Ranking")
    
    # CORRECTED: Proper list formatting with square brackets
    app_mode = st.sidebar.selectbox(
        "Choose Application Mode",
        [
            "Company Dashboard",
            "User Assessment",
            "Experiment 7: Prompt Engineering",
            "Experiment 8: MCQ Generation",
            "Experiment 9: AI Chatbot"
        ]
    )
    
    # Route to appropriate interface
    if app_mode == "Company Dashboard":
        company_interface(ranking_system)
    elif app_mode == "User Assessment":
        user_interface(ranking_system)
    elif app_mode == "Experiment 7: Prompt Engineering":
        experiment7_interface(ranking_system)
    elif app_mode == "Experiment 8: MCQ Generation":
        experiment8_interface(ranking_system)
    elif app_mode == "Experiment 9: AI Chatbot":
        experiment9_interface(ranking_system)

def company_interface(ranking_system):
    """Company dashboard interface"""
    st.title("🏢 Company Dashboard - Bulk Resume Ranking")
    st.markdown("Upload multiple resumes and get them ranked against your job description")
    
    company_dashboard = CompanyDashboard(ranking_system)
    
    # Job description input
    st.subheader("📋 Job Description")
    job_description = st.text_area(
        "Enter the job description and requirements:",
        height=200,
        placeholder="Paste your job description here..."
    )
    
    # File upload
    st.subheader("📁 Upload Resumes")
    uploaded_files = st.file_uploader(
        "Choose resume files",
        type=['pdf', 'docx', 'txt'],
        accept_multiple_files=True,
        help="Supported formats: PDF, DOCX, TXT"
    )
    
    if uploaded_files and job_description.strip():
        if st.button("🚀 Process and Rank Resumes", type="primary"):
            with st.spinner("Processing resumes..."):
                results = company_dashboard.process_bulk_resumes(uploaded_files, job_description)
                
                if results:
                    st.success(f"Successfully processed {len(results)} resumes!")
                    
                    # Display results summary
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total Resumes", len(results))
                    with col2:
                        excellent_count = sum(1 for r in results if r['match_level'] == 'Excellent Match')
                        st.metric("Excellent Matches", excellent_count)
                    with col3:
                        avg_score = np.mean([r['similarity_score'] for r in results])
                        st.metric("Average Score", f"{avg_score:.2f}")
                    with col4:
                        top_score = max(r['similarity_score'] for r in results)
                        st.metric("Top Score", f"{top_score:.2f}")
                    
                    # Detailed results table
                    st.subheader("📋 Detailed Rankings")
                    results_df = pd.DataFrame([
                        {
                            'Rank': r['rank'],
                            'Resume': r['file_name'],
                            'Score': f"{r['similarity_score']:.3f}",
                            'Match Level': r['match_level'],
                            'Skills Found': len(r.get('skills', []))
                        }
                        for r in results
                    ])
                    
                    st.dataframe(results_df, use_container_width=True)
                    
                    # Export functionality
                    csv = results_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Results as CSV",
                        data=csv,
                        file_name=f"resume_rankings_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                        mime='text/csv'
                    )

def user_interface(ranking_system):
    """User assessment interface"""
    st.title("👤 User Assessment - Resume Analysis")
    st.markdown("Get detailed feedback on your resume against a specific job description")
    
    user_assessment = UserAssessment(ranking_system)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📄 Upload Your Resume")
        resume_file = st.file_uploader(
            "Choose your resume file",
            type=['pdf', 'docx', 'txt'],
            help="Supported formats: PDF, DOCX, TXT"
        )
    
    with col2:
        st.subheader("📋 Job Description")
        job_description = st.text_area(
            "Paste the job description you're targeting:",
            height=200,
            placeholder="Paste the job description here..."
        )
    
    if resume_file and job_description.strip():
        if st.button("🔍 Analyze My Resume", type="primary"):
            with st.spinner("Analyzing your resume..."):
                assessment = user_assessment.assess_resume(resume_file, job_description)
                
                if 'error' in assessment:
                    st.error(f"Error processing resume: {assessment['error']}")
                else:
                    st.success("Analysis complete!")
                    
                    # Overall score
                    st.subheader("📊 Overall Assessment")
                    similarity_score = assessment['similarity_score']
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Match Score", f"{similarity_score:.1%}")
                    with col2:
                        match_level = assessment['match_level']
                        st.metric("Match Level", match_level)
                    
                    # Skills breakdown
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("✅ Your Strengths")
                        gap_analysis = assessment['gap_analysis']
                        if gap_analysis['matching_skills']:
                            for skill in gap_analysis['matching_skills']:
                                st.success(f"✓ {skill.title()}")
                        else:
                            st.info("No matching skills found")
                    
                    with col2:
                        st.subheader("❌ Skills to Develop")
                        if gap_analysis['missing_skills']:
                            for skill in gap_analysis['missing_skills']:
                                st.error(f"✗ {skill.title()}")
                        else:
                            st.success("Great! You have all the required skills.")

# ============================================================================
# EXPERIMENT INTERFACE FUNCTIONS
# ============================================================================

def experiment7_interface(ranking_system):
    """Experiment 7: Prompt Engineering Interface"""
    st.title("🎯 Experiment 7: Customized Prompts for Recruitment")
    st.markdown("### Prompt Engineering for Customer Service Context")
    
    prompt_engineer = PromptEngineer()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📄 Upload Resume")
        resume_file = st.file_uploader(
            "Choose resume file",
            type=['pdf', 'docx', 'txt'],
            key="exp7_resume"
        )
    
    with col2:
        st.subheader("📋 Job Description")
        job_description = st.text_area(
            "Paste job description:",
            height=200,
            key="exp7_jd"
        )
    
    if resume_file and job_description.strip():
        if st.button("🚀 Generate Prompts", type="primary"):
            with st.spinner("Processing..."):
                file_extension = os.path.splitext(resume_file.name)[1].lower()
                result = ranking_system.process_single_resume(
                    file_content=resume_file.read(),
                    file_extension=file_extension
                )
                
                if result['success']:
                    resume_text = result['processed_text']
                    similarity_score = ranking_system.analyzer.calculate_similarity(
                        resume_text, job_description
                    )
                    
                    resume_skills = result.get('skills', [])
                    jd_skills = ranking_system.preprocessor.extract_skills(job_description)
                    
                    gap_analyzer = SkillGapAnalyzer()
                    gap_analysis = gap_analyzer.analyze_skill_gaps(resume_skills, jd_skills)
                    
                    skills_data = {
                        'resume_skills': resume_skills,
                        'jd_skills': jd_skills
                    }
                    
                    st.success(f"✅ Semantic Similarity Score: {similarity_score:.2%}")
                    
                    tab1, tab2, tab3 = st.tabs([
                        "Basic Prompt",
                        "Advanced Prompt",
                        "Contextual Prompt"
                    ])
                    
                    with tab1:
                        st.subheader("📝 Basic Prompt")
                        basic_prompt = prompt_engineer.create_basic_prompt(
                            resume_text, job_description, similarity_score
                        )
                        st.text_area("Generated Basic Prompt", basic_prompt, height=300)
                    
                    with tab2:
                        st.subheader("📝 Advanced Prompt")
                        advanced_prompt = prompt_engineer.create_advanced_prompt(
                            resume_text, job_description, similarity_score, skills_data
                        )
                        st.text_area("Generated Advanced Prompt", advanced_prompt, height=400)
                    
                    with tab3:
                        st.subheader("📝 Contextual Prompt")
                        contextual_prompt = prompt_engineer.create_contextual_prompt(
                            resume_text, job_description, similarity_score,
                            skills_data, gap_analysis
                        )
                        st.text_area("Generated Contextual Prompt", contextual_prompt, height=500)
                    
                    st.markdown("---")
                    st.subheader("📊 Comparison")
                    comparison_df = pd.DataFrame(prompt_engineer.get_prompt_comparison())
                    st.table(comparison_df)

def experiment8_interface(ranking_system):
    """Experiment 8: MCQ Generation Interface"""
    st.title("📝 Experiment 8: MCQ Generation using LangChain")
    st.markdown("### Automated Assessment Generation")
    
    st.sidebar.subheader("🔑 OpenAI Configuration")
    openai_api_key = st.sidebar.text_input(
        "Enter OpenAI API Key",
        type="password",
        key="exp8_api_key"
    )
    
    if not openai_api_key:
        st.warning("⚠️ Please enter your OpenAI API key in the sidebar")
        return
    
    mcq_generator = MCQGenerator(openai_api_key)
    
    mode = st.radio(
        "Select Generation Mode",
        ["Job Description Based", "Resume + JD Based"],
        key="exp8_mode"
    )
    
    num_questions = st.slider("Number of Questions", 3, 10, 5, key="exp8_num")
    
    if mode == "Job Description Based":
        st.subheader("🎯 Generate MCQs from Job Description")
        jd_text = st.text_area(
            "Enter Job Description",
            height=300,
            placeholder="Paste job description here...",
            key="exp8_jd"
        )
        
        if st.button("Generate MCQs", type="primary") and jd_text:
            with st.spinner("Generating questions..."):
                result = mcq_generator.generate_jd_based_mcqs(jd_text, num_questions)
                
                if result.get('success'):
                    st.success("✅ MCQs Generated!")
                    parsed = mcq_generator.parse_mcq_response(result['content'])
                    
                    if parsed.get('success'):
                        mcqs_data = parsed['mcqs']
                        for q in mcqs_data['questions']:
                            st.markdown(f"### Question {q['question_number']}")
                            st.markdown(f"**{q['question_text']}**")
                            for opt in q['options']:
                                st.markdown(f"- {opt['option_id']}. {opt['text']}")
                            with st.expander("Show Answer"):
                                st.success(f"**Correct:** {q['correct_answer']}")
                                st.info(f"**Explanation:** {q['explanation']}")
                            st.markdown("---")

def experiment9_interface(ranking_system):
    """Experiment 9: AI Chatbot Interface"""
    st.title("💬 Experiment 9: AI Chatbot for Job Matching")
    st.markdown("### Interactive Q&A using RAG")
    
    if 'exp9_chat_history' not in st.session_state:
        st.session_state.exp9_chat_history = []
    if 'exp9_vectorstore_ready' not in st.session_state:
        st.session_state.exp9_vectorstore_ready = False
    
    st.sidebar.subheader("🔑 OpenAI Configuration")
    openai_api_key = st.sidebar.text_input(
        "Enter OpenAI API Key",
        type="password",
        key="exp9_api_key"
    )
    
    if not openai_api_key:
        st.warning("⚠️ Please enter your OpenAI API key in the sidebar")
        return
    
    st.sidebar.subheader("📄 Upload Documents")
    resume_file = st.sidebar.file_uploader(
        "Upload Resume",
        type=['pdf', 'docx', 'txt'],
        key="exp9_resume"
    )
    
    jd_text = st.sidebar.text_area(
        "Paste Job Description",
        height=200,
        key="exp9_jd"
    )
    
    if st.sidebar.button("🚀 Initialize Chatbot"):
        if resume_file and jd_text:
            with st.spinner("Initializing..."):
                try:
                    file_extension = os.path.splitext(resume_file.name)[1].lower()
                    resume_result = ranking_system.process_single_resume(
                        file_content=resume_file.read(),
                        file_extension=file_extension
                    )
                    
                    if resume_result['success']:
                        resume_text = resume_result['processed_text']
                        chatbot = RAGChatbot(openai_api_key)
                        vs_result = chatbot.create_vectorstore(resume_text, jd_text)
                        
                        if vs_result['success']:
                            similarity_score = ranking_system.analyzer.calculate_similarity(
                                resume_text, jd_text
                            )
                            chain_result = chatbot.initialize_qa_chain(
                                similarity_score,
                                st.session_state.exp9_chat_history
                            )
                            
                            if chain_result['success']:
                                st.session_state.exp9_chatbot = chatbot
                                st.session_state.exp9_similarity = similarity_score
                                st.session_state.exp9_system_context = chain_result['system_context']
                                st.session_state.exp9_vectorstore_ready = True
                                st.sidebar.success("✅ Chatbot ready!")
                except Exception as e:
                    st.sidebar.error(f"Error: {str(e)}")
    
    if st.session_state.exp9_vectorstore_ready:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Match Score", f"{st.session_state.exp9_similarity:.1%}")
        with col2:
            st.metric("Messages", len(st.session_state.exp9_chat_history))
        
        st.markdown("---")
        
        # Chat display
        for message in st.session_state.exp9_chat_history:
            with st.chat_message(message['role']):
                st.markdown(message['content'])
        
        # Chat input
        user_input = st.chat_input("Ask a question...")
        if user_input:
            st.session_state.exp9_chat_history.append({'role': 'user', 'content': user_input})
            with st.chat_message("user"):
                st.markdown(user_input)
            
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    chatbot = st.session_state.exp9_chatbot
                    response = chatbot.get_response(
                        user_input,
                        st.session_state.exp9_system_context
                    )
                    
                    if response['success']:
                        st.markdown(response['answer'])
                        st.session_state.exp9_chat_history.append({
                            'role': 'assistant',
                            'content': response['answer']
                        })

if __name__ == "__main__":
    main()