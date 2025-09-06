
"""
Local AI Assistant for RTX 4090
RAG-based Q&A system for accounting and auditing questions.
"""

import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import json

try:
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
    from sentence_transformers import SentenceTransformer
    import chromadb
    HAS_AI_LIBS = True
except ImportError:
    HAS_AI_LIBS = False

from .exceptions import ModelLoadError, AuditorException


class LocalAIAssistant:
    """Local AI assistant with RAG capabilities for RTX 4090."""
    
    def __init__(self, config_path: Path):
        self.config_path = config_path
        self.logger = logging.getLogger(__name__)
        self.config = self._load_config()
        
        self.llm_model = None
        self.llm_tokenizer = None
        self.embedding_model = None
        self.vector_db = None
        
        if HAS_AI_LIBS:
            self._initialize_models()
        else:
            self.logger.warning("AI libraries not available. Install: pip install torch transformers sentence-transformers chromadb")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load AI configuration."""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            raise AuditorException(f"Failed to load AI config: {e}")
    
    def _initialize_models(self):
        """Initialize AI models for RTX 4090."""
        try:
            # Initialize LLM with 4-bit quantization
            llm_config = self.config['llm']
            
            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_quant_type="nf4"
            )
            
            self.llm_tokenizer = AutoTokenizer.from_pretrained(
                f"meta-llama/{llm_config['model']}",
                trust_remote_code=True
            )
            
            self.llm_model = AutoModelForCausalLM.from_pretrained(
                f"meta-llama/{llm_config['model']}",
                quantization_config=quantization_config,
                device_map="auto",
                trust_remote_code=True
            )
            
            # Initialize embeddings model
            embedding_config = self.config['embeddings']
            self.embedding_model = SentenceTransformer(
                f"sentence-transformers/{embedding_config['model']}"
            )
            
            # Initialize vector database
            self.vector_db = chromadb.PersistentClient(
                path=str(Path("data/vector_db"))
            )
            
            self.logger.info("AI models initialized successfully")
            
        except Exception as e:
            raise ModelLoadError(f"Failed to initialize AI models: {e}")
    
    def add_documents(self, documents: List[str], metadata: List[Dict] = None):
        """Add documents to the knowledge base."""
        if not self.embedding_model or not self.vector_db:
            raise AuditorException("AI models not initialized")
        
        try:
            # Generate embeddings
            embeddings = self.embedding_model.encode(documents)
            
            # Add to vector database
            collection = self.vector_db.get_or_create_collection("audit_knowledge")
            
            ids = [f"doc_{i}" for i in range(len(documents))]
            metadatas = metadata or [{"source": "audit_data"} for _ in documents]
            
            collection.add(
                embeddings=embeddings.tolist(),
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            self.logger.info(f"Added {len(documents)} documents to knowledge base")
            
        except Exception as e:
            raise AuditorException(f"Failed to add documents: {e}")
    
    def ask_question(self, question: str, context: str = "") -> str:
        """Ask a question using RAG."""
        if not self.llm_model or not self.embedding_model:
            return "AI models not available. Please check installation."
        
        try:
            # Retrieve relevant documents
            relevant_docs = self._retrieve_relevant_documents(question)
            
            # Create context
            context_text = "\n".join(relevant_docs)
            if context:
                context_text = f"{context}\n{context_text}"
            
            # Generate response
            prompt = f"""Context: {context_text}

Question: {question}

Answer:"""
            
            inputs = self.llm_tokenizer(prompt, return_tensors="pt")
            inputs = {k: v.to(self.llm_model.device) for k, v in inputs.items()}
            
            with torch.no_grad():
                outputs = self.llm_model.generate(
                    **inputs,
                    max_new_tokens=self.config['llm']['max_tokens'],
                    temperature=self.config['llm']['temperature'],
                    top_p=self.config['llm']['top_p'],
                    do_sample=True,
                    pad_token_id=self.llm_tokenizer.eos_token_id
                )
            
            response = self.llm_tokenizer.decode(
                outputs[0][inputs['input_ids'].shape[1]:], 
                skip_special_tokens=True
            )
            
            return response.strip()
            
        except Exception as e:
            self.logger.error(f"Failed to generate response: {e}")
            return f"Error generating response: {e}"
    
    def _retrieve_relevant_documents(self, question: str, top_k: int = 5) -> List[str]:
        """Retrieve relevant documents for the question."""
        try:
            # Generate question embedding
            question_embedding = self.embedding_model.encode([question])
            
            # Query vector database
            collection = self.vector_db.get_collection("audit_knowledge")
            results = collection.query(
                query_embeddings=question_embedding.tolist(),
                n_results=top_k
            )
            
            return results['documents'][0] if results['documents'] else []
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve documents: {e}")
            return []
    
    def is_ready(self) -> bool:
        """Check if AI assistant is ready."""
        return (
            self.llm_model is not None and 
            self.embedding_model is not None and 
            self.vector_db is not None
        )


def create_ai_assistant(config_path: Path) -> LocalAIAssistant:
    """Create AI assistant instance."""
    return LocalAIAssistant(config_path)
