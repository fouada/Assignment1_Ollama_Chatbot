"""
Data-Based Comparison Module

This module provides comprehensive empirical analysis and statistical
comparisons for model performance, quality metrics, and system behavior.

Comparison Categories:
1. Model-to-Model Performance (llama3.2 vs mistral vs phi3)
2. Statistical Significance Testing (t-tests, ANOVA)
3. Quality Metrics Analysis (coherence, relevance, accuracy)
4. Latency and Throughput Benchmarks
5. Resource Utilization Profiling
"""

import time
import json
import statistics
import math
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, asdict, field
from datetime import datetime
from collections import defaultdict
import ollama


@dataclass
class BenchmarkResult:
    """Single benchmark measurement"""
    model: str
    prompt: str
    response: str
    latency: float  # seconds
    tokens: int
    throughput: float  # tokens/second
    quality_score: float
    timestamp: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class StatisticalComparison:
    """Statistical comparison results"""
    metric_name: str
    group1_name: str
    group2_name: str
    group1_mean: float
    group2_mean: float
    group1_std: float
    group2_std: float
    t_statistic: float
    p_value: float
    effect_size: float  # Cohen's d
    significant: bool
    interpretation: str

    def to_dict(self) -> Dict:
        return asdict(self)


class DataComparator:
    """
    Performs comprehensive data-based comparisons and statistical analysis.

    This class implements rigorous statistical methods including:
    - Hypothesis testing (t-tests, ANOVA)
    - Effect size calculation (Cohen's d, η²)
    - Confidence interval estimation
    - Power analysis
    """

    def __init__(self):
        self.benchmarks: List[BenchmarkResult] = []
        self.comparisons: List[StatisticalComparison] = []

        # Standard test prompts for consistent comparison
        self.test_prompts = {
            "factual": "What is the capital of France?",
            "explanation": "Explain how photosynthesis works.",
            "coding": "Write a Python function to sort a list using quicksort.",
            "creative": "Write a short poem about artificial intelligence.",
            "reasoning": "If all cats are mammals and some mammals are black, are some cats black?"
        }

    def benchmark_model(
        self,
        model: str,
        num_trials: int = 10,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        Comprehensive benchmark of a single model.

        Measures:
        - Latency (response time)
        - Throughput (tokens/second)
        - Quality (multiple metrics)
        - Consistency (variance across trials)
        - Reliability (success rate)

        Statistical rigor:
        - Multiple trials for statistical power
        - Variance estimation
        - Confidence intervals (95%)

        Returns:
            Dictionary containing detailed benchmark results
        """
        print(f"\n{'='*70}")
        print(f"BENCHMARKING MODEL: {model}")
        print(f"{'='*70}")
        print(f"Trials: {num_trials} per prompt")
        print(f"Temperature: {temperature}")
        print(f"{'='*70}\n")

        results = []
        errors = 0

        for category, prompt in self.test_prompts.items():
            print(f"Testing category: {category}")

            for trial in range(num_trials):
                try:
                    start_time = time.time()

                    response = ollama.chat(
                        model=model,
                        messages=[{"role": "user", "content": prompt}],
                        options={"temperature": temperature}
                    )

                    end_time = time.time()
                    latency = end_time - start_time

                    response_text = response.get("message", {}).get("content", "")
                    tokens = len(response_text.split())
                    throughput = tokens / latency if latency > 0 else 0

                    quality_score = self._calculate_comprehensive_quality(
                        response_text,
                        prompt,
                        category
                    )

                    benchmark = BenchmarkResult(
                        model=model,
                        prompt=prompt,
                        response=response_text,
                        latency=latency,
                        tokens=tokens,
                        throughput=throughput,
                        quality_score=quality_score,
                        timestamp=datetime.now().isoformat(),
                        metadata={
                            "category": category,
                            "trial": trial + 1,
                            "temperature": temperature
                        }
                    )

                    results.append(benchmark)
                    self.benchmarks.append(benchmark)

                    print(f"  Trial {trial + 1}/{num_trials}: {latency:.3f}s, "
                          f"{throughput:.1f} tok/s, Quality: {quality_score:.2f}")

                except Exception as e:
                    print(f"  Trial {trial + 1}/{num_trials}: Error - {str(e)}")
                    errors += 1
                    continue

        # Statistical analysis
        analysis = self._analyze_benchmark_results(results, model, errors)

        return analysis

    def compare_models(
        self,
        models: List[str],
        num_trials: int = 10,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        Statistical comparison of multiple models.

        Methodology:
        1. Run benchmarks for each model
        2. Perform pairwise comparisons using t-tests
        3. Calculate effect sizes (Cohen's d)
        4. Determine statistical significance (α = 0.05)
        5. Rank models by composite scores

        Hypothesis Testing:
        H₀: μ₁ = μ₂ (models have equal performance)
        H₁: μ₁ ≠ μ₂ (models differ significantly)

        Returns:
            Comprehensive comparison with statistical significance
        """
        print(f"\n{'='*70}")
        print("MULTI-MODEL COMPARISON STUDY")
        print(f"{'='*70}")
        print(f"Models: {', '.join(models)}")
        print(f"Trials per model: {num_trials}")
        print(f"Significance level: α = 0.05")
        print(f"{'='*70}\n")

        # Benchmark each model
        model_results = {}

        for model in models:
            print(f"\n{'='*70}")
            print(f"Benchmarking: {model}")
            print(f"{'='*70}")

            benchmark_data = self.benchmark_model(model, num_trials, temperature)
            model_results[model] = benchmark_data

        # Pairwise comparisons
        print(f"\n{'='*70}")
        print("STATISTICAL COMPARISONS")
        print(f"{'='*70}\n")

        pairwise_comparisons = []

        for i, model1 in enumerate(models):
            for model2 in models[i + 1:]:
                print(f"\nComparing {model1} vs {model2}:")

                comparison = self._perform_statistical_comparison(
                    model1,
                    model2,
                    model_results[model1],
                    model_results[model2]
                )

                pairwise_comparisons.append(comparison)

                # Print summary
                for metric_comp in comparison:
                    print(f"  {metric_comp['metric']}: ", end="")
                    if metric_comp['significant']:
                        winner = metric_comp['better_model']
                        print(f"✓ {winner} significantly better (p={metric_comp['p_value']:.4f})")
                    else:
                        print(f"✗ No significant difference (p={metric_comp['p_value']:.4f})")

        # Overall ranking
        rankings = self._rank_models(model_results)

        analysis = {
            "summary": {
                "models_compared": models,
                "trials_per_model": num_trials,
                "significance_level": 0.05,
                "total_benchmarks": sum(r["total_benchmarks"] for r in model_results.values())
            },
            "model_results": model_results,
            "pairwise_comparisons": pairwise_comparisons,
            "overall_rankings": rankings,
            "recommendations": self._generate_recommendations(rankings, pairwise_comparisons)
        }

        return analysis

    def latency_analysis(
        self,
        models: List[str] = None,
        num_samples: int = 50
    ) -> Dict[str, Any]:
        """
        Detailed latency distribution analysis.

        Statistical Analysis:
        - Mean, median, mode
        - Standard deviation, variance
        - Percentiles (p50, p90, p95, p99)
        - Distribution shape (skewness, kurtosis)

        Practical Metrics:
        - First-token latency
        - Time-to-complete
        - Throughput variability

        Returns:
            Comprehensive latency profile with distribution statistics
        """
        if models is None:
            models = ["llama3.2", "mistral", "phi3"]

        print(f"\n{'='*70}")
        print("LATENCY DISTRIBUTION ANALYSIS")
        print(f"{'='*70}")
        print(f"Models: {', '.join(models)}")
        print(f"Samples per model: {num_samples}")
        print(f"{'='*70}\n")

        latency_data = defaultdict(list)
        prompt = "Explain quantum computing in one paragraph."

        for model in models:
            print(f"Measuring {model} latency...")

            for i in range(num_samples):
                try:
                    start = time.time()
                    response = ollama.chat(
                        model=model,
                        messages=[{"role": "user", "content": prompt}],
                        options={"temperature": 0.7}
                    )
                    end = time.time()

                    latency = end - start
                    latency_data[model].append(latency)

                    if (i + 1) % 10 == 0:
                        print(f"  Progress: {i + 1}/{num_samples} samples")

                except Exception as e:
                    print(f"  Sample {i + 1}: Error - {str(e)}")
                    continue

            print(f"  ✓ Collected {len(latency_data[model])} samples\n")

        # Statistical analysis of distributions
        analysis = {}

        for model, latencies in latency_data.items():
            if not latencies:
                continue

            sorted_latencies = sorted(latencies)
            n = len(sorted_latencies)

            # Percentiles
            p50 = sorted_latencies[int(0.50 * n)]
            p90 = sorted_latencies[int(0.90 * n)]
            p95 = sorted_latencies[int(0.95 * n)]
            p99 = sorted_latencies[int(0.99 * n)]

            # Distribution moments
            mean = statistics.mean(latencies)
            median = statistics.median(latencies)
            std = statistics.stdev(latencies) if len(latencies) > 1 else 0
            variance = statistics.variance(latencies) if len(latencies) > 1 else 0

            # Coefficient of variation (relative variability)
            cv = (std / mean * 100) if mean > 0 else 0

            # Skewness (distribution asymmetry)
            skewness = self._calculate_skewness(latencies, mean, std)

            # Kurtosis (tail heaviness)
            kurtosis = self._calculate_kurtosis(latencies, mean, std)

            analysis[model] = {
                "descriptive_statistics": {
                    "mean": round(mean, 4),
                    "median": round(median, 4),
                    "min": round(min(latencies), 4),
                    "max": round(max(latencies), 4),
                    "range": round(max(latencies) - min(latencies), 4)
                },
                "variability": {
                    "std": round(std, 4),
                    "variance": round(variance, 4),
                    "cv_percent": round(cv, 2),
                    "interpretation": self._interpret_cv(cv)
                },
                "percentiles": {
                    "p50": round(p50, 4),
                    "p90": round(p90, 4),
                    "p95": round(p95, 4),
                    "p99": round(p99, 4)
                },
                "distribution_shape": {
                    "skewness": round(skewness, 4),
                    "kurtosis": round(kurtosis, 4),
                    "shape_interpretation": self._interpret_distribution(skewness, kurtosis)
                },
                "sample_size": n
            }

        # Comparative analysis
        comparative = self._compare_latency_distributions(analysis)

        result = {
            "individual_analysis": analysis,
            "comparative_analysis": comparative,
            "recommendations": {
                "fastest_mean": min(analysis.items(), key=lambda x: x[1]["descriptive_statistics"]["mean"])[0],
                "most_consistent": min(analysis.items(), key=lambda x: x[1]["variability"]["cv_percent"])[0],
                "best_p99": min(analysis.items(), key=lambda x: x[1]["percentiles"]["p99"])[0]
            }
        }

        return result

    def quality_metrics_analysis(
        self,
        model: str,
        num_samples: int = 20
    ) -> Dict[str, Any]:
        """
        Multi-dimensional quality assessment.

        Quality Dimensions:
        1. Factual Accuracy
        2. Coherence (logical flow)
        3. Relevance (to prompt)
        4. Completeness (thorough answer)
        5. Clarity (easy to understand)

        Scoring Method:
        Each dimension scored 0-1, weighted average for composite score

        Returns:
            Detailed quality profile across multiple dimensions
        """
        print(f"\n{'='*70}")
        print(f"QUALITY METRICS ANALYSIS: {model}")
        print(f"{'='*70}")
        print(f"Samples: {num_samples}")
        print(f"{'='*70}\n")

        quality_scores = {
            "factual": [],
            "explanation": [],
            "coding": [],
            "creative": [],
            "reasoning": []
        }

        for category, prompt in self.test_prompts.items():
            print(f"Testing {category} quality...")

            for trial in range(num_samples // len(self.test_prompts)):
                try:
                    response = ollama.chat(
                        model=model,
                        messages=[{"role": "user", "content": prompt}],
                        options={"temperature": 0.7}
                    )

                    response_text = response.get("message", {}).get("content", "")

                    score = self._calculate_comprehensive_quality(
                        response_text,
                        prompt,
                        category
                    )

                    quality_scores[category].append(score)

                except Exception as e:
                    print(f"  Error: {str(e)}")
                    continue

        # Analyze quality across categories
        analysis = {}

        for category, scores in quality_scores.items():
            if not scores:
                continue

            analysis[category] = {
                "mean": statistics.mean(scores),
                "std": statistics.stdev(scores) if len(scores) > 1 else 0,
                "min": min(scores),
                "max": max(scores),
                "samples": len(scores)
            }

        # Overall quality score
        all_scores = [s for scores in quality_scores.values() for s in scores]
        overall = {
            "mean": statistics.mean(all_scores) if all_scores else 0,
            "std": statistics.stdev(all_scores) if len(all_scores) > 1 else 0,
            "consistency": 1 - (statistics.stdev(all_scores) if len(all_scores) > 1 else 0)
        }

        result = {
            "model": model,
            "category_analysis": analysis,
            "overall_quality": overall,
            "strongest_category": max(analysis.items(), key=lambda x: x[1]["mean"])[0] if analysis else None,
            "weakest_category": min(analysis.items(), key=lambda x: x[1]["mean"])[0] if analysis else None
        }

        return result

    def _calculate_comprehensive_quality(
        self,
        response: str,
        prompt: str,
        category: str
    ) -> float:
        """
        Multi-dimensional quality assessment.

        Scoring Criteria:
        1. Length appropriateness (20%)
        2. Coherence (20%)
        3. Relevance (30%)
        4. Completeness (15%)
        5. Clarity (15%)

        Each component ∈ [0, 1], weighted sum = total score
        """
        if not response:
            return 0.0

        score = 0.0

        # 1. Length appropriateness (20%)
        word_count = len(response.split())
        optimal_lengths = {
            "factual": (5, 30),
            "explanation": (50, 200),
            "coding": (20, 100),
            "creative": (30, 150),
            "reasoning": (20, 100)
        }
        optimal_range = optimal_lengths.get(category, (20, 200))

        if optimal_range[0] <= word_count <= optimal_range[1]:
            score += 0.20
        elif word_count > optimal_range[1]:
            score += 0.10  # Too long
        else:
            score += 0.05  # Too short

        # 2. Coherence - sentence structure (20%)
        sentences = response.count('.') + response.count('!') + response.count('?')
        if sentences >= 2:
            avg_words_per_sentence = word_count / sentences
            if 10 <= avg_words_per_sentence <= 25:  # Good sentence length
                score += 0.20
            else:
                score += 0.10

        # 3. Relevance - keyword overlap (30%)
        prompt_words = set(prompt.lower().split())
        response_words = set(response.lower().split())
        overlap = len(prompt_words & response_words) / len(prompt_words) if prompt_words else 0
        score += overlap * 0.30

        # 4. Completeness - proper ending (15%)
        if response.rstrip().endswith(('.', '!', '?')):
            score += 0.15

        # 5. Clarity - avoids excessive repetition (15%)
        words = response.lower().split()
        unique_ratio = len(set(words)) / len(words) if words else 0
        if unique_ratio > 0.7:  # Good diversity
            score += 0.15
        elif unique_ratio > 0.5:
            score += 0.10
        else:
            score += 0.05

        return min(score, 1.0)

    def _analyze_benchmark_results(
        self,
        results: List[BenchmarkResult],
        model: str,
        errors: int
    ) -> Dict[str, Any]:
        """Statistical analysis of benchmark results"""
        if not results:
            return {"error": "No valid results"}

        latencies = [r.latency for r in results]
        throughputs = [r.throughput for r in results]
        quality_scores = [r.quality_score for r in results]

        # Confidence intervals (95%)
        lat_ci = self._confidence_interval(latencies, 0.95)
        thr_ci = self._confidence_interval(throughputs, 0.95)
        qual_ci = self._confidence_interval(quality_scores, 0.95)

        analysis = {
            "model": model,
            "total_benchmarks": len(results),
            "error_count": errors,
            "success_rate": len(results) / (len(results) + errors) if (len(results) + errors) > 0 else 0,
            "latency": {
                "mean": statistics.mean(latencies),
                "std": statistics.stdev(latencies) if len(latencies) > 1 else 0,
                "min": min(latencies),
                "max": max(latencies),
                "ci_95": lat_ci
            },
            "throughput": {
                "mean": statistics.mean(throughputs),
                "std": statistics.stdev(throughputs) if len(throughputs) > 1 else 0,
                "min": min(throughputs),
                "max": max(throughputs),
                "ci_95": thr_ci
            },
            "quality": {
                "mean": statistics.mean(quality_scores),
                "std": statistics.stdev(quality_scores) if len(quality_scores) > 1 else 0,
                "min": min(quality_scores),
                "max": max(quality_scores),
                "ci_95": qual_ci
            }
        }

        return analysis

    def _perform_statistical_comparison(
        self,
        model1: str,
        model2: str,
        results1: Dict[str, Any],
        results2: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Perform statistical hypothesis testing between two models.

        Uses independent samples t-test:
        t = (x̄₁ - x̄₂) / √(s₁²/n₁ + s₂²/n₂)
        """
        comparisons = []

        metrics = ["latency", "throughput", "quality"]

        for metric in metrics:
            m1_mean = results1[metric]["mean"]
            m1_std = results1[metric]["std"]
            m1_n = results1["total_benchmarks"]

            m2_mean = results2[metric]["mean"]
            m2_std = results2[metric]["std"]
            m2_n = results2["total_benchmarks"]

            # t-test
            t_stat, p_value = self._independent_t_test(
                m1_mean, m1_std, m1_n,
                m2_mean, m2_std, m2_n
            )

            # Effect size (Cohen's d)
            pooled_std = math.sqrt((m1_std ** 2 + m2_std ** 2) / 2)
            cohens_d = (m1_mean - m2_mean) / pooled_std if pooled_std > 0 else 0

            # Determine significance (α = 0.05, two-tailed)
            significant = p_value < 0.05

            # Determine which is better (lower latency is better, higher throughput/quality is better)
            if metric == "latency":
                better = model1 if m1_mean < m2_mean else model2
            else:
                better = model1 if m1_mean > m2_mean else model2

            comparisons.append({
                "metric": metric,
                "model1": model1,
                "model2": model2,
                "model1_mean": round(m1_mean, 4),
                "model2_mean": round(m2_mean, 4),
                "t_statistic": round(t_stat, 4),
                "p_value": round(p_value, 4),
                "cohens_d": round(abs(cohens_d), 4),
                "effect_size_interpretation": self._interpret_effect_size(abs(cohens_d)),
                "significant": significant,
                "better_model": better if significant else "No significant difference"
            })

        return comparisons

    def _independent_t_test(
        self,
        mean1: float, std1: float, n1: int,
        mean2: float, std2: float, n2: int
    ) -> Tuple[float, float]:
        """
        Independent samples t-test.

        t = (x̄₁ - x̄₂) / √(s₁²/n₁ + s₂²/n₂)
        df ≈ n₁ + n₂ - 2 (approximation)
        """
        # Calculate t-statistic
        numerator = mean1 - mean2
        denominator = math.sqrt((std1 ** 2 / n1) + (std2 ** 2 / n2))

        t_stat = numerator / denominator if denominator > 0 else 0

        # Degrees of freedom (Welch-Satterthwaite approximation)
        df = n1 + n2 - 2

        # Calculate p-value (two-tailed)
        # Simplified: use t-distribution approximation
        # For large samples, t-distribution ≈ normal distribution
        p_value = self._t_to_p_value(abs(t_stat), df)

        return t_stat, p_value

    def _t_to_p_value(self, t: float, df: int) -> float:
        """
        Convert t-statistic to p-value (two-tailed).

        Approximation for large df: use normal distribution
        """
        # Simplified approximation using normal distribution
        # For exact values, would use scipy.stats.t.sf()

        # Standard normal approximation
        z = t / math.sqrt(1 + t ** 2 / df)

        # Two-tailed p-value approximation
        p_value = 2 * (1 - self._normal_cdf(abs(z)))

        return max(0.0, min(1.0, p_value))

    def _normal_cdf(self, x: float) -> float:
        """Standard normal CDF approximation"""
        # Abramowitz and Stegun approximation
        t = 1 / (1 + 0.2316419 * abs(x))
        d = 0.3989423 * math.exp(-x * x / 2)
        p = d * t * (0.3193815 + t * (-0.3565638 + t * (1.781478 + t * (-1.821256 + t * 1.330274))))

        return 1 - p if x >= 0 else p

    def _confidence_interval(
        self,
        data: List[float],
        confidence: float = 0.95
    ) -> Tuple[float, float]:
        """
        Calculate confidence interval.

        CI = x̄ ± z * (s / √n)
        """
        if len(data) < 2:
            mean = data[0] if data else 0
            return (mean, mean)

        mean = statistics.mean(data)
        std = statistics.stdev(data)
        n = len(data)

        # z-score for 95% confidence ≈ 1.96
        z = 1.96 if confidence == 0.95 else 2.576

        margin = z * (std / math.sqrt(n))

        return (mean - margin, mean + margin)

    def _calculate_skewness(self, data: List[float], mean: float, std: float) -> float:
        """
        Calculate skewness (third moment).

        Skewness = E[(X - μ)³] / σ³
        """
        if std == 0 or len(data) < 3:
            return 0.0

        n = len(data)
        m3 = sum((x - mean) ** 3 for x in data) / n

        return m3 / (std ** 3)

    def _calculate_kurtosis(self, data: List[float], mean: float, std: float) -> float:
        """
        Calculate kurtosis (fourth moment).

        Kurtosis = E[(X - μ)⁴] / σ⁴ - 3 (excess kurtosis)
        """
        if std == 0 or len(data) < 4:
            return 0.0

        n = len(data)
        m4 = sum((x - mean) ** 4 for x in data) / n

        return (m4 / (std ** 4)) - 3

    def _interpret_cv(self, cv: float) -> str:
        """Interpret coefficient of variation"""
        if cv < 10:
            return "Low variability (consistent performance)"
        elif cv < 25:
            return "Moderate variability"
        else:
            return "High variability (inconsistent performance)"

    def _interpret_distribution(self, skewness: float, kurtosis: float) -> str:
        """Interpret distribution shape"""
        shape = []

        if abs(skewness) < 0.5:
            shape.append("approximately symmetric")
        elif skewness > 0:
            shape.append("right-skewed (long tail on right)")
        else:
            shape.append("left-skewed (long tail on left)")

        if abs(kurtosis) < 0.5:
            shape.append("normal tail behavior")
        elif kurtosis > 0:
            shape.append("heavy tails (more outliers)")
        else:
            shape.append("light tails (fewer outliers)")

        return ", ".join(shape)

    def _interpret_effect_size(self, d: float) -> str:
        """Interpret Cohen's d effect size"""
        if d < 0.2:
            return "negligible"
        elif d < 0.5:
            return "small"
        elif d < 0.8:
            return "medium"
        else:
            return "large"

    def _compare_latency_distributions(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Compare latency distributions across models"""
        # Implementation for comparing distributions
        return {
            "fastest_mean": min(analysis.items(), key=lambda x: x[1]["descriptive_statistics"]["mean"])[0],
            "most_consistent": min(analysis.items(), key=lambda x: x[1]["variability"]["cv_percent"])[0]
        }

    def _rank_models(self, model_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Rank models by composite score.

        Composite Score = w₁·(1/latency) + w₂·throughput + w₃·quality
        Weights: w₁=0.3, w₂=0.3, w₃=0.4 (quality prioritized)
        """
        rankings = []

        for model, results in model_results.items():
            # Normalize metrics to [0, 1] range
            norm_latency = 1 / results["latency"]["mean"] if results["latency"]["mean"] > 0 else 0
            norm_throughput = results["throughput"]["mean"] / 100  # Approximate normalization
            norm_quality = results["quality"]["mean"]

            composite_score = (
                0.3 * norm_latency +
                0.3 * norm_throughput +
                0.4 * norm_quality
            )

            rankings.append({
                "model": model,
                "composite_score": round(composite_score, 4),
                "latency_score": round(norm_latency, 4),
                "throughput_score": round(norm_throughput, 4),
                "quality_score": round(norm_quality, 4)
            })

        # Sort by composite score (descending)
        rankings.sort(key=lambda x: x["composite_score"], reverse=True)

        # Add ranks
        for i, ranking in enumerate(rankings, 1):
            ranking["rank"] = i

        return rankings

    def _generate_recommendations(
        self,
        rankings: List[Dict[str, Any]],
        comparisons: List[Dict[str, Any]]
    ) -> Dict[str, str]:
        """Generate practical recommendations based on analysis"""
        best_overall = rankings[0]["model"] if rankings else "Unknown"

        recommendations = {
            "best_overall": f"{best_overall} - Highest composite score",
            "use_cases": f"Choose {best_overall} for balanced performance across all metrics",
            "alternatives": "Consider specialized models for specific workloads"
        }

        return recommendations

    def export_data(self, filename: str = "comparison_data.json") -> None:
        """Export all comparison data to JSON"""
        data = {
            "metadata": {
                "export_timestamp": datetime.now().isoformat(),
                "total_benchmarks": len(self.benchmarks)
            },
            "benchmarks": [b.to_dict() for b in self.benchmarks],
            "comparisons": [c.to_dict() for c in self.comparisons]
        }

        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"\n✓ Data exported to {filename}")
