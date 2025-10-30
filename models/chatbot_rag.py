# ============================================================================ 
# EXPERIMENT 9 MODULE - RAG Chatbot (GEMINI VERSION, Simplified - No LangChain)
# ============================================================================

import google.generativeai as genai

class RAGChatbot:
    """RAG-based chatbot for job matching Q&A using Google Gemini"""
    
    def __init__(self, gemini_api_key=None):
        self.api_key = gemini_api_key
        self.resume_text = ""
        self.jd_text = ""
        self.similarity_score = 0.0
        self.chat_history = []
        self.model = None
        self.system_context = ""
        
        if gemini_api_key:
            self.initialize_llm(gemini_api_key)
    
    def initialize_llm(self, api_key):
        """Initialize the Gemini LLM"""
        self.api_key = api_key
        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(
                'gemini-2.0-flash-exp',
                generation_config={
                    'temperature': 0.7,
                    'top_p': 0.95,
                    'top_k': 40,
                    'max_output_tokens': 2048,
                }
            )
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def create_vectorstore(self, resume_text, jd_text):
        """Store resume and job description text"""
        if not self.api_key:
            return {"success": False, "error": "API key not initialized"}
        
        try:
            self.resume_text = resume_text
            self.jd_text = jd_text
            
            # Calculate approximate chunks for user feedback
            combined_text = f"RESUME:\n{resume_text}\n\nJOB DESCRIPTION:\n{jd_text}"
            estimated_chunks = len(combined_text) // 1000 + 1
            
            return {"success": True, "chunks": estimated_chunks}
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def initialize_qa_chain(self, similarity_score, chat_history=[]):
        """Initialize conversational context"""
        if not self.resume_text or not self.jd_text:
            return {"success": False, "error": "Resume or Job Description not loaded"}
        
        if not self.model:
            return {"success": False, "error": "Gemini model not initialized"}
        
        try:
            self.similarity_score = similarity_score
            self.chat_history = chat_history
            
            self.system_context = f"""You are an intelligent recruitment assistant chatbot.
You help candidates and recruiters understand job-candidate matches.

You have access to:
1. A candidate's resume
2. A job description
3. Semantic similarity score: {similarity_score:.2%}

Answer questions about:
- How well the resume matches the job
- Skills gaps and missing qualifications
- Recommendations for improving the candidate's profile
- Specific questions about the resume or job requirements
- Career advice and next steps

Be helpful, professional, and provide specific, actionable advice.
Based on the resume and job description provided, give clear and concise answers.
"""
            
            return {"success": True, "system_context": self.system_context}
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_response(self, user_query, system_context=""):
        """Generate a response using Gemini AI"""
        if not self.model:
            return {"success": False, "error": "Model not initialized"}
        
        try:
            # Build the complete context with resume, JD, and conversation history
            context_parts = [
                "=== CONTEXT ===",
                "",
                "RESUME:",
                self.resume_text[:3000],  # Limit to first 3000 chars to stay within token limits
                "",
                "JOB DESCRIPTION:",
                self.jd_text[:3000],
                "",
                f"SIMILARITY SCORE: {self.similarity_score:.2%}",
                "",
                "=== INSTRUCTIONS ===",
                system_context if system_context else self.system_context,
                "",
            ]
            
            # Add conversation history
            if self.chat_history:
                context_parts.append("=== CONVERSATION HISTORY ===")
                for msg in self.chat_history[-5:]:  # Last 5 messages
                    role = "User" if msg['role'] == 'user' else "Assistant"
                    context_parts.append(f"{role}: {msg['content']}")
                context_parts.append("")
            
            # Add current question
            context_parts.extend([
                "=== CURRENT QUESTION ===",
                user_query,
                "",
                "Please provide a clear, professional, and helpful answer based on the resume and job description above."
            ])
            
            full_prompt = "\n".join(context_parts)
            
            # Generate response
            response = self.model.generate_content(full_prompt)
            
            # Extract text from response
            answer_text = response.text if hasattr(response, 'text') else str(response)
            
            return {
                "success": True,
                "answer": answer_text,
                "source_documents": []  # For compatibility with existing code
            }
        
        except Exception as e:
            return {
                "success": False, 
                "error": f"Error generating response: {str(e)}"
            }
    
    def get_sample_questions(self):
        """Return sample questions for candidates and recruiters"""
        return {
            "Candidate": [
                "Does my resume match this job description?",
                "What skills am I missing for this role?",
                "How can I improve my resume for this position?",
                "What courses should I take to be better qualified?",
                "What is my matching score and what does it mean?"
            ],
            "Recruiter": [
                "Is this candidate suitable for the role?",
                "What are the candidate's key strengths?",
                "What experience does the candidate have relevant to this job?",
                "Does the candidate have the required technical skills?",
                "What concerns should I have about this candidate?"
            ]
        }
    
    def clear_history(self):
        """Clear chat history"""
        self.chat_history = []
        return {"success": True, "message": "Chat history cleared"}