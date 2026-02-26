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
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Global background and base text */
    .stApp {
        font-size: 13px;
        background: linear-gradient(180deg, #0f172a 0%, #020617 100%) !important;
        color: #f8fafc;
    }
    
    /* High-contrast solid background for visibility */
    .glass-card {
        background: rgba(10, 15, 28, 0.95) !important;
        backdrop-filter: blur(16px) !important;
        -webkit-backdrop-filter: blur(16px) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 12px !important;
        box-shadow: 0 10px 40px 0 rgba(0, 0, 0, 0.6) !important;
    }

    /* Remove header white bar */
    header, [data-testid="stHeader"] {
        background-color: transparent !important;
    }
    
    /* Top decoration bar */
    [data-testid="stDecoration"] {
        background: linear-gradient(90deg, #6366f1 0%, #a855f7 50%, #ec4899 100%) !important;
        height: 4px !important;
    }
    
    .subtitle {
        text-align: center;
        color: #ffffff !important; /* Pure white */
        font-size: 0.95rem;
        margin-bottom: 1.5rem;
        font-weight: 500;
        letter-spacing: 0.01em;
    }
    
    .section-header {
        font-size: 1.3rem;
        font-weight: 900;
        color: #ffffff !important;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid rgba(255, 255, 255, 0.4);
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }
    
    /* Metric styling with ABSOLUTE CONTRAST */
    div[data-testid="stMetric"], 
    div[data-testid="stMetricValue"], 
    div[data-testid="stMetricLabel"] {
        background-color: rgba(5, 10, 20, 0.98) !important;
        border-radius: 12px !important;
    }

    div[data-testid="stMetric"] {
        padding: 0.75rem !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5) !important;
    }
    
    /* Target ALL possible metric text elements */
    div[data-testid="stMetric"] *, 
    [data-testid="stMetricValue"] *,
    [data-testid="metric-container"] * {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }

    /* Except for the delta colors which should remain visible */
    div[data-testid="stMetricDelta"] * {
        -webkit-text-fill-color: initial !important;
    }
    
    div[data-testid="stMetricValue"] {
        font-size: 2.2rem !important;
        font-weight: 900 !important;
    }

    div[data-testid="stMetricLabel"] p {
        font-size: 0.95rem !important;
        font-weight: 800 !important;
        text-transform: uppercase !important;
    }
    
    /* Sidebar styling with ultra-bright text */
    [data-testid="stSidebar"] {
        background: rgba(10, 15, 28, 1.0) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.15);
    }
    
    [data-testid="stSidebar"] *, 
    [data-testid="stSidebarCollapse"] * {
        color: #ffffff !important;
        font-weight: 600 !important;
    }
    
    /* File uploader visibility - DARK TEXT for better contrast on light dropzone */
    [data-testid="stFileUploader"] [data-testid="stMarkdownContainer"] p {
        color: #1e293b !important; /* Dark slate */
        font-weight: 600 !important;
    }
    
    [data-testid="stFileUploader"] button {
        color: #1e293b !important;
        border-color: #1e293b !important;
    }

    /* Small text like "Limit 200MB per file" */
    [data-testid="stFileUploader"] small {
        color: #475569 !important;
    }
    
    [data-testid="stFileUploader"] section {
        background: rgba(255, 255, 255, 0.9) !important; /* Brighter background */
        border: 2px dashed #6366f1 !important;
        border-radius: 8px !important;
    }
    
    /* Uploaded file list should be white for readability on dark sidebar */
    [data-testid="stUploadedFile"] * {
        color: #ffffff !important;
    }
    
    /* Info cards styling with near-total opacity */
    .info-card {
        background: rgba(10, 15, 28, 0.98) !important;
        backdrop-filter: blur(12px);
        padding: 1.25rem;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        margin: 1rem 0;
    }
    
    .info-card h3 {
        color: #ffffff !important;
        font-weight: 800;
        margin-bottom: 0.75rem;
    }

    /* Alert box refinements */
    .stAlert {
        background: rgba(10, 15, 28, 0.95) !important;
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
    }
    
    /* Universal white for all interactive sub-elements */
    .stAlert *, .stCaption, [data-testid="stCaptionContainer"] {
        color: #ffffff !important;
        font-weight: 600 !important;
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
        title={'text': title, 'font': {'size': 14, 'color': '#ffffff'}},
        number={'suffix': "%", 'font': {'size': 36, 'color': '#ffffff'}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#334155"},
            'bar': {'color': "#6366f1", 'thickness': 0.8},
            'bgcolor': "rgba(30, 41, 59, 0.5)",
            'borderwidth': 0,
            'steps': [
                {'range': [0, 40], 'color': 'rgba(239, 68, 68, 0.1)'},
                {'range': [40, 60], 'color': 'rgba(245, 158, 11, 0.1)'},
                {'range': [60, 75], 'color': 'rgba(234, 179, 8, 0.1)'},
                {'range': [75, 90], 'color': 'rgba(34, 197, 94, 0.1)'},
                {'range': [90, 100], 'color': 'rgba(16, 185, 129, 0.1)'}
            ],
            'threshold': {
                'line': {'color': "#ec4899", 'width': 3},
                'thickness': 0.8,
                'value': target * 100
            }
        }
    ))
    fig.update_layout(
        height=140,
        margin=dict(l=15, r=15, t=30, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'family': 'Inter, sans-serif', 'color': '#ffffff'}
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
        x=['Annotator 2: Pos', 'Annotator 2: Neg'],
        y=['Annotator 1: Pos', 'Annotator 1: Neg'],
        colorscale=[[0, '#1e293b'], [1, '#6366f1']],
        text=text,
        texttemplate='%{text}',
        textfont={"size": 16, "color": "white", "family": "Inter, sans-serif"},
        hoverongaps=False,
        showscale=False
    ))
    
    fig.update_layout(
        title={
            'text': f'{category.upper()} - Matrix',
            'font': {'color': '#ffffff', 'size': 13, 'family': 'Inter, sans-serif'}
        },
        xaxis=dict(
            tickfont={'color': '#ffffff', 'size': 12},
            side='bottom'
        ),
        yaxis=dict(
            tickfont={'color': '#ffffff', 'size': 12},
            autorange='reversed'
        ),
        height=240,
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': '#ffffff', 'family': 'Inter, sans-serif'}
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
        color=metric_name,
        color_continuous_scale=[[0, '#1e293b'], [1, '#a855f7']],
        range_color=[0, 100]
    )
    
    fig.update_layout(
        title={
            'text': f'{metric_name} by Category',
            'font': {'color': '#ffffff', 'size': 14}
        },
        xaxis_title=None,
        yaxis_title=None,
        yaxis_range=[0, 105],
        height=220,
        margin=dict(l=10, r=10, t=40, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': '#ffffff', 'size': 11},
        xaxis={'gridcolor': 'rgba(255,255,255,0.2)', 'tickfont': {'size': 11, 'color': '#ffffff'}},
        yaxis={'gridcolor': 'rgba(255,255,255,0.2)', 'ticksuffix': '%', 'tickfont': {'color': '#ffffff'}},
        coloraxis_showscale=False,
        showlegend=False
    )
    
    # Modern bar styling
    fig.update_traces(
        marker_line_width=0,
        marker_opacity=0.8,
        width=0.6
    )
    return fig

def main():
    # Premium Main Header
    st.markdown("""
    <div style="text-align: center; margin-top: 2.5rem; margin-bottom: 0.5rem;">
        <h1 style="
            font-size: 4.8rem !important; 
            font-weight: 900 !important; 
            background: linear-gradient(90deg, #6366f1 0%, #a855f7 50%, #ec4899 100%); 
            -webkit-background-clip: text; 
            -webkit-text-fill-color: transparent; 
            margin: 0; 
            line-height: 1.1; 
            letter-spacing: -3px;
            filter: drop-shadow(0 4px 12px rgba(99, 102, 241, 0.3));
        ">Nutrition Label Dashboard</h1>
    </div>
    """, unsafe_allow_html=True)
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
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="info-card glass-card">', unsafe_allow_html=True)
            st.markdown("### 👥 Annotator Agreement")
            st.markdown("""
            Check if your reviewers are giving consistent feedback on the AI's performance.
            """)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with c2:
            st.markdown('<div class="info-card glass-card">', unsafe_allow_html=True)
            st.markdown("### 🎯 Model Accuracy")
            st.markdown("""
            Measure how often the AI gets it right based on human consensus.
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
        display_results(st.session_state['iaa_results'], st.session_state['eval_results'])

def display_results(iaa_results, eval_results):
    """Display analysis results in a clean, modern format."""
    
    left_col, right_col = st.columns(2)
    
    with left_col:
        st.markdown('<div class="glass-card" style="padding: 1.5rem; margin-bottom: 2rem;">', unsafe_allow_html=True)
        st.markdown('<h2 class="section-header">Annotator Agreement Analysis</h2>', unsafe_allow_html=True)
        st.caption("How consistently did your annotators evaluate?")
        
        # Overview metrics
        m1, m2, m3, m4 = st.columns(4)
        
        with m1:
            kappa_val = iaa_results['overall_kappa']
            interpretation, color = interpret_score(kappa_val if kappa_val else 0)
            st.metric(
                "Kappa",
                f"{kappa_val:.2f}" if kappa_val else "N/A",
                delta=interpretation,
                help="Cohen's/Fleiss' Kappa"
            )
        
        with m2:
            agreement = iaa_results.get('overall_raw_agreement', 0)
            st.metric(
                "Agreement",
                f"{agreement*100:.0f}%",
                help="Simple percentage"
            )
        
        with m3:
            st.metric(
                "Reviewers",
                iaa_results['n_annotators']
            )
        
        with m4:
            st.metric(
                "Posts",
                iaa_results['n_posts']
            )
        
        # Agreement gauge and info
        g_col1, g_col2 = st.columns([1, 1])
        
        with g_col1:
            kappa_val = iaa_results['overall_kappa']
            fig = create_score_gauge(kappa_val if kappa_val else 0, "Kappa Score", target=0.60)
            st.plotly_chart(fig, width="stretch")
        
        with g_col2:
            kappa = kappa_val if kappa_val else 0
            if kappa >= 0.80:
                st.success("**Excellent Agreement!**")
            elif kappa >= 0.60:
                st.success("**Substantial Agreement!**")
            elif kappa >= 0.40:
                st.info("**Moderate Agreement**")
            else:
                st.warning("**Low Agreement**")
        
        # Category-wise Kappa scores
        if 'category_scores' in iaa_results:
            fig = create_category_comparison(iaa_results['category_scores'], 'Kappa Score')
            st.plotly_chart(fig, width="stretch")
        
        # Confusion Matrices
        if 'confusion_matrices' in iaa_results and iaa_results['n_annotators'] == 2:
            with st.expander("Advanced Matrix"):
                available_categories = {cat: data for cat, data in iaa_results['confusion_matrices'].items() if data is not None}
                if available_categories:
                    selected_category = st.selectbox("Category", list(available_categories.keys()), key="cm_sel")
                    cm_data = available_categories[selected_category]
                    fig = create_confusion_matrix_heatmap(cm_data, selected_category)
                    st.plotly_chart(fig, width="stretch")
        st.markdown('</div>', unsafe_allow_html=True)

    with right_col:
        st.markdown('<div class="glass-card" style="padding: 1.5rem; margin-bottom: 2rem;">', unsafe_allow_html=True)
        st.markdown('<h2 class="section-header">Model Performance Results</h2>', unsafe_allow_html=True)
        st.caption("How accurate is your model based on consensus?")
        
        # Overview metrics
        a1, a2, a3, a4 = st.columns(4)
        
        overall = eval_results['overall_metrics']
        accuracy = overall['overall_accuracy']
        
        with a1:
            interpretation, _ = interpret_score(accuracy)
            st.metric(
                "Accuracy",
                f"{accuracy*100:.1f}%",
                delta=interpretation
            )
        
        with a2:
            st.metric("Correct", overall['total_correct'])
        
        with a3:
            st.metric("Errors", overall['total_incorrect'], delta_color="inverse")
        
        with a4:
            st.metric("Unclear", overall['total_uncertain'])
        
        # Accuracy gauge
        fig = create_score_gauge(accuracy, "Model Accuracy", target=0.75)
        st.plotly_chart(fig, width="stretch")
        
        # Category-wise accuracy
        accuracy_data = {cat: metrics['accuracy'] for cat, metrics in eval_results['category_results'].items()}
        fig = create_category_comparison(accuracy_data, 'ModelAccuracy')
        st.plotly_chart(fig, width="stretch")
        
        # Strengths and weaknesses
        sw1, sw2 = st.columns(2)
        with sw1:
            strong_categories = [(cat, metrics['accuracy']) for cat, metrics in eval_results['category_results'].items() if metrics['accuracy'] >= 0.75]
            if strong_categories:
                st.markdown("**Top Performers**")
                for cat, acc in sorted(strong_categories, key=lambda x: x[1], reverse=True):
                    st.success(f"**{cat.title()}** ({acc*100:.0f}%)")
        
        with sw2:
            weak_categories = [(cat, metrics['accuracy']) for cat, metrics in eval_results['category_results'].items() if metrics['accuracy'] < 0.75]
            if weak_categories:
                st.markdown("**Focus Areas**")
                for cat, acc in sorted(weak_categories, key=lambda x: x[1]):
                    st.warning(f"**{cat.title()}** ({acc*100:.0f}%)")
        st.markdown('</div>', unsafe_allow_html=True)

    # Sample size footer
    st.markdown("---")
    n_posts = eval_results['n_posts']
    if n_posts < 30:
        st.info(f"📊 **Data Size:** {n_posts} posts. (Small sample size)")
    else:
        st.success(f"📊 **Data Size:** {n_posts} posts. (Robust sample size)")

if __name__ == "__main__":
    main()