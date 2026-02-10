"""
AI Annotation Quality Dashboard
Clean, modern interface for evaluating AI model performance
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
import json
import sys

# Add pipeline to path
sys.path.append(str(Path(__file__).parent / 'pipeline'))
from kappa_calculator import KappaCalculator
from model_evaluator import ModelEvaluator

# Page config
st.set_page_config(
    page_title="Nutrition Label Dashboard",
    page_icon="🏷️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern, dark mode look
st.markdown("""
<style>
    /* Import modern font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Dark mode color scheme */
    .stApp {
        background-color: #0e1117 !important;
        color: #ffffff;
    }
    
    /* Remove header white bar - COMPLETE FIX */
    header {
        background-color: #0e1117 !important;
    }
    
    header[data-testid="stHeader"] {
        background-color: #0e1117 !important;
    }
    
    .stApp > header {
        background-color: #0e1117 !important;
    }
    
    [data-testid="stToolbar"] {
        background-color: #0e1117 !important;
    }
    
    /* Top decoration bar */
    [data-testid="stDecoration"] {
        background: linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%) !important;
        height: 3px !important;
    }
    
    /* Ensure header elements are visible */
    header * {
        background-color: transparent !important;
    }
    
    /* Sidebar toggle button - SUPER VISIBLE */
    button[kind="header"] {
        color: white !important;
        background: linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%) !important;
        border-radius: 8px !important;
        padding: 0.5rem !important;
        border: 2px solid white !important;
    }
    
    button[kind="header"]:hover {
        background: linear-gradient(135deg, #a78bfa 0%, #f472b6 100%) !important;
        transform: scale(1.1);
    }
    
    [data-testid="collapsedControl"] {
        color: white !important;
        background: linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%) !important;
        border-radius: 8px !important;
        padding: 0.75rem !important;
        border: 2px solid white !important;
        box-shadow: 0 0 20px rgba(139, 92, 246, 0.8) !important;
    }
    
    [data-testid="collapsedControl"]:hover {
        background: linear-gradient(135deg, #a78bfa 0%, #f472b6 100%) !important;
        transform: scale(1.1);
        box-shadow: 0 0 30px rgba(236, 72, 153, 0.9) !important;
    }
    
    [data-testid="collapsedControl"] svg {
        fill: white !important;
        stroke: white !important;
        width: 24px !important;
        height: 24px !important;
    }
    
    /* Sidebar toggle when expanded */
    [data-testid="stSidebarCollapse"] button {
        color: white !important;
        background: linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%) !important;
        border-radius: 8px !important;
        padding: 0.5rem !important;
        border: 2px solid white !important;
    }
    
    [data-testid="stSidebarCollapse"] button:hover {
        background: linear-gradient(135deg, #a78bfa 0%, #f472b6 100%) !important;
        transform: scale(1.1);
    }
    
    [data-testid="stSidebarCollapse"] button svg {
        fill: white !important;
        stroke: white !important;
        width: 24px !important;
        height: 24px !important;
    }
    
    /* Base button styling override */
    section[data-testid="stSidebar"] button[kind="header"] {
        background: linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%) !important;
        border: 2px solid white !important;
    }
    
    /* AGGRESSIVE - Make ALL header buttons white */
    button[data-testid*="baseButton-header"] {
        background: linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%) !important;
        border: 2px solid white !important;
        color: white !important;
    }
    
    /* Target all SVG paths in header buttons */
    header button svg path {
        fill: white !important;
        stroke: white !important;
    }
    
    header button svg {
        color: white !important;
    }
    
    /* Universal - ANY button in header area */
    header button {
        color: white !important;
        filter: brightness(200%) !important;
    }
    
    header button:hover {
        filter: brightness(250%) !important;
    }
    
    /* Main content area backgrounds */
    .main, .main .block-container {
        background-color: #0e1117 !important;
    }
    
    /* All container elements transparent */
    [data-testid="column"],
    [data-testid="stVerticalBlock"],
    [data-testid="stHorizontalBlock"],
    [data-testid="stMarkdownContainer"],
    .element-container {
        background-color: transparent !important;
    }
    
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    
    .subtitle {
        text-align: center;
        color: #9ca3af;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    
    .section-header {
        font-size: 1.6rem;
        font-weight: 600;
        color: #f3f4f6;
        margin-top: 3rem;
        margin-bottom: 1.5rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #374151;
    }
    
    .subsection-header {
        font-size: 1.2rem;
        font-weight: 600;
        color: #e5e7eb;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    
    .stMetric {
        background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
        padding: 1.2rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        border: 1px solid #374151;
    }
    
    .stMetric label {
        font-size: 0.9rem !important;
        font-weight: 500 !important;
        color: #9ca3af !important;
    }
    
    .stMetric [data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 700 !important;
        color: #f3f4f6 !important;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1f2937 0%, #111827 100%) !important;
        border-right: 1px solid #374151;
    }
    
    [data-testid="stSidebar"] * {
        color: #e5e7eb !important;
    }
    
    /* Button styling */
    .stButton button {
        background: linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        box-shadow: 0 4px 12px rgba(139, 92, 246, 0.4);
        transition: all 0.3s ease;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(139, 92, 246, 0.6);
    }
    
    /* Ensure button text is visible */
    button[kind="primary"] {
        background: linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%) !important;
        color: white !important;
    }
    
    button p {
        color: white !important;
    }
    
    /* File uploader - complete dark mode */
    [data-testid="stFileUploader"] {
        background-color: #1f2937 !important;
        border: 2px dashed #4b5563 !important;
        border-radius: 12px;
        padding: 1.5rem;
    }
    
    [data-testid="stFileUploader"] label {
        color: #e5e7eb !important;
    }
    
    [data-testid="stFileUploader"] section {
        background-color: #1f2937 !important;
        border: none !important;
    }
    
    [data-testid="stFileUploader"] > div {
        background-color: transparent !important;
    }
    
    [data-testid="stFileUploader"] button {
        background-color: #374151 !important;
        color: #e5e7eb !important;
        border: 1px solid #4b5563 !important;
    }
    
    [data-testid="stFileUploader"] button:hover {
        background-color: #4b5563 !important;
    }
    
    [data-testid="stFileUploader"] small {
        color: #9ca3af !important;
    }
    
    /* Info cards styling */
    .info-card {
        background: linear-gradient(135deg, #1f2937 0%, #111827 100%) !important;
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 4px solid #8b5cf6;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        margin: 1rem 0;
        color: #e5e7eb;
    }
    
    .info-card h3 {
        color: #f3f4f6;
    }
    
    /* Alert boxes styling */
    .stAlert,
    [data-baseweb="notification"] {
        background-color: #1f2937 !important;
        border: 1px solid #374151 !important;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        color: #e5e7eb !important;
    }
    
    /* Other component styling */
    .stDataFrame {
        background-color: #1f2937;
    }
    
    .streamlit-expanderHeader {
        background-color: #1f2937;
        color: #e5e7eb;
        border-radius: 8px;
    }
    
    .stProgress > div > div {
        background: linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%);
    }
    
    .js-plotly-plot {
        background-color: transparent !important;
    }
    
    section[data-testid="stFileUploadDropzone"] {
        background-color: #1f2937 !important;
        border: 2px dashed #4b5563 !important;
    }
    
    [data-testid="stFileUploadDropzone"] span {
        color: #9ca3af !important;
    }
</style>
""", unsafe_allow_html=True)

def interpret_score(score):
    """Interpret agreement/accuracy score with user-friendly language."""
    if score is None:
        return "Not Available", "gray"
    elif score >= 0.90:
        return "Excellent", "#38ef7d"
    elif score >= 0.75:
        return "Good", "#11998e"
    elif score >= 0.60:
        return "Fair", "#f5a623"
    elif score >= 0.40:
        return "Needs Improvement", "#f5576c"
    else:
        return "Poor", "#d63031"

def create_score_gauge(score_value, title, target=0.75):
    """Create a modern gauge chart for scores (dark mode)."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score_value * 100 if score_value else 0,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 18, 'color': '#e5e7eb'}},
        number={'suffix': "%", 'font': {'size': 40, 'color': '#f3f4f6'}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#4b5563"},
            'bar': {'color': "#8b5cf6", 'thickness': 0.75},
            'bgcolor': "#1f2937",
            'borderwidth': 0,
            'steps': [
                {'range': [0, 40], 'color': '#4c1d1d'},
                {'range': [40, 60], 'color': '#4c3a1d'},
                {'range': [60, 75], 'color': '#4c4c1d'},
                {'range': [75, 90], 'color': '#1d4c1d'},
                {'range': [90, 100], 'color': '#0f3d0f'}
            ],
            'threshold': {
                'line': {'color': "#ec4899", 'width': 3},
                'thickness': 0.75,
                'value': target * 100
            }
        }
    ))
    fig.update_layout(
        height=280,
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'family': 'Inter, sans-serif', 'color': '#e5e7eb'}
    )
    return fig

def create_confusion_matrix_heatmap(cm_data, category):
    """Create confusion matrix heatmap (dark mode)."""
    matrix = cm_data['matrix']
    
    z = [[matrix['positive_positive'], matrix['positive_negative']],
         [matrix['negative_positive'], matrix['negative_negative']]]
    
    # Create custom text with better visibility
    text = [[f"<b>{val}</b>" for val in row] for row in z]
    
    fig = go.Figure(data=go.Heatmap(
        z=z,
        x=['Annotator 2: Positive', 'Annotator 2: Negative'],
        y=['Annotator 1: Positive', 'Annotator 1: Negative'],
        colorscale='Purples',
        text=text,
        texttemplate='%{text}',
        textfont={"size": 28, "color": "black", "family": "Inter, sans-serif"},
        hoverongaps=False,
        showscale=True,
        colorbar=dict(
            tickfont=dict(color='#e5e7eb'),
            title=dict(text="Count", font=dict(color='#e5e7eb'))
        )
    ))
    
    fig.update_layout(
        title=dict(
            text=f'{category.upper()} - Confusion Matrix',
            font=dict(color='#e5e7eb', size=16)
        ),
        xaxis=dict(
            title=dict(text='Annotator 2', font=dict(color='#e5e7eb', size=14)),
            tickfont=dict(color='#e5e7eb', size=12)
        ),
        yaxis=dict(
            title=dict(text='Annotator 1', font=dict(color='#e5e7eb', size=14)),
            tickfont=dict(color='#e5e7eb', size=12)
        ),
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': '#e5e7eb', 'family': 'Inter, sans-serif'}
    )
    return fig

def create_category_comparison(category_scores, metric_name):
    """Create bar chart comparing categories (dark mode)."""
    df = pd.DataFrame([
        {'Category': cat, metric_name: score * 100}
        for cat, score in category_scores.items()
        if score is not None
    ])
    
    fig = px.bar(
        df,
        x='Category',
        y=metric_name,
        title=f'{metric_name} by Category',
        color=metric_name,
        color_continuous_scale='Purples',
        range_color=[0, 100]
    )
    
    fig.update_layout(
        xaxis_title='Category',
        yaxis_title=f'{metric_name} (%)',
        yaxis_range=[0, 100],
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': '#e5e7eb'},
        xaxis={'gridcolor': '#374151'},
        yaxis={'gridcolor': '#374151'}
    )
    return fig

def main():
    # Header
    st.markdown('<h1 class="main-header">Nutrition Label Dashboard</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Evaluate annotation and model\'s performance with human feedback</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 📁 Upload Data")
        st.caption("Upload feedback files from your reviewers")
        
        uploaded_files = st.file_uploader(
            "Choose JSON files",
            type=['json'],
            accept_multiple_files=True,
            help="Upload 2 or more feedback files from different reviewers",
            label_visibility="collapsed"
        )
        
        if uploaded_files:
            st.success(f"✅ {len(uploaded_files)} file(s) ready")
            st.markdown("---")
            run_analysis = st.button(" Analyze", type="primary", width="stretch")
        else:
            run_analysis = False
            st.markdown("---")
            st.info(" Upload 2+ files to start")
        
        st.markdown("---")
        st.markdown("### Guide")
        st.markdown("""
        **What you'll see:**
        - How well reviewers agree
        - Model accuracy metrics  
        - Performance by category
        - Areas to improve
        """)
        
        st.markdown("---")
    
    # Main content
    if not uploaded_files:
        # Clear any previous results
        if 'iaa_results' in st.session_state:
            del st.session_state['iaa_results']
        if 'eval_results' in st.session_state:
            del st.session_state['eval_results']
            
        # Welcome screen
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="info-card">', unsafe_allow_html=True)
            st.markdown("### 👥 Annotator Agreement")
            st.markdown("""
            Check if your reviewers are giving consistent feedback on the AI's performance.
            
            **You'll see:**
            - Agreement percentage
            - Consistency scores
            - Where reviewers disagree
            """)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="info-card">', unsafe_allow_html=True)
            st.markdown("### 🎯 Model Accuracy")
            st.markdown("""
            Measure how often the AI gets it right based on human consensus.
            
            **You'll see:**
            - Overall accuracy
            - Performance by category
            - Error patterns
            """)
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        st.info("**Upload your feedback files from the sidebar to get started**")
        
    elif run_analysis or ('iaa_results' in st.session_state and 'eval_results' in st.session_state):
        # If run_analysis button is clicked, run the analysis
        if run_analysis:
            # Save uploaded files temporarily
            temp_dir = Path("temp_uploads")
            temp_dir.mkdir(exist_ok=True)
            
            file_paths = []
            for uploaded_file in uploaded_files:
                file_path = temp_dir / uploaded_file.name
                with open(file_path, 'wb') as f:
                    f.write(uploaded_file.getbuffer())
                file_paths.append(str(file_path))
            
            # Progress indicator
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # Phase 3: IAA Analysis
                status_text.text("📊 Phase 3: Calculating Inter-Annotator Agreement...")
                progress_bar.progress(25)
                
                kappa_calc = KappaCalculator()
                iaa_results = kappa_calc.calculate_agreement(file_paths)
                
                progress_bar.progress(50)
                
                # Phase 4: Model Evaluation
                status_text.text("📈 Phase 4: Evaluating Model Performance...")
                
                model_eval = ModelEvaluator()
                eval_results = model_eval.evaluate_model(file_paths)
                
                progress_bar.progress(100)
                status_text.text("✅ Analysis Complete!")
                
                # Store results in session state
                st.session_state['iaa_results'] = iaa_results
                st.session_state['eval_results'] = eval_results
                
                # Cleanup
                for file_path in file_paths:
                    Path(file_path).unlink()
                
            except Exception as e:
                st.error(f"❌ Error during analysis: {str(e)}")
                st.exception(e)
                return
        
        # Display results (from session state or just computed)
        st.markdown("---")
        display_results(st.session_state['iaa_results'], st.session_state['eval_results'])

def display_results(iaa_results, eval_results):
    """Display analysis results in a clean, modern format."""
    
    # ========================================================================
    # REVIEWER AGREEMENT SECTION
    # ========================================================================
    st.markdown('<h2 class="section-header">Annotator Agreement Analysis</h2>', unsafe_allow_html=True)
    st.caption("How consistently did your annotators evaluate?")
    
    # Overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        kappa_val = iaa_results['overall_kappa']
        interpretation, color = interpret_score(kappa_val if kappa_val else 0)
        st.metric(
            "Kappa Score",
            f"{kappa_val:.3f}" if kappa_val else "N/A",
            delta=interpretation,
            help="Cohen's/Fleiss' Kappa - measures agreement corrected for chance"
        )
    
    with col2:
        agreement = iaa_results.get('overall_raw_agreement', 0)
        st.metric(
            "Agreement Rate",
            f"{agreement*100:.1f}%",
            help="Simple percentage - how often reviewers gave the same feedback"
        )
    
    with col3:
        st.metric(
            "Reviewers",
            iaa_results['n_annotators'],
            help="Number of people who reviewed"
        )
    
    with col4:
        st.metric(
            "Posts Reviewed",
            iaa_results['n_posts'],
            help="Total posts analyzed"
        )
    
    # Agreement gauge chart
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<p class="subsection-header">Overall Kappa Score</p>', unsafe_allow_html=True)
        kappa_val = iaa_results['overall_kappa']
        fig = create_score_gauge(kappa_val if kappa_val else 0, "Inter-Annotator Agreement (Kappa)", target=0.60)
        st.plotly_chart(fig, width="stretch")
    
    with col2:
        st.markdown('<p class="subsection-header">💡 What This Means</p>', unsafe_allow_html=True)
        kappa = kappa_val if kappa_val else 0
        if kappa >= 0.80:
            st.success("""
            **Almost Perfect!** Your reviewers show excellent agreement. 
            
            """)
        elif kappa >= 0.60:
            st.success("""
            **Substantial Agreement!** Reviewers are quite consistent. 
            R
            """)
        elif kappa >= 0.40:
            st.info("""
            **Moderate Agreement:** Reviewers show fair consistency. 
            
            """)
        else:
            st.warning("""
            **Low Agreement:** Reviewers need clearer guidelines 
            or training to improve consistency.
            """)
    
    # Category-wise Kappa scores
    st.markdown('<p class="subsection-header">📋 Kappa Score by Category</p>', unsafe_allow_html=True)
    
    if 'category_scores' in iaa_results:
        fig = create_category_comparison(iaa_results['category_scores'], 'Kappa Score')
        st.plotly_chart(fig, width="stretch")
    
    # Detailed table with Kappa scores
    with st.expander(" View Detailed Breakdown"):
        df_data = []
        for category in iaa_results['category_scores'].keys():
            kappa_score = iaa_results['category_scores'].get(category)
            raw_agr = iaa_results.get('raw_agreement_scores', {}).get(category)
            
            # Interpret based on Kappa
            if kappa_score is not None:
                if kappa_score >= 0.80:
                    interpretation = "Almost Perfect"
                elif kappa_score >= 0.60:
                    interpretation = "Substantial"
                elif kappa_score >= 0.40:
                    interpretation = "Moderate"
                elif kappa_score >= 0.20:
                    interpretation = "Fair"
                else:
                    interpretation = "Poor"
            else:
                interpretation = "N/A"
            
            df_data.append({
                'Category': category.title(),
                'Kappa Score': f"{kappa_score:.3f}" if kappa_score is not None else "N/A",
                'Interpretation': interpretation,
                'Raw Agreement': f"{raw_agr*100:.1f}%" if raw_agr else "N/A"
            })
        
        df = pd.DataFrame(df_data)
        st.dataframe(df, width="stretch", hide_index=True)
    
    # Confusion Matrices (optional, hidden by default)
    if 'confusion_matrices' in iaa_results and iaa_results['n_annotators'] == 2:
        with st.expander(" Advanced: Reviewer Comparison Matrix"):
            st.caption("See exactly where reviewers agreed and disagreed")
            
            # Filter out categories with None data
            available_categories = {
                cat: data for cat, data in iaa_results['confusion_matrices'].items() 
                if data is not None
            }
            
            if not available_categories:
                st.warning("⚠️ No confusion matrix data available. Confusion matrices require at least some annotated data for each category.")
            else:
                categories = list(available_categories.keys())
                selected_category = st.selectbox(
                    "Select category", 
                    categories, 
                    label_visibility="collapsed",
                    key="cm_category_selector"
                )
                
                cm_data = available_categories[selected_category]
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    fig = create_confusion_matrix_heatmap(cm_data, selected_category)
                    st.plotly_chart(fig, width="stretch")
                
                with col2:
                    st.metric("Posts", cm_data['total_items'])
                    st.metric("Reviewer 1 Approval", f"{cm_data['annotator_1_positive_rate']*100:.1f}%")
                    st.metric("Reviewer 2 Approval", f"{cm_data['annotator_2_positive_rate']*100:.1f}%")
    
    # ========================================================================
    # AI PERFORMANCE SECTION
    # ========================================================================
    st.markdown("---")
    st.markdown('<h2 class="section-header">Model Performance Results</h2>', unsafe_allow_html=True)
    st.caption("How accurate is your model based on reviewer consensus?")
    
    # Overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    overall = eval_results['overall_metrics']
    accuracy = overall['overall_accuracy']
    
    with col1:
        interpretation, _ = interpret_score(accuracy)
        st.metric(
            "Model Accuracy",
            f"{accuracy*100:.1f}%",
            delta=interpretation,
            help="How often the model predictions were correct"
        )
    
    with col2:
        st.metric(
            "Correct",
            overall['total_correct'],
            delta="✓ Right",
            help="Number of correct model predictions"
        )
    
    with col3:
        st.metric(
            "Errors",
            overall['total_incorrect'],
            delta="✗ Wrong",
            delta_color="inverse",
            help="Number of incorrect model predictions"
        )
    
    with col4:
        unclear = overall['total_uncertain']
        st.metric(
            "Unclear",
            unclear,
            delta=f"{unclear} cases",
            help="Cases where reviewers disagreed"
        )
    
    # Accuracy gauge
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<p class="subsection-header">Overall Performance</p>', unsafe_allow_html=True)
        fig = create_score_gauge(accuracy, "Model Accuracy Score", target=0.75)
        st.plotly_chart(fig, width="stretch")
    
    # with col2:
    #     st.markdown('<p class="subsection-header">💡 Assessment</p>', unsafe_allow_html=True)
    #     if accuracy >= 0.90:
    #         st.success("""
    #         **Outstanding!** Your model is performing excellently. 
    #         Ready for production use.
    #         """)
    #     elif accuracy >= 0.75:
    #         st.success("""
    #         **Good!** Your model is performing well. 
    #         Minor improvements possible.
    #         """)
    #     elif accuracy >= 0.60:
    #         st.warning("""
    #         **Fair:** model is acceptable but has room for improvement. 
    #         Review error patterns.
    #         """)
    #     else:
    #         st.error("""
    #         **Needs Work:** Model accuracy is below target. 
    #         Significant improvements needed.
    #         """)
    
    # Category-wise accuracy
    st.markdown('<p class="subsection-header">📋 Performance by Category</p>', unsafe_allow_html=True)
    
    # Prepare data
    accuracy_data = {
        cat: metrics['accuracy'] 
        for cat, metrics in eval_results['category_results'].items()
    }
    
    fig = create_category_comparison(accuracy_data, 'ModelAccuracy')
    st.plotly_chart(fig, use_container_width=True)
    
    # Detailed results table
    with st.expander(" View Detailed Breakdown"):
        df_data = []
        for category, metrics in eval_results['category_results'].items():
            df_data.append({
                'Category': category.title(),
                'Accuracy': f"{metrics['accuracy']*100:.1f}%",
                'Correct': metrics['correct'],
                'Errors': metrics['incorrect'],
                'Unclear': metrics['uncertain']
            })
        
        df = pd.DataFrame(df_data)
        st.dataframe(df, width="stretch", hide_index=True)
    
    # Strengths and weaknesses
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<p class="subsection-header">✅ Top Performers</p>', unsafe_allow_html=True)
        strong_categories = [
            (cat, metrics['accuracy']) 
            for cat, metrics in eval_results['category_results'].items()
            if metrics['accuracy'] >= 0.75
        ]
        strong_categories.sort(key=lambda x: x[1], reverse=True)
        
        if strong_categories:
            for cat, acc in strong_categories:
                st.success(f"**{cat.title()}** — {acc*100:.0f}% ")
        else:
            st.info("_No categories above 75% yet_")
    
    with col2:
        st.markdown('<p class="subsection-header">Focus Areas</p>', unsafe_allow_html=True)
        weak_categories = [
            (cat, metrics['accuracy']) 
            for cat, metrics in eval_results['category_results'].items()
            if metrics['accuracy'] < 0.75
        ]
        weak_categories.sort(key=lambda x: x[1])
        
        if weak_categories:
            for cat, acc in weak_categories:
                st.warning(f"**{cat.title()}** — {acc*100:.0f}% ")
        else:
            st.success("🎉 All categories performing well!")
    
    # Sample size notice
    st.markdown("---")
    if eval_results['n_posts'] < 30:
        st.info(f"""
        📊 **Data Size:** Currently analyzed {eval_results['n_posts']} posts.  
        
        """)
    elif eval_results['n_posts'] < 100:
        st.success(f"""
         Good sample size ({eval_results['n_posts']} posts). 
        """)
    else:
        st.success(f"""
        Excellent sample size ({eval_results['n_posts']} posts)! 
        """)

if __name__ == "__main__":
    main()