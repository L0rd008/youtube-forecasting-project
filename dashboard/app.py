"""
Streamlit Dashboard for YouTube Sri Lankan Content Analysis
Interactive visualization and analysis tool for the collected YouTube data
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os
from datetime import datetime, timedelta
import json

# Add scripts directory to path
sys.path.append('../scripts')

try:
    from utils import load_from_csv
    from config import SRI_LANKAN_CHANNELS, VIDEO_CATEGORIES
except ImportError:
    st.error("Could not import required modules. Please ensure the scripts directory is accessible.")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="YouTube Sri Lankan Content Dashboard",
    page_icon="📺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #FF0000;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #FF0000;
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load the most recent processed data"""
    try:
        # Check for processed data files
        processed_dir = '../data/processed'
        if not os.path.exists(processed_dir):
            return None, "Processed data directory not found"
        
        processed_files = [f for f in os.listdir(processed_dir) 
                          if f.startswith('processed_videos_') and f.endswith('.csv')]
        
        if not processed_files:
            return None, "No processed data files found"
        
        # Load the most recent file
        latest_file = max(processed_files)
        file_path = os.path.join(processed_dir, latest_file)
        df = load_from_csv(file_path)
        
        # Convert datetime columns
        if 'published_at' in df.columns:
            df['published_at'] = pd.to_datetime(df['published_at'])
        
        return df, f"Loaded {len(df)} videos from {latest_file}"
    
    except Exception as e:
        return None, f"Error loading data: {str(e)}"

@st.cache_data
def load_snapshots():
    """Load performance snapshot data"""
    try:
        snapshots_dir = '../data/snapshots'
        if not os.path.exists(snapshots_dir):
            return None
        
        snapshot_files = [f for f in os.listdir(snapshots_dir) 
                         if f.startswith('snapshot_') and f.endswith('.csv')]
        
        if not snapshot_files:
            return None
        
        # Load all snapshots
        all_snapshots = []
        for file in snapshot_files:
            file_path = os.path.join(snapshots_dir, file)
            snapshot_df = load_from_csv(file_path)
            if not snapshot_df.empty:
                all_snapshots.append(snapshot_df)
        
        if all_snapshots:
            combined_snapshots = pd.concat(all_snapshots, ignore_index=True)
            combined_snapshots['snapshot_date'] = pd.to_datetime(combined_snapshots['snapshot_date'])
            return combined_snapshots
        
        return None
    
    except Exception as e:
        st.error(f"Error loading snapshots: {str(e)}")
        return None

def create_overview_metrics(df):
    """Create overview metrics cards"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Videos",
            value=f"{len(df):,}",
            delta=None
        )
    
    with col2:
        avg_views = df['view_count'].mean() if 'view_count' in df.columns else 0
        st.metric(
            label="Average Views",
            value=f"{avg_views:,.0f}",
            delta=None
        )
    
    with col3:
        total_views = df['view_count'].sum() if 'view_count' in df.columns else 0
        st.metric(
            label="Total Views",
            value=f"{total_views:,.0f}",
            delta=None
        )
    
    with col4:
        if 'engagement_ratio' in df.columns:
            avg_engagement = df['engagement_ratio'].mean()
            st.metric(
                label="Avg Engagement Ratio",
                value=f"{avg_engagement:.4f}",
                delta=None
            )
        else:
            st.metric(
                label="Features",
                value=f"{len(df.columns)}",
                delta=None
            )

def create_category_analysis(df):
    """Create category analysis visualizations"""
    st.subheader("📊 Channel Category Analysis")
    
    if 'channel_category' not in df.columns:
        st.warning("Channel category data not available")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Category distribution
        category_counts = df['channel_category'].value_counts()
        fig_pie = px.pie(
            values=category_counts.values,
            names=category_counts.index,
            title="Distribution of Videos by Category"
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # Performance by category
        if 'view_count' in df.columns:
            avg_views_by_category = df.groupby('channel_category')['view_count'].mean().sort_values(ascending=True)
            fig_bar = px.bar(
                x=avg_views_by_category.values,
                y=avg_views_by_category.index,
                orientation='h',
                title="Average Views by Category",
                labels={'x': 'Average Views', 'y': 'Category'}
            )
            st.plotly_chart(fig_bar, use_container_width=True)

def create_temporal_analysis(df):
    """Create temporal analysis visualizations"""
    st.subheader("⏰ Temporal Analysis")
    
    if 'published_at' not in df.columns:
        st.warning("Publication date data not available")
        return
    
    # Extract time features
    df['hour'] = df['published_at'].dt.hour
    df['day_of_week'] = df['published_at'].dt.day_name()
    df['month'] = df['published_at'].dt.month_name()
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Publishing by hour
        hourly_counts = df['hour'].value_counts().sort_index()
        fig_hour = px.bar(
            x=hourly_counts.index,
            y=hourly_counts.values,
            title="Videos Published by Hour of Day",
            labels={'x': 'Hour', 'y': 'Number of Videos'}
        )
        st.plotly_chart(fig_hour, use_container_width=True)
    
    with col2:
        # Publishing by day of week
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        daily_counts = df['day_of_week'].value_counts().reindex(day_order)
        fig_day = px.bar(
            x=day_order,
            y=daily_counts.values,
            title="Videos Published by Day of Week",
            labels={'x': 'Day', 'y': 'Number of Videos'}
        )
        st.plotly_chart(fig_day, use_container_width=True)
    
    # Performance by time
    if 'view_count' in df.columns:
        col3, col4 = st.columns(2)
        
        with col3:
            hourly_views = df.groupby('hour')['view_count'].mean()
            fig_hour_perf = px.line(
                x=hourly_views.index,
                y=hourly_views.values,
                title="Average Views by Publishing Hour",
                labels={'x': 'Hour', 'y': 'Average Views'},
                markers=True
            )
            st.plotly_chart(fig_hour_perf, use_container_width=True)
        
        with col4:
            daily_views = df.groupby('day_of_week')['view_count'].mean().reindex(day_order)
            fig_day_perf = px.bar(
                x=day_order,
                y=daily_views.values,
                title="Average Views by Day of Week",
                labels={'x': 'Day', 'y': 'Average Views'}
            )
            st.plotly_chart(fig_day_perf, use_container_width=True)

def create_engagement_analysis(df):
    """Create engagement analysis visualizations"""
    st.subheader("💬 Engagement Analysis")
    
    required_cols = ['view_count', 'like_count', 'comment_count']
    if not all(col in df.columns for col in required_cols):
        st.warning("Engagement data not available")
        return
    
    # Calculate engagement metrics if not present
    if 'engagement_ratio' not in df.columns:
        df['engagement_ratio'] = (df['like_count'] + df['comment_count']) / (df['view_count'] + 1)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Views vs Likes scatter
        fig_scatter = px.scatter(
            df,
            x='view_count',
            y='like_count',
            title="Likes vs Views",
            labels={'view_count': 'Views', 'like_count': 'Likes'},
            log_x=True,
            log_y=True,
            hover_data=['title'] if 'title' in df.columns else None
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    with col2:
        # Engagement ratio distribution
        fig_hist = px.histogram(
            df,
            x='engagement_ratio',
            title="Distribution of Engagement Ratios",
            labels={'engagement_ratio': 'Engagement Ratio', 'count': 'Frequency'},
            nbins=30
        )
        st.plotly_chart(fig_hist, use_container_width=True)
    
    # Top performing videos
    st.subheader("🏆 Top Performing Videos")
    if 'title' in df.columns:
        top_videos = df.nlargest(10, 'view_count')[['title', 'channel_title', 'view_count', 'like_count', 'comment_count']]
        st.dataframe(top_videos, use_container_width=True)

def create_content_analysis(df):
    """Create content analysis visualizations"""
    st.subheader("📝 Content Analysis")
    
    if 'title' not in df.columns:
        st.warning("Title data not available")
        return
    
    # Calculate title length if not present
    if 'title_length' not in df.columns:
        df['title_length'] = df['title'].str.len()
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Title length distribution
        fig_title_dist = px.histogram(
            df,
            x='title_length',
            title="Distribution of Title Lengths",
            labels={'title_length': 'Title Length (characters)', 'count': 'Frequency'},
            nbins=30
        )
        st.plotly_chart(fig_title_dist, use_container_width=True)
    
    with col2:
        # Title length vs views
        if 'view_count' in df.columns:
            fig_title_views = px.scatter(
                df,
                x='title_length',
                y='view_count',
                title="Title Length vs Views",
                labels={'title_length': 'Title Length', 'view_count': 'Views'},
                log_y=True
            )
            st.plotly_chart(fig_title_views, use_container_width=True)
    
    # Duration analysis
    if 'duration_seconds' in df.columns:
        col3, col4 = st.columns(2)
        
        with col3:
            df['duration_minutes'] = df['duration_seconds'] / 60
            fig_duration = px.histogram(
                df,
                x='duration_minutes',
                title="Distribution of Video Durations",
                labels={'duration_minutes': 'Duration (minutes)', 'count': 'Frequency'},
                nbins=30
            )
            st.plotly_chart(fig_duration, use_container_width=True)
        
        with col4:
            if 'view_count' in df.columns:
                fig_duration_views = px.scatter(
                    df,
                    x='duration_minutes',
                    y='view_count',
                    title="Duration vs Views",
                    labels={'duration_minutes': 'Duration (minutes)', 'view_count': 'Views'},
                    log_y=True
                )
                st.plotly_chart(fig_duration_views, use_container_width=True)

def create_performance_tracking(snapshots_df):
    """Create performance tracking visualizations"""
    st.subheader("📈 Performance Tracking")
    
    if snapshots_df is None or snapshots_df.empty:
        st.warning("No performance tracking data available")
        return
    
    # Select a video for tracking
    video_options = snapshots_df['video_id'].unique()[:20]  # Limit to first 20 for performance
    selected_video = st.selectbox("Select a video to track:", video_options)
    
    if selected_video:
        video_data = snapshots_df[snapshots_df['video_id'] == selected_video].sort_values('snapshot_date')
        
        if len(video_data) > 1:
            col1, col2 = st.columns(2)
            
            with col1:
                # Views over time
                fig_views = px.line(
                    video_data,
                    x='snapshot_date',
                    y='view_count',
                    title=f"Views Over Time",
                    labels={'snapshot_date': 'Date', 'view_count': 'Views'}
                )
                st.plotly_chart(fig_views, use_container_width=True)
            
            with col2:
                # Engagement over time
                fig_engagement = px.line(
                    video_data,
                    x='snapshot_date',
                    y='engagement_ratio',
                    title=f"Engagement Ratio Over Time",
                    labels={'snapshot_date': 'Date', 'engagement_ratio': 'Engagement Ratio'}
                )
                st.plotly_chart(fig_engagement, use_container_width=True)
        else:
            st.info("Not enough tracking data for this video")

def create_predictive_insights(df):
    """Create predictive insights and correlations"""
    st.subheader("🔮 Predictive Insights")
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    
    if len(numeric_cols) < 3:
        st.warning("Not enough numeric features for correlation analysis")
        return
    
    # Key features for correlation
    key_features = ['view_count', 'like_count', 'comment_count', 'duration_seconds']
    if 'engagement_ratio' in df.columns:
        key_features.append('engagement_ratio')
    if 'title_length' in df.columns:
        key_features.append('title_length')
    
    available_features = [f for f in key_features if f in df.columns]
    
    if len(available_features) > 2:
        col1, col2 = st.columns(2)
        
        with col1:
            # Correlation heatmap
            correlation_matrix = df[available_features].corr()
            fig_corr = px.imshow(
                correlation_matrix,
                title="Feature Correlation Matrix",
                color_continuous_scale="RdBu",
                aspect="auto"
            )
            st.plotly_chart(fig_corr, use_container_width=True)
        
        with col2:
            # Feature importance for views
            if 'view_count' in available_features:
                view_correlations = correlation_matrix['view_count'].abs().sort_values(ascending=True)
                view_correlations = view_correlations[view_correlations.index != 'view_count']
                
                fig_importance = px.bar(
                    x=view_correlations.values,
                    y=view_correlations.index,
                    orientation='h',
                    title="Feature Correlation with Views",
                    labels={'x': 'Absolute Correlation', 'y': 'Feature'}
                )
                st.plotly_chart(fig_importance, use_container_width=True)
    
    # Viewership prediction insights
    if 'viewership_category' in df.columns:
        st.subheader("📊 Viewership Categories")
        viewership_dist = df['viewership_category'].value_counts()
        
        col3, col4 = st.columns(2)
        
        with col3:
            fig_viewership = px.pie(
                values=viewership_dist.values,
                names=viewership_dist.index,
                title="Distribution of Viewership Categories"
            )
            st.plotly_chart(fig_viewership, use_container_width=True)
        
        with col4:
            # Category performance by channel category
            if 'channel_category' in df.columns:
                category_performance = pd.crosstab(df['channel_category'], df['viewership_category'])
                fig_cross = px.imshow(
                    category_performance,
                    title="Viewership by Channel Category",
                    labels={'x': 'Viewership Category', 'y': 'Channel Category'},
                    aspect="auto"
                )
                st.plotly_chart(fig_cross, use_container_width=True)

def main():
    """Main application function"""
    # Header
    st.markdown('<h1 class="main-header">📺 YouTube Sri Lankan Content Dashboard</h1>', unsafe_allow_html=True)
    
    # Load data
    df, load_message = load_data()
    snapshots_df = load_snapshots()
    
    # Sidebar
    st.sidebar.title("🎛️ Dashboard Controls")
    st.sidebar.info(load_message)
    
    if df is None:
        st.error("No data available. Please run the data collection scripts first.")
        st.markdown("""
        ### Getting Started
        1. Set up your YouTube API key in `.env` file
        2. Run `python scripts/collect_videos.py` to collect video data
        3. Run `python scripts/process_data.py` to process the data
        4. Refresh this dashboard
        """)
        return
    
    # Sidebar filters
    st.sidebar.subheader("🔍 Filters")
    
    # Date range filter
    if 'published_at' in df.columns:
        min_date = df['published_at'].min().date()
        max_date = df['published_at'].max().date()
        
        date_range = st.sidebar.date_input(
            "Select date range:",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
        
        if len(date_range) == 2:
            start_date, end_date = date_range
            df = df[(df['published_at'].dt.date >= start_date) & 
                   (df['published_at'].dt.date <= end_date)]
    
    # Category filter
    if 'channel_category' in df.columns:
        categories = ['All'] + list(df['channel_category'].unique())
        selected_category = st.sidebar.selectbox("Select category:", categories)
        
        if selected_category != 'All':
            df = df[df['channel_category'] == selected_category]
    
    # View count filter
    if 'view_count' in df.columns:
        min_views = int(df['view_count'].min())
        max_views = int(df['view_count'].max())
        
        view_range = st.sidebar.slider(
            "View count range:",
            min_value=min_views,
            max_value=max_views,
            value=(min_views, max_views)
        )
        
        df = df[(df['view_count'] >= view_range[0]) & 
               (df['view_count'] <= view_range[1])]
    
    # Display filtered data info
    st.sidebar.markdown(f"**Filtered dataset:** {len(df)} videos")
    
    # Main dashboard tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Overview", 
        "📈 Categories", 
        "⏰ Temporal", 
        "💬 Engagement", 
        "📝 Content", 
        "🔮 Insights"
    ])
    
    with tab1:
        st.header("📊 Dataset Overview")
        create_overview_metrics(df)
        
        # Data quality metrics
        st.subheader("📋 Data Quality")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            missing_data = df.isnull().sum().sum()
            st.metric("Missing Values", missing_data)
        
        with col2:
            duplicate_videos = df.duplicated(subset=['video_id']).sum() if 'video_id' in df.columns else 0
            st.metric("Duplicate Videos", duplicate_videos)
        
        with col3:
            date_range_days = (df['published_at'].max() - df['published_at'].min()).days if 'published_at' in df.columns else 0
            st.metric("Date Range (days)", date_range_days)
        
        # Recent activity
        if 'published_at' in df.columns:
            st.subheader("📅 Recent Activity")
            recent_videos = df.nlargest(5, 'published_at')[['title', 'channel_title', 'published_at', 'view_count']]
            st.dataframe(recent_videos, use_container_width=True)
    
    with tab2:
        create_category_analysis(df)
    
    with tab3:
        create_temporal_analysis(df)
    
    with tab4:
        create_engagement_analysis(df)
        
        # Performance tracking
        if snapshots_df is not None:
            create_performance_tracking(snapshots_df)
    
    with tab5:
        create_content_analysis(df)
    
    with tab6:
        create_predictive_insights(df)
        
        # Data export
        st.subheader("💾 Data Export")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Download Filtered Data"):
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"youtube_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
        
        with col2:
            if st.button("Generate Report"):
                st.info("Report generation feature coming soon!")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>YouTube Sri Lankan Content Analysis Dashboard</p>
        <p>Built with Streamlit • Data from YouTube Data API v3</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
