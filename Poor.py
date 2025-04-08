# YouTube Viral Topics Analyzer - Professional Edition

import streamlit as st
import requests
from datetime import datetime, timedelta
import pandas as pd
import os
import json
import plotly.express as px
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import base64

# Page configuration
st.set_page_config(
    page_title="YouTube Viral Topics Analyzer",
    page_icon="🎬",
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
        margin-bottom: 1rem;
        font-weight: bold;
    }
    .card {
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 15px;
        background-color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .card-title {
        font-size: 1.2rem;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .pagination-button {
        background-color: #f0f0f0;
        border: 1px solid #ddd;
        border-radius: 4px;
        padding: 5px 10px;
        margin: 5px;
        cursor: pointer;
    }
    .pagination-button:hover {
        background-color: #e0e0e0;
    }
    .pagination-active {
        background-color: #FF0000;
        color: white;
    }
    .stButton button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# Constants
YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEO_URL = "https://www.googleapis.com/youtube/v3/videos"
YOUTUBE_CHANNEL_URL = "https://www.googleapis.com/youtube/v3/channels"

# Session state initialization
if 'results' not in st.session_state:
    st.session_state.results = []
if 'filtered_results' not in st.session_state:
    st.session_state.filtered_results = []
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""
if 'search_complete' not in st.session_state:
    st.session_state.search_complete = False
if 'last_search_params' not in st.session_state:
    st.session_state.last_search_params = {}
if 'page' not in st.session_state:
    st.session_state.page = 1
if 'items_per_page' not in st.session_state:
    st.session_state.items_per_page = 10
if 'saved_searches' not in st.session_state:
    st.session_state.saved_searches = []
if 'date_filter' not in st.session_state:
    st.session_state.date_filter = "all"
if 'show_analytics' not in st.session_state:
    st.session_state.show_analytics = False

# Functions
def save_results(filename, data):
    """Save results to a JSON file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if not os.path.exists("saved_searches"):
        os.makedirs("saved_searches")
    
    filename = f"saved_searches/{filename}_{timestamp}.json"
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)
    
    st.session_state.saved_searches.append({
        "filename": filename,
        "timestamp": timestamp,
        "count": len(data.get("results", [])),
        "keywords": st.session_state.last_search_params.get("keywords", [])
    })
    
    return filename

def load_results(filename):
    """Load results from a JSON file"""
    with open(filename, "r") as f:
        data = json.load(f)
    return data

def download_link(df, filename, text):
    """Generate a download link for a dataframe"""
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'
    return href

def next_page():
    """Go to next page"""
    max_page = (len(st.session_state.filtered_results) - 1) // st.session_state.items_per_page + 1
    if st.session_state.page < max_page:
        st.session_state.page += 1

def previous_page():
    """Go to previous page"""
    if st.session_state.page > 1:
        st.session_state.page -= 1

def toggle_analytics():
    """Toggle analytics view"""
    st.session_state.show_analytics = not st.session_state.show_analytics

def fetch_youtube_data(api_key, keywords, days, max_results_per_keyword, min_views, max_subscriber_count, order_by):
    """Fetch data from YouTube API"""
    all_results = []
    
    # Calculate date range
    start_date = (datetime.utcnow() - timedelta(days=int(days))).isoformat("T") + "Z"
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, keyword in enumerate(keywords):
        progress = (i) / len(keywords)
        progress_bar.progress(progress)
        status_text.text(f"Searching for keyword: {keyword} ({i+1}/{len(keywords)})")
        
        # Define search parameters
        search_params = {
            "part": "snippet",
            "q": keyword,
            "type": "video",
            "order": order_by,
            "publishedAfter": start_date,
            "maxResults": max_results_per_keyword,
            "key": api_key,
        }
        
        try:
            # Fetch video data
            response = requests.get(YOUTUBE_SEARCH_URL, params=search_params)
            data = response.json()
            
            # Handle API errors
            if "error" in data:
                st.sidebar.error(f"API Error: {data['error']['message']}")
                continue
                
            # Check if "items" key exists
            if "items" not in data or not data["items"]:
                st.sidebar.info(f"No videos found for keyword: {keyword}")
                continue
            
            videos = data["items"]
            video_ids = [video["id"]["videoId"] for video in videos if "id" in video and "videoId" in video["id"]]
            if not video_ids:
                continue
                
            channel_ids = [video["snippet"]["channelId"] for video in videos if "snippet" in video and "channelId" in video["snippet"]]
            if not channel_ids:
                continue
            
            # Fetch video statistics
            stats_params = {"part": "statistics,contentDetails", "id": ",".join(video_ids), "key": api_key}
            stats_response = requests.get(YOUTUBE_VIDEO_URL, params=stats_params)
            stats_data = stats_response.json()
            
            if "items" not in stats_data:
                continue
                
            # Fetch channel statistics
            channel_params = {"part": "statistics,snippet", "id": ",".join(channel_ids), "key": api_key}
            channel_response = requests.get(YOUTUBE_CHANNEL_URL, params=channel_params)
            channel_data = channel_response.json()
            
            if "items" not in channel_data:
                continue
                
            # Map video stats and channel data for easier access
            stats_map = {item["id"]: item for item in stats_data["items"]}
            channel_map = {item["id"]: item for item in channel_data["items"]}
            
            # Process each video
            for video in videos:
                video_id = video["id"]["videoId"]
                channel_id = video["snippet"]["channelId"]
                
                # Skip if we don't have stats or channel info
                if video_id not in stats_map or channel_id not in channel_map:
                    continue
                    
                # Get statistics
                video_stats = stats_map[video_id]["statistics"]
                channel_stats = channel_map[channel_id]["statistics"]
                
                # Get view count and subscriber count
                view_count = int(video_stats.get("viewCount", 0))
                subscriber_count = int(channel_stats.get("subscriberCount", 0))
                
                # Apply filters
                if view_count < min_views or subscriber_count > max_subscriber_count:
                    continue
                    
                # Parse and format dates
                published_at = video["snippet"]["publishedAt"]
                published_date = datetime.strptime(published_at, "%Y-%m-%dT%H:%M:%SZ")
                
                # Parse duration
                duration = stats_map[video_id]["contentDetails"]["duration"]
                
                # Format duration from ISO 8601
                duration_str = duration.replace("PT", "")
                hours = 0
                minutes = 0
                seconds = 0
                
                if "H" in duration_str:
                    hours = int(duration_str.split("H")[0])
                    duration_str = duration_str.split("H")[1]
                
                if "M" in duration_str:
                    minutes = int(duration_str.split("M")[0])
                    duration_str = duration_str.split("M")[1]
                    
                if "S" in duration_str:
                    seconds = int(duration_str.split("S")[0])
                
                formatted_duration = f"{hours:02d}:{minutes:02d}:{seconds:02d}" if hours > 0 else f"{minutes:02d}:{seconds:02d}"
                
                # Channel info
                channel_title = channel_map[channel_id]["snippet"]["title"]
                
                # Likes, comments, etc
                like_count = int(video_stats.get("likeCount", 0))
                comment_count = int(video_stats.get("commentCount", 0))
                
                # Save the result
                all_results.append({
                    "Title": video["snippet"]["title"],
                    "Description": video["snippet"]["description"][:200] + "..." if len(video["snippet"]["description"]) > 200 else video["snippet"]["description"],
                    "Full Description": video["snippet"]["description"],
                    "Video ID": video_id,
                    "URL": f"https://www.youtube.com/watch?v={video_id}",
                    "Thumbnail": video["snippet"]["thumbnails"]["high"]["url"],
                    "Channel Name": channel_title,
                    "Channel ID": channel_id,
                    "Channel URL": f"https://www.youtube.com/channel/{channel_id}",
                    "Published Date": published_date.strftime("%Y-%m-%d %H:%M:%S"),
                    "Duration": formatted_duration,
                    "Views": view_count,
                    "Likes": like_count,
                    "Comments": comment_count,
                    "Subscribers": subscriber_count,
                    "Engagement Rate": round((like_count + comment_count) / view_count * 100, 2) if view_count > 0 else 0,
                    "Keyword": keyword,
                    "Raw Published Date": published_date  # Keep the actual datetime for sorting
                })
                
        except Exception as e:
            st.sidebar.error(f"Error processing keyword '{keyword}': {str(e)}")
    
    # Update progress to 100%
    progress_bar.progress(1.0)
    status_text.text("Search completed!")
    
    # Remove duplicates based on Video ID
    unique_results = []
    seen_video_ids = set()
    
    for result in all_results:
        if result["Video ID"] not in seen_video_ids:
            seen_video_ids.add(result["Video ID"])
            unique_results.append(result)
    
    return unique_results

def apply_filters(results, filters):
    """Apply filters to the results"""
    filtered = results.copy()
    
    # Min views filter
    if filters.get("min_views", 0) > 0:
        filtered = [r for r in filtered if r["Views"] >= filters["min_views"]]
    
    # Max views filter
    if filters.get("max_views", 0) > 0:
        filtered = [r for r in filtered if r["Views"] <= filters["max_views"]]
    
    # Min subscribers filter
    if filters.get("min_subscribers", 0) > 0:
        filtered = [r for r in filtered if r["Subscribers"] >= filters["min_subscribers"]]
    
    # Max subscribers filter
    if filters.get("max_subscribers", 0) > 0:
        filtered = [r for r in filtered if r["Subscribers"] <= filters["max_subscribers"]]
    
    # Min engagement rate filter
    if filters.get("min_engagement", 0) > 0:
        filtered = [r for r in filtered if r["Engagement Rate"] >= filters["min_engagement"]]
    
    # Keyword filter - FIX HERE: Check if keyword exists and is not empty first
    if filters.get("keyword") and filters.get("keyword").strip() != "":
        keyword = filters.get("keyword", "").lower()  # Using get() to avoid errors
        filtered = [r for r in filtered if (
            keyword in r["Title"].lower() or 
            keyword in r["Description"].lower() or 
            keyword in r["Keyword"].lower() or
            keyword in r["Channel Name"].lower()
        )]
    
    # Date filter
    if filters.get("date_range") == "today":
        today = datetime.now().date()
        filtered = [r for r in filtered if r["Raw Published Date"].date() == today]
    elif filters.get("date_range") == "yesterday":
        yesterday = (datetime.now() - timedelta(days=1)).date()
        filtered = [r for r in filtered if r["Raw Published Date"].date() == yesterday]
    elif filters.get("date_range") == "last_week":
        week_ago = (datetime.now() - timedelta(days=7)).date()
        filtered = [r for r in filtered if r["Raw Published Date"].date() >= week_ago]
    elif filters.get("date_range") == "last_month":
        month_ago = (datetime.now() - timedelta(days=30)).date()
        filtered = [r for r in filtered if r["Raw Published Date"].date() >= month_ago]
    
    # Custom date range
    if filters.get("custom_start_date") and filters.get("custom_end_date"):
        start = filters["custom_start_date"]
        end = filters["custom_end_date"]
        filtered = [r for r in filtered if start <= r["Raw Published Date"].date() <= end]
    
    return filtered

def generate_charts(results):
    """Generate analytics charts from results"""
    if not results:
        return None, None, None, None
    
    # Convert to DataFrame for easier analysis
    df = pd.DataFrame(results)
    
    # 1. Views distribution by keywords
    keyword_views = df.groupby("Keyword")["Views"].sum().reset_index()
    keyword_views = keyword_views.sort_values("Views", ascending=False)
    
    views_by_keyword = px.bar(
        keyword_views, 
        x="Keyword", 
        y="Views", 
        title="Total Views by Keyword",
        color="Views",
        color_continuous_scale="reds"
    )
    views_by_keyword.update_layout(xaxis_title="Keyword", yaxis_title="Total Views")
    
    # 2. Subscriber distribution
    subscriber_bins = [0, 1000, 5000, 10000, 50000, 100000, float('inf')]
    subscriber_labels = ["0-1K", "1K-5K", "5K-10K", "10K-50K", "50K-100K", "100K+"]
    
    df["Subscriber Range"] = pd.cut(df["Subscribers"], bins=subscriber_bins, labels=subscriber_labels)
    subscriber_counts = df["Subscriber Range"].value_counts().reset_index()
    subscriber_counts.columns = ["Subscriber Range", "Count"]
    
    subscriber_chart = px.pie(
        subscriber_counts, 
        values="Count", 
        names="Subscriber Range", 
        title="Videos by Channel Size",
        color_discrete_sequence=px.colors.sequential.Reds
    )
    
    # 3. Publication time analysis
    df["Publication Hour"] = df["Raw Published Date"].apply(lambda x: x.hour)
    hourly_distribution = df.groupby("Publication Hour").size().reset_index()
    hourly_distribution.columns = ["Hour", "Count"]
    
    publication_time_chart = px.line(
        hourly_distribution, 
        x="Hour", 
        y="Count", 
        title="Publication Time Distribution (24-hour)",
        markers=True
    )
    publication_time_chart.update_layout(xaxis_title="Hour of Day", yaxis_title="Number of Videos")
    
    # 4. Engagement rate vs Views
    engagement_chart = px.scatter(
        df,
        x="Views",
        y="Engagement Rate",
        color="Subscribers",
        size="Comments",
        hover_name="Title",
        color_continuous_scale="reds",
        title="Engagement Rate vs. Views"
    )
    engagement_chart.update_layout(xaxis_title="Views", yaxis_title="Engagement Rate (%)")
    
    return views_by_keyword, subscriber_chart, publication_time_chart, engagement_chart

# Sidebar
with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>Settings</h2>", unsafe_allow_html=True)
    
    # API Key input
    api_key = st.text_input("YouTube API Key:", type="password", value=st.session_state.api_key)
    st.session_state.api_key = api_key
    
    # Tabs for different sidebar sections
    sidebar_tab1, sidebar_tab2, sidebar_tab3 = st.tabs(["Search Parameters", "Filters", "Saved Searches"])
    
    # Tab 1: Search Parameters
    with sidebar_tab1:
        st.subheader("Search Parameters")
        
        # Date range selection
        days = st.slider("Days to Search:", min_value=1, max_value=30, value=7)
        
        # Results per keyword - INCREASED MAXIMUM TO 500 as requested
        max_results_per_keyword = st.slider("Max Results per Keyword:", min_value=5, max_value=500, value=50)
        
        # Order by options
        order_by_options = {
            "viewCount": "View Count (High to Low)",
            "relevance": "Relevance",
            "date": "Date (Newest First)",
            "rating": "Rating"
        }
        order_by = st.selectbox("Order Results By:", options=list(order_by_options.keys()), 
                                format_func=lambda x: order_by_options[x])
        
        # Initial filters
        min_views = st.number_input("Minimum Views:", min_value=0, value=1000)
        max_subscriber_count = st.number_input("Maximum Subscriber Count:", min_value=0, value=10000)
        
        # Keywords input
        st.subheader("Keywords")
        default_keywords = """Affair Relationship Stories
Reddit Update
Reddit Relationship Advice
Reddit Relationship
Reddit Cheating
AITA Update
Open Marriage
Open Relationship"""
        
        keywords_text = st.text_area("Enter keywords (one per line):", value=default_keywords, height=200)
        keywords = [k.strip() for k in keywords_text.splitlines() if k.strip()]
        
        st.info(f"Total keywords: {len(keywords)}")
        
        # Search button
        if st.button("Start Search", use_container_width=True):
            if not api_key:
                st.error("Please enter your YouTube API Key")
            elif not keywords:
                st.error("Please enter at least one keyword")
            else:
                with st.spinner("Searching YouTube..."):
                    # Store search parameters
                    st.session_state.last_search_params = {
                        "days": days,
                        "min_views": min_views,
                        "max_subscriber_count": max_subscriber_count,
                        "keywords": keywords,
                        "order_by": order_by,
                        "max_results_per_keyword": max_results_per_keyword
                    }
                    
                    # Fetch data
                    results = fetch_youtube_data(
                        api_key=api_key,
                        keywords=keywords,
                        days=days,
                        max_results_per_keyword=max_results_per_keyword,
                        min_views=min_views,
                        max_subscriber_count=max_subscriber_count,
                        order_by=order_by
                    )
                    
                    # Store results in session state
                    st.session_state.results = results
                    st.session_state.filtered_results = results
                    st.session_state.search_complete = True
                    st.session_state.page = 1
    
    # Tab 2: Filters
    with sidebar_tab2:
        st.subheader("Filter Results")
        
        # Only show filters if we have results
        if st.session_state.search_complete and len(st.session_state.results) > 0:
            # View count range
            st.write("View Count Range")
            min_views_filter = st.number_input("Min Views:", min_value=0, value=0)
            max_views_filter = st.number_input("Max Views:", min_value=0, value=0)
            
            # Subscriber range
            st.write("Subscriber Range")
            min_subs_filter = st.number_input("Min Subscribers:", min_value=0, value=0)
            max_subs_filter = st.number_input("Max Subscribers:", min_value=0, value=0)
            
            # Engagement rate
            min_engagement = st.number_input("Min Engagement Rate (%):", min_value=0.0, value=0.0, step=0.1)
            
            # Date filter
            date_range = st.select_slider(
                "Date Range:",
                options=["all", "last_month", "last_week", "yesterday", "today", "custom"],
                value="all"
            )
            
            custom_start_date = None
            custom_end_date = None
            if date_range == "custom":
                col1, col2 = st.columns(2)
                with col1:
                    custom_start_date = st.date_input("Start Date:", value=datetime.now() - timedelta(days=7))
                with col2:
                    custom_end_date = st.date_input("End Date:", value=datetime.now())
            
            # Keyword text search
            keyword_filter = st.text_input("Search in results:", "")
            
            # Apply filters button
            if st.button("Apply Filters", use_container_width=True):
                filters = {
                    "min_views": min_views_filter,
                    "max_views": max_views_filter,
                    "min_subscribers": min_subs_filter,
                    "max_subscribers": max_subs_filter,
                    "min_engagement": min_engagement,
                    "keyword": keyword_filter,  # This will be checked properly in apply_filters
                    "date_range": date_range,
                    "custom_start_date": custom_start_date,
                    "custom_end_date": custom_end_date
                }
                
                # Apply filters
                st.session_state.filtered_results = apply_filters(st.session_state.results, filters)
                st.session_state.page = 1  # Reset to first page
                
            # Reset filters button
            if st.button("Reset Filters", use_container_width=True):
                st.session_state.filtered_results = st.session_state.results
            
            st.info(f"Showing {len(st.session_state.filtered_results)} of {len(st.session_state.results)} total results")
        else:
            st.info("Run a search to enable filtering")
    
    # Tab 3: Saved Searches
    with sidebar_tab3:
        st.subheader("Saved Searches")
        
        if st.session_state.search_complete and len(st.session_state.results) > 0:
            save_name = st.text_input("Save search as:", "viral_topics")
            
            if st.button("Save Current Results", use_container_width=True):
                with st.spinner("Saving results..."):
                    saved_file = save_results(save_name, {
                        "results": st.session_state.results,
                        "search_params": st.session_state.last_search_params,
                        "timestamp": datetime.now().isoformat()
                    })
                    st.success(f"Saved {len(st.session_state.results)} results to {saved_file}")
        
        # Display saved searches
        if st.session_state.saved_searches:
            st.write("Previous searches:")
            
            for i, saved in enumerate(st.session_state.saved_searches):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"{i+1}. {saved['filename']} ({saved['count']} results)")
                with col2:
                    if st.button(f"Load #{i+1}", key=f"load_{i}"):
                        with st.spinner("Loading saved search..."):
                            loaded_data = load_results(saved["filename"])
                            st.session_state.results = loaded_data["results"]
                            st.session_state.filtered_results = loaded_data["results"]
                            st.session_state.search_complete = True
                            st.session_state.last_search_params = loaded_data["search_params"]
                            st.session_state.page = 1
                            st.success(f"Loaded {len(loaded_data['results'])} results")
        else:
            st.info("No saved searches yet")

# Main content
st.markdown("<h1 class='main-header'>YouTube Viral Topics Analyzer</h1>", unsafe_allow_html=True)

# Check if search has been performed
if st.session_state.search_complete:
    # Action buttons row
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📈 Toggle Analytics", key="toggle_analytics", use_container_width=True):
            toggle_analytics()
    
    with col2:
        if st.button("🔄 Card View", key="card_view", use_container_width=True):
            st.session_state.show_analytics = False
    
    with col3:
        # Export button - Fixed this to work properly
        if len(st.session_state.filtered_results) > 0:
            df_export = pd.DataFrame(st.session_state.filtered_results)
            # Drop the Raw Published Date column which is not useful for export
            if "Raw Published Date" in df_export.columns:
                df_export = df_export.drop(columns=["Raw Published Date"])
            
            csv = df_export.to_csv(index=False)
            b64 = base64.b64encode(csv.encode()).decode()
            export_filename = f"youtube_results_{datetime.now().strftime('%Y%m%d')}.csv"
            href = f'<a href="data:file/csv;base64,{b64}" download="{export_filename}">📥 Export to CSV</a>'
            st.markdown(href, unsafe_allow_html=True)
    
    # Analytics tab
    if st.session_state.show_analytics:
        st.header("Analytics Dashboard")
        
        if len(st.session_state.filtered_results) > 0:
            views_chart, subscribers_chart, publication_chart, engagement_chart = generate_charts(st.session_state.filtered_results)
            
            # Display charts in a 2x2 grid
            chart_col1, chart_col2 = st.columns(2)
            
            with chart_col1:
                st.plotly_chart(views_chart, use_container_width=True)
                st.plotly_chart(publication_chart, use_container_width=True)
                
            with chart_col2:
                st.plotly_chart(subscribers_chart, use_container_width=True)
                st.plotly_chart(engagement_chart, use_container_width=True)
                
            # Summary statistics
            st.header("Summary Statistics")
            
            # Create a DataFrame for easier analysis
            df = pd.DataFrame(st.session_state.filtered_results)
            
            stats_col1, stats_col2, stats_col3 = st.columns(3)
            
            with stats_col1:
                st.metric("Total Videos", len(df))
                st.metric("Average Views", f"{int(df['Views'].mean()):,}")
                
            with stats_col2:
                st.metric("Total Views", f"{int(df['Views'].sum()):,}")
                st.metric("Average Engagement Rate", f"{df['Engagement Rate'].mean():.2f}%")
                
            with stats_col3:
                st.metric("Most Popular Channel", df.loc[df['Views'].idxmax()]["Channel Name"])
                st.metric("Total Engagement", f"{int(df['Likes'].sum() + df['Comments'].sum()):,}")
        else:
            st.info("No data available for analytics. Please run a search first.")
    
    # Results display
    else:
        st.header(f"Search Results ({len(st.session_state.filtered_results)} videos found)")
        
        if len(st.session_state.filtered_results) > 0:
            # Pagination controls
            total_pages = (len(st.session_state.filtered_results) - 1) // st.session_state.items_per_page + 1
            
            # Display in card format
            start_idx = (st.session_state.page - 1) * st.session_state.items_per_page
            end_idx = min(start_idx + st.session_state.items_per_page, len(st.session_state.filtered_results))
            
            for idx in range(start_idx, end_idx):
                video = st.session_state.filtered_results[idx]
                
                # Create a card for each video
                st.markdown(f"""
                <div class="card">
                    <div style="display: flex; align-items: flex-start;">
                        <div style="flex: 0 0 200px; margin-right: 15px;">
                            <a href="{video['URL']}" target="_blank">
                                <img src="{video['Thumbnail']}" width="200" style="border-radius: 4px;">
                            </a>
                        </div>
                        <div style="flex: 1;">
                            <div class="card-title">{video['Title']}</div>
                            <p><strong>Channel:</strong> {video['Channel Name']}</p>
                            <p><strong>Published:</strong> {video['Published Date']}</p>
                            <p><strong>Duration:</strong> {video['Duration']}</p>
                            <p><strong>Views:</strong> {video['Views']:,} | <strong>Likes:</strong> {video['Likes']:,} | <strong>Comments:</strong> {video['Comments']:,}</p>
                            <p><strong>Engagement Rate:</strong> {video['Engagement Rate']}%</p>
                            <p><strong>Subscribers:</strong> {video['Subscribers']:,}</p>
                            <p><strong>Keyword:</strong> {video['Keyword']}</p>
                            <p>{video['Description']}</p>
                            <p><a href="{video['URL']}" target="_blank">Watch on YouTube</a> | <a href="{video['Channel URL']}" target="_blank">View Channel</a></p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # Page navigation - Fixed the Next and Previous buttons
            st.markdown("<div style='display: flex; justify-content: space-between; margin: 20px 0;'>", unsafe_allow_html=True)
            
            col1, col2, col3, col4, col5 = st.columns([1, 1, 3, 1, 1])
            
            with col1:
                if st.button("⏮ Previous", key="prev_button", disabled=st.session_state.page <= 1):
                    previous_page()
                    
            with col2:
                st.write(f"Page {st.session_state.page} of {total_pages}")
                
            with col4:
                if st.button("⏭ Next", key="next_button", disabled=st.session_state.page >= total_pages):
                    next_page()
                    
            with col5:
                items_per_page = st.selectbox(
                    "Per Page:",
                    options=[5, 10, 20, 50],
                    index=1,
                    key="items_per_page_select"
                )
                if items_per_page != st.session_state.items_per_page:
                    st.session_state.items_per_page = items_per_page
                    st.session_state.page = 1  # Reset to first page when changing items per page
                    
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("No results found. Try adjusting your search parameters or filters.")
else:
    # Display welcome message and instructions
    st.markdown("""
    ## Welcome to YouTube Viral Topics Analyzer
    
    This tool helps you discover trending and viral content on YouTube based on your keywords.
    
    ### How to use:
    1. Enter your YouTube API key in the sidebar
    2. Enter your keywords (one per line)
    3. Adjust search parameters if needed
    4. Click "Start Search"
    5. Use the filters to narrow down results
    
    ### Features:
    - Search for trending videos by keywords
    - Filter results by views, subscribers, and more
    - Analyze content trends with built-in analytics
    - Save and export your search results
    
    Get started by entering your API key and keywords in the sidebar!
    """)

    # Display sample image or video
    st.image("https://i.imgur.com/UYrEOvA.png", caption="YouTube Viral Topics Analyzer", use_column_width=True)
