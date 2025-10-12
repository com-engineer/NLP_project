class SkillGapAnalyzer:
    """Analyzes skill gaps and provides improvement suggestions"""
    
    def __init__(self):
        self.skill_database = {
            'programming': ['python', 'java', 'javascript', 'c++'],
            'web_development': ['html', 'css', 'react', 'angular'],
            'databases': ['sql', 'mysql', 'postgresql', 'mongodb'],
            'cloud': ['aws', 'azure', 'docker', 'kubernetes'],
            'data_science': ['pandas', 'numpy', 'scikit-learn', 'tensorflow']
        }
        
        self.course_recommendations = {
            'python': ['Python for Everybody - Coursera', 'Complete Python Bootcamp - Udemy'],
            'machine learning': ['ML Course - Andrew Ng', 'Hands-On ML - Udemy'],
            'aws': ['AWS Solutions Architect - A Cloud Guru']
        }
    
    def analyze_skill_gaps(self, resume_skills, jd_skills):
        missing_skills = [skill for skill in jd_skills if skill not in resume_skills]
        matching_skills = [skill for skill in jd_skills if skill in resume_skills]
        
        return {
            'missing_skills': missing_skills,
            'matching_skills': matching_skills,
            'match_percentage': len(matching_skills) / len(jd_skills) * 100 if jd_skills else 0
        }
    
    def get_improvement_suggestions(self, missing_skills):
        suggestions = []
        for skill in missing_skills:
            courses = self.course_recommendations.get(skill.lower(), [f"Search for '{skill}' courses"])
            suggestions.append({
                'skill': skill,
                'priority': 'High' if skill.lower() in ['python', 'sql'] else 'Medium',
                'courses': courses
            })
        return suggestions
