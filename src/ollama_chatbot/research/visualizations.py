"""
Research Visualization Module

This module provides comprehensive visualization capabilities for research data
including interactive charts, dashboards, and performance monitoring.

Visualization Types:
- Line plots (sensitivity analysis)
- Bar charts (model comparisons)
- Box plots (distribution analysis)
- Heatmaps (correlation matrices)
- Scatter plots (parameter relationships)
- Radar charts (multi-dimensional quality)
- Time series (performance trends)
"""

import json
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd


class ResearchVisualizer:
    """
    Creates interactive visualizations for research data.

    Supports multiple chart types optimized for different data patterns:
    - Temporal: Line charts, time series
    - Comparative: Bar charts, grouped bars
    - Distributional: Histograms, box plots, violin plots
    - Correlational: Scatter plots, heatmaps
    - Multi-dimensional: Radar charts, parallel coordinates
    """

    def __init__(self):
        self.color_scheme = {
            'primary': '#1f77b4',
            'secondary': '#ff7f0e',
            'success': '#2ca02c',
            'danger': '#d62728',
            'warning': '#ff9800',
            'info': '#17a2b8',
            'neutral': '#7f7f7f'
        }

        self.model_colors = {
            'llama3.2': '#1f77b4',
            'mistral': '#ff7f0e',
            'phi3': '#2ca02c',
            'codellama': '#d62728'
        }

    def load_json_data(self, filepath: str) -> Dict:
        """Load JSON data from file"""
        with open(filepath, 'r') as f:
            return json.load(f)

    def create_sensitivity_chart(
        self,
        data: Dict[str, Any],
        metric: str = 'quality'
    ) -> go.Figure:
        """
        Create interactive line chart for sensitivity analysis.

        Shows how metrics change with parameter variations (e.g., temperature).
        Includes confidence bands and annotations for optimal values.
        """
        if 'raw_data' not in data:
            return self._create_empty_chart("No sensitivity data available")

        raw_data = data['raw_data']

        # Extract data points
        param_values = []
        metric_values = []

        for point in raw_data:
            param_values.append(point['parameter_value'])

            if metric == 'quality':
                metric_values.append(point['response_quality_score'])
            elif metric == 'latency':
                metric_values.append(point['response_time'])
            elif metric == 'throughput':
                metric_values.append(point['tokens_per_second'])

        # Create figure
        fig = go.Figure()

        # Add main line
        fig.add_trace(go.Scatter(
            x=param_values,
            y=metric_values,
            mode='lines+markers',
            name=metric.capitalize(),
            line=dict(color=self.color_scheme['primary'], width=3),
            marker=dict(size=8, color=self.color_scheme['primary']),
            hovertemplate='Parameter: %{x:.2f}<br>Value: %{y:.4f}<extra></extra>'
        ))

        # Add optimal value annotation if available
        if 'summary' in data and 'optimal_temperature' in data['summary']:
            optimal = data['summary']['optimal_temperature']
            fig.add_vline(
                x=optimal,
                line_dash="dash",
                line_color=self.color_scheme['success'],
                annotation_text=f"Optimal: {optimal:.2f}",
                annotation_position="top"
            )

        # Layout
        param_name = data['raw_data'][0]['parameter_name'] if raw_data else 'Parameter'

        fig.update_layout(
            title=f'Sensitivity Analysis: {metric.capitalize()} vs {param_name.capitalize()}',
            xaxis_title=param_name.capitalize(),
            yaxis_title=metric.capitalize(),
            hovermode='x unified',
            template='plotly_white',
            height=500,
            showlegend=True
        )

        return fig

    def create_model_comparison_chart(
        self,
        data: Dict[str, Any],
        metric: str = 'composite_score'
    ) -> go.Figure:
        """
        Create grouped bar chart for model comparisons.

        Compares multiple models across various metrics with error bars
        showing confidence intervals.
        """
        if 'detailed_statistics' not in data:
            return self._create_empty_chart("No model comparison data available")

        models = list(data['detailed_statistics'].keys())

        if metric == 'composite_score':
            values = [data['detailed_statistics'][m]['composite_score'] for m in models]
            errors = None
            ylabel = 'Composite Score'
        elif metric == 'latency':
            values = [data['detailed_statistics'][m]['response_time']['mean'] for m in models]
            errors = [data['detailed_statistics'][m]['response_time']['std'] for m in models]
            ylabel = 'Response Time (seconds)'
        elif metric == 'quality':
            values = [data['detailed_statistics'][m]['quality_score']['mean'] for m in models]
            errors = [data['detailed_statistics'][m]['quality_score']['std'] for m in models]
            ylabel = 'Quality Score'
        elif metric == 'throughput':
            values = [data['detailed_statistics'][m]['throughput']['mean'] for m in models]
            errors = [data['detailed_statistics'][m]['throughput']['std'] for m in models]
            ylabel = 'Throughput (tokens/sec)'
        else:
            values = [data['detailed_statistics'][m]['composite_score'] for m in models]
            errors = None
            ylabel = metric.capitalize()

        # Create bar chart
        colors = [self.model_colors.get(m, self.color_scheme['neutral']) for m in models]

        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=models,
            y=values,
            error_y=dict(type='data', array=errors) if errors else None,
            marker_color=colors,
            text=[f'{v:.4f}' for v in values],
            textposition='outside',
            hovertemplate='Model: %{x}<br>Value: %{y:.4f}<extra></extra>'
        ))

        fig.update_layout(
            title=f'Model Comparison: {ylabel}',
            xaxis_title='Model',
            yaxis_title=ylabel,
            template='plotly_white',
            height=500,
            showlegend=False
        )

        return fig

    def create_latency_distribution_chart(
        self,
        data: Dict[str, Any],
        model: Optional[str] = None
    ) -> go.Figure:
        """
        Create box plot or violin plot for latency distributions.

        Shows distribution shape, percentiles, and outliers.
        """
        if 'individual_analysis' not in data:
            return self._create_empty_chart("No latency data available")

        models_to_plot = [model] if model else list(data['individual_analysis'].keys())

        fig = go.Figure()

        for m in models_to_plot:
            if m not in data['individual_analysis']:
                continue

            stats = data['individual_analysis'][m]
            desc = stats['descriptive_statistics']
            perc = stats['percentiles']

            # Create box plot data
            fig.add_trace(go.Box(
                y=[desc['min'], perc['p50'], desc['mean'], perc['p90'], perc['p95'], perc['p99'], desc['max']],
                name=m,
                marker_color=self.model_colors.get(m, self.color_scheme['neutral']),
                boxmean='sd',
                hovertext=[
                    f"Min: {desc['min']:.4f}",
                    f"Median (p50): {perc['p50']:.4f}",
                    f"Mean: {desc['mean']:.4f}",
                    f"p90: {perc['p90']:.4f}",
                    f"p95: {perc['p95']:.4f}",
                    f"p99: {perc['p99']:.4f}",
                    f"Max: {desc['max']:.4f}"
                ]
            ))

        fig.update_layout(
            title='Latency Distribution Analysis',
            yaxis_title='Latency (seconds)',
            template='plotly_white',
            height=500,
            showlegend=True
        )

        return fig

    def create_percentile_chart(
        self,
        data: Dict[str, Any]
    ) -> go.Figure:
        """
        Create grouped bar chart showing percentiles (p50, p90, p95, p99).

        Critical for understanding tail latency and SLA compliance.
        """
        if 'individual_analysis' not in data:
            return self._create_empty_chart("No latency data available")

        models = list(data['individual_analysis'].keys())
        percentiles = ['p50', 'p90', 'p95', 'p99']

        fig = go.Figure()

        for perc in percentiles:
            values = [data['individual_analysis'][m]['percentiles'][perc] for m in models]

            fig.add_trace(go.Bar(
                name=perc.upper(),
                x=models,
                y=values,
                text=[f'{v:.3f}s' for v in values],
                textposition='outside',
                hovertemplate=f'{perc.upper()}: %{{y:.4f}}s<extra></extra>'
            ))

        fig.update_layout(
            title='Latency Percentiles by Model',
            xaxis_title='Model',
            yaxis_title='Latency (seconds)',
            barmode='group',
            template='plotly_white',
            height=500,
            showlegend=True
        )

        return fig

    def create_quality_radar_chart(
        self,
        data: Dict[str, Any]
    ) -> go.Figure:
        """
        Create radar chart for multi-dimensional quality assessment.

        Shows quality across different categories (factual, explanation,
        coding, creative, reasoning) for one or more models.
        """
        if 'category_analysis' not in data:
            return self._create_empty_chart("No quality data available")

        categories = list(data['category_analysis'].keys())
        values = [data['category_analysis'][cat]['mean'] for cat in categories]

        # Close the radar chart
        categories_plot = categories + [categories[0]]
        values_plot = values + [values[0]]

        fig = go.Figure()

        fig.add_trace(go.Scatterpolar(
            r=values_plot,
            theta=categories_plot,
            fill='toself',
            name=data.get('model', 'Model'),
            marker_color=self.color_scheme['primary']
        ))

        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )
            ),
            title='Multi-Dimensional Quality Profile',
            template='plotly_white',
            height=500,
            showlegend=True
        )

        return fig

    def create_comparison_heatmap(
        self,
        data: Dict[str, Any]
    ) -> go.Figure:
        """
        Create heatmap showing statistical comparison results.

        Visualizes p-values and effect sizes for pairwise model comparisons.
        """
        if 'pairwise_comparisons' not in data:
            return self._create_empty_chart("No comparison data available")

        comparisons = data['pairwise_comparisons']

        # Extract unique models
        models = set()
        for comp_group in comparisons:
            for comp in comp_group:
                models.add(comp['model1'])
                models.add(comp['model2'])

        models = sorted(list(models))
        n = len(models)

        # Create matrix for each metric
        metrics = ['latency', 'throughput', 'quality']

        # Create subplots for each metric
        fig = make_subplots(
            rows=1,
            cols=len(metrics),
            subplot_titles=[m.capitalize() for m in metrics],
            specs=[[{'type': 'heatmap'} for _ in metrics]]
        )

        for idx, metric in enumerate(metrics, 1):
            # Initialize matrix with NaN
            matrix = [[None for _ in range(n)] for _ in range(n)]

            # Fill matrix with p-values
            for comp_group in comparisons:
                for comp in comp_group:
                    if comp['metric'] == metric:
                        i = models.index(comp['model1'])
                        j = models.index(comp['model2'])

                        # Use p-value, color-coded by significance
                        p_val = comp['p_value']
                        matrix[i][j] = p_val
                        matrix[j][i] = p_val

            # Self-comparison is 1.0
            for i in range(n):
                matrix[i][i] = 1.0

            fig.add_trace(
                go.Heatmap(
                    z=matrix,
                    x=models,
                    y=models,
                    colorscale='RdYlGn',
                    reversescale=True,
                    text=[[f'{v:.3f}' if v is not None else 'N/A' for v in row] for row in matrix],
                    texttemplate='%{text}',
                    textfont={"size": 10},
                    colorbar=dict(title='p-value'),
                    hovertemplate='%{y} vs %{x}<br>p-value: %{z:.4f}<extra></extra>'
                ),
                row=1,
                col=idx
            )

        fig.update_layout(
            title='Statistical Comparison Heatmap (p-values)',
            template='plotly_white',
            height=400,
            showlegend=False
        )

        return fig

    def create_performance_overview_dashboard(
        self,
        sensitivity_data: Dict[str, Any],
        comparison_data: Dict[str, Any],
        latency_data: Dict[str, Any]
    ) -> go.Figure:
        """
        Create comprehensive dashboard with multiple subplots.

        Combines key visualizations into a single overview dashboard.
        """
        fig = make_subplots(
            rows=2,
            cols=2,
            subplot_titles=(
                'Temperature Sensitivity',
                'Model Rankings',
                'Latency Distribution',
                'Quality by Category'
            ),
            specs=[
                [{'type': 'scatter'}, {'type': 'bar'}],
                [{'type': 'box'}, {'type': 'bar'}]
            ]
        )

        # 1. Temperature sensitivity (if available)
        if 'raw_data' in sensitivity_data:
            temps = [p['parameter_value'] for p in sensitivity_data['raw_data']]
            qualities = [p['response_quality_score'] for p in sensitivity_data['raw_data']]

            fig.add_trace(
                go.Scatter(x=temps, y=qualities, mode='lines+markers', name='Quality',
                          line=dict(color=self.color_scheme['primary'])),
                row=1, col=1
            )

        # 2. Model rankings (if available)
        if 'overall_rankings' in comparison_data:
            models = [r['model'] for r in comparison_data['overall_rankings']]
            scores = [r['composite_score'] for r in comparison_data['overall_rankings']]
            colors = [self.model_colors.get(m, self.color_scheme['neutral']) for m in models]

            fig.add_trace(
                go.Bar(x=models, y=scores, marker_color=colors, name='Score',
                      showlegend=False),
                row=1, col=2
            )

        # 3. Latency distribution (if available)
        if 'individual_analysis' in latency_data:
            for model in latency_data['individual_analysis'].keys():
                stats = latency_data['individual_analysis'][model]['descriptive_statistics']
                fig.add_trace(
                    go.Box(y=[stats['min'], stats['mean'], stats['max']], name=model,
                          marker_color=self.model_colors.get(model, self.color_scheme['neutral'])),
                    row=2, col=1
                )

        fig.update_layout(
            title='Research Performance Overview Dashboard',
            template='plotly_white',
            height=800,
            showlegend=True
        )

        return fig

    def create_correlation_matrix(
        self,
        data: Dict[str, Any]
    ) -> go.Figure:
        """
        Create correlation matrix for multiple metrics.

        Shows relationships between different performance dimensions.
        """
        if 'correlations' not in data:
            return self._create_empty_chart("No correlation data available")

        corr_data = data['correlations']

        # Build correlation matrix
        metrics = list(corr_data.keys())
        n = len(metrics)

        matrix = [[0.0 for _ in range(n)] for _ in range(n)]

        for i, metric in enumerate(metrics):
            matrix[i][i] = 1.0  # Self-correlation
            if isinstance(corr_data[metric], (int, float)):
                # If we have direct correlation values
                for j in range(i + 1, n):
                    matrix[i][j] = corr_data[metric]
                    matrix[j][i] = corr_data[metric]

        fig = go.Figure(data=go.Heatmap(
            z=matrix,
            x=metrics,
            y=metrics,
            colorscale='RdBu',
            zmid=0,
            text=[[f'{v:.2f}' for v in row] for row in matrix],
            texttemplate='%{text}',
            textfont={"size": 12},
            colorbar=dict(title='Correlation'),
            hovertemplate='%{y} vs %{x}<br>Correlation: %{z:.4f}<extra></extra>'
        ))

        fig.update_layout(
            title='Correlation Matrix',
            template='plotly_white',
            height=500
        )

        return fig

    def create_streaming_comparison_chart(
        self,
        data: Dict[str, Any]
    ) -> go.Figure:
        """
        Create comparison chart for streaming vs non-streaming performance.

        Highlights first-token latency advantage of streaming.
        """
        if not all(k in data for k in ['streaming', 'non_streaming']):
            return self._create_empty_chart("No streaming comparison data available")

        categories = ['Mean Response Time', 'First Token Latency']

        streaming = [
            data['streaming']['mean_response_time'],
            data['streaming'].get('mean_first_token_latency', 0) or 0
        ]

        non_streaming = [
            data['non_streaming']['mean_response_time'],
            data['non_streaming']['mean_response_time']  # No first token in non-streaming
        ]

        fig = go.Figure()

        fig.add_trace(go.Bar(
            name='Streaming',
            x=categories,
            y=streaming,
            marker_color=self.color_scheme['success'],
            text=[f'{v:.3f}s' for v in streaming],
            textposition='outside'
        ))

        fig.add_trace(go.Bar(
            name='Non-Streaming',
            x=categories,
            y=non_streaming,
            marker_color=self.color_scheme['primary'],
            text=[f'{v:.3f}s' for v in non_streaming],
            textposition='outside'
        ))

        fig.update_layout(
            title='Streaming vs Non-Streaming Performance',
            xaxis_title='Metric',
            yaxis_title='Time (seconds)',
            barmode='group',
            template='plotly_white',
            height=500,
            showlegend=True
        )

        # Add improvement annotation if available
        if 'comparison' in data and 'perceived_performance_improvement' in data['comparison']:
            improvement = data['comparison']['perceived_performance_improvement']
            fig.add_annotation(
                text=f"Improvement: {improvement}",
                xref="paper",
                yref="paper",
                x=0.5,
                y=1.05,
                showarrow=False,
                font=dict(size=14, color=self.color_scheme['success'])
            )

        return fig

    def _create_empty_chart(self, message: str) -> go.Figure:
        """Create empty chart with message"""
        fig = go.Figure()

        fig.add_annotation(
            text=message,
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=16, color=self.color_scheme['neutral'])
        )

        fig.update_layout(
            template='plotly_white',
            height=400,
            xaxis=dict(visible=False),
            yaxis=dict(visible=False)
        )

        return fig

    def export_chart_html(self, fig: go.Figure, filename: str) -> None:
        """Export chart as standalone HTML file"""
        fig.write_html(filename)
        print(f"✓ Chart exported to {filename}")

    def export_chart_image(self, fig: go.Figure, filename: str, format: str = 'png') -> None:
        """Export chart as static image (requires kaleido)"""
        try:
            fig.write_image(filename, format=format)
            print(f"✓ Chart exported to {filename}")
        except Exception as e:
            print(f"⚠ Image export failed: {str(e)}")
            print("  Install kaleido for image export: pip install kaleido")
