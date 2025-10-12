from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class SemanticAnalyzer:
    """Handles semantic similarity analysis using BERT"""

    def __init__(self, model_name='all-mpnet-base-v2'):
        """Initialize BERT model"""
        try:
            self.sbert_model = SentenceTransformer(model_name)
            print(f"Loaded SBERT model: {model_name}")
        except Exception as e:
            print(f"Error loading SBERT model: {e}")
            self.sbert_model = None

    def encode_text(self, texts):
        """Encode texts to embeddings"""
        if self.sbert_model is None:
            raise ValueError("SBERT model not available")

        if isinstance(texts, str):
            texts = [texts]

        embeddings = self.sbert_model.encode(texts)
        return embeddings

    def calculate_similarity(self, text1, text2):
        """Calculate cosine similarity between two texts"""
        embeddings1 = self.encode_text([text1])
        embeddings2 = self.encode_text([text2])

        similarity = cosine_similarity(embeddings1, embeddings2)[0][0]
        return similarity

    def calculate_batch_similarity(self, resumes, job_description):
        """Calculate similarity for multiple resumes"""
        job_embedding = self.encode_text([job_description])
        resume_embeddings = self.encode_text(resumes)

        similarities = cosine_similarity(resume_embeddings, job_embedding).flatten()
        return similarities

    def calculate_section_similarity(self, resume_text, jd_text):
        """Calculate similarity by sections with weights"""
        # Split into sections
        resume_sections = self.extract_sections(resume_text)
        jd_sections = self.extract_sections(jd_text)

        # Section weights
        weights = {
            'skills': 0.4,
            'experience': 0.3,
            'education': 0.2,
            'other': 0.1
        }

        total_similarity = 0
        for section, weight in weights.items():
            if section in resume_sections and section in jd_sections:
                similarity = self.calculate_similarity(
                    resume_sections[section],
                    jd_sections[section]
                )
                total_similarity += similarity * weight

        return total_similarity

    def extract_sections(self, text):
        """Basic section extraction"""
        sections = {'skills': '', 'experience': '', 'education': '', 'other': ''}

        # Simple keyword-based section detection
        lines = text.split('\n')
        current_section = 'other'

        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in ['skill', 'technical', 'competenc']):
                current_section = 'skills'
            elif any(keyword in line_lower for keyword in ['experience', 'work', 'employ']):
                current_section = 'experience'
            elif any(keyword in line_lower for keyword in ['education', 'degree', 'university']):
                current_section = 'education'

            sections[current_section] += line + ' '

        return sections
