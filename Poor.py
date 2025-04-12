import streamlit as st
import pandas as pd

# Set page config
st.set_page_config(
    page_title="YouTube Data Scraper",
    page_icon="📊",
    layout="wide"
)

# App title and description
st.title("YouTube Data Scraper")
st.markdown("""
This tool allows you to search and filter YouTube videos by various criteria including:
- View counts
- Subscriber counts
- Publication dates
- Video duration (long videos vs shorts)
- Language
- Country
- Keywords and more!
""")

# Custom CSS
st.markdown("""
<style>
    .card {
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 15px;
        background-color: white;
    }
    .card-title {
        font-size: 18px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .stButton button {
        background-color: #FF0000;
        color: white;
    }
    .stSelectbox label, .stSlider label {
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Function to format duration from ISO 8601 format
def format_duration(duration_str):
    # Remove PT from the beginning
    duration = duration_str[2:]
    
    hours = re.search(r'(\d+)H', duration)
    minutes = re.search(r'(\d+)M', duration)
    seconds = re.search(r'(\d+)S', duration)
    
    hours_val = int(hours.group(1)) if hours else 0
    minutes_val = int(minutes.group(1)) if minutes else 0
    seconds_val = int(seconds.group(1)) if seconds else 0
    
    # Format the duration
    if hours_val > 0:
        return f"{hours_val}:{minutes_val:02d}:{seconds_val:02d}"
    else:
        return f"{minutes_val}:{seconds_val:02d}"

# Function to format numbers with commas
def format_number(num):
    if num is None:
        return "0"
    return f"{int(num):,}"

# Function to check if video is a short (less than 60 seconds)
def is_short(duration_str):
    # Remove PT from the beginning
    duration = duration_str[2:]
    
    hours = re.search(r'(\d+)H', duration)
    minutes = re.search(r'(\d+)M', duration)
    seconds = re.search(r'(\d+)S', duration)
    
    hours_val = int(hours.group(1)) if hours else 0
    minutes_val = int(minutes.group(1)) if minutes else 0
    seconds_val = int(seconds.group(1)) if seconds else 0
    
    total_seconds = hours_val * 3600 + minutes_val * 60 + seconds_val
    return total_seconds <= 60

# Function to convert date to YYYY-MM-DD format
def format_date(date_str):
    try:
        date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
        return date_obj.strftime("%Y-%m-%d")
    except:
        return date_str

# Function to get language name from language code
def get_language_name(lang_code):
    try:
        if lang_code:
            return iso639.languages.get(part1=lang_code).name
        return "Unknown"
    except:
        return lang_code or "Unknown"

# Function to get country name from country code
def get_country_name(country_code):
    try:
        if country_code:
            return pycountry.countries.get(alpha_2=country_code).name
        return "Unknown"
    except:
        return country_code or "Unknown"

# Function to get channel info
def get_channel_info(youtube, channel_id):
    try:
        request = youtube.channels().list(
            part="snippet,statistics",
            id=channel_id
        )
        response = request.execute()
        
        if not response['items']:
            return {"name": "Unknown", "subscribers": 0, "url": f"https://www.youtube.com/channel/{channel_id}"}
        
        channel = response['items'][0]
        return {
            "name": channel['snippet']['title'],
            "subscribers": int(channel['statistics'].get('subscriberCount', 0)),
            "url": f"https://www.youtube.com/channel/{channel_id}"
        }
    except Exception as e:
        st.error(f"Error retrieving channel info: {str(e)}")
        return {"name": "Error", "subscribers": 0, "url": f"https://www.youtube.com/channel/{channel_id}"}

# Function to download dataframe as CSV
def download_csv(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="youtube_data.csv">Download CSV File</a>'
    return href

# Function to download dataframe as Excel
def download_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='YouTube Data')
    excel_data = output.getvalue()
    b64 = base64.b64encode(excel_data).decode()
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="youtube_data.xlsx">Download Excel File</a>'
    return href

# Create sidebar for API key input
st.sidebar.header("API Configuration")
api_key = st.sidebar.text_input("Enter your YouTube API Key", type="password")
api_key_info = st.sidebar.expander("How to get an API Key")
with api_key_info:
    st.markdown("""
    1. Go to [Google Cloud Console](https://console.cloud.google.com/)
    2. Create a new project
    3. Enable the YouTube Data API v3
    4. Create credentials (API Key)
    5. Copy the API Key and paste it here
    """)

# Create tabs for different sections
tab1, tab2, tab3 = st.tabs(["Search & Filter", "Results", "About"])

with tab1:
    st.header("Search and Filter Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        search_type = st.radio("Search Type", ["Keyword", "Channel ID", "Video ID"])
        search_query = st.text_input("Enter search query or ID")
        
        st.subheader("Date Filters")
        date_filter = st.checkbox("Enable date filter")
        if date_filter:
            col1a, col1b = st.columns(2)
            with col1a:
                start_date = st.date_input("From Date", datetime.date.today() - datetime.timedelta(days=30))
            with col1b:
                end_date = st.date_input("To Date", datetime.date.today())
        
        st.subheader("View Count Filters")
        view_filter = st.checkbox("Enable view count filter")
        if view_filter:
            col1c, col1d = st.columns(2)
            with col1c:
                min_views = st.number_input("Minimum Views", min_value=0, value=0)
            with col1d:
                max_views = st.number_input("Maximum Views", min_value=0, value=10000000)
    
    with col2:
        st.subheader("Subscriber Filters")
        subscriber_filter = st.checkbox("Enable subscriber filter")
        if subscriber_filter:
            col2a, col2b = st.columns(2)
            with col2a:
                min_subscribers = st.number_input("Minimum Subscribers", min_value=0, value=0)
            with col2b:
                max_subscribers = st.number_input("Maximum Subscribers", min_value=0, value=10000000)
        
        st.subheader("Video Type")
        video_type = st.radio("Video Type", ["All Videos", "Long Videos Only", "Shorts Only"])
        
        st.subheader("Language & Region")
        language_filter = st.checkbox("Filter by language")
        if language_filter:
            # Get common languages
            languages = [
                {"code": "", "name": "Any Language"},
                {"code": "en", "name": "English"},
                {"code": "es", "name": "Spanish"},
                {"code": "hi", "name": "Hindi"},
                {"code": "fr", "name": "French"},
                {"code": "ar", "name": "Arabic"},
                {"code": "pt", "name": "Portuguese"},
                {"code": "ru", "name": "Russian"},
                {"code": "ja", "name": "Japanese"},
                {"code": "de", "name": "German"},
                {"code": "ko", "name": "Korean"},
                {"code": "zh", "name": "Chinese"}
            ]
            selected_language = st.selectbox(
                "Select Language", 
                options=[lang["code"] for lang in languages],
                format_func=lambda x: next((lang["name"] for lang in languages if lang["code"] == x), x)
            )
        
        region_filter = st.checkbox("Filter by region")
        if region_filter:
            # Get common countries
            countries = [
                {"code": "", "name": "Any Country"},
                {"code": "US", "name": "United States"},
                {"code": "IN", "name": "India"},
                {"code": "GB", "name": "United Kingdom"},
                {"code": "CA", "name": "Canada"},
                {"code": "AU", "name": "Australia"},
                {"code": "DE", "name": "Germany"},
                {"code": "FR", "name": "France"},
                {"code": "JP", "name": "Japan"},
                {"code": "BR", "name": "Brazil"},
                {"code": "RU", "name": "Russia"}
            ]
            selected_region = st.selectbox(
                "Select Region/Country", 
                options=[country["code"] for country in countries],
                format_func=lambda x: next((country["name"] for country in countries if country["code"] == x), x)
            )
    
    max_results = st.slider("Maximum Results to Retrieve", min_value=5, max_value=50, value=20)
    
    search_button = st.button("Search YouTube")
    
    # Initialize the YouTube API
    if api_key:
        try:
            youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=api_key)
        except Exception as e:
            st.error(f"Error initializing YouTube API: {str(e)}")
    
    # Search and get results when button is clicked
    if search_button:
        if not api_key:
            st.error("Please enter your YouTube API Key in the sidebar first.")
        elif not search_query:
            st.error("Please enter a search query or ID.")
        else:
            st.session_state.search_performed = True
            
            try:
                with st.spinner("Fetching data from YouTube API..."):
                    videos_data = []
                    
                    # Prepare search parameters
                    search_params = {
                        "part": "snippet",
                        "maxResults": max_results,
                        "type": "video"
                    }
                    
                    # Add appropriate search parameter based on search type
                    if search_type == "Keyword":
                        search_params["q"] = search_query
                    elif search_type == "Channel ID":
                        search_params["channelId"] = search_query
                    elif search_type == "Video ID":
                        search_params = {
                            "part": "snippet",
                            "id": search_query
                        }
                    
                    # Add date filter if enabled
                    if date_filter:
                        start_date_str = start_date.strftime("%Y-%m-%dT00:00:00Z")
                        end_date_str = end_date.strftime("%Y-%m-%dT23:59:59Z")
                        search_params["publishedAfter"] = start_date_str
                        search_params["publishedBefore"] = end_date_str
                    
                    # Add language filter if enabled
                    if language_filter and selected_language:
                        search_params["relevanceLanguage"] = selected_language
                    
                    # Add region filter if enabled
                    if region_filter and selected_region:
                        search_params["regionCode"] = selected_region
                    
                    # Execute search
                    if search_type in ["Keyword", "Channel ID"]:
                        search_response = youtube.search().list(**search_params).execute()
                    else:  # Video ID
                        search_response = youtube.videos().list(**search_params).execute()
                    
                    # Process search results
                    video_ids = []
                    if search_type in ["Keyword", "Channel ID"]:
                        for item in search_response.get("items", []):
                            video_ids.append(item["id"]["videoId"])
                    else:  # Video ID
                        for item in search_response.get("items", []):
                            video_ids.append(item["id"])
                    
                    # Get detailed video information
                    if video_ids:
                        chunks = [video_ids[i:i+50] for i in range(0, len(video_ids), 50)]
                        
                        for chunk in chunks:
                            videos_response = youtube.videos().list(
                                part="snippet,contentDetails,statistics",
                                id=",".join(chunk)
                            ).execute()
                            
                            for video in videos_response.get("items", []):
                                video_id = video["id"]
                                snippet = video["snippet"]
                                statistics = video["statistics"]
                                content_details = video["contentDetails"]
                                
                                # Get channel info
                                channel_id = snippet["channelId"]
                                channel_info = get_channel_info(youtube, channel_id)
                                
                                # Check if video is a short
                                duration = content_details["duration"]
                                is_short_video = is_short(duration)
                                
                                # Skip based on video type filter
                                if (video_type == "Long Videos Only" and is_short_video) or \
                                   (video_type == "Shorts Only" and not is_short_video):
                                    continue
                                
                                # Get view count
                                view_count = int(statistics.get("viewCount", 0))
                                
                                # Skip based on view filter
                                if view_filter and (view_count < min_views or view_count > max_views):
                                    continue
                                
                                # Skip based on subscriber filter
                                if subscriber_filter and (channel_info["subscribers"] < min_subscribers or 
                                                         channel_info["subscribers"] > max_subscribers):
                                    continue
                                
                                # Calculate engagement rate
                                likes = int(statistics.get("likeCount", 0))
                                comments = int(statistics.get("commentCount", 0))
                                engagement = likes + comments
                                engagement_rate = round((engagement / view_count * 100), 2) if view_count > 0 else 0
                                
                                # Get thumbnail
                                thumbnail_url = snippet["thumbnails"]["high"]["url"] if "high" in snippet["thumbnails"] else \
                                               snippet["thumbnails"]["default"]["url"]
                                
                                # Add to videos data
                                video_data = {
                                    "Video ID": video_id,
                                    "Title": snippet["title"],
                                    "URL": f"https://www.youtube.com/watch?v={video_id}",
                                    "Thumbnail": thumbnail_url,
                                    "Channel Name": channel_info["name"],
                                    "Channel URL": channel_info["url"],
                                    "Subscribers": channel_info["subscribers"],
                                    "Published Date": format_date(snippet["publishedAt"]),
                                    "Duration": format_duration(duration),
                                    "Is Short": "Yes" if is_short_video else "No",
                                    "Views": view_count,
                                    "Likes": likes,
                                    "Comments": comments,
                                    "Engagement Rate": engagement_rate,
                                    "Language": get_language_name(snippet.get("defaultLanguage", "")),
                                    "Country": get_country_name(snippet.get("defaultAudioLanguage", "")),
                                    "Description": snippet["description"],
                                    "Keyword": search_query if search_type == "Keyword" else ""
                                }
                                
                                videos_data.append(video_data)
                                
                                # Add a small delay to avoid hitting API rate limits
                                time.sleep(0.1)
                    
                    # Store results in session state
                    if videos_data:
                        st.session_state.videos_df = pd.DataFrame(videos_data)
                        st.session_state.videos_data = videos_data
                        st.success(f"Found {len(videos_data)} videos matching your criteria.")
                    else:
                        st.warning("No videos found matching your criteria.")
            
            except Exception as e:
                st.error(f"Error retrieving data: {str(e)}")

# Results tab
with tab2:
    st.header("Search Results")
    
    if 'search_performed' in st.session_state and st.session_state.search_performed:
        if 'videos_df' in st.session_state and not st.session_state.videos_df.empty:
            df = st.session_state.videos_df
            
            # Display download buttons
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(download_csv(df), unsafe_allow_html=True)
            with col2:
                st.markdown(download_excel(df), unsafe_allow_html=True)
            
            # Display summary statistics
            st.subheader("Summary Statistics")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Videos", len(df))
            with col2:
                st.metric("Average Views", format_number(df["Views"].mean()))
            with col3:
                st.metric("Average Likes", format_number(df["Likes"].mean()))
            with col4:
                st.metric("Average Engagement Rate", f"{df['Engagement Rate'].mean():.2f}%")
            
            # Display data table
            st.subheader("Data Table")
            st.dataframe(df.drop(columns=["Thumbnail", "Description"]))
            
            # Display individual video cards
            st.subheader("Video Details")
            
            for video in st.session_state.videos_data:
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
                            <p><strong>Views:</strong> {format_number(video['Views'])}</p>
                            <p><strong>Likes:</strong> {format_number(video['Likes'])} | <strong>Comments:</strong> {format_number(video['Comments'])}</p>
                            <p><strong>Subscribers:</strong> {format_number(video['Subscribers'])}</p>
                            <p><strong>Engagement Rate:</strong> {video['Engagement Rate']}%</p>
                            <p><strong>Language:</strong> {video['Language']} | <strong>Country:</strong> {video['Country']}</p>
                            <p><strong>Is Short:</strong> {video['Is Short']}</p>
                            <p><strong>Found with keyword:</strong> {video['Keyword']}</p>
                            <p>{video['Description'][:200]}...</p>
                            <p><a href="{video['URL']}" target="_blank">Watch on YouTube</a> | 
                               <a href="{video['Channel URL']}" target="_blank">Visit Channel</a></p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No results to display. Please perform a search first.")
    else:
        st.info("No search performed yet. Go to the Search & Filter tab to get started.")

# About tab
with tab3:
    st.header("About This Tool")
    
    st.markdown("""
    ### YouTube Data Scraper
    
    This tool allows you to search and filter YouTube videos using the YouTube Data API. You can use it to:
    
    - Find videos by keyword, channel ID, or specific video ID
    - Filter by view count, subscriber count, publish date, and more
    - Filter for long videos or shorts
    - Find videos in specific languages or regions
    - Export data to CSV or Excel for further analysis
    
    ### API Usage
    
    This tool uses the YouTube Data API v3, which has usage limits. With a free API key, you get 10,000 units per day. 
    Different operations consume different numbers of units:
    
    - Search request: 100 units
    - Video details request: 1 unit per video
    - Channel details request: 1 unit per channel
    
    ### Privacy Notice
    
    This tool runs entirely in your browser. Your API key and the data retrieved are not stored on any server.
    
    ### Need Help?
    
    If you have any questions or need assistance with using this tool, please contact the developer.
    """)
    
    st.subheader("Required Libraries")
    st.code("""
    pip install streamlit
    pip install pandas
    pip install google-api-python-client
    pip install iso639
    pip install pycountry
    pip install xlsxwriter
    """)
