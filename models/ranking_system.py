from models.file_handler import ResumeFileHandler
from models.text_processor import TextPreprocessor
from models.semantic_analyzer import SemanticAnalyzer


class ResumeRankingSystem:
    """Complete resume ranking system"""

    def __init__(self):
        self.file_handler = ResumeFileHandler()
        self.preprocessor = TextPreprocessor()
        self.analyzer = SemanticAnalyzer()

    def process_single_resume(self, file_path=None, file_content=None, file_extension=None):
        """Process a single resume file"""
        try:
            # Extract text
            raw_text = self.file_handler.extract_text_from_file(
                file_path=file_path,
                file_content=file_content,
                file_extension=file_extension
            )

            # Preprocess text
            cleaned_text = self.preprocessor.clean_text(raw_text)
            processed_text = self.preprocessor.preprocess_text(cleaned_text)

            # Extract features
            email = self.preprocessor.extract_email(raw_text)
            phone = self.preprocessor.extract_phone(raw_text)
            skills = self.preprocessor.extract_skills(raw_text)

            return {
                'raw_text': raw_text,
                'cleaned_text': cleaned_text,
                'processed_text': processed_text,
                'email': email,
                'phone': phone,
                'skills': skills,
                'success': True
            }
        except Exception as e:
            return {
                'error': str(e),
                'success': False
            }

    def rank_resumes(self, resume_files, job_description):
        """Rank multiple resumes against job description"""
        results = []

        for i, resume_file in enumerate(resume_files):
            print(f"Processing resume {i+1}/{len(resume_files)}")

            # Process resume
            if isinstance(resume_file, dict):
                # File already processed
                result = resume_file
            else:
                # Process file
                result = self.process_single_resume(file_path=resume_file)

            if not result['success']:
                print(f"Failed to process resume {i+1}: {result['error']}")
                continue

            # Calculate similarity
            similarity = self.analyzer.calculate_similarity(
                result['processed_text'],
                job_description
            )

            # Add ranking information
            result['similarity_score'] = similarity
            result['rank'] = None  # Will be set after sorting
            results.append(result)

        # Sort by similarity score
        results.sort(key=lambda x: x['similarity_score'], reverse=True)

        # Assign ranks
        for i, result in enumerate(results):
            result['rank'] = i + 1
            result['match_level'] = self.get_match_level(result['similarity_score'])

        return results

    def get_match_level(self, score):
        """Determine match level based on similarity score"""
        if score > 0.7:
            return "Excellent Match"
        elif score > 0.5:
            return "Good Match"
        elif score > 0.3:
            return "Fair Match"
        else:
            return "Poor Match"

    def create_ranking_report(self, results, job_description):
        """Create a detailed ranking report"""
        report = {
            'job_description': job_description,
            'total_resumes': len(results),
            'ranking_summary': [],
            'detailed_results': results
        }

        for result in results:
            summary = {
                'rank': result['rank'],
                'similarity_score': round(result['similarity_score'], 3),
                'match_level': result['match_level'],
                'email': result.get('email', ['Not found'])[0] if result.get('email') else 'Not found',
                'skills_count': len(result.get('skills', [])),
                'top_skills': result.get('skills', [])[:5]
            }
            report['ranking_summary'].append(summary)

        return report

    def visualize_results(self, results):
        """Create visualizations for ranking results"""
        if not results:
            print("No results to visualize")
            return

        # Extract data for visualization
        ranks = [r['rank'] for r in results]
        scores = [r['similarity_score'] for r in results]
        match_levels = [r['match_level'] for r in results]

        # Create subplots
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))

        # 1. Similarity scores bar plot
        axes[0, 0].bar(ranks, scores, color='skyblue')
        axes[0, 0].set_title('Resume Similarity Scores')
        axes[0, 0].set_xlabel('Resume Rank')
        axes[0, 0].set_ylabel('Similarity Score')

        # 2. Match level distribution
        match_counts = {}
        for level in match_levels:
            match_counts[level] = match_counts.get(level, 0) + 1

        axes[0, 1].pie(match_counts.values(), labels=match_counts.keys(), autopct='%1.1f%%')
        axes[0, 1].set_title('Match Level Distribution')

        # 3. Skills distribution
        all_skills = []
        for result in results:
            all_skills.extend(result.get('skills', []))

        skill_counts = {}
        for skill in all_skills:
            skill_counts[skill] = skill_counts.get(skill, 0) + 1

        top_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        skills_names = [s[0] for s in top_skills]
        skills_counts = [s[1] for s in top_skills]

        axes[1, 0].barh(skills_names, skills_counts, color='lightgreen')
        axes[1, 0].set_title('Top 10 Skills Across Resumes')
        axes[1, 0].set_xlabel('Frequency')

        # 4. Score distribution histogram
        axes[1, 1].hist(scores, bins=10, color='orange', alpha=0.7)
        axes[1, 1].set_title('Similarity Score Distribution')
        axes[1, 1].set_xlabel('Similarity Score')
        axes[1, 1].set_ylabel('Frequency')

        plt.tight_layout()
        plt.show()