import streamlit as st
import pandas as pd
import googleapiclient.discovery
import googleapiclient.errors
import iso639
import pycountry
import datetime
import re
import base64
from io import BytesIO

# Set page config
st.set_page_config(
    page_title="YouTube Data Scraper",
    page_icon="📊",
    layout="wide"
)

st.title("YouTube Data Scraper")
st.markdown("""
This tool allows you to search YouTube videos with filters like:
- View count, Subscribers
- Date ranges, Duration
- Language, Region
- Keyword / Channel ID / Video ID search
""")

# Function to format video duration
def format_duration(duration_str):
    duration = duration_str[2:]
    hours = re.search(r'(\d+)H', duration)
    minutes = re.search(r'(\d+)M', duration)
    seconds = re.search(r'(\d+)S', duration)

    hours_val = int(hours.group(1)) if hours else 0
    minutes_val = int(minutes.group(1)) if minutes else 0
    seconds_val = int(seconds.group(1)) if seconds else 0

    if hours_val > 0:
        return f"{hours_val}:{minutes_val:02d}:{seconds_val:02d}"
    else:
        return f"{minutes_val}:{seconds_val:02d}"

# Function to check if video is a Short
def is_short(duration_str):
    duration = duration_str[2:]
    hours = re.search(r'(\d+)H', duration)
    minutes = re.search(r'(\d+)M', duration)
    seconds = re.search(r'(\d+)S', duration)

    total_seconds = (int(hours.group(1)) * 3600 if hours else 0) + \
                    (int(minutes.group(1)) * 60 if minutes else 0) + \
                    (int(seconds.group(1)) if seconds else 0)
    return total_seconds <= 60

# Function to convert ISO date to normal
def format_date(date_str):
    try:
        date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
        return date_obj.strftime("%Y-%m-%d")
    except:
        return date_str

# Get language name from code
def get_language_name(lang_code):
    try:
        if lang_code:
            return iso639.languages.get(part1=lang_code).name
        return "Unknown"
    except:
        return lang_code or "Unknown"

# Get country name from code
def get_country_name(country_code):
    try:
        if country_code:
            return pycountry.countries.get(alpha_2=country_code).name
        return "Unknown"
    except:
        return country_code or "Unknown"

# Get channel info
def get_channel_info(youtube, channel_id):
    try:
        request = youtube.channels().list(part="snippet,statistics", id=channel_id)
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
        st.error(f"Error getting channel info: {str(e)}")
        return {"name": "Error", "subscribers": 0, "url": f"https://www.youtube.com/channel/{channel_id}"}

# Download CSV
def download_csv(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="youtube_data.csv">Download CSV File</a>'
    return href

# Download Excel
def download_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='YouTube Data')
    excel_data = output.getvalue()
    b64 = base64.b64encode(excel_data).decode()
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="youtube_data.xlsx">Download Excel File</a>'
    return href

# Sidebar for API Key
st.sidebar.header("API Key")
api_key = st.sidebar.text_input("Enter your YouTube API Key", type="password")

if api_key:
    youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=api_key)

# Search form
st.subheader("Search Videos")
search_query = st.text_input("Enter Keyword / Channel ID / Video ID")
search_type = st.selectbox("Search Type", ["Keyword", "Channel ID", "Video ID"])
max_results = st.slider("Max Results", 5, 50, 20)
start_date = st.date_input("Start Date", datetime.date.today() - datetime.timedelta(days=30))
end_date = st.date_input("End Date", datetime.date.today())
video_type = st.selectbox("Video Type", ["All Videos", "Long Videos Only", "Shorts Only"])

if st.button("Search"):
    if not api_key:
        st.error("Please enter API Key.")
    elif not search_query:
        st.error("Please enter search input.")
    else:
        try:
            search_params = {
                "part": "snippet",
                "maxResults": max_results,
                "type": "video"
            }
            if search_type == "Keyword":
                search_params["q"] = search_query
            elif search_type == "Channel ID":
                search_params["channelId"] = search_query
            elif search_type == "Video ID":
                search_params = {"part": "snippet", "id": search_query}

            # Date filters
            start_date_str = start_date.strftime("%Y-%m-%dT00:00:00Z")
            end_date_str = end_date.strftime("%Y-%m-%dT23:59:59Z")
            if search_type != "Video ID":
                search_params["publishedAfter"] = start_date_str
                search_params["publishedBefore"] = end_date_str

            if search_type in ["Keyword", "Channel ID"]:
                search_response = youtube.search().list(**search_params).execute()
                video_ids = [item["id"]["videoId"] for item in search_response.get("items", [])]
            else:
                search_response = youtube.videos().list(**search_params).execute()
                video_ids = [item["id"] for item in search_response.get("items", [])]

            if not video_ids:
                st.warning("No videos found.")
            else:
                df_rows = []
                chunks = [video_ids[i:i+50] for i in range(0, len(video_ids), 50)]
                for chunk in chunks:
                    videos_response = youtube.videos().list(
                        part="snippet,contentDetails,statistics",
                        id=",".join(chunk)
                    ).execute()

                    for video in videos_response.get("items", []):
                        vid_id = video["id"]
                        snippet = video["snippet"]
                        stats = video.get("statistics", {})
                        content = video["contentDetails"]

                        duration = content["duration"]
                        is_short_video = is_short(duration)

                        if (video_type == "Long Videos Only" and is_short_video) or \
                           (video_type == "Shorts Only" and not is_short_video):
                            continue

                        channel_info = get_channel_info(youtube, snippet["channelId"])

                        df_rows.append({
                            "Video Title": snippet["title"],
                            "Video ID": vid_id,
                            "Published Date": format_date(snippet["publishedAt"]),
                            "Channel Name": channel_info["name"],
                            "Subscribers": channel_info["subscribers"],
                            "Views": int(stats.get("viewCount", 0)),
                            "Likes": int(stats.get("likeCount", 0)) if "likeCount" in stats else "N/A",
                            "Comments": int(stats.get("commentCount", 0)) if "commentCount" in stats else "N/A",
                            "Duration": format_duration(duration),
                            "Video URL": f"https://www.youtube.com/watch?v={vid_id}"
                        })

                if df_rows:
                    df = pd.DataFrame(df_rows)
                    st.dataframe(df)

                    st.markdown(download_csv(df), unsafe_allow_html=True)
                    st.markdown(download_excel(df), unsafe_allow_html=True)
                else:
                    st.warning("No videos matched the filters.")
        except Exception as e:
            st.error(f"API Error: {str(e)}")
