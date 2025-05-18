from __future__ import annotations
from typing import Any, Optional
from datetime import date, timedelta
import streamlit as st
import pandas as pd
import plotly.express as px

def apply_modern_styles() -> None:
    """Apply modern CSS styles to the application."""
    st.markdown("""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        /* Your existing styles */
        body {
            font-family: 'Poppins', sans-serif;
            background-color: #0e1117;
            color: #f0f0f0;
        }
        .stDateInput>div>div>input {
            color: #f0f0f0 !important;
            background-color: #1e1e1e !important;
            border-radius: 8px !important;
        }
        /* Add more styles as needed */
    </style>
    """, unsafe_allow_html=True)

def render_date_picker() -> date:
    """Render an interactive date selection component."""
    with st.container():
        st.markdown("### 📅 Select Date")
        
        # Option 1: Simple Streamlit Date Picker (recommended)
        selected_date = st.date_input(
            label="Choose a date",
            value=date.today(),
            min_value=date.today() - timedelta(days=365),
            max_value=date.today(),
            key="global_date_selector",
            label_visibility="collapsed"
        )
        
        # Option 2: Calendar Heatmap (uncomment if needed)
        """
        dates = pd.date_range(start=date.today() - timedelta(days=30), periods=30)
        data = pd.DataFrame({
            "date": dates,
            "value": [i%5 for i in range(30)]  # Sample metric values
        })
        
        fig = px.imshow(
            data.pivot_table(
                index=data['date'].dt.isocalendar().week,
                columns=data['date'].dt.weekday,
                values="value"
            ),
            labels={"x": "Weekday", "y": "Week", "color": "Activity"},
            color_continuous_scale="Blues",
            aspect="auto"
        )
        st.plotly_chart(fig, use_container_width=True)
        """
        
        return selected_date

def about_section() -> None:
    """Render the about section in sidebar."""
    with st.sidebar:
        st.header("About")
        st.markdown("""
        <div style='color: #aaa; line-height: 1.6;'>
            <p>This AI-powered resume analyzer helps job seekers optimize their resumes.</p>
            <p>Features include:</p>
            <ul style='padding-left: 1.2rem;'>
                <li>ATS compatibility scoring</li>
                <li>Skill gap analysis</li>
                <li>Personalized improvement suggestions</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

def hero_section(title, subtitle):
    st.markdown(f"""
    <div class="hero-section" style='
        background: linear-gradient(to right, rgb(63,76,107) 0%, rgb(63,76,107) 100%);
        padding: 3rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    '>
        <h1 style='
            font-size: 2.8rem;
            margin-bottom: 1.2rem;
            font-weight: 700;
            color: white;
            text-shadow: 1px 1px 3px rgba(0,0,0,0.3);
        '>{title}</h1>
        <p style='
            font-size: 1.3rem;
            font-weight: 500;
            opacity: 0.9;
            color: white;
            margin-bottom: 0;
        '>{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)

def feature_card(icon: str, title: str, description: str) -> None:
    """Render a feature card with icon, title and description."""
    st.markdown(f"""
    <div class="feature-card" style='
        background: rgba(45, 45, 45, 0.9);
        border-radius: 15px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border: 1px solid rgba(255,255,255,0.1);
    '>
        <div style='display: flex; align-items: center; margin-bottom: 1rem;'>
            <i class='fas fa-{icon}' style='font-size: 1.5rem; color: #4CAF50; margin-right: 1rem;'></i>
            <h3 style='margin: 0; color: white;'>{title}</h3>
        </div>
        <p style='color: #aaa; line-height: 1.6;'>{description}</p>
    </div>
    """, unsafe_allow_html=True)

def page_header(title: str, subtitle: str) -> None:
    """Render a page header with title and subtitle."""
    st.markdown(f"""
    <div style='margin-bottom: 2rem;'>
        <h1 style='color: white; font-size: 2rem; margin-bottom: 0.5rem;'>{title}</h1>
        <p style='color: #aaa; font-size: 1.1rem;'>{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)

def render_analytics_section(metrics: dict[str, Any]) -> None:
    """Render analytics metrics with date filtering."""
    selected_date = render_date_picker()  # Add date picker
    
    st.markdown(f"""
    <div style='margin: 1rem 0 2rem 0;'>
        <h3 style='color: white;'>Metrics for {selected_date.strftime('%B %d, %Y')}</h3>
    </div>
    """, unsafe_allow_html=True)
    
    cols = st.columns(len(metrics))
    for idx, (name, value) in enumerate(metrics.items()):
        with cols[idx]:
            st.markdown(f"""
            <div style='
                background: rgba(45, 45, 45, 0.9);
                border-radius: 10px;
                padding: 1rem;
                text-align: center;
            '>
                <p style='color: #aaa; margin-bottom: 0.5rem;'>{name}</p>
                <h3 style='color: #4CAF50; margin: 0;'>{value}</h3>
            </div>
            """, unsafe_allow_html=True)

def render_activity_section(activities: list[dict[str, str]]) -> None:
    """Render recent activities in a timeline."""
    selected_date = render_date_picker()  # Add date filtering
    
    filtered_activities = [
        act for act in activities 
        if pd.to_datetime(act['date']).date() == selected_date
    ]
    
    st.markdown("""
    <div style='
        background: rgba(45, 45, 45, 0.9);
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 2rem;
    '>
        <h3 style='color: white; margin-bottom: 1rem;'>Activities for Selected Date</h3>
    """, unsafe_allow_html=True)
    
    for activity in filtered_activities[:5]:
        st.markdown(f"""
        <div style='
            display: flex;
            align-items: flex-start;
            margin-bottom: 1rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        '>
            <div style='
                width: 12px;
                height: 12px;
                background: #4CAF50;
                border-radius: 50%;
                margin-right: 1rem;
                margin-top: 4px;
            '></div>
            <div>
                <p style='color: white; margin: 0;'>{activity['title']}</p>
                <p style='color: #aaa; margin: 0; font-size: 0.9rem;'>{activity['time']}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

def render_suggestions_section(suggestions: list[str]) -> None:
    """Render improvement suggestions in an expandable section."""
    with st.expander("📋 Improvement Suggestions", expanded=True):
        st.markdown("""
        <div style='
            background: rgba(45, 45, 45, 0.9);
            border-radius: 10px;
            padding: 1rem;
        '>
        """, unsafe_allow_html=True)
        
        for suggestion in suggestions:
            st.markdown(f"""
            <div style='
                display: flex;
                align-items: flex-start;
                margin-bottom: 0.5rem;
            '>
                <div style='
                    color: #4CAF50;
                    margin-right: 0.5rem;
                '>✓</div>
                <p style='margin: 0;'>{suggestion}</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)