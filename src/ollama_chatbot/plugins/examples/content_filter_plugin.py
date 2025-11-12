"""
Content Filter Plugin - Example Message Processor
Demonstrates message processing with profanity filtering

Features:
- Profanity detection and replacement
- Configurable word list
- PII detection (emails, phone numbers)
- Case-insensitive matching
"""

import re
from typing import Set

from ..base_plugin import BaseMessageProcessor
from ..types import ChatContext, Message, PluginConfig, PluginMetadata, PluginResult, PluginType


class ContentFilterPlugin(BaseMessageProcessor):
    """
    Content filter for messages

    Configuration:
        - filter_profanity: Enable profanity filtering (default: True)
        - filter_pii: Enable PII filtering (default: True)
        - custom_words: Additional words to filter (list)
        - replacement: Replacement text (default: "***")
    """

    def __init__(self):
        super().__init__()
        self._profanity_words: Set[str] = set()
        self._filter_profanity = True
        self._filter_pii = True
        self._replacement = "***"

        # Common profanity words (sample - expand as needed)
        self._default_profanity = {
            "damn",
            "hell",
            "crap",
            "bastard",
            # Add more as needed - this is just a sample
        }

        # Regex patterns for PII
        self._email_pattern = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")
        self._phone_pattern = re.compile(r"\b(?:\+?1[-.]?)?\(?([0-9]{3})\)?[-.]?([0-9]{3})[-.]?([0-9]{4})\b")
        self._ssn_pattern = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="content_filter",
            version="1.0.0",
            author="System",
            description="Filters profanity and PII from messages",
            plugin_type=PluginType.MESSAGE_PROCESSOR,
            tags=("filter", "profanity", "pii", "security"),
        )

    async def _do_initialize(self, config: PluginConfig) -> PluginResult[None]:
        """Initialize filter with configuration"""
        try:
            # Load configuration
            self._filter_profanity = config.config.get("filter_profanity", True)
            self._filter_pii = config.config.get("filter_pii", True)
            self._replacement = config.config.get("replacement", "***")

            # Load custom words
            custom_words = config.config.get("custom_words", [])
            self._profanity_words = self._default_profanity.copy()
            self._profanity_words.update(word.lower() for word in custom_words)

            self._logger.info(
                f"Content filter initialized: {len(self._profanity_words)} words, "
                f"profanity={self._filter_profanity}, pii={self._filter_pii}"
            )

            return PluginResult.ok(None)

        except Exception as e:
            return PluginResult.fail(f"Initialization error: {e}")

    async def _do_shutdown(self) -> PluginResult[None]:
        """Cleanup"""
        self._profanity_words.clear()
        return PluginResult.ok(None)

    async def _process_message(self, message: Message, context: ChatContext) -> PluginResult[Message]:
        """
        Filter message content

        Processing steps:
        1. Filter profanity if enabled
        2. Filter PII if enabled
        3. Return filtered message
        """
        try:
            content = message.content
            filtered_count = 0

            # Filter profanity
            if self._filter_profanity:
                content, prof_count = self._filter_profanity_text(content)
                filtered_count += prof_count

            # Filter PII
            if self._filter_pii:
                content, pii_count = self._filter_pii_text(content)
                filtered_count += pii_count

            # Create filtered message
            filtered_message = Message(
                content=content,
                role=message.role,
                timestamp=message.timestamp,
                metadata={
                    **message.metadata,
                    "filtered": filtered_count > 0,
                    "filter_count": filtered_count,
                },
                model=message.model,
                tokens=message.tokens,
            )

            if filtered_count > 0:
                self._logger.info(f"Filtered {filtered_count} item(s) from message")

            return PluginResult.ok(filtered_message)

        except Exception as e:
            self._logger.exception("Message filtering failed")
            return PluginResult.fail(f"Filter error: {e}")

    def _filter_profanity_text(self, text: str) -> tuple[str, int]:
        """
        Filter profanity from text

        Returns:
            (filtered_text, count_of_replacements)
        """
        count = 0
        words = text.split()
        filtered_words = []

        for word in words:
            # Remove punctuation for checking
            clean_word = re.sub(r"[^\w\s]", "", word).lower()

            if clean_word in self._profanity_words:
                # Replace with same length of replacement characters
                filtered_words.append(self._replacement)
                count += 1
            else:
                filtered_words.append(word)

        return " ".join(filtered_words), count

    def _filter_pii_text(self, text: str) -> tuple[str, int]:
        """
        Filter PII (emails, phone numbers, SSNs) from text

        Returns:
            (filtered_text, count_of_replacements)
        """
        count = 0

        # Filter emails
        filtered_text, email_count = self._replace_pattern(text, self._email_pattern, "[EMAIL]")
        count += email_count

        # Filter phone numbers
        filtered_text, phone_count = self._replace_pattern(filtered_text, self._phone_pattern, "[PHONE]")
        count += phone_count

        # Filter SSNs
        filtered_text, ssn_count = self._replace_pattern(filtered_text, self._ssn_pattern, "[SSN]")
        count += ssn_count

        return filtered_text, count

    def _replace_pattern(self, text: str, pattern: re.Pattern, replacement: str) -> tuple[str, int]:
        """
        Replace regex pattern matches

        Returns:
            (replaced_text, count)
        """
        matches = pattern.findall(text)
        replaced_text = pattern.sub(replacement, text)
        return replaced_text, len(matches)
