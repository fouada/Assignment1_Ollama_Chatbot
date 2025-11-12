"""
RAG (Retrieval Augmented Generation) Plugin - Advanced Feature Extension
Demonstrates context enhancement with external knowledge retrieval

Features:
- Document embedding and storage
- Semantic search
- Context injection
- Relevance scoring
- Mock implementation (production would use vector DB like Chroma, Pinecone)
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple

from ..base_plugin import BaseFeatureExtension
from ..types import ChatContext, Message, PluginConfig, PluginMetadata, PluginResult, PluginType


@dataclass
class Document:
    """Document with embedding"""

    id: str
    content: str
    metadata: Dict
    embedding: List[float] = None  # In production: actual embeddings


class SimpleVectorStore:
    """
    Simple in-memory vector store (mock implementation)

    Production version would use:
    - ChromaDB
    - Pinecone
    - Weaviate
    - FAISS
    """

    def __init__(self):
        self.documents: Dict[str, Document] = {}

    def add_document(self, doc: Document) -> None:
        """Add document to store"""
        self.documents[doc.id] = doc

    def search(self, query: str, top_k: int = 3) -> List[Document]:
        """
        Search for relevant documents

        Production implementation would:
        1. Embed query
        2. Calculate cosine similarity
        3. Return top-k matches

        Mock implementation: Simple keyword matching
        """
        query_lower = query.lower()
        scored_docs = []

        for doc in self.documents.values():
            # Simple relevance score based on keyword matching
            score = sum(word in doc.content.lower() for word in query_lower.split())
            scored_docs.append((score, doc))

        # Sort by score and return top-k
        scored_docs.sort(key=lambda x: x[0], reverse=True)
        return [doc for score, doc in scored_docs[:top_k] if score > 0]


class RAGPlugin(BaseFeatureExtension):
    """
    RAG (Retrieval Augmented Generation) plugin

    Enhances chat context with relevant external knowledge

    Configuration:
        - enable_rag: Enable RAG (default: True)
        - top_k: Number of documents to retrieve (default: 3)
        - knowledge_base_path: Path to knowledge base (optional)
        - relevance_threshold: Minimum relevance score (default: 0.5)
    """

    def __init__(self):
        super().__init__()
        self._vector_store = SimpleVectorStore()
        self._enable_rag = True
        self._top_k = 3
        self._relevance_threshold = 0.5

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="rag",
            version="1.0.0",
            author="System",
            description="Retrieval Augmented Generation for context enhancement",
            plugin_type=PluginType.FEATURE_EXTENSION,
            tags=("rag", "retrieval", "knowledge", "embeddings"),
        )

    async def _do_initialize(self, config: PluginConfig) -> PluginResult[None]:
        """Initialize RAG system"""
        try:
            self._enable_rag = config.config.get("enable_rag", True)
            self._top_k = config.config.get("top_k", 3)
            self._relevance_threshold = config.config.get("relevance_threshold", 0.5)

            # Load knowledge base if path provided
            kb_path = config.config.get("knowledge_base_path")
            if kb_path:
                await self._load_knowledge_base(kb_path)

            # Add some default documents for demonstration
            await self._load_default_documents()

            self._logger.info(
                f"RAG initialized: {len(self._vector_store.documents)} documents, " f"top_k={self._top_k}"
            )

            return PluginResult.ok(None)

        except Exception as e:
            return PluginResult.fail(f"Initialization error: {e}")

    async def _do_shutdown(self) -> PluginResult[None]:
        """Cleanup"""
        self._vector_store.documents.clear()
        self._logger.info("RAG system shutdown")
        return PluginResult.ok(None)

    async def _extend(self, context: ChatContext) -> PluginResult[ChatContext]:
        """
        Extend context with retrieved documents

        Process:
        1. Extract query from last user message
        2. Retrieve relevant documents
        3. Inject as system message
        4. Return enhanced context
        """
        try:
            if not self._enable_rag or not context.messages:
                return PluginResult.ok(context)

            # Get last user message as query
            user_messages = [msg for msg in context.messages if msg.role == "user"]
            if not user_messages:
                return PluginResult.ok(context)

            query = user_messages[-1].content

            # Retrieve relevant documents
            relevant_docs = self._vector_store.search(query, top_k=self._top_k)

            if not relevant_docs:
                self._logger.debug("No relevant documents found")
                return PluginResult.ok(context)

            # Format retrieved context
            context_text = self._format_retrieved_context(relevant_docs)

            # Create system message with retrieved context
            rag_message = Message(
                content=f"Relevant context from knowledge base:\n\n{context_text}",
                role="system",
                metadata={
                    "rag_enhanced": True,
                    "num_documents": len(relevant_docs),
                },
            )

            # Insert RAG message before last user message
            enhanced_messages = context.messages[:-1] + [rag_message, context.messages[-1]]

            # Create enhanced context
            enhanced_context = ChatContext(
                messages=enhanced_messages,
                model=context.model,
                temperature=context.temperature,
                max_tokens=context.max_tokens,
                stream=context.stream,
                metadata={
                    **context.metadata,
                    "rag_enabled": True,
                    "retrieved_docs": len(relevant_docs),
                },
            )

            self._logger.info(f"Enhanced context with {len(relevant_docs)} document(s)")

            return PluginResult.ok(enhanced_context)

        except Exception as e:
            self._logger.exception("RAG enhancement failed")
            return PluginResult.fail(f"RAG error: {e}")

    def _format_retrieved_context(self, docs: List[Document]) -> str:
        """Format retrieved documents for injection"""
        formatted = []

        for i, doc in enumerate(docs, 1):
            formatted.append(f"[Document {i}]")
            formatted.append(doc.content)
            formatted.append("")  # Blank line

        return "\n".join(formatted)

    async def _load_knowledge_base(self, path: str) -> None:
        """
        Load knowledge base from file

        Production implementation would:
        - Read documents from file/database
        - Generate embeddings
        - Store in vector database
        """
        # Mock implementation
        self._logger.info(f"Loading knowledge base from {path}")
        # In production: implement actual loading

    async def _load_default_documents(self) -> None:
        """Load some default documents for demonstration"""
        default_docs = [
            Document(
                id="doc1",
                content="Python is a high-level, interpreted programming language known for its simplicity and readability.",
                metadata={"source": "python_docs", "topic": "programming"},
            ),
            Document(
                id="doc2",
                content="Machine learning is a subset of artificial intelligence that enables systems to learn from data.",
                metadata={"source": "ml_guide", "topic": "ai"},
            ),
            Document(
                id="doc3",
                content="REST APIs use HTTP methods like GET, POST, PUT, and DELETE for resource operations.",
                metadata={"source": "api_docs", "topic": "web"},
            ),
            Document(
                id="doc4",
                content="Docker containers provide lightweight virtualization for application deployment.",
                metadata={"source": "devops_guide", "topic": "infrastructure"},
            ),
            Document(
                id="doc5",
                content="Ollama is a tool for running large language models locally on your machine.",
                metadata={"source": "ollama_docs", "topic": "ai"},
            ),
        ]

        for doc in default_docs:
            self._vector_store.add_document(doc)

    async def add_document(self, content: str, metadata: Dict = None) -> str:
        """
        Add document to knowledge base

        Args:
            content: Document content
            metadata: Optional metadata

        Returns:
            Document ID
        """
        doc_id = f"doc_{len(self._vector_store.documents) + 1}"
        doc = Document(id=doc_id, content=content, metadata=metadata or {})
        self._vector_store.add_document(doc)
        self._logger.info(f"Added document: {doc_id}")
        return doc_id

    async def health_check(self) -> PluginResult[Dict]:
        """Health check with RAG stats"""
        base_health = await super().health_check()

        if base_health.success and base_health.data:
            base_health.data.update(
                {
                    "document_count": len(self._vector_store.documents),
                    "top_k": self._top_k,
                    "rag_enabled": self._enable_rag,
                }
            )

        return base_health
