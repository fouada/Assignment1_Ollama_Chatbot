# Interactive Research Dashboard Guide

## 📊 Overview

The Research Dashboard provides **highest-level visualization** of all research findings through an interactive web interface. Built with Streamlit and Plotly, it offers:

- 📈 **Real-time interactive charts** (zoom, pan, hover for details)
- 🎨 **Professional visualizations** (publication-quality)
- 🔄 **Dynamic filtering** (explore data from multiple angles)
- 📱 **Responsive design** (works on all screen sizes)
- 💾 **Export capabilities** (save charts as PNG/HTML)

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Install visualization libraries
pip install plotly>=5.18.0 pandas>=2.1.0

# Or install all requirements
pip install -r requirements.txt
```

### 2. Run Experiments (Generate Data)

```bash
# Generate research data first
python run_research_experiments.py --all --model llama3.2
```

This creates the data files:
- `sensitivity_analysis_results.json`
- `data_comparison_results.json`
- `mathematical_proofs_results.json`

### 3. Launch Dashboard

```bash
# Start the interactive dashboard
streamlit run research_dashboard.py
```

The dashboard will open automatically in your browser at `http://localhost:8501`

---

## 🎯 Dashboard Sections

### 🏠 Overview
**Executive summary with key metrics**

Features:
- Total experiments count
- Proofs verified (5/5)
- Models analyzed
- Key findings summary
- Performance summary table

**Use this for:** Quick project status and high-level insights

---

### 🔬 Sensitivity Analysis
**Parameter optimization visualization**

Charts:
- Temperature vs Quality (line plot)
- Temperature vs Latency (line plot)
- Temperature vs Throughput (line plot)
- Statistical summary (mean, std, range)

Features:
- **Interactive**: Hover for exact values
- **Metric selection**: Switch between quality/latency/throughput
- **Optimal value indicators**: Vertical line shows best configuration

**Use this for:** Finding optimal temperature and understanding parameter effects

**Example Insights:**
- Temperature 0.7 maximizes quality/performance balance
- Correlation coefficient shows strength of relationship
- Range shows variability across parameter space

---

### 📊 Model Comparison
**Statistical model evaluation**

Charts:
- Composite score bar chart
- Latency comparison (grouped bars)
- Quality comparison (grouped bars)
- Throughput comparison (grouped bars)
- Model rankings table

Features:
- **Error bars**: Show confidence intervals
- **Color coding**: Consistent model colors
- **Statistical significance**: Markers for significant differences

**Use this for:** Choosing the best model for your workload

**Example Insights:**
- llama3.2 has highest composite score
- mistral is fastest but phi3 has best quality
- Statistical tests show which differences are significant

---

### ⚡ Latency Analysis
**Distribution and percentile analysis**

Charts:
- Box plots (distribution shape)
- Percentile chart (p50, p90, p95, p99)
- Detailed statistics table

Features:
- **Percentiles**: Critical for SLA definition
- **Distribution shape**: Skewness and kurtosis
- **Variability**: Coefficient of variation (CV)

**Use this for:** Setting performance SLAs and understanding tail latency

**Example Insights:**
- p95 latency: 95% of requests complete within X seconds
- p99 latency: Shows worst-case performance
- CV < 15%: Consistent, predictable performance

---

### ✨ Quality Metrics
**Multi-dimensional quality assessment**

Charts:
- Radar chart (5 dimensions)
- Category breakdown table
- Overall quality metrics

Dimensions:
1. **Factual**: Short factual answers
2. **Explanation**: Detailed explanations
3. **Coding**: Code generation quality
4. **Creative**: Creative writing
5. **Reasoning**: Logical reasoning

Features:
- **Model selection**: Compare quality profiles
- **Category scores**: See strengths/weaknesses
- **Overall consistency**: Variance across tasks

**Use this for:** Understanding model strengths for specific tasks

**Example Insights:**
- Model X excels at coding but weaker at creative tasks
- Overall quality score of 0.85/1.0
- High consistency (low variance) indicates reliability

---

### 📈 Statistical Tests
**Hypothesis testing results**

Charts:
- Heatmap (p-values for all comparisons)
- Detailed test results table

Metrics:
- **p-value**: Statistical significance (p < 0.05)
- **Cohen's d**: Effect size (practical significance)
- **Better model**: Which model wins comparison

Features:
- **Color coding**: Green = significant, Red = not significant
- **Multiple metrics**: Latency, quality, throughput
- **Pairwise comparisons**: All model pairs tested

**Use this for:** Evidence-based model selection with statistical rigor

**Example Insights:**
- llama3.2 vs mistral: p=0.0023 → significantly different
- Effect size d=0.67 → medium practical difference
- Quality comparison: p=0.34 → no significant difference

---

### 🎯 Recommendations
**Data-driven configuration guidance**

Sections:
- Temperature configuration
- Model selection
- Streaming mode
- Resource configuration
- Error handling
- Production checklist

Features:
- **Research-backed**: Based on experimental data
- **Specific values**: Exact configuration recommendations
- **Context-aware**: Different recommendations for different scenarios

**Use this for:** Configuring your production system optimally

---

## 🎨 Visualization Types

### Line Plots
**Best for:** Showing trends and relationships
- Temperature sensitivity
- Performance over time
- Correlation analysis

**Interactive Features:**
- Zoom: Click and drag
- Pan: Shift + drag
- Hover: See exact values
- Download: Camera icon (top right)

### Bar Charts
**Best for:** Comparing categories
- Model comparisons
- Percentile values
- Category scores

**Interactive Features:**
- Grouped bars: Compare multiple metrics
- Error bars: Show uncertainty
- Click legend: Show/hide series

### Box Plots
**Best for:** Distribution analysis
- Latency distributions
- Outlier detection
- Quartile visualization

**Interactive Features:**
- Shows min, Q1, median, Q3, max
- Outliers displayed as points
- Multiple models side-by-side

### Radar Charts
**Best for:** Multi-dimensional comparison
- Quality profiles
- Strength/weakness patterns
- Overall capability visualization

**Interactive Features:**
- 360° view of capabilities
- Area shows overall strength
- Easy pattern recognition

### Heatmaps
**Best for:** Matrix data
- Correlation matrices
- P-value comparisons
- Multi-factor analysis

**Interactive Features:**
- Color intensity shows magnitude
- Hover for exact values
- Annotations on cells

---

## 💡 Pro Tips

### Data Exploration

1. **Start with Overview** - Get the big picture
2. **Drill into specifics** - Use navigation for detailed views
3. **Compare metrics** - Use dropdown menus to switch views
4. **Check statistics** - Expand sections for detailed numbers

### Chart Interactions

```
Hover          → See exact values
Click & Drag   → Zoom into region
Double Click   → Reset zoom
Click Legend   → Show/hide series
Camera Icon    → Download chart as PNG
```

### Export Results

**Export individual charts:**
1. Hover over chart
2. Click camera icon (top right)
3. Choose format: PNG or SVG

**Export as HTML:**
```python
from research.visualizations import ResearchVisualizer

viz = ResearchVisualizer()
fig = viz.create_model_comparison_chart(data)
viz.export_chart_html(fig, "comparison.html")
```

### Custom Analysis

**Filter data:**
- Use sidebar dropdowns
- Select specific models
- Choose metrics of interest

**Compare scenarios:**
- Open dashboard in multiple tabs
- Compare different experiment runs
- Analyze parameter variations

---

## 📋 Dashboard Structure

```
research_dashboard.py              # Main dashboard app
├── Overview                       # Executive summary
│   ├── Key metrics (4 cards)
│   ├── Key findings (2 boxes)
│   └── Performance summary table
│
├── Sensitivity Analysis          # Parameter optimization
│   ├── Interactive line chart
│   ├── Metric selector
│   └── Statistical summary
│
├── Model Comparison              # Model evaluation
│   ├── Bar charts (4 metrics)
│   ├── Rankings table
│   └── Pairwise comparisons
│
├── Latency Analysis             # Distribution analysis
│   ├── Box plots
│   ├── Percentile chart
│   └── Detailed statistics
│
├── Quality Metrics              # Quality assessment
│   ├── Radar chart
│   ├── Category breakdown
│   └── Overall quality
│
├── Statistical Tests            # Hypothesis testing
│   ├── P-value heatmap
│   └── Detailed test results
│
└── Recommendations              # Configuration guidance
    ├── Temperature config
    ├── Model selection
    ├── Resource settings
    └── Production checklist
```

---

## 🔧 Customization

### Change Colors

Edit `research/visualizations.py`:

```python
self.color_scheme = {
    'primary': '#1f77b4',      # Change to your brand color
    'secondary': '#ff7f0e',
    'success': '#2ca02c',
    # ... etc
}
```

### Add New Charts

1. Add visualization method to `ResearchVisualizer` class:

```python
def create_my_custom_chart(self, data: Dict) -> go.Figure:
    fig = go.Figure()
    # Your chart code here
    return fig
```

2. Add section to `research_dashboard.py`:

```python
def render_my_section(visualizer):
    st.markdown("## My Custom Analysis")
    fig = visualizer.create_my_custom_chart(data)
    st.plotly_chart(fig, use_container_width=True)
```

3. Add to navigation:

```python
page = st.sidebar.radio("Select Section", [
    # ... existing sections
    "📌 My Custom Section"
])

if "Custom" in page:
    render_my_section(visualizer)
```

### Modify Layout

**Change page width:**
```python
st.set_page_config(layout="wide")  # or "centered"
```

**Adjust columns:**
```python
col1, col2, col3 = st.columns([2, 1, 1])  # Proportional widths
```

**Add custom CSS:**
```python
st.markdown("""
<style>
    .my-custom-class {
        /* Your styles */
    }
</style>
""", unsafe_allow_html=True)
```

---

## 🐛 Troubleshooting

### Dashboard Won't Start

```bash
# Check Streamlit is installed
pip install streamlit

# Check version
streamlit --version

# Try running with verbose output
streamlit run research_dashboard.py --logger.level=debug
```

### No Data Displayed

**Problem:** "No data found" warnings

**Solution:**
```bash
# Run experiments first
python run_research_experiments.py --all

# Verify data files exist
ls -la *.json
```

### Charts Not Rendering

**Problem:** Blank charts or errors

**Solution:**
```bash
# Install plotly
pip install plotly

# Update if old version
pip install --upgrade plotly
```

### Import Errors

**Problem:** `ModuleNotFoundError`

**Solution:**
```bash
# Install all dependencies
pip install -r requirements.txt

# Or manually install
pip install streamlit plotly pandas
```

### Port Already in Use

**Problem:** "Port 8501 is already in use"

**Solution:**
```bash
# Use different port
streamlit run research_dashboard.py --server.port 8502

# Or kill existing process
lsof -ti:8501 | xargs kill
```

---

## 📸 Screenshots (Example Views)

### Overview Page
- 4 metric cards showing: Total Experiments, Proofs Verified, Models Analyzed, Data Points
- Key findings in colored boxes
- Performance summary table with all models

### Sensitivity Analysis
- Interactive line chart: Temperature (x-axis) vs Quality (y-axis)
- Vertical line indicating optimal temperature
- Hoverable points with exact values

### Model Comparison
- Grouped bar chart comparing 3 models across metrics
- Color-coded by model (consistent colors throughout)
- Error bars showing standard deviation

### Latency Analysis
- Box plots showing distribution for each model
- Percentile chart (p50, p90, p95, p99)
- Statistics table with detailed metrics

### Quality Metrics
- Radar chart with 5 dimensions
- Perfect pentagon = perfect scores in all categories
- Area size represents overall quality

### Statistical Tests
- Heatmap showing p-values
- Green cells = significant difference
- Red cells = no significant difference

---

## 🎓 For Academic Presentation

### Demonstration Flow

1. **Start with Overview** (30 seconds)
   - "Our research framework analyzed X experiments across Y models"
   - Show key metrics cards
   - Highlight proof verification

2. **Show Sensitivity Analysis** (1 minute)
   - "We tested temperatures from 0.0 to 2.0"
   - Interactive: Move mouse over chart
   - "Optimal value is 0.7 with correlation r=-0.23"

3. **Model Comparison** (1 minute)
   - "Statistical comparison of multiple models"
   - Show bar chart with error bars
   - "llama3.2 ranked highest with composite score 0.85"

4. **Statistical Significance** (1 minute)
   - Show p-value heatmap
   - "Green indicates statistical significance (p<0.05)"
   - "Model A vs B: p=0.0023, Cohen's d=0.67 (medium effect)"

5. **Quality Analysis** (30 seconds)
   - Show radar chart
   - "Multi-dimensional quality assessment"
   - Point out strengths/weaknesses

6. **Recommendations** (30 seconds)
   - "Based on our analysis, we recommend..."
   - Show configuration checklist
   - Highlight research-backed values

### Key Talking Points

✅ **Interactive**: "Dashboard provides real-time exploration of results"
✅ **Comprehensive**: "Covers all aspects: sensitivity, comparison, quality"
✅ **Statistical**: "Rigorous hypothesis testing with p-values and effect sizes"
✅ **Visual**: "Publication-quality charts with professional styling"
✅ **Actionable**: "Clear recommendations based on empirical data"

---

## 🔗 Integration

### Use with Other Tools

**Export for Reports:**
```python
# Generate charts programmatically
from research.visualizations import ResearchVisualizer

viz = ResearchVisualizer()
data = viz.load_json_data("sensitivity_analysis_results.json")

# Create chart
fig = viz.create_sensitivity_chart(data)

# Export as HTML (embeddable)
viz.export_chart_html(fig, "sensitivity_chart.html")

# Export as image (for papers)
viz.export_chart_image(fig, "sensitivity_chart.png")
```

**Embed in Notebooks:**
```python
# In Jupyter notebook
import plotly.graph_objects as go
from research.visualizations import ResearchVisualizer

viz = ResearchVisualizer()
fig = viz.create_model_comparison_chart(data)
fig.show()  # Renders inline
```

**Automated Reporting:**
```python
# Generate all charts automatically
from research.visualizations import ResearchVisualizer

viz = ResearchVisualizer()

# Load all data
sens_data = viz.load_json_data("sensitivity_analysis_results.json")
comp_data = viz.load_json_data("data_comparison_results.json")

# Generate charts
charts = [
    viz.create_sensitivity_chart(sens_data),
    viz.create_model_comparison_chart(comp_data),
    # ... more charts
]

# Export all
for i, fig in enumerate(charts):
    viz.export_chart_html(fig, f"chart_{i}.html")
```

---

## 📚 Additional Resources

### Streamlit Documentation
- [Streamlit Docs](https://docs.streamlit.io/)
- [Plotly in Streamlit](https://docs.streamlit.io/library/api-reference/charts/st.plotly_chart)

### Plotly Documentation
- [Plotly Python](https://plotly.com/python/)
- [Chart Types](https://plotly.com/python/basic-charts/)
- [Interactivity](https://plotly.com/python/interactive-html-export/)

### Best Practices
- [Data Visualization Principles](https://datavizproject.com/)
- [Color Theory for Dashboards](https://www.tableau.com/learn/articles/color-theory)

---

## 🎉 Summary

The Interactive Research Dashboard provides:

✅ **Highest-level visualization** - Professional charts for all research data
✅ **Interactive exploration** - Zoom, filter, hover for insights
✅ **Multiple perspectives** - 7 different views of your data
✅ **Statistical rigor** - P-values, effect sizes, confidence intervals
✅ **Publication-ready** - Export charts for papers/presentations
✅ **User-friendly** - No coding required to explore results
✅ **Comprehensive** - Covers sensitivity, comparison, quality, statistics

**Ready to visualize your research findings at the highest level! 📊✨**

---

*For questions or issues, refer to the troubleshooting section or review the source code in `research_dashboard.py` and `research/visualizations.py`.*
