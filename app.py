# Complete Resume Ranking Web Application
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
            
            # Find category for the skill
            category = None
            for cat, skills in self.skill_database.items():
                if skill_lower in skills:
                    category = cat
                    break
            
            # Get course recommendations
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
            
            # Proper file extension handling
            file_extension = os.path.splitext(uploaded_file.name)[1].lower()
            
            # DEBUG: Add this line to see what's happening
            st.write(f"Debug: Processing {uploaded_file.name} with extension {file_extension}")
            
            try:
                # Process individual resume
                result = self.ranking_system.process_single_resume(
                    file_content=uploaded_file.read(),
                    file_extension=file_extension
                )
                
                # DEBUG: Add this to see the result
                st.write(f"Debug: Result success = {result.get('success', 'Unknown')}")
                
                if result['success']:
                    # Calculate similarity
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
                    # DEBUG: Show error
                    st.error(f"Failed to process {uploaded_file.name}: {result.get('error', 'Unknown error')}")
            
            except Exception as e:
                st.error(f"Error processing {uploaded_file.name}: {str(e)}")
        
        # DEBUG: Show final results count
        st.write(f"Debug: Total successful results = {len(results)}")
        
        # Sort by similarity score
        results.sort(key=lambda x: x['similarity_score'], reverse=True)
        for i, result in enumerate(results):
            result['rank'] = i + 1
        
        status_text.text('Processing complete!')
        progress_bar.progress(1.0)
        
        return results
    
    def create_ranking_visualizations(self, results):
        """Create comprehensive visualizations for company dashboard"""
        
        if not results:
            st.warning("No results to display")
            return
        
        # 1. Top candidates bar chart
        fig1 = px.bar(
            x=[r['file_name'] for r in results[:10]],
            y=[r['similarity_score'] for r in results[:10]],
            title="Top 10 Candidates by Similarity Score",
            labels={'x': 'Resume', 'y': 'Similarity Score'},
            color=[r['similarity_score'] for r in results[:10]],
            color_continuous_scale='Viridis'
        )
        fig1.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig1, use_container_width=True)
        
        # 2. Match level distribution
        match_counts = {}
        for result in results:
            level = result['match_level']
            match_counts[level] = match_counts.get(level, 0) + 1
        
        fig2 = px.pie(
            values=list(match_counts.values()),
            names=list(match_counts.keys()),
            title="Candidate Distribution by Match Level"
        )
        st.plotly_chart(fig2, use_container_width=True)
        
        # 3. Skills distribution heatmap
        all_skills = []
        for result in results:
            all_skills.extend(result.get('skills', []))
        
        skill_counts = {}
        for skill in all_skills:
            skill_counts[skill] = skill_counts.get(skill, 0) + 1
        
        top_skills = dict(sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:15])
        
        if top_skills:
            fig3 = px.bar(
                x=list(top_skills.values()),
                y=list(top_skills.keys()),
                orientation='h',
                title="Most Common Skills Across All Resumes",
                labels={'x': 'Frequency', 'y': 'Skills'}
            )
            st.plotly_chart(fig3, use_container_width=True)


class UserAssessment:
    """Enhanced assessment for individual users"""
    
    def __init__(self, ranking_system):
        self.ranking_system = ranking_system
        self.gap_analyzer = SkillGapAnalyzer()
    
    def assess_resume(self, resume_file, job_description):
        """Comprehensive resume assessment"""
        
        # Proper file extension handling
        file_extension = os.path.splitext(resume_file.name)[1].lower()
        
        # Process resume
        result = self.ranking_system.process_single_resume(
            file_content=resume_file.read(),
            file_extension=file_extension
        )
        
        if not result['success']:
            return {'error': result['error']}
        
        # Calculate similarity
        similarity = self.ranking_system.analyzer.calculate_similarity(
            result['processed_text'], 
            job_description
        )
        
        # Extract job description skills
        jd_skills = self.ranking_system.preprocessor.extract_skills(job_description)
        resume_skills = result.get('skills', [])
        
        # Analyze skill gaps
        gap_analysis = self.gap_analyzer.analyze_skill_gaps(resume_skills, jd_skills)
        
        # Get improvement suggestions
        suggestions = self.gap_analyzer.get_improvement_suggestions(gap_analysis['missing_skills'])
        
        # Generate detailed assessment
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
    
    def create_assessment_report(self, assessment):
        """Create detailed assessment report with visualizations"""
        
        # Overall score gauge
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = assessment['similarity_score'] * 100,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Resume Match Score (%)"},
            delta = {'reference': 70},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 80], 'color': "gray"},
                    {'range': [80, 100], 'color': "lightgreen"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        
        st.plotly_chart(fig_gauge, use_container_width=True)
        
        # Skills comparison chart
        gap_data = assessment['gap_analysis']
        
        if gap_data['matching_skills'] or gap_data['missing_skills']:
            skills_df = pd.DataFrame({
                'Skill': gap_data['matching_skills'] + gap_data['missing_skills'],
                'Status': ['Present'] * len(gap_data['matching_skills']) + ['Missing'] * len(gap_data['missing_skills'])
            })
            
            fig_skills = px.bar(
                skills_df, 
                x='Skill', 
                y=[1] * len(skills_df), 
                color='Status',
                title="Skills Analysis: Present vs Missing",
                color_discrete_map={'Present': 'green', 'Missing': 'red'}
            )
            fig_skills.update_layout(xaxis_tickangle=-45, showlegend=True)
            st.plotly_chart(fig_skills, use_container_width=True)


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
    app_mode = st.sidebar.selectbox(
        "Choose Application Mode",
        ["Company Dashboard", "User Assessment"]
    )
    
    if app_mode == "Company Dashboard":
        company_interface(ranking_system)
    else:
        user_interface(ranking_system)


def company_interface(ranking_system):
    """Company dashboard interface"""
    
    st.title("🏢 Company Dashboard - Bulk Resume Ranking")
    st.markdown("Upload multiple resumes and get them ranked against your job description")
    
    # Initialize company dashboard
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
                
                # Visualizations
                st.subheader("📊 Ranking Analysis")
                company_dashboard.create_ranking_visualizations(results)
                
                # Detailed results table
                st.subheader("📋 Detailed Rankings")
                
                results_df = pd.DataFrame([
                    {
                        'Rank': r['rank'],
                        'Resume': r['file_name'],
                        'Score': f"{r['similarity_score']:.3f}",
                        'Match Level': r['match_level'],
                        'Skills Found': len(r.get('skills', [])),
                        'Email': r.get('email', ['N/A'])[0] if r.get('email') else 'N/A',
                        'Phone': r.get('phone', ['N/A'])[0] if r.get('phone') else 'N/A'
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
            else:
                st.warning("No resumes were successfully processed. Please check the debug messages above.")


def user_interface(ranking_system):
    """User assessment interface"""
    
    st.title("👤 User Assessment - Resume Analysis")
    st.markdown("Get detailed feedback on your resume against a specific job description")
    
    # Initialize user assessment
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
                
                # Overall assessment
                st.subheader("📊 Overall Assessment")
                user_assessment.create_assessment_report(assessment)
                
                # Detailed breakdown
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("✅ Your Strengths")
                    gap_analysis = assessment['gap_analysis']
                    
                    if gap_analysis['matching_skills']:
                        for skill in gap_analysis['matching_skills']:
                            st.success(f"✓ {skill.title()}")
                    else:
                        st.info("No matching skills found in the basic skill set")
                    
                    if gap_analysis['extra_skills']:
                        st.subheader("🌟 Additional Skills")
                        for skill in gap_analysis['extra_skills']:
                            st.info(f"+ {skill.title()}")
                
                with col2:
                    st.subheader("❌ Skills to Develop")
                    
                    if gap_analysis['missing_skills']:
                        for skill in gap_analysis['missing_skills']:
                            st.error(f"✗ {skill.title()}")
                    else:
                        st.success("Great! You have all the required skills.")
                
                # Improvement suggestions
                if assessment['suggestions']:
                    st.subheader("💡 Improvement Suggestions")
                    
                    for suggestion in assessment['suggestions']:
                        with st.expander(f"📚 Learn {suggestion['skill'].title()} ({suggestion['priority']} Priority)"):
                            
                            st.write(f"**Category:** {suggestion['category'].title()}")
                            
                            st.write("**Recommended Courses:**")
                            for course in suggestion['courses']:
                                st.write(f"• {course}")
                            
                            st.write("**Learning Path:**")
                            for i, step in enumerate(suggestion['learning_path'], 1):
                                st.write(f"{i}. {step}")
                
                # Match percentage
                match_pct = gap_analysis['match_percentage']
                st.subheader(f"📈 Skill Match: {match_pct:.1f}%")
                
                if match_pct >= 80:
                    st.success("Excellent match! You're well-qualified for this role.")
                elif match_pct >= 60:
                    st.warning("Good match! Consider developing a few more skills.")
                else:
                    st.error("Consider gaining more relevant skills before applying.")


if __name__ == "__main__":
    main()