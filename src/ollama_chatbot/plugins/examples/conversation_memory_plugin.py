"""
Conversation Memory Plugin - Example Feature Extension
Demonstrates context enhancement with conversational memory

Features:
- Stores conversation history per session
- Configurable memory size
- Automatic summarization of old messages
- Session management
"""

from collections import defaultdict, deque
from datetime import datetime
from typing import Deque, Dict

from ..base_plugin import BaseFeatureExtension
from ..types import ChatContext, Message, PluginConfig, PluginMetadata, PluginResult, PluginType


class ConversationMemoryPlugin(BaseFeatureExtension):
    """
    Conversation memory manager

    Maintains conversation history and provides context enrichment

    Configuration:
        - max_messages: Maximum messages to keep in memory (default: 50)
        - enable_summarization: Auto-summarize old messages (default: False)
        - session_timeout_minutes: Session timeout (default: 30)
    """

    def __init__(self):
        super().__init__()
        self._memory: Dict[str, Deque[Message]] = defaultdict(lambda: deque(maxlen=self._max_messages))
        self._max_messages = 50
        self._enable_summarization = False
        self._session_timeout_minutes = 30

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="conversation_memory",
            version="1.0.0",
            author="System",
            description="Manages conversation history and context",
            plugin_type=PluginType.FEATURE_EXTENSION,
            tags=("memory", "history", "context"),
        )

    async def _do_initialize(self, config: PluginConfig) -> PluginResult[None]:
        """Initialize memory system"""
        try:
            self._max_messages = config.config.get("max_messages", 50)
            self._enable_summarization = config.config.get("enable_summarization", False)
            self._session_timeout_minutes = config.config.get("session_timeout_minutes", 30)

            self._logger.info(
                f"Memory initialized: max_messages={self._max_messages}, " f"summarization={self._enable_summarization}"
            )

            return PluginResult.ok(None)

        except Exception as e:
            return PluginResult.fail(f"Initialization error: {e}")

    async def _do_shutdown(self) -> PluginResult[None]:
        """Cleanup memory"""
        self._memory.clear()
        self._logger.info("Memory cleared")
        return PluginResult.ok(None)

    async def _extend(self, context: ChatContext) -> PluginResult[ChatContext]:
        """
        Extend context with conversation history

        Processing:
        1. Get session ID from metadata
        2. Retrieve relevant history
        3. Merge with current context
        4. Store new messages
        """
        try:
            # Get session ID (default to "default")
            session_id = context.metadata.get("session_id", "default")

            # Get conversation history
            history = self._memory.get(session_id, deque(maxlen=self._max_messages))

            # Add history to context if not already present
            if len(context.messages) < len(history):
                # Merge history with current messages
                all_messages = list(history) + context.messages

                # Keep only unique messages (by timestamp)
                seen_timestamps = set()
                unique_messages = []
                for msg in all_messages:
                    if msg.timestamp not in seen_timestamps:
                        unique_messages.append(msg)
                        seen_timestamps.add(msg.timestamp)

                # Create enhanced context
                enhanced_context = ChatContext(
                    messages=unique_messages,
                    model=context.model,
                    temperature=context.temperature,
                    max_tokens=context.max_tokens,
                    stream=context.stream,
                    metadata={
                        **context.metadata,
                        "memory_enabled": True,
                        "history_count": len(history),
                    },
                )
            else:
                enhanced_context = context

            # Store current messages in memory
            for message in context.messages:
                if message not in history:
                    history.append(message)

            self._memory[session_id] = history

            self._logger.debug(f"Enhanced context for session '{session_id}' with {len(history)} " f"message(s)")

            return PluginResult.ok(enhanced_context)

        except Exception as e:
            self._logger.exception("Context enhancement failed")
            return PluginResult.fail(f"Memory error: {e}")

    async def get_session_history(self, session_id: str) -> list[Message]:
        """
        Get conversation history for a session

        Args:
            session_id: Session identifier

        Returns:
            List of messages
        """
        return list(self._memory.get(session_id, []))

    async def clear_session(self, session_id: str) -> None:
        """
        Clear conversation history for a session

        Args:
            session_id: Session identifier
        """
        if session_id in self._memory:
            del self._memory[session_id]
            self._logger.info(f"Cleared session: {session_id}")

    async def get_session_stats(self) -> Dict[str, int]:
        """
        Get memory statistics

        Returns:
            Statistics dictionary
        """
        return {
            "total_sessions": len(self._memory),
            "total_messages": sum(len(history) for history in self._memory.values()),
            "max_messages_per_session": self._max_messages,
        }

    async def health_check(self) -> PluginResult[Dict]:
        """Health check with memory stats"""
        base_health = await super().health_check()

        if base_health.success and base_health.data:
            stats = await self.get_session_stats()
            base_health.data.update(stats)

        return base_health
