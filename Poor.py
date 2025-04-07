# YouTube Analytics Platform 

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pathankot YouTube Analysis Platform</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <!-- Chart.js for analytics -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {
            --primary-color: #FF0000;
            --secondary-color: #606060;
            --light-bg: #f8f9fa;
            --dark-bg: #343a40;
            --hover-color: #e9ecef;
        }
        
        body {
            background-color: var(--light-bg);
            
            font-family: 'Roboto', sans-serif;
        }
        
        .sidebar {
            width: 280px;
            position: fixed;
            top: 56px;
            left: 0;
            height: calc(100vh - 56px);
            background-color: var(--dark-bg);
            padding: 20px;
            overflow-y: auto;
            z-index: 999;
            color: white;
            transition: all 0.3s;
        }
        
        .sidebar.collapsed {
            width: 60px;
            padding: 20px 10px;
        }
        
        .sidebar.collapsed .sidebar-heading,
        .sidebar.collapsed .sidebar-item span,
        .sidebar.collapsed .filter-section,
        .sidebar.collapsed .category-list {
            display: none;
        }
        
        .sidebar-item {
            padding: 8px 10px;
            border-radius: 5px;
            cursor: pointer;
            margin-bottom: 5px;
            transition: background-color 0.3s;
        }
        
        .sidebar-item:hover {
            background-color: #495057;
        }
        
        .sidebar-item.active {
            background-color: var(--primary-color);
        }
        
        .sidebar-item i {
            width: 20px;
            text-align: center;
            margin-right: 10px;
        }
        
        .main-content {
            margin-left: 280px;
            padding: 20px;
            transition: all 0.3s;
        }
        
        .main-content.expanded {
            margin-left: 60px;
        }
        
        .video-card {
            cursor: pointer;
            transition: transform 0.3s, box-shadow 0.3s;
            margin-bottom: 20px;
            height: 100%;
            border-radius: 10px;
            overflow: hidden;
            border: none;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .video-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        }
        
        .card-img-top {
            height: 180px;
            object-fit: cover;
        }
        
        .truncate {
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        
        .toggle-sidebar {
            cursor: pointer;
            margin-right: 15px;
        }
        
        .video-controls {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            opacity: 0;
            transition: opacity 0.3s;
        }
        
        .card:hover .video-controls {
            opacity: 1;
        }
        
        .play-btn {
            background-color: rgba(255, 255, 255, 0.7);
            border-radius: 50%;
            width: 50px;
            height: 50px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.3);
        }
        
        .duration-badge {
            position: absolute;
            bottom: 8px;
            right: 8px;
            background-color: rgba(0, 0, 0, 0.7);
            color: white;
            padding: 3px 6px;
            border-radius: 3px;
            font-size: 12px;
        }
        
        .category-badge {
            position: absolute;
            top: 8px;
            left: 8px;
            font-size: 12px;
            padding: 3px 8px;
        }

        .trending-badge {
            position: absolute;
            top: 8px;
            right: 8px;
            background-color: var(--primary-color);
            color: white;
            padding: 3px 8px;
            border-radius: 3px;
            font-size: 12px;
        }
        
        .filter-section {
            background-color: #495057;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 15px;
        }
        
        .filter-section h6 {
            margin-bottom: 15px;
            border-bottom: 1px solid #6c757d;
            padding-bottom: 5px;
        }
        
        .search-box {
            position: relative;
        }
        
        .search-box .suggestions {
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            z-index: 1000;
            background: white;
            border-radius: 0 0 4px 4px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            max-height: 200px;
            overflow-y: auto;
            display: none;
        }
        
        .search-box .suggestions.active {
            display: block;
        }
        
        .suggestion-item {
            padding: 8px 15px;
            cursor: pointer;
            border-bottom: 1px solid #eee;
            color: #333;
        }
        
        .suggestion-item:hover {
            background-color: #f0f0f0;
        }
        
        .analytics-card {
            background-color: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        
        .pagination {
            justify-content: center;
            margin-top: 20px;
        }
        
        .metric-card {
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            padding: 15px;
            text-align: center;
            margin-bottom: 20px;
        }
        
        .metric-value {
            font-size: 1.8rem;
            font-weight: bold;
            color: var(--primary-color);
            margin-bottom: 5px;
        }
        
        .metric-label {
            color: var(--secondary-color);
            font-size: 0.9rem;
        }
        
        .video-detail-row {
            display: flex;
            margin-bottom: 10px;
        }
        
        .video-detail-label {
            flex: 0 0 120px;
            font-weight: bold;
        }
        
        .video-performance {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 4px;
            color: white;
            font-size: 0.8rem;
            margin-left: 5px;
        }
        
        .performance-high {
            background-color: #28a745;
        }
        
        .performance-medium {
            background-color: #ffc107;
        }
        
        .performance-low {
            background-color: #dc3545;
        }
        
        .custom-control label {
            color: white;
            font-size: 0.9rem;
        }
        
        .nav-pills .nav-link.active {
            background-color: var(--primary-color);
        }
        
        .nav-pills .nav-link {
            color: var(--secondary-color);
        }
        
        .badge-transcript {
            position: absolute;
            top: 35px;
            left: 8px;
            font-size: 11px;
            padding: 2px 6px;
        }
        
        /* Responsive adjustments */
        @media (max-width: 992px) {
            .sidebar {
                width: 60px;
                padding: 20px 10px;
            }
            
            .sidebar .sidebar-heading,
            .sidebar .sidebar-item span,
            .sidebar .filter-section,
            .sidebar .category-list {
                display: none;
            }
            
            .main-content {
                margin-left: 60px;
            }
        }
    </style>
</head>
<body>
    <!-- Navigation Bar -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark fixed-top">
        <div class="container-fluid">
            <div class="toggle-sidebar" id="sidebarToggle">
                <i class="fas fa-bars text-white"></i>
            </div>
            <a class="navbar-brand" href="#">
                <i class="fab fa-youtube text-danger me-2"></i>
                Pathankot YouTube Analysis
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarSupportedContent">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarSupportedContent">
                <div class="search-box w-50 mx-auto">
                    <div class="input-group">
                        <input type="text" class="form-control" id="searchInput" placeholder="Search keywords..." aria-label="Search keywords">
                        <button class="btn btn-danger" type="button" id="searchButton">
                            <i class="fas fa-search"></i>
                        </button>
                    </div>
                    <div class="suggestions" id="searchSuggestions"></div>
                </div>
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item">
                        <a class="nav-link" href="#" data-bs-toggle="modal" data-bs-target="#apiKeyModal">
                            <i class="fas fa-key"></i> API Key
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="#" data-bs-toggle="modal" data-bs-target="#savedSearchesModal">
                            <i class="fas fa-bookmark"></i> Saved Searches
                        </a>
                    </li>
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown">
                            <i class="fas fa-cog"></i> Settings
                        </a>
                        <ul class="dropdown-menu dropdown-menu-end">
                            <li><a class="dropdown-item" href="#" data-bs-toggle="modal" data-bs-target="#settingsModal">Preferences</a></li>
                            <li><a class="dropdown-item" href="#" id="exportDataBtn">Export Data</a></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item" href="#" data-bs-toggle="modal" data-bs-target="#helpModal">Help</a></li>
                        </ul>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <!-- Sidebar -->
    <div class="sidebar" id="sidebar">
        <div class="sidebar-heading mb-3">Filters</div>
        
        <!-- Main navigation -->
        <div class="sidebar-item active" data-view="discover">
            <i class="fas fa-compass"></i> <span>Discover</span>
        </div>
        <div class="sidebar-item" data-view="trending">
            <i class="fas fa-chart-line"></i> <span>Trending</span>
        </div>
        <div class="sidebar-item" data-view="analytics">
            <i class="fas fa-chart-bar"></i> <span>Analytics</span>
        </div>
        <div class="sidebar-item" data-view="saved">
            <i class="fas fa-bookmark"></i> <span>Saved</span>
        </div>
        <div class="sidebar-item" data-view="history">
            <i class="fas fa-history"></i> <span>History</span>
        </div>
        
        <!-- Filter sections -->
        <div class="filter-section">
            <h6><i class="fas fa-filter me-2"></i>Filters</h6>
            
            <!-- Upload date filter -->
            <div class="mb-3">
                <label class="form-label text-light small">Upload Date</label>
                <select class="form-select form-select-sm" id="uploadDateFilter">
                    <option value="any">Any time</option>
                    <option value="hour">Last hour</option>
                    <option value="today">Today</option>
                    <option value="week">This week</option>
                    <option value="month">This month</option>
                    <option value="year">This year</option>
                    <option value="custom">Custom range</option>
                </select>
                <div id="customDateRange" class="mt-2" style="display: none;">
                    <input type="date" class="form-control form-control-sm mb-2" id="startDate">
                    <input type="date" class="form-control form-control-sm" id="endDate">
                </div>
            </div>
            
            <!-- Language filter -->
            <div class="mb-3">
                <label class="form-label text-light small">Language</label>
                <select class="form-select form-select-sm" id="languageFilter">
                    <option value="any">Any language</option>
                    <option value="en">English</option>
                    <option value="hi">Hindi</option>
                    <option value="es">Spanish</option>
                    <option value="fr">French</option>
                    <option value="de">German</option>
                    <option value="ja">Japanese</option>
                    <option value="ko">Korean</option>
                    <option value="zh">Chinese</option>
                    <option value="ar">Arabic</option>
                    <option value="ru">Russian</option>
                </select>
            </div>
            
            <!-- Duration filter -->
            <div class="mb-3">
                <label class="form-label text-light small">Duration</label>
                <select class="form-select form-select-sm" id="durationFilter">
                    <option value="any">Any duration</option>
                    <option value="short">Short (< 4 minutes)</option>
                    <option value="medium">Medium (4-20 minutes)</option>
                    <option value="long">Long (> 20 minutes)</option>
                    <option value="custom">Custom range</option>
                </select>
                <div id="customDurationRange" class="mt-2" style="display: none;">
                    <div class="row g-2">
                        <div class="col-6">
                            <input type="number" class="form-control form-control-sm" id="minDuration" placeholder="Min (seconds)">
                        </div>
                        <div class="col-6">
                            <input type="number" class="form-control form-control-sm" id="maxDuration" placeholder="Max (seconds)">
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- View count filter -->
            <div class="mb-3">
                <label class="form-label text-light small">View Count</label>
                <div class="row g-2">
                    <div class="col-6">
                        <input type="number" class="form-control form-control-sm" id="minViews" placeholder="Min views">
                    </div>
                    <div class="col-6">
                        <input type="number" class="form-control form-control-sm" id="maxViews" placeholder="Max views">
                    </div>
                </div>
            </div>
            
            <!-- Subscriber count filter -->
            <div class="mb-3">
                <label class="form-label text-light small">Channel Subscribers</label>
                <div class="row g-2">
                    <div class="col-6">
                        <input type="number" class="form-control form-control-sm" id="minSubs" placeholder="Min subs">
                    </div>
                    <div class="col-6">
                        <input type="number" class="form-control form-control-sm" id="maxSubs" placeholder="Max subs">
                    </div>
                </div>
            </div>
            
            <!-- Has transcript filter -->
            <div class="mb-3">
                <div class="form-check">
                    <input class="form-check-input" type="checkbox" id="hasTranscript">
                    <label class="form-check-label text-light small" for="hasTranscript">
                        Has transcript
                    </label>
                </div>
            </div>
            
            <!-- Categories -->
            <div class="mb-3">
                <label class="form-label text-light small">Categories</label>
                <select class="form-select form-select-sm" id="categoryFilter" multiple size="5">
                    <option value="1">Film & Animation</option>
                    <option value="2">Autos & Vehicles</option>
                    <option value="10">Music</option>
                    <option value="15">Pets & Animals</option>
                    <option value="17">Sports</option>
                    <option value="18">Short Movies</option>
                    <option value="19">Travel & Events</option>
                    <option value="20">Gaming</option>
                    <option value="21">Videoblogging</option>
                    <option value="22">People & Blogs</option>
                    <option value="23">Comedy</option>
                    <option value="24">Entertainment</option>
                    <option value="25">News & Politics</option>
                    <option value="26">Howto & Style</option>
                    <option value="27">Education</option>
                    <option value="28">Science & Technology</option>
                    <option value="29">Nonprofits & Activism</option>
                    <option value="30">Movies</option>
                    <option value="31">Anime/Animation</option>
                    <option value="32">Action/Adventure</option>
                    <option value="33">Classics</option>
                    <option value="34">Comedy</option>
                    <option value="35">Documentary</option>
                    <option value="36">Drama</option>
                    <option value="37">Family</option>
                    <option value="38">Foreign</option>
                    <option value="39">Horror</option>
                    <option value="40">Sci-Fi/Fantasy</option>
                    <option value="41">Thriller</option>
                    <option value="42">Shorts</option>
                    <option value="43">Shows</option>
                    <option value="44">Trailers</option>
                </select>
            </div>
            
            <!-- Apply filters button -->
            <button class="btn btn-danger btn-sm w-100 mb-2" id="applyFiltersBtn">
                <i class="fas fa-filter me-2"></i>Apply Filters
            </button>
            <button class="btn btn-outline-light btn-sm w-100" id="resetFiltersBtn">
                <i class="fas fa-undo me-2"></i>Reset Filters
            </button>
        </div>
        
        <!-- Saved searches section -->
        <div class="filter-section">
            <h6><i class="fas fa-bookmark me-2"></i>Saved Searches</h6>
            <div class="saved-searches-list" id="savedSearchesList">
                <div class="text-center text-light small">
                    <p>No saved searches yet</p>
                </div>
            </div>
            <div class="mt-2">
                <button class="btn btn-outline-light btn-sm w-100" id="saveCurrentSearch" disabled>
                    <i class="fas fa-save me-2"></i>Save Current Search
                </button>
            </div>
        </div>
    </div>

    <!-- Main Content -->
    <div class="main-content" id="mainContent">
        <!-- Dynamic content area -->
        <div id="contentArea">
            <!-- Initial loading state -->
            <div class="text-center py-5" id="initialState">
                <img src="https://www.gstatic.com/youtube/img/branding/youtubelogo/svg/youtubelogo.svg" alt="YouTube" height="50" class="mb-4">
                <h2 class="mb-3">Pathankot YouTube Video Analysis and Search</h2>
                <p class="lead mb-4">Search for keywords to discover trending videos and analyze performance data</p>
                <div class="row justify-content-center gap-4 mb-4">
                    <div class="col-md-3">
                        <div class="card text-center p-4">
                            <i class="fas fa-search fa-3x text-danger mb-3"></i>
                            <h5>Search Videos</h5>
                            <p class="small text-muted">Find latest videos for your keywords</p>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card text-center p-4">
                            <i class="fas fa-chart-line fa-3x text-danger mb-3"></i>
                            <h5>Track Trends</h5>
                            <p class="small text-muted">See what's trending in your area</p>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card text-center p-4">
                            <i class="fas fa-film fa-3x text-danger mb-3"></i>
                            <h5>Content Analysis</h5>
                            <p class="small text-muted">Gain insights on video performance</p>
                        </div>
                    </div>
                </div>
                <div class="input-group mb-3 mx-auto" style="max-width: 500px;">
                    <input type="text" class="form-control form-control-lg" placeholder="Enter keywords to search..." id="mainSearchInput">
                    <button class="btn btn-danger btn-lg" type="button" id="mainSearchButton">
                        <i class="fas fa-search me-2"></i>Search
                    </button>
                </div>
                <div class="small text-muted">
                    <strong>Popular Keywords:</strong>
                    <a href="#" class="keyword-suggestion">Pathankot News</a> • 
                    <a href="#" class="keyword-suggestion">Pathankot Tourism</a> • 
                    <a href="#" class="keyword-suggestion">Pathankot Food</a> • 
                    <a href="#" class="keyword-suggestion">Pathankot Temple</a>
                </div>
            </div>
            
            <!-- Loading state -->
            <div id="loadingState" style="display: none;">
                <div class="text-center py-5">
                    <div class="spinner-border text-danger mb-3" role="status" style="width: 3rem; height: 3rem;">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <h4 class="mt-3">YouTube Search in Progress...</h4>
                    <p class="text-muted" id="loadingMessage">Retrieving videos for your keywords</p>
                    <div class="progress mt-4" style="height: 10px; max-width: 500px; margin: 0 auto;">
                        <div class="progress-bar progress-bar-striped progress-bar-animated bg-danger" role="progressbar" id="searchProgress" style="width: 0%"></div>
                    </div>
                </div>
            </div>
            
            <!-- Results state (initially hidden) -->
            <div id="resultsState" style="display: none;">
                <!-- Results header with metrics -->
                <div class="d-flex justify-content-between align-items-center mb-4 flex-wrap">
                    <h3 id="resultsTitle">Results for "<span id="searchTermDisplay"></span>"</h3>
                    <div class="d-flex">
                        <div class="btn-group me-2">
                            <button type="button" class="btn btn-outline-secondary active" id="gridViewBtn">
                                <i class="fas fa-th"></i>
                            </button>
                            <button type="button" class="btn btn-outline-secondary" id="listViewBtn">
                                <i class="fas fa-list"></i>
                            </button>
                        </div>
                        <select class="form-select" id="sortOptions" style="width: auto;">
                            <option value="relevance">Relevance</option>
                            <option value="date">Upload date (latest)</option>
                            <option value="viewCount">View count (highest)</option>
                            <option value="rating">Rating (highest)</option>
                        </select>
                    </div>
                </div>
                
                <!-- Results metrics -->
                <div class="row mb-4">
                    <div class="col-md-3 col-sm-6">
                        <div class="metric-card">
                            <div class="metric-value" id="totalVideosMetric">0</div>
                            <div class="metric-label">Total Videos</div>
                        </div>
                    </div>
                    <div class="col-md-3 col-sm-6">
                        <div class="metric-card">
                            <div class="metric-value" id="totalViewsMetric">0</div>
                            <div class="metric-label">Total Views</div>
                        </div>
                    </div>
                    <div class="col-md-3 col-sm-6">
                        <div class="metric-card">
                            <div class="metric-value" id="avgViewsMetric">0</div>
                            <div class="metric-label">Average Views</div>
                        </div>
                    </div>
                    <div class="col-md-3 col-sm-6">
                        <div class="metric-card">
                            <div class="metric-value" id="avgEngagementMetric">0%</div>
                            <div class="metric-label">Avg. Engagement</div>
                        </div>
                    </div>
                </div>
                
                <!-- Results tabs -->
                <ul class="nav nav-pills mb-4" id="resultsTabs" role="tablist">
                    <li class="nav-item" role="presentation">
                        <button class="nav-link active" id="videos-tab" data-bs-toggle="pill" data-bs-target="#videos-tab-pane" type="button" role="tab">Videos</button>
                    </li>
                    <li class="nav-item" role="presentation">
                        <button class="nav-link" id="analytics-tab" data-bs-toggle="pill" data-bs-target="#analytics-tab-pane" type="button" role="tab">Analytics</button>
                    </li>
                    <li class="nav-item" role="presentation">
                        <button class="nav-link" id="trending-tab" data-bs-toggle="pill" data-bs-target="#trending-tab-pane" type="button" role="tab">Trending Topics</button>
                    </li>
                </ul>
                
                <div class="tab-content" id="resultsTabContent">
                    <!-- Videos tab -->
                    <div class="tab-pane fade show active" id="videos-tab-pane" role="tabpanel" aria-labelledby="videos-tab" tabindex="0">
                        <div class="row" id="videoGrid">
                            <!-- Video cards will be generated dynamically -->
                        </div>
                        
                        <!-- Pagination -->
                        <nav aria-label="Video results pagination">
                            <ul class="pagination" id="pagination">
                                <li class="page-item disabled">
                                    <a class="page-link" href="#" id="prevPage" aria-label="Previous">
                                        <span aria-hidden="true">&laquo;</span>
                                    </a>
                                </li>
                                <li class="page-item active"><a class="page-link" href="#" data-page="1">1</a></li>
                                <li class="page-item"><a class="page-link" href="#" data-page="2">2</a></li>
                                <li class="page-item"><a class="page-link" href="#" data-page="3">3</a></li>
                                <li class="page-item">
                                    <a class="page-link" href="#" id="nextPage" aria-label="Next">
                                        <span aria-hidden="true">&raquo;</span>
                                    </a>
                                </li>
                            </ul>
                        </nav>
                    </div>
                    
                    <!-- Analytics tab -->
                    <div class="tab-pane fade" id="analytics-tab-pane" role="tabpanel" aria-labelledby="analytics-tab" tabindex="0">
                        <div class="row">
                            <!-- Views by keyword chart -->
                            <div class="col-md-6 mb-4">
                                <div class="analytics-card">
                                    <h5 class="mb-3">Views by Keyword</h5>
                                    <canvas id="keywordViewsChart"></canvas>
                                </div>
                            </div>
                            
                            <!-- Video duration distribution chart -->
                            <div class="col-md-6 mb-4">
                                <div class="analytics-card">
                                    <h5 class="mb-3">Video Duration Distribution</h5>
                                    <canvas id="durationDistributionChart"></canvas>
                                </div>
                            </div>
                            
                            <!-- Upload time analysis -->
                            <div class="col-md-6 mb-4">
                                <div class="analytics-card">
                                    <h5 class="mb-3">Upload Time Analysis</h5>
                                    <canvas id="uploadTimeChart"></canvas>
                                </div>
                            </div>
                            
                            <!-- Engagement vs Views scatter chart -->
                            <div class="col-md-6 mb-4">
                                <div class="analytics-card">
                                    <h5 class="mb-3">Engagement vs Views</h5>
                                    <canvas id="engagementScatterChart"></canvas>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Trending Topics tab -->
                    <div class="tab-pane fade" id="trending-tab-pane" role="tabpanel" aria-labelledby="trending-tab" tabindex="0">
                        <div class="row">
                            <!-- Trending topics word cloud -->
                            <div class="col-md-6 mb-4">
                                <div class="analytics-card">
                                    <h5 class="mb-3">Trending Topics</h5>
                                    <div id="topicCloud" style="height: 300px; position: relative;"></div>
                                </div>
                            </div>
                            
                            <!-- Top performing topics -->
                            <div class="col-md-6 mb-4">
                                <div class="analytics-card">
                                    <h5 class="mb-3">Top Performing Topics</h5>
                                    <div class="table-responsive">
                                        <table class="table table-striped table-hover" id="topTopicsTable">
                                            <thead>
                                                <tr>
                                                    <th>Topic</th>
                                                    <th>Videos</th>
                                                    <th>Avg Views</th>
                                                    <th>Engagement</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                <!-- Will be populated dynamically -->
                                            </tbody>
                                        </table>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Recently trending videos for your keywords -->
                            <div class="col-12">
                                <div class="analytics-card">
                                    <h5 class="mb-3">Recently Trending Videos</h5>
                                    <div class="table-responsive">
                                        <table class="table table-hover" id="trendingVideosTable">
                                            <thead>
                                                <tr>
                                                    <th>Video</th>
                                                    <th>Channel</th>
                                                    <th>Views</th>
                                                    <th>Published</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                <!-- Will be populated dynamically -->
                                            </tbody>
                                        </table>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- JavaScript Script -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // This will be your JavaScript implementation
        document.addEventListener('DOMContentLoaded', function() {
            // Initialize sidebar toggle
            const sidebarToggle = document.getElementById('sidebarToggle');
            const sidebar = document.getElementById('sidebar');
            const mainContent = document.getElementById('mainContent');
            
            sidebarToggle.addEventListener('click', function() {
                sidebar.classList.toggle('collapsed');
                mainContent.classList.toggle('expanded');
            });
            
            // Main search functionality
            const mainSearchButton = document.getElementById('mainSearchButton');
            const mainSearchInput = document.getElementById('mainSearchInput');
            const searchButton = document.getElementById('searchButton');
            const searchInput = document.getElementById('searchInput');
            
            function performSearch(query) {
                if (!query) return;
                
                // Show loading state
                document.getElementById('initialState').style.display = 'none';
                document.getElementById('resultsState').style.display = 'none';
                document.getElementById('loadingState').style.display = 'block';
                
                // Simulate search progress
                let progress = 0;
                const progressBar = document.getElementById('searchProgress');
                const loadingMessage = document.getElementById('loadingMessage');
                
                const progressInterval = setInterval(() => {
                    progress += 5;
                    progressBar.style.width = progress + '%';
                    
                    if (progress === 30) {
                        loadingMessage.textContent = 'Analyzing video metrics...';
                    } else if (progress === 60) {
                        loadingMessage.textContent = 'Processing data...';
                    } else if (progress === 90) {
                        loadingMessage.textContent = 'Preparing results...';
                    }
                    
                    if (progress >= 100) {
                        clearInterval(progressInterval);
                        // Show results
                        setTimeout(() => {
                            document.getElementById('loadingState').style.display = 'none';
                            document.getElementById('resultsState').style.display = 'block';
                            document.getElementById('searchTermDisplay').textContent = query;
                            // Update metrics with random data for demo
                            document.getElementById('totalVideosMetric').textContent = Math.floor(Math.random() * 500 + 100);
                            document.getElementById('totalViewsMetric').textContent = (Math.floor(Math.random() * 10000 + 5000) / 1000).toFixed(1) + 'K';
                            document.getElementById('avgViewsMetric').textContent = (Math.floor(Math.random() * 50 + 10) * 100).toLocaleString();
                            document.getElementById('avgEngagementMetric').textContent = (Math.random() * 10 + 2).toFixed(1) + '%';
                            
                            // Populate video grid with demo data
                            populateVideoGrid(query);
                        }, 500);
                    }
                }, 100);
            }
            
            mainSearchButton.addEventListener('click', function() {
                performSearch(mainSearchInput.value);
            });
            
            mainSearchInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    performSearch(mainSearchInput.value);
                }
            });
            
            searchButton.addEventListener('click', function() {
                performSearch(searchInput.value);
            });
            
            searchInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    performSearch(searchInput.value);
                }
            });
            
            // Suggested keywords
            document.querySelectorAll('.keyword-suggestion').forEach(elem => {
                elem.addEventListener('click', function(e) {
                    e.preventDefault();
                    mainSearchInput.value = this.textContent;
                    performSearch(this.textContent);
                });
            });
            
            // Function to populate video grid with mock data
            function populateVideoGrid(query) {
                const videoGrid = document.getElementById('videoGrid');
                videoGrid.innerHTML = '';
                
                // Mock video data
                const categories = ['News', 'Travel', 'Food', 'Entertainment', 'Education'];
                const channels = ['Pathankot News Network', 
