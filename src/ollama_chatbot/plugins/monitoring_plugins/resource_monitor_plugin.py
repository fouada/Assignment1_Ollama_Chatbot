"""
Resource Monitoring Plugin
Tracks CPU, RAM, GPU, and disk usage per model for cost analysis
"""

import time
from dataclasses import asdict, dataclass
from typing import Any, Dict, Optional

import psutil

from ..base_plugin import BasePlugin
from ..types import PluginResult

try:
    import GPUtil

    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False


@dataclass
class ResourceSnapshot:
    """System resource usage at a point in time"""

    timestamp: float
    cpu_percent: float
    memory_mb: float
    memory_percent: float
    gpu_memory_mb: Optional[float]
    gpu_utilization: Optional[float]
    disk_io_read_mb: float
    disk_io_write_mb: float


class ResourceMonitorPlugin(BasePlugin):
    """Monitor system resource usage for cost tracking"""

    def __init__(self):
        self.plugin_name = "resource_monitor"
        self.plugin_version = "1.0.0"
        self.plugin_description = "Tracks system resource usage per model for cost analysis"
        self.model_usage: Dict[str, Dict[str, Any]] = {}
        self.baseline_snapshot: Optional[ResourceSnapshot] = None
        self.config: Dict = {}

    async def initialize(self, config: Dict) -> PluginResult[None]:
        """Initialize resource monitoring"""
        self.config = config
        self.baseline_snapshot = self._take_snapshot()
        return PluginResult(
            success=True,
            data=None,
            metadata={
                "message": "Resource monitor initialized",
                "gpu_available": GPU_AVAILABLE,
                "baseline": asdict(self.baseline_snapshot),
            },
        )

    def _take_snapshot(self) -> ResourceSnapshot:
        """Capture current resource usage"""
        try:
            disk_io = psutil.disk_io_counters()
            disk_read_mb = disk_io.read_bytes / (1024**2) if disk_io else 0
            disk_write_mb = disk_io.write_bytes / (1024**2) if disk_io else 0
        except Exception:
            disk_read_mb = 0
            disk_write_mb = 0

        gpu_memory = None
        gpu_util = None
        if GPU_AVAILABLE:
            try:
                gpus = GPUtil.getGPUs()
                if gpus:
                    gpu_memory = gpus[0].memoryUsed
                    gpu_util = gpus[0].load * 100
            except Exception:
                pass

        return ResourceSnapshot(
            timestamp=time.time(),
            cpu_percent=psutil.cpu_percent(interval=0.1),
            memory_mb=psutil.virtual_memory().used / (1024**2),
            memory_percent=psutil.virtual_memory().percent,
            gpu_memory_mb=gpu_memory,
            gpu_utilization=gpu_util,
            disk_io_read_mb=disk_read_mb,
            disk_io_write_mb=disk_write_mb,
        )

    async def before_request(self, context: Dict) -> PluginResult[Dict]:
        """Capture resources before model inference"""
        context["resource_snapshot_before"] = self._take_snapshot()
        return PluginResult(success=True, data=context)

    async def after_request(self, context: Dict) -> PluginResult[Dict]:
        """Calculate resource usage after inference"""
        model = context.get("model", "unknown")
        before = context.get("resource_snapshot_before")
        after = self._take_snapshot()

        if before:
            usage = {
                "model": model,
                "duration_seconds": after.timestamp - before.timestamp,
                "cpu_percent_avg": (before.cpu_percent + after.cpu_percent) / 2,
                "memory_delta_mb": after.memory_mb - before.memory_mb,
                "memory_current_mb": after.memory_mb,
                "disk_read_mb": after.disk_io_read_mb - before.disk_io_read_mb,
                "disk_write_mb": after.disk_io_write_mb - before.disk_io_write_mb,
            }

            if GPU_AVAILABLE and after.gpu_memory_mb is not None:
                usage["gpu_memory_mb"] = after.gpu_memory_mb
                if before.gpu_utilization is not None and after.gpu_utilization is not None:
                    usage["gpu_utilization_avg"] = (before.gpu_utilization + after.gpu_utilization) / 2

            # Accumulate model-specific usage
            if model not in self.model_usage:
                self.model_usage[model] = {
                    "total_requests": 0,
                    "total_duration": 0,
                    "total_cpu_time": 0,
                    "total_memory_mb": 0,
                    "peak_memory_mb": 0,
                    "total_disk_read_mb": 0,
                    "total_disk_write_mb": 0,
                }

            stats = self.model_usage[model]
            stats["total_requests"] += 1
            stats["total_duration"] += usage["duration_seconds"]
            stats["total_cpu_time"] += usage["cpu_percent_avg"] * usage["duration_seconds"] / 100
            stats["total_memory_mb"] += max(0, usage["memory_delta_mb"])  # Only count positive deltas
            stats["peak_memory_mb"] = max(stats["peak_memory_mb"], after.memory_mb)
            stats["total_disk_read_mb"] += usage["disk_read_mb"]
            stats["total_disk_write_mb"] += usage["disk_write_mb"]

            context["resource_usage"] = usage

            # Check alert thresholds
            thresholds = self.config.get("alert_thresholds", {})
            alerts = []

            if after.cpu_percent > thresholds.get("cpu_percent", 100):
                alerts.append(f"High CPU usage: {after.cpu_percent:.1f}%")

            if after.memory_percent > thresholds.get("memory_percent", 100):
                alerts.append(f"High memory usage: {after.memory_percent:.1f}%")

            if alerts:
                context["resource_alerts"] = alerts

        return PluginResult(success=True, data=context)

    async def get_usage_report(self) -> Dict:
        """Generate cost report with resource usage by model"""
        return {
            "baseline": asdict(self.baseline_snapshot) if self.baseline_snapshot else None,
            "current": asdict(self._take_snapshot()),
            "model_usage": self.model_usage,
            "estimated_costs": self._calculate_costs(),
            "summary": self._generate_summary(),
        }

    def _calculate_costs(self) -> Dict:
        """Estimate infrastructure costs based on usage"""
        # Cost model (adjust based on your cloud/hardware costs)
        COST_PER_CPU_HOUR = 0.05  # $0.05 per CPU core hour
        COST_PER_GB_RAM_HOUR = 0.01  # $0.01 per GB RAM hour
        COST_PER_GPU_HOUR = 1.00  # $1.00 per GPU hour
        COST_PER_GB_DISK_IO = 0.001  # $0.001 per GB disk I/O

        costs = {}
        total_cost = 0

        for model, stats in self.model_usage.items():
            cpu_hours = stats["total_cpu_time"] / 3600
            ram_gb_hours = (stats["total_memory_mb"] / 1024) * (stats["total_duration"] / 3600)
            disk_io_gb = (stats["total_disk_read_mb"] + stats["total_disk_write_mb"]) / 1024

            cpu_cost = cpu_hours * COST_PER_CPU_HOUR
            ram_cost = ram_gb_hours * COST_PER_GB_RAM_HOUR
            disk_cost = disk_io_gb * COST_PER_GB_DISK_IO
            model_total = cpu_cost + ram_cost + disk_cost

            costs[model] = {
                "cpu_cost": round(cpu_cost, 4),
                "ram_cost": round(ram_cost, 4),
                "disk_cost": round(disk_cost, 4),
                "total_cost": round(model_total, 4),
                "cost_per_request": round(model_total / max(stats["total_requests"], 1), 6),
                "requests": stats["total_requests"],
                "avg_duration_seconds": round(stats["total_duration"] / max(stats["total_requests"], 1), 3),
            }

            total_cost += model_total

        return {
            "by_model": costs,
            "total_cost": round(total_cost, 4),
            "currency": "USD",
            "note": "Estimated costs based on standard cloud pricing",
        }

    def _generate_summary(self) -> Dict:
        """Generate summary statistics"""
        total_requests = sum(stats["total_requests"] for stats in self.model_usage.values())
        total_duration = sum(stats["total_duration"] for stats in self.model_usage.values())

        most_used_model = None
        if self.model_usage:
            most_used_model = max(self.model_usage.items(), key=lambda x: x[1]["total_requests"])[0]

        return {
            "total_requests": total_requests,
            "total_duration_hours": round(total_duration / 3600, 2),
            "models_tracked": len(self.model_usage),
            "most_used_model": most_used_model,
            "avg_request_duration": round(total_duration / max(total_requests, 1), 3) if total_requests > 0 else 0,
        }

    async def health_check(self) -> PluginResult[Dict]:
        """Health check for the plugin"""
        current = self._take_snapshot()

        status = "healthy"
        issues = []

        # Check resource levels
        if current.memory_percent > 90:
            status = "degraded"
            issues.append("Memory usage above 90%")

        if current.cpu_percent > 95:
            status = "degraded"
            issues.append("CPU usage above 95%")

        return PluginResult(
            success=True,
            data={
                "status": status,
                "issues": issues,
                "current_resources": asdict(current),
                "models_tracked": len(self.model_usage),
                "total_requests": sum(s["total_requests"] for s in self.model_usage.values()),
            },
        )

    async def cleanup(self) -> PluginResult[None]:
        """Cleanup and save final report"""
        return PluginResult(
            success=True,
            data=None,
            metadata={"message": "Resource monitor cleaned up", "final_report": await self.get_usage_report()},
        )
