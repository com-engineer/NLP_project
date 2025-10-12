import re
import spacy


class TextPreprocessor:
    """Handles text preprocessing for semantic analysis"""

    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("spaCy model not found. Using basic preprocessing.")
            self.nlp = None

    def clean_text(self, text):
        """Basic text cleaning"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)

        # Remove special characters but keep important ones
        text = re.sub(r'[^\w\s@.-]', ' ', text)

        # Remove extra newlines
        text = re.sub(r'\n+', '\n', text)

        return text.strip()

    def preserve_phrases(self, text):
        """Preserve multi-word technical phrases"""
        phrases = {
            'machine learning': 'machinelearning',
            'deep learning': 'deeplearning',
            'data science': 'datascience',
            'computer science': 'computerscience',
            'software engineer': 'softwareengineer',
            'full stack': 'fullstack',
            'front end': 'frontend',
            'back end': 'backend'
        }

        for phrase, replacement in phrases.items():
            text = text.replace(phrase, replacement)

        return text

    def preprocess_text(self, text):
        """Improved preprocessing that preserves semantic meaning"""

        # Clean text
        cleaned_text = self.clean_text(text)

        # Preserve important phrases
        cleaned_text = self.preserve_phrases(cleaned_text)

        if self.nlp:
            doc = self.nlp(cleaned_text)
            tokens = []

            for token in doc:
                # Keep more tokens for better semantic analysis
                if not token.is_stop and not token.is_punct and len(token.text) > 1:
                    tokens.append(token.lemma_.lower())

            return ' '.join(tokens)
        else:
            return cleaned_text.lower()

    def extract_email(self, text):
        """Extract email addresses"""
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
        return emails

    def extract_phone(self, text):
        """Extract phone numbers"""
        phones = re.findall(r'[\+]?[1-9]?[0-9]{7,14}', text)
        return phones

    def extract_skills(self, text, skill_list=None):
        """Enhanced skill extraction with synonyms"""

        # Expanded skill database with synonyms
        skill_synonyms = {
            'python': ['python', 'py'],
            'javascript': ['javascript', 'js', 'node.js', 'nodejs', 'react', 'angular', 'vue'],
            'html_css': ['html', 'css', 'markup', 'styling', 'web markup', 'stylesheet'],
            'backend': ['backend', 'server-side', 'api', 'restful', 'microservices'],
            'database': ['sql', 'mysql', 'postgresql', 'mongodb', 'database', 'db'],
            'cloud': ['aws', 'azure', 'gcp', 'cloud', 'docker', 'kubernetes'],
            'git': ['git', 'github', 'version control', 'source control'],
            'machine_learning': ['machine learning', 'ml', 'ai', 'artificial intelligence', 'deep learning']
        }

        text_lower = text.lower()
        found_skills = []

        for main_skill, synonyms in skill_synonyms.items():
            for synonym in synonyms:
                if synonym in text_lower:
                    found_skills.append(main_skill)
                    break  # Avoid duplicates

        return list(set(found_skills))  # Remove duplicates
