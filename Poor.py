
# YouTube API settings
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'
CLIENT_SECRETS_FILE = 'client_secret.json'  # You'll need to obtain this from Google Cloud Console
SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']

# Cache for API results to reduce API calls
cache = {}

def get_authenticated_service():
    """Get YouTube API client with proper authentication."""
    credentials = None
    if os.path.exists('token.json'):
        credentials = google.oauth2.credentials.Credentials.from_authorized_user_info(
            json.loads(open('token.json').read()))
    
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRETS_FILE, SCOPES)
            credentials = flow.run_local_server(port=8080)
        
        with open('token.json', 'w') as token:
            token.write(credentials.to_json())
    
    return googleapiclient.discovery.build(
        API_SERVICE_NAME, API_VERSION, credentials=credentials)

def format_duration(duration_str):
    """Convert ISO 8601 duration to readable format."""
    match = re.match(r'PT(\d+H)?(\d+M)?(\d+S)?', duration_str)
    if not match:
        return "0:00"
    
    hours = match.group(1)[:-1] if match.group(1) else 0
    minutes = match.group(2)[:-1] if match.group(2) else 0
    seconds = match.group(3)[:-1] if match.group(3) else 0
    
    if int(hours) > 0:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes}:{seconds:02d}"

def duration_to_seconds(duration_str):
    """Convert ISO 8601 duration to seconds."""
    match = re.match(r'PT(\d+H)?(\d+M)?(\d+S)?', duration_str)
    if not match:
        return 0
    
    hours = int(match.group(1)[:-1]) if match.group(1) else 0
    minutes = int(match.group(2)[:-1]) if match.group(2) else 0
    seconds = int(match.group(3)[:-1]) if match.group(3) else 0
    
    return hours * 3600 + minutes * 60 + seconds

def calculate_engagement_score(views, likes, comments, subscriber_count, published_date):
    """Calculate engagement score based on video metrics."""
    if subscriber_count == 0:
        subscriber_count = 1  # Avoid division by zero
    
    # Calculate days since publication
    published_date_obj = parser.parse(published_date)
    current_date = datetime.datetime.now(published_date_obj.tzinfo)
    days_since_publication = (current_date - published_date_obj).days
    if days_since_publication == 0:
        days_since_publication = 1  # Avoid division by zero
    
    # Normalize metrics by time and channel size
    views_per_day = views / days_since_publication
    views_per_sub_ratio = views / subscriber_count
    likes_per_view_ratio = likes / views if views > 0 else 0
    comments_per_view_ratio = comments / views if views > 0 else 0
    
    # Calculate weighted score
    engagement_score = (
        (0.4 * views_per_day) + 
        (0.2 * views_per_sub_ratio) + 
        (0.25 * likes_per_view_ratio * 1000) + 
        (0.15 * comments_per_view_ratio * 1000)
    )
    
    return engagement_score

def search_youtube(youtube, keyword, max_results=50, published_after=None, 
                  min_duration=0, max_duration=None, 
                  min_subscribers=0, max_subscribers=None):
    """Search YouTube and filter results based on criteria."""
    cache_key = f"{keyword}_{max_results}_{published_after}_{min_duration}_{max_duration}"
    
    if cache_key in cache:
        return cache[cache_key]
    
    # Convert published_after to RFC 3339 format
    if published_after:
        published_after_date = datetime.datetime.now() - datetime.timedelta(days=published_after)
        published_after_str = published_after_date.isoformat() + 'Z'
    else:
        published_after_str = None
    
    # Search for videos
    search_request = youtube.search().list(
        part="snippet",
        q=keyword,
        type="video",
        maxResults=max_results,
        order="date",
        publishedAfter=published_after_str
    )
    search_response = search_request.execute()
    
    video_ids = [item['id']['videoId'] for item in search_response['items']]
    
    if not video_ids:
        return []
    
    # Get detailed video information
    videos_request = youtube.videos().list(
        part="snippet,contentDetails,statistics",
        id=','.join(video_ids)
    )
    videos_response = videos_request.execute()
    
    # Get channel information
    channel_ids = list(set([item['snippet']['channelId'] for item in videos_response['items']]))
    channels_request = youtube.channels().list(
        part="statistics",
        id=','.join(channel_ids)
    )
    channels_response = channels_request.execute()
    
    # Create mapping of channel IDs to subscriber counts
    channel_subscribers = {}
    for channel in channels_response['items']:
        channel_subscribers[channel['id']] = int(channel['statistics'].get('subscriberCount', 0))
    
    # Process video results
    results = []
    for video in videos_response['items']:
        # Extract data
        video_id = video['id']
        title = video['snippet']['title']
        description = video['snippet']['description']
        channel_id = video['snippet']['channelId']
        channel_title = video['snippet']['channelTitle']
        published_at = video['snippet']['publishedAt']
        thumbnail = video['snippet']['thumbnails']['high']['url']
        
        # Get video stats
        view_count = int(video['statistics'].get('viewCount', 0))
        like_count = int(video['statistics'].get('likeCount', 0))
        comment_count = int(video['statistics'].get('commentCount', 0))
        
        # Get duration and convert to seconds
        duration_str = video['contentDetails']['duration']
        duration_seconds = duration_to_seconds(duration_str)
        
        # Get subscriber count
        subscriber_count = channel_subscribers.get(channel_id, 0)
        
        # Apply duration filter
        if duration_seconds < min_duration:
            continue
        if max_duration and duration_seconds > max_duration:
            continue
        
        # Apply subscriber count filter
        if subscriber_count < min_subscribers:
            continue
        if max_subscribers and subscriber_count > max_subscribers:
            continue
        
        # Calculate engagement score
        engagement_score = calculate_engagement_score(
            view_count, like_count, comment_count, subscriber_count, published_at
        )
        
        results.append({
            'id': video_id,
            'title': title,
            'description': description,
            'channel_id': channel_id,
            'channel_title': channel_title,
            'published_at': published_at,
            'thumbnail': thumbnail,
            'view_count': view_count,
            'like_count': like_count,
            'comment_count': comment_count,
            'duration': format_duration(duration_str),
            'duration_seconds': duration_seconds,
            'subscriber_count': subscriber_count,
            'engagement_score': engagement_score
        })
    
    # Cache results
    cache[cache_key] = results
    
    return results

def ai_analyze_trends(videos):
    """Use basic AI to analyze video trends and success factors."""
    if not videos:
        return {
            "performance_insights": "No videos to analyze.",
            "trend_keywords": [],
            "optimal_duration": "N/A",
            "best_publish_time": "N/A"
        }
    
    # Convert to DataFrame for analysis
    df = pd.DataFrame(videos)
    
    # Normalize scores for better comparison
    scaler = MinMaxScaler()
    if len(df) > 1:  # Need at least 2 samples for scaling
        df['normalized_engagement'] = scaler.fit_transform(df[['engagement_score']])
    else:
        df['normalized_engagement'] = 1.0  # Single item gets maximum score
    
    # Find optimal duration range
    if len(df) >= 3:
        duration_bins = [0, 60, 300, 600, 1200, 1800, 3600, float('inf')]
        duration_labels = ['< 1 min', '1-5 mins', '5-10 mins', '10-20 mins', '20-30 mins', '30-60 mins', '> 60 mins']
        df['duration_range'] = pd.cut(df['duration_seconds'], bins=duration_bins, labels=duration_labels)
        
        duration_performance = df.groupby('duration_range')['engagement_score'].mean().sort_values(ascending=False)
        optimal_duration = duration_performance.index[0] if not duration_performance.empty else "Varies"
    else:
        optimal_duration = "Insufficient data"
    
    # Extract common keywords from titles (basic approach)
    title_words = ' '.join(df['title']).lower()
    common_words = [word for word in re.findall(r'\w+', title_words) 
                   if len(word) > 3 and word not in ['this', 'that', 'with', 'from', 'what', 'when', 'where', 'which', 'your']]
    
    word_freq = {}
    for word in common_words:
        if word in word_freq:
            word_freq[word] += 1
        else:
            word_freq[word] = 1
    
    trend_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
    trend_keywords = [word for word, _ in trend_keywords]
    
    # Identify best publishing time (basic analysis)
    if len(df) >= 5:
        df['pub_hour'] = df['published_at'].apply(lambda x: parser.parse(x).hour)
        best_hours = df.groupby('pub_hour')['engagement_score'].mean().sort_values(ascending=False)
        best_hour = best_hours.index[0] if not best_hours.empty else None
        
        if best_hour is not None:
            if best_hour < 12:
                time_desc = f"{best_hour} AM"
            elif best_hour == 12:
                time_desc = "12 PM"
            else:
                time_desc = f"{best_hour - 12} PM"
            
            best_publish_time = time_desc
        else:
            best_publish_time = "Varies"
    else:
        best_publish_time = "Insufficient data"
    
    # Get top performing video
    if not df.empty:
        top_video = df.loc[df['engagement_score'].idxmax()]
        top_video_title = top_video['title']
        top_channel = top_video['channel_title']
    else:
        top_video_title = "N/A"
        top_channel = "N/A"
    
    # Create insights
    performance_insights = f"""
    Top performing videos in this category tend to be {optimal_duration} in length.
    The highest engagement is for "{top_video_title}" by {top_channel}.
    Videos uploaded around {best_publish_time} tend to perform better.
    """
    
    return {
        "performance_insights": performance_insights,
        "trend_keywords": trend_keywords,
        "optimal_duration": optimal_duration,
        "best_publish_time": best_publish_time
    }

def index():
    return render_template('index.html')

def search():
    data = request.json
    keyword = data.get('keyword', '')
    max_results = int(data.get('max_results', 50))
    
    # Time filters
    time_filter = int(data.get('time_filter', 0))  # Days
    
    # Duration filters (in seconds)
    min_duration = int(data.get('min_duration', 0))
    max_duration = int(data.get('max_duration', 0))
    if max_duration <= 0:
        max_duration = None
    
    # Subscriber filters
    min_subscribers = int(data.get('min_subscribers', 0))
    max_subscribers = int(data.get('max_subscribers', 0))
    if max_subscribers <= 0:
        max_subscribers = None
    
    try:
        youtube = get_authenticated_service()
        videos = search_youtube(
            youtube, 
            keyword, 
            max_results=max_results,
            published_after=time_filter if time_filter > 0 else None,
            min_duration=min_duration,
            max_duration=max_duration,
            min_subscribers=min_subscribers,
            max_subscribers=max_subscribers
        )
        
        # Sort videos by engagement score
        videos.sort(key=lambda x: x['engagement_score'], reverse=True)
        
        # Get AI analysis
        ai_analysis = ai_analyze_trends(videos)
        
        return jsonify({
            'success': True,
            'videos': videos,
            'ai_analysis': ai_analysis
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    
    app.run(debug=True)
