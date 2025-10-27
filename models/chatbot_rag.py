# ============================================================================
# EXPERIMENT 9 MODULE - RAG Chatbot
# Add this to a new file: models/chatbot_rag.py
# ============================================================================

from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory

class RAGChatbot:
    """RAG-based chatbot for job matching Q&A"""

    def __init__(self, openai_api_key=None):
        self.api_key = openai_api_key
        self.vectorstore = None
        self.llm = None
        self.qa_chain = None
        if openai_api_key:
            self.initialize_llm(openai_api_key)

    def initialize_llm(self, api_key):
        """Initialize LLM with API key"""
        self.api_key = api_key
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.7,
            openai_api_key=api_key
        )

    def create_vectorstore(self, resume_text, jd_text):
        """Create FAISS vectorstore from documents"""
        if not self.api_key:
            return {"success": False, "error": "API key not initialized"}

        try:
            # Combine documents
            combined_text = f"RESUME:\n{resume_text}\n\nJOB DESCRIPTION:\n{jd_text}"

            # Split text into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len
            )
            chunks = text_splitter.split_text(combined_text)

            # Create embeddings and vectorstore
            embeddings = OpenAIEmbeddings(openai_api_key=self.api_key)
            self.vectorstore = FAISS.from_texts(chunks, embeddings)

            return {"success": True, "chunks": len(chunks)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def initialize_qa_chain(self, similarity_score, chat_history=[]):
        """Initialize conversational retrieval chain"""
        if not self.vectorstore or not self.llm:
            return {"success": False, "error": "Vectorstore or LLM not initialized"}

        try:
            # System context
            system_context = f"""You are an intelligent recruitment assistant chatbot. You help candidates and recruiters 
understand job-candidate matches.

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
"""

            # Create memory
            memory = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True,
                output_key="answer"
            )

            # Add previous history to memory
            for msg in chat_history:
                if msg['role'] == 'user':
                    memory.chat_memory.add_user_message(msg['content'])
                else:
                    memory.chat_memory.add_ai_message(msg['content'])

            # Create chain
            self.qa_chain = ConversationalRetrievalChain.from_llm(
                llm=self.llm,
                retriever=self.vectorstore.as_retriever(search_kwargs={"k": 3}),
                memory=memory,
                return_source_documents=True,
                verbose=False
            )

            return {"success": True, "system_context": system_context}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_response(self, user_query, system_context):
        """Get chatbot response for user query"""
        if not self.qa_chain:
            return {"success": False, "error": "QA chain not initialized"}

        try:
            # Enhanced query with system context
            enhanced_query = f"{system_context}\n\nUser Question: {user_query}"

            # Get response
            response = self.qa_chain({"question": enhanced_query})

            return {
                "success": True,
                "answer": response['answer'],
                "source_documents": response.get('source_documents', [])
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

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
