#!/usr/bin/env python3
"""
Test suite for AI Assistant with RAG.
Tests question answering, document retrieval, and knowledge base management.
"""

import sys
import tempfile
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.ai_assistant import (
    AIAssistant, Document, RAGResult, AIResponse,
    DocumentStore, EmbeddingModel, LLMModel, RAGSystem,
    ask_ai_assistant
)


def test_document_creation():
    """Test Document creation."""
    print("🧪 Testing Document Creation...")
    
    try:
        doc = Document(
            id="test_doc",
            title="Test Document",
            content="This is a test document with some content about accounting and audit procedures.",
            source="Test Source",
            metadata={"category": "test", "level": "basic"}
        )
        
        assert doc.id == "test_doc"
        assert doc.title == "Test Document"
        assert "accounting" in doc.content
        assert doc.source == "Test Source"
        assert doc.metadata["category"] == "test"
        
        print("✅ Document creation working")
        print(f"   ID: {doc.id}")
        print(f"   Title: {doc.title}")
        print(f"   Content length: {len(doc.content)}")
        print(f"   Source: {doc.source}")
        return True
        
    except Exception as e:
        print(f"❌ Document creation failed: {e}")
        return False


def test_document_store():
    """Test DocumentStore functionality."""
    print("🧪 Testing Document Store...")
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = DocumentStore(Path(temp_dir))
            
            # Test adding document
            doc = Document(
                id="test_doc_1",
                title="Test Document 1",
                content="This is test content for document 1.",
                source="Test Source 1"
            )
            
            store.add_document(doc)
            assert len(store.documents) == 1
            assert "test_doc_1" in store.documents
            
            # Test retrieving document
            retrieved_doc = store.get_document("test_doc_1")
            assert retrieved_doc is not None
            assert retrieved_doc.title == "Test Document 1"
            
            # Test searching documents
            results = store.search_documents("test content", limit=5)
            assert len(results) >= 1
            assert results[0].id == "test_doc_1"
            
            print("✅ Document store working")
            print(f"   Documents stored: {len(store.documents)}")
            print(f"   Search results: {len(results)}")
            return True
        
    except Exception as e:
        print(f"❌ Document store test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_embedding_model():
    """Test EmbeddingModel functionality."""
    print("🧪 Testing Embedding Model...")
    
    try:
        model = EmbeddingModel()
        
        # Test encoding
        texts = ["This is a test sentence.", "Another test sentence."]
        embeddings = model.encode(texts)
        
        assert len(embeddings) == 2
        assert len(embeddings[0]) > 0  # Should have some dimensions
        assert len(embeddings[1]) > 0
        
        print("✅ Embedding model working")
        print(f"   Model name: {model.model_name}")
        print(f"   Embedding dimensions: {len(embeddings[0])}")
        print(f"   Texts encoded: {len(texts)}")
        return True
        
    except Exception as e:
        print(f"❌ Embedding model test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_llm_model():
    """Test LLMModel functionality."""
    print("🧪 Testing LLM Model...")
    
    try:
        model = LLMModel()
        
        # Test text generation
        prompt = "What is accounting?"
        response = model.generate(prompt, max_length=100, temperature=0.7)
        
        assert response is not None
        assert len(response) > 0
        
        print("✅ LLM model working")
        print(f"   Model name: {model.model_name}")
        print(f"   Prompt: {prompt[:50]}...")
        print(f"   Response: {response[:100]}...")
        return True
        
    except Exception as e:
        print(f"❌ LLM model test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_rag_system():
    """Test RAGSystem functionality."""
    print("🧪 Testing RAG System...")
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            rag = RAGSystem(Path(temp_dir))
            
            # Add test documents
            doc1 = Document(
                id="audit_doc",
                title="Audit Procedures",
                content="Audit procedures include testing controls, substantive testing, and analytical procedures. The auditor must obtain sufficient appropriate audit evidence.",
                source="Audit Manual"
            )
            
            doc2 = Document(
                id="accounting_doc",
                title="Accounting Principles",
                content="Accounting principles include going concern, accrual basis, and materiality. Financial statements must be prepared in accordance with applicable standards.",
                source="Accounting Standards"
            )
            
            rag.document_store.add_document(doc1)
            rag.document_store.add_document(doc2)
            
            # Test search
            results = rag.search("audit procedures", top_k=2)
            assert len(results) >= 1
            
            # Test answer generation
            answer = rag.generate_answer("What are audit procedures?", results)
            assert answer is not None
            assert len(answer) > 0
            
            print("✅ RAG system working")
            print(f"   Documents: {len(rag.document_store.documents)}")
            print(f"   Search results: {len(results)}")
            print(f"   Answer length: {len(answer)}")
            return True
        
    except Exception as e:
        print(f"❌ RAG system test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ai_assistant_initialization():
    """Test AIAssistant initialization."""
    print("🧪 Testing AI Assistant Initialization...")
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            assistant = AIAssistant(Path(temp_dir))
            
            assert assistant.store_dir == Path(temp_dir)
            assert assistant.rag_system is not None
            assert len(assistant.rag_system.document_store.documents) > 0  # Should have default docs
            
            print("✅ AI Assistant initialization working")
            print(f"   Store directory: {assistant.store_dir}")
            print(f"   Documents loaded: {len(assistant.rag_system.document_store.documents)}")
            return True
        
    except Exception as e:
        print(f"❌ AI Assistant initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_question_answering():
    """Test question answering functionality."""
    print("🧪 Testing Question Answering...")
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            assistant = AIAssistant(Path(temp_dir))
            
            # Test asking a question
            question = "Co to jest audyt?"
            response = assistant.ask_question(question, top_k=3)
            
            assert response is not None
            assert response.question == question
            assert response.answer is not None
            assert len(response.answer) > 0
            assert response.confidence >= 0.0
            assert response.response_time > 0.0
            assert response.model_used is not None
            
            print("✅ Question answering working")
            print(f"   Question: {question}")
            print(f"   Answer: {response.answer[:100]}...")
            print(f"   Confidence: {response.confidence:.2f}")
            print(f"   Response time: {response.response_time:.2f}s")
            print(f"   Sources: {len(response.sources)}")
            return True
        
    except Exception as e:
        print(f"❌ Question answering test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_document_addition():
    """Test adding documents to knowledge base."""
    print("🧪 Testing Document Addition...")
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            assistant = AIAssistant(Path(temp_dir))
            
            initial_count = len(assistant.rag_system.document_store.documents)
            
            # Add new document
            new_doc = Document(
                id="custom_doc",
                title="Custom Document",
                content="This is a custom document about financial analysis and risk assessment procedures.",
                source="Custom Source",
                metadata={"category": "custom", "level": "advanced"}
            )
            
            assistant.add_document(new_doc)
            
            # Check if document was added
            final_count = len(assistant.rag_system.document_store.documents)
            assert final_count == initial_count + 1
            
            # Test if document can be found
            retrieved_doc = assistant.rag_system.document_store.get_document("custom_doc")
            assert retrieved_doc is not None
            assert retrieved_doc.title == "Custom Document"
            
            print("✅ Document addition working")
            print(f"   Initial documents: {initial_count}")
            print(f"   Final documents: {final_count}")
            print(f"   Added document: {new_doc.title}")
            return True
        
    except Exception as e:
        print(f"❌ Document addition test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_knowledge_stats():
    """Test knowledge base statistics."""
    print("🧪 Testing Knowledge Base Statistics...")
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            assistant = AIAssistant(Path(temp_dir))
            
            stats = assistant.get_knowledge_stats()
            
            assert "total_documents" in stats
            assert "total_embeddings" in stats
            assert "store_directory" in stats
            assert "embedding_model" in stats
            assert "llm_model" in stats
            
            assert stats["total_documents"] > 0
            assert stats["total_embeddings"] >= 0
            
            print("✅ Knowledge base statistics working")
            print(f"   Total documents: {stats['total_documents']}")
            print(f"   Total embeddings: {stats['total_embeddings']}")
            print(f"   Store directory: {stats['store_directory']}")
            print(f"   Embedding model: {stats['embedding_model']}")
            print(f"   LLM model: {stats['llm_model']}")
            return True
        
    except Exception as e:
        print(f"❌ Knowledge base statistics test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_convenience_function():
    """Test convenience function."""
    print("🧪 Testing Convenience Function...")
    
    try:
        # Test convenience function
        question = "Jakie są podstawy audytu?"
        response = ask_ai_assistant(question, top_k=2)
        
        assert response is not None
        assert response.question == question
        assert response.answer is not None
        assert len(response.answer) > 0
        
        print("✅ Convenience function working")
        print(f"   Question: {question}")
        print(f"   Answer: {response.answer[:100]}...")
        print(f"   Confidence: {response.confidence:.2f}")
        return True
        
    except Exception as e:
        print(f"❌ Convenience function test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_polish_questions():
    """Test Polish language questions."""
    print("🧪 Testing Polish Language Questions...")
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            assistant = AIAssistant(Path(temp_dir))
            
            polish_questions = [
                "Co to jest audyt finansowy?",
                "Jak walidować faktury?",
                "Co to jest KRS?",
                "Jak oceniać ryzyko w audycie?",
                "Co to jest biała lista VAT?"
            ]
            
            for question in polish_questions:
                response = assistant.ask_question(question, top_k=2)
                
                assert response is not None
                assert response.answer is not None
                assert len(response.answer) > 0
                
                print(f"   Q: {question}")
                print(f"   A: {response.answer[:80]}...")
                print(f"   Confidence: {response.confidence:.2f}")
                print()
            
            print("✅ Polish language questions working")
            return True
        
    except Exception as e:
        print(f"❌ Polish language questions test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all AI Assistant tests."""
    print("🚀 Starting AI Assistant Test Suite...")
    print("=" * 60)
    
    tests = [
        test_document_creation,
        test_document_store,
        test_embedding_model,
        test_llm_model,
        test_rag_system,
        test_ai_assistant_initialization,
        test_question_answering,
        test_document_addition,
        test_knowledge_stats,
        test_convenience_function,
        test_polish_questions
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            failed += 1
        print()
    
    print("=" * 60)
    print(f"📊 AI Assistant Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All AI Assistant tests passed!")
        return 0
    else:
        print("❌ Some AI Assistant tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())

