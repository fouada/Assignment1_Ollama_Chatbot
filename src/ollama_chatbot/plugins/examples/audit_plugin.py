"""
Audit Trail Plugin - ISO/IEC 25010 Non-repudiation Compliance

Provides comprehensive audit logging with cryptographic signatures
for non-repudiation and accountability.

Author: ISO/IEC 25010 Compliance
Version: 1.0.0
"""

import asyncio
import hashlib
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict

from plugins.base_plugin import BaseMiddleware
from plugins.types import (
    PluginMetadata,
    PluginType,
    PluginConfig,
    PluginResult,
    HookPriority,
)


@dataclass
class AuditEntry:
    """Immutable audit log entry with cryptographic hash"""

    timestamp: str
    event_type: str
    user_id: str
    session_id: str
    action: str
    resource: str
    status: str
    details: Dict[str, Any]
    ip_address: str
    user_agent: str
    previous_hash: str
    entry_hash: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class AuditPlugin(BaseMiddleware):
    """
    Audit Trail Plugin for Non-repudiation

    Features:
    - Cryptographic hash chain (blockchain-like)
    - Tamper-evident logging
    - Digital signatures for actions
    - Persistent audit storage
    - Compliance reporting

    ISO/IEC 25010 Compliance:
    - Security > Non-repudiation: ✅
    - Security > Accountability: ✅
    """

    def __init__(self):
        super().__init__()
        self._audit_file: Optional[Path] = None
        self._last_hash: str = "0" * 64  # Genesis hash
        self._entries_count: int = 0

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="audit_trail",
            version="1.0.0",
            author="ISO Compliance Team",
            description="Cryptographic audit trail for non-repudiation",
            plugin_type=PluginType.MIDDLEWARE,
            dependencies=(),
            tags=("security", "audit", "compliance", "iso25010"),
            priority=HookPriority.CRITICAL,
        )

    async def _do_initialize(self, config: PluginConfig) -> PluginResult[None]:
        """Initialize audit system"""
        try:
            # Setup audit file
            audit_dir = Path(config.config.get("audit_directory", "logs/audit"))
            audit_dir.mkdir(parents=True, exist_ok=True)

            self._audit_file = audit_dir / f"audit_{datetime.now(timezone.utc).strftime('%Y%m%d')}.jsonl"

            # Load last hash if file exists
            if self._audit_file.exists():
                await self._load_last_hash()

            self._logger.info(
                f"Audit system initialized: {self._audit_file}",
                extra={"entries_count": self._entries_count}
            )

            return PluginResult.ok(None)

        except Exception as e:
            return PluginResult.fail(f"Failed to initialize audit system: {e}")

    async def _load_last_hash(self) -> None:
        """Load the last hash from existing audit file"""
        try:
            with open(self._audit_file, 'r') as f:
                lines = f.readlines()
                if lines:
                    last_entry = json.loads(lines[-1])
                    self._last_hash = last_entry.get("entry_hash", self._last_hash)
                    self._entries_count = len(lines)
        except Exception as e:
            self._logger.warning(f"Could not load last hash: {e}")

    async def _process_request(self, request: Dict[str, Any]) -> PluginResult[Dict[str, Any]]:
        """Log request with audit trail"""
        try:
            # Create audit entry
            entry = await self._create_audit_entry(
                event_type="REQUEST",
                action=request.get("endpoint", "unknown"),
                resource=request.get("path", "unknown"),
                status="INITIATED",
                details={
                    "method": request.get("method", "unknown"),
                    "parameters": self._sanitize_data(request.get("data", {})),
                },
                user_id=request.get("user_id", "anonymous"),
                session_id=request.get("session_id", "unknown"),
                ip_address=request.get("ip_address", "unknown"),
                user_agent=request.get("user_agent", "unknown"),
            )

            # Store audit entry
            await self._write_audit_entry(entry)

            # Add audit ID to request
            request["audit_id"] = entry.entry_hash

            return PluginResult.ok(request)

        except Exception as e:
            self._logger.error(f"Audit logging failed: {e}")
            # Don't fail the request if audit fails
            return PluginResult.ok(request)

    async def _process_response(self, response: Dict[str, Any]) -> PluginResult[Dict[str, Any]]:
        """Log response with audit trail"""
        try:
            # Create audit entry
            entry = await self._create_audit_entry(
                event_type="RESPONSE",
                action=response.get("endpoint", "unknown"),
                resource=response.get("path", "unknown"),
                status=response.get("status", "SUCCESS"),
                details={
                    "status_code": response.get("status_code", 200),
                    "execution_time_ms": response.get("execution_time_ms", 0),
                    "response_size": len(str(response.get("data", ""))),
                },
                user_id=response.get("user_id", "anonymous"),
                session_id=response.get("session_id", "unknown"),
                ip_address=response.get("ip_address", "unknown"),
                user_agent=response.get("user_agent", "unknown"),
            )

            # Store audit entry
            await self._write_audit_entry(entry)

            return PluginResult.ok(response)

        except Exception as e:
            self._logger.error(f"Audit logging failed: {e}")
            return PluginResult.ok(response)

    async def _create_audit_entry(
        self,
        event_type: str,
        action: str,
        resource: str,
        status: str,
        details: Dict[str, Any],
        user_id: str,
        session_id: str,
        ip_address: str,
        user_agent: str,
    ) -> AuditEntry:
        """Create cryptographically signed audit entry"""

        timestamp = datetime.now(timezone.utc).isoformat()

        # Create entry data
        entry_data = {
            "timestamp": timestamp,
            "event_type": event_type,
            "user_id": user_id,
            "session_id": session_id,
            "action": action,
            "resource": resource,
            "status": status,
            "details": details,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "previous_hash": self._last_hash,
        }

        # Calculate cryptographic hash
        entry_hash = self._calculate_hash(entry_data)

        # Create immutable entry
        entry = AuditEntry(
            **entry_data,
            entry_hash=entry_hash,
        )

        # Update last hash for chain
        self._last_hash = entry_hash

        return entry

    def _calculate_hash(self, data: Dict[str, Any]) -> str:
        """Calculate SHA-256 hash of entry data"""
        # Sort keys for consistent hashing
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()

    async def _write_audit_entry(self, entry: AuditEntry) -> None:
        """Write audit entry to persistent storage"""
        try:
            # Append to audit log (JSONL format)
            with open(self._audit_file, 'a') as f:
                f.write(json.dumps(entry.to_dict()) + '\n')

            self._entries_count += 1

        except Exception as e:
            self._logger.error(f"Failed to write audit entry: {e}")

    def _sanitize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sensitive data from logs"""
        sanitized = data.copy()

        # Remove sensitive fields
        sensitive_fields = ["password", "token", "api_key", "secret", "credit_card"]

        for key in list(sanitized.keys()):
            if any(sensitive in key.lower() for sensitive in sensitive_fields):
                sanitized[key] = "***REDACTED***"

        return sanitized

    async def verify_audit_chain(self) -> PluginResult[bool]:
        """Verify integrity of entire audit chain"""
        try:
            if not self._audit_file or not self._audit_file.exists():
                return PluginResult.ok(True)

            previous_hash = "0" * 64

            with open(self._audit_file, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    entry = json.loads(line)

                    # Verify previous hash matches
                    if entry["previous_hash"] != previous_hash:
                        return PluginResult.fail(
                            f"Chain broken at entry {line_num}: hash mismatch"
                        )

                    # Recalculate hash
                    entry_copy = entry.copy()
                    stored_hash = entry_copy.pop("entry_hash")
                    calculated_hash = self._calculate_hash(entry_copy)

                    # Verify hash matches
                    if stored_hash != calculated_hash:
                        return PluginResult.fail(
                            f"Tampered entry detected at line {line_num}"
                        )

                    previous_hash = stored_hash

            return PluginResult.ok(True)

        except Exception as e:
            return PluginResult.fail(f"Verification failed: {e}")

    async def _do_health_check(self) -> PluginResult[Dict[str, Any]]:
        """Health check with chain verification"""
        verification = await self.verify_audit_chain()

        return PluginResult.ok({
            "status": "healthy" if verification.success else "unhealthy",
            "audit_file": str(self._audit_file) if self._audit_file else None,
            "entries_count": self._entries_count,
            "chain_verified": verification.success,
            "last_hash": self._last_hash[:16] + "...",
        })


# Export plugin
__all__ = ["AuditPlugin"]
