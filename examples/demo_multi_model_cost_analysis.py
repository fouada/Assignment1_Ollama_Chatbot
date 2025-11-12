#!/usr/bin/env python3
"""
Multi-Model Cost Analysis Demo
Demonstrates what happens when different clients use different Ollama models
"""

import asyncio
import time
import ollama
import psutil
from typing import List, Dict, Tuple
from dataclasses import dataclass, asdict
import json
from datetime import datetime


@dataclass
class ClientRequest:
    """Represents a client request"""
    client_id: str
    model: str
    prompt: str
    temperature: float = 0.7


@dataclass
class RequestResult:
    """Result of processing a request"""
    client_id: str
    model: str
    response_length: int
    duration_seconds: float
    cpu_percent_before: float
    cpu_percent_after: float
    memory_mb_before: float
    memory_mb_after: float
    memory_delta_mb: float
    tokens_estimated: int


class MultiModelCostAnalyzer:
    """Analyze costs of serving multiple models to different clients"""

    def __init__(self):
        self.results: List[RequestResult] = []
        self.model_load_times: Dict[str, float] = {}

    def get_system_resources(self) -> Tuple[float, float]:
        """Get current CPU and memory usage"""
        cpu = psutil.cpu_percent(interval=0.1)
        memory_mb = psutil.virtual_memory().used / (1024**2)
        return cpu, memory_mb

    def estimate_tokens(self, text: str) -> int:
        """Rough token estimation (4 chars ≈ 1 token)"""
        return len(text) // 4

    async def process_request(self, request: ClientRequest) -> RequestResult:
        """Process a single client request and measure resources"""
        print(f"\n{'='*60}")
        print(f"Client: {request.client_id}")
        print(f"Model: {request.model}")
        print(f"Prompt: {request.prompt[:50]}...")
        print(f"{'='*60}")

        # Measure resources before
        cpu_before, mem_before = self.get_system_resources()
        start_time = time.time()

        try:
            # Make the request to Ollama
            response = ollama.chat(
                model=request.model,
                messages=[{"role": "user", "content": request.prompt}],
                options={"temperature": request.temperature}
            )

            response_text = response["message"]["content"]
            duration = time.time() - start_time

            # Measure resources after
            cpu_after, mem_after = self.get_system_resources()

            result = RequestResult(
                client_id=request.client_id,
                model=request.model,
                response_length=len(response_text),
                duration_seconds=duration,
                cpu_percent_before=cpu_before,
                cpu_percent_after=cpu_after,
                memory_mb_before=mem_before,
                memory_mb_after=mem_after,
                memory_delta_mb=mem_after - mem_before,
                tokens_estimated=self.estimate_tokens(response_text)
            )

            self.results.append(result)

            print(f"✓ Response received ({len(response_text)} chars, ~{result.tokens_estimated} tokens)")
            print(f"✓ Duration: {duration:.2f}s")
            print(f"✓ CPU: {cpu_before:.1f}% → {cpu_after:.1f}%")
            print(f"✓ Memory: {mem_before:.0f}MB → {mem_after:.0f}MB (Δ {result.memory_delta_mb:+.0f}MB)")

            return result

        except Exception as e:
            print(f"✗ Error: {e}")
            raise

    def get_available_models(self) -> List[str]:
        """Get list of available Ollama models"""
        try:
            models = ollama.list()
            return [model.model for model in models.models]
        except Exception as e:
            print(f"Error fetching models: {e}")
            return []

    def calculate_costs(self) -> Dict:
        """Calculate estimated costs based on resource usage"""
        # Cost model (adjust to your infrastructure)
        COST_PER_CPU_HOUR = 0.05  # $0.05 per CPU core hour
        COST_PER_GB_RAM_HOUR = 0.01  # $0.01 per GB RAM hour

        model_stats = {}

        for result in self.results:
            model = result.model

            if model not in model_stats:
                model_stats[model] = {
                    "requests": 0,
                    "total_duration": 0,
                    "total_cpu_time": 0,
                    "total_memory_gb_hours": 0,
                    "total_tokens": 0
                }

            stats = model_stats[model]
            stats["requests"] += 1
            stats["total_duration"] += result.duration_seconds
            stats["total_tokens"] += result.tokens_estimated

            # CPU time (average CPU % during request * duration)
            avg_cpu = (result.cpu_percent_before + result.cpu_percent_after) / 2
            cpu_hours = (avg_cpu / 100) * (result.duration_seconds / 3600)
            stats["total_cpu_time"] += cpu_hours

            # Memory GB-hours (memory used during request * duration)
            avg_memory_gb = (result.memory_mb_after / 1024)
            memory_gb_hours = avg_memory_gb * (result.duration_seconds / 3600)
            stats["total_memory_gb_hours"] += memory_gb_hours

        # Calculate costs
        cost_breakdown = {}
        total_cost = 0

        for model, stats in model_stats.items():
            cpu_cost = stats["total_cpu_time"] * COST_PER_CPU_HOUR
            ram_cost = stats["total_memory_gb_hours"] * COST_PER_GB_RAM_HOUR
            model_total = cpu_cost + ram_cost

            cost_breakdown[model] = {
                "requests": stats["requests"],
                "total_duration_seconds": round(stats["total_duration"], 2),
                "cpu_cost_usd": round(cpu_cost, 6),
                "ram_cost_usd": round(ram_cost, 6),
                "total_cost_usd": round(model_total, 6),
                "cost_per_request_usd": round(model_total / stats["requests"], 6),
                "tokens_generated": stats["total_tokens"],
                "cost_per_1k_tokens_usd": round((model_total / stats["total_tokens"]) * 1000, 6) if stats["total_tokens"] > 0 else 0
            }

            total_cost += model_total

        return {
            "by_model": cost_breakdown,
            "total_cost_usd": round(total_cost, 6),
            "total_requests": len(self.results)
        }

    def generate_report(self) -> str:
        """Generate a comprehensive cost analysis report"""
        costs = self.calculate_costs()

        report = "\n" + "="*70 + "\n"
        report += "MULTI-MODEL COST ANALYSIS REPORT\n"
        report += "="*70 + "\n\n"

        report += f"Total Requests: {costs['total_requests']}\n"
        report += f"Total Estimated Cost: ${costs['total_cost_usd']:.6f}\n\n"

        report += "="*70 + "\n"
        report += "COST BREAKDOWN BY MODEL\n"
        report += "="*70 + "\n\n"

        for model, stats in costs["by_model"].items():
            report += f"Model: {model}\n"
            report += f"  Requests: {stats['requests']}\n"
            report += f"  Duration: {stats['total_duration_seconds']:.2f}s\n"
            report += f"  CPU Cost: ${stats['cpu_cost_usd']:.6f}\n"
            report += f"  RAM Cost: ${stats['ram_cost_usd']:.6f}\n"
            report += f"  Total Cost: ${stats['total_cost_usd']:.6f}\n"
            report += f"  Cost per Request: ${stats['cost_per_request_usd']:.6f}\n"
            report += f"  Tokens Generated: ~{stats['tokens_generated']}\n"
            report += f"  Cost per 1K Tokens: ${stats['cost_per_1k_tokens_usd']:.6f}\n\n"

        report += "="*70 + "\n"
        report += "COMPARISON WITH CLOUD APIs\n"
        report += "="*70 + "\n\n"

        # Compare with cloud pricing
        total_tokens = sum(stats["tokens_generated"] for stats in costs["by_model"].values())

        openai_cost = (total_tokens / 1000) * 0.15  # GPT-4o-mini input pricing
        anthropic_cost = (total_tokens / 1000) * 0.25  # Claude Haiku pricing
        ollama_cost = costs['total_cost_usd']

        report += f"OpenAI GPT-4o-mini (est.): ${openai_cost:.4f}\n"
        report += f"Anthropic Claude Haiku (est.): ${anthropic_cost:.4f}\n"
        report += f"Your Ollama Setup: ${ollama_cost:.6f}\n\n"

        if ollama_cost > 0:
            openai_savings = ((openai_cost - ollama_cost) / openai_cost) * 100
            anthropic_savings = ((anthropic_cost - ollama_cost) / anthropic_cost) * 100
            report += f"Savings vs OpenAI: {openai_savings:.1f}%\n"
            report += f"Savings vs Anthropic: {anthropic_savings:.1f}%\n\n"

        report += "="*70 + "\n"
        report += "KEY INSIGHTS\n"
        report += "="*70 + "\n\n"

        # Identify most/least efficient models
        if costs["by_model"]:
            models_by_efficiency = sorted(
                costs["by_model"].items(),
                key=lambda x: x[1]["cost_per_request_usd"]
            )

            most_efficient = models_by_efficiency[0]
            least_efficient = models_by_efficiency[-1]

            report += f"Most Efficient: {most_efficient[0]} (${most_efficient[1]['cost_per_request_usd']:.6f}/req)\n"
            report += f"Least Efficient: {least_efficient[0]} (${least_efficient[1]['cost_per_request_usd']:.6f}/req)\n\n"

            if len(models_by_efficiency) > 1:
                efficiency_ratio = least_efficient[1]['cost_per_request_usd'] / most_efficient[1]['cost_per_request_usd']
                report += f"Efficiency Gap: {efficiency_ratio:.2f}x difference\n\n"

        report += "RECOMMENDATIONS:\n"
        report += "• Use smaller models (phi3, llama3.2:1b) for simple queries\n"
        report += "• Reserve larger models for complex analysis\n"
        report += "• Pre-load frequently used models to avoid loading delays\n"
        report += "• Implement caching for repeated queries\n"
        report += "• Monitor resource usage during peak hours\n\n"

        return report


async def main():
    """Run the multi-model cost analysis demo"""
    analyzer = MultiModelCostAnalyzer()

    print("\n" + "="*70)
    print("MULTI-MODEL COST ANALYSIS DEMO")
    print("="*70)

    # Check available models
    print("\nFetching available Ollama models...")
    available_models = analyzer.get_available_models()

    if not available_models:
        print("✗ No Ollama models found. Please install models first:")
        print("  ollama pull llama3.2")
        print("  ollama pull phi3")
        print("  ollama pull mistral")
        return

    print(f"✓ Found {len(available_models)} models: {', '.join(available_models)}")

    # Select models for demo (use first 2-3 available)
    demo_models = available_models[:min(3, len(available_models))]
    print(f"\nUsing models for demo: {', '.join(demo_models)}")

    # Define test prompts of varying complexity
    test_prompts = [
        "What is 2+2?",  # Simple
        "Explain the concept of recursion in programming.",  # Medium
        "Write a short poem about artificial intelligence.",  # Creative
        "What are the main differences between Python and JavaScript?"  # Detailed
    ]

    # Simulate multiple clients using different models
    requests = []
    client_id = 1

    print("\n" + "="*70)
    print("SIMULATING MULTIPLE CLIENTS WITH DIFFERENT MODELS")
    print("="*70)

    for i, prompt in enumerate(test_prompts):
        # Rotate through available models
        model = demo_models[i % len(demo_models)]
        requests.append(ClientRequest(
            client_id=f"client_{client_id}",
            model=model,
            prompt=prompt,
            temperature=0.7
        ))
        client_id += 1

    # Add some repeated requests to show caching potential
    requests.append(ClientRequest(
        client_id=f"client_{client_id}",
        model=demo_models[0],
        prompt=test_prompts[0],  # Repeat first prompt
        temperature=0.7
    ))

    # Process all requests
    print(f"\nProcessing {len(requests)} requests...\n")

    for request in requests:
        try:
            await analyzer.process_request(request)
            # Small delay between requests
            await asyncio.sleep(1)
        except Exception as e:
            print(f"Failed to process request: {e}")

    # Generate and display report
    report = analyzer.generate_report()
    print(report)

    # Save report to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"cost_analysis_report_{timestamp}.txt"

    with open(report_file, "w") as f:
        f.write(report)

    # Save detailed JSON data
    json_file = f"cost_analysis_data_{timestamp}.json"
    with open(json_file, "w") as f:
        json.dump({
            "timestamp": timestamp,
            "results": [asdict(r) for r in analyzer.results],
            "costs": analyzer.calculate_costs()
        }, f, indent=2)

    print(f"Report saved to: {report_file}")
    print(f"Detailed data saved to: {json_file}")


if __name__ == "__main__":
    asyncio.run(main())
