
```html
<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>पठानकोट यूट्यूब विश्लेषण प्लेटफॉर्म</title>
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
            padding-top: 60px;
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
                पठानकोट यूट्यूब विश्लेषण
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarSupportedContent">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarSupportedContent">
                <div class="search-box w-50 mx-auto">
                    <div class="input-group">
                        <input type="text" class="form-control" id="searchInput" placeholder="कीवर्ड खोजें..." aria-label="कीवर्ड खोजें">
                        <button class="btn btn-danger" type="button" id="searchButton">
                            <i class="fas fa-search"></i>
                        </button>
                    </div>
                    <div class="suggestions" id="searchSuggestions"></div>
                </div>
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item">
                        <a class="nav-link" href="#" data-bs-toggle="modal" data-bs-target="#apiKeyModal">
                            <i class="fas fa-key"></i> API कुंजी
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="#" data-bs-toggle="modal" data-bs-target="#savedSearchesModal">
                            <i class="fas fa-bookmark"></i> सहेजी गई खोजें
                        </a>
                    </li>
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown">
                            <i class="fas fa-cog"></i> सेटिंग्स
                        </a>
                        <ul class="dropdown-menu dropdown-menu-end">
                            <li><a class="dropdown-item" href="#" data-bs-toggle="modal" data-bs-target="#settingsModal">प्राथमिकताएँ</a></li>
                            <li><a class="dropdown-item" href="#" id="exportDataBtn">डेटा निर्यात करें</a></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item" href="#" data-bs-toggle="modal" data-bs-target="#helpModal">सहायता</a></li>
                        </ul>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <!-- Sidebar -->
    <div class="sidebar" id="sidebar">
        <div class="sidebar-heading mb-3">फिल्टर</div>
        
        <!-- Main navigation -->
        <div class="sidebar-item active" data-view="discover">
            <i class="fas fa-compass"></i> <span>खोज</span>
        </div>
        <div class="sidebar-item" data-view="trending">
            <i class="fas fa-chart-line"></i> <span>ट्रेंडिंग</span>
        </div>
        <div class="sidebar-item" data-view="analytics">
            <i class="fas fa-chart-bar"></i> <span>विश्लेषण</span>
        </div>
        <div class="sidebar-item" data-view="saved">
            <i class="fas fa-bookmark"></i> <span>सहेजे गए</span>
        </div>
        <div class="sidebar-item" data-view="history">
            <i class="fas fa-history"></i> <span>इतिहास</span>
        </div>
        
        <!-- Filter sections -->
        <div class="filter-section">
            <h6><i class="fas fa-filter me-2"></i>फिल्टर्स</h6>
            
            <!-- Upload date filter -->
            <div class="mb-3">
                <label class="form-label text-light small">अपलोड दिनांक</label>
                <select class="form-select form-select-sm" id="uploadDateFilter">
                    <option value="any">किसी भी समय</option>
                    <option value="hour">पिछले घंटे</option>
                    <option value="today">आज</option>
                    <option value="week">इस सप्ताह</option>
                    <option value="month">इस महीने</option>
                    <option value="year">इस वर्ष</option>
                    <option value="custom">कस्टम रेंज</option>
                </select>
                <div id="customDateRange" class="mt-2" style="display: none;">
                    <input type="date" class="form-control form-control-sm mb-2" id="startDate">
                    <input type="date" class="form-control form-control-sm" id="endDate">
                </div>
            </div>
            
            <!-- Language filter -->
            <div class="mb-3">
                <label class="form-label text-light small">भाषा</label>
                <select class="form-select form-select-sm" id="languageFilter">
                    <option value="any">कोई भी भाषा</option>
                    <option value="en">अंग्रेज़ी</option>
                    <option value="hi">हिंदी</option>
                    <option value="es">स्पेनिश</option>
                    <option value="fr">फ्रेंच</option>
                    <option value="de">जर्मन</option>
                    <option value="ja">जापानी</option>
                    <option value="ko">कोरियाई</option>
                    <option value="zh">चीनी</option>
                    <option value="ar">अरबी</option>
                    <option value="ru">रूसी</option>
                </select>
            </div>
            
            <!-- Duration filter -->
            <div class="mb-3">
                <label class="form-label text-light small">अवधि</label>
                <select class="form-select form-select-sm" id="durationFilter">
                    <option value="any">कोई भी अवधि</option>
                    <option value="short">छोटी (< 4 मिनट)</option>
                    <option value="medium">मध्यम (4-20 मिनट)</option>
                    <option value="long">लंबी (> 20 मिनट)</option>
                    <option value="custom">कस्टम रेंज</option>
                </select>
                <div id="customDurationRange" class="mt-2" style="display: none;">
                    <div class="row g-2">
                        <div class="col-6">
                            <input type="number" class="form-control form-control-sm" id="minDuration" placeholder="न्यूनतम (सेकंड)">
                        </div>
                        <div class="col-6">
                            <input type="number" class="form-control form-control-sm" id="maxDuration" placeholder="अधिकतम (सेकंड)">
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- View count filter -->
            <div class="mb-3">
                <label class="form-label text-light small">व्यू काउंट</label>
                <div class="row g-2">
                    <div class="col-6">
                        <input type="number" class="form-control form-control-sm" id="minViews" placeholder="न्यूनतम व्यूज़">
                    </div>
                    <div class="col-6">
                        <input type="number" class="form-control form-control-sm" id="maxViews" placeholder="अधिकतम व्यूज़">
                    </div>
                </div>
            </div>
            
            <!-- Subscriber count filter -->
            <div class="mb-3">
                <label class="form-label text-light small">चैनल सब्सक्राइबर्स</label>
                <div class="row g-2">
                    <div class="col-6">
                        <input type="number" class="form-control form-control-sm" id="minSubs" placeholder="न्यूनतम सब्स">
                    </div>
                    <div class="col-6">
                        <input type="number" class="form-control form-control-sm" id="maxSubs" placeholder="अधिकतम सब्स">
                    </div>
                </div>
            </div>
            
            <!-- Has transcript filter -->
            <div class="mb-3">
                <div class="form-check">
                    <input class="form-check-input" type="checkbox" id="hasTranscript">
                    <label class="form-check-label text-light small" for="hasTranscript">
                        ट्रांसक्रिप्ट है
                    </label>
                </div>
            </div>
            
            <!-- Categories -->
            <div class="mb-3">
                <label class="form-label text-light small">श्रेणियां</label>
                <select class="form-select form-select-sm" id="categoryFilter" multiple size="5">
                    <option value="1">फिल्म और एनीमेशन</option>
                    <option value="2">ऑटो और वाहन</option>
                    <option value="10">संगीत</option>
                    <option value="15">पालतू जानवर और प्राणी</option>
                    <option value="17">खेल</option>
                    <option value="18">लघु फिल्में</option>
                    <option value="19">यात्रा और कार्यक्रम</option>
                    <option value="20">गेमिंग</option>
                    <option value="21">वीडियो ब्लॉगिंग</option>
                    <option value="22">लोग और ब्लॉग</option>
                    <option value="23">कॉमेडी</option>
                    <option value="24">मनोरंजन</option>
                    <option value="25">समाचार और राजनीति</option>
                    <option value="26">हाउटू और स्टाइल</option>
                    <option value="27">शिक्षा</option>
                    <option value="28">विज्ञान और प्रौद्योगिकी</option>
                    <option value="29">गैर-लाभकारी और सक्रियता</option>
                    <option value="30">फिल्में</option>
                    <option value="31">एनीमे/एनिमेशन</option>
                    <option value="32">एक्शन/एडवेंचर</option>
                    <option value="33">क्लासिक्स</option>
                    <option value="34">कॉमेडी</option>
                    <option value="35">डॉक्यूमेंट्री</option>
                    <option value="36">ड्रामा</option>
                    <option value="37">परिवार</option>
                    <option value="38">विदेशी</option>
                    <option value="39">हॉरर</option>
                    <option value="40">साइंस-फिक्शन/फैंटेसी</option>
                    <option value="41">थ्रिलर</option>
                    <option value="42">शॉर्ट्स</option>
                    <option value="43">शोज़</option>
                    <option value="44">ट्रेलर्स</option>
                </select>
            </div>
            
            <!-- Apply filters button -->
            <button class="btn btn-danger btn-sm w-100 mb-2" id="applyFiltersBtn">
                <i class="fas fa-filter me-2"></i>फिल्टर लागू करें
            </button>
            <button class="btn btn-outline-light btn-sm w-100" id="resetFiltersBtn">
                <i class="fas fa-undo me-2"></i>फिल्टर रीसेट करें
            </button>
        </div>
        
        <!-- Saved searches section -->
        <div class="filter-section">
            <h6><i class="fas fa-bookmark me-2"></i>सहेजी गई खोजें</h6>
            <div class="saved-searches-list" id="savedSearchesList">
                <div class="text-center text-light small">
                    <p>अभी तक कोई सहेजी गई खोज नहीं</p>
                </div>
            </div>
            <div class="mt-2">
                <button class="btn btn-outline-light btn-sm w-100" id="saveCurrentSearch" disabled>
                    <i class="fas fa-save me-2"></i>वर्तमान खोज सहेजें
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
                <h2 class="mb-3">पठानकोट यूट्यूब वीडियो विश्लेषण और खोज</h2>
                <p class="lead mb-4">ट्रेंडिंग वीडियो खोजने और प्रदर्शन डेटा का विश्लेषण करने के लिए कीवर्ड खोजें</p>
                <div class="row justify-content-center gap-4 mb-4">
                    <div class="col-md-3">
                        <div class="card text-center p-4">
                            <i class="fas fa-search fa-3x text-danger mb-3"></i>
                            <h5>वीडियो खोजें</h5>
                            <p class="small text-muted">अपने कीवर्ड के लिए नवीनतम वीडियो खोजें</p>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card text-center p-4">
                            <i class="fas fa-chart-line fa-3x text-danger mb-3"></i>
                            <h5>रुझान ट्रैक करें</h5>
                            <p class="small text-muted">अपने क्षेत्र में ट्रेंडिंग क्या है, देखें</p>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card text-center p-4">
                            <i class="fas fa-film fa-3x text-danger mb-3"></i>
                            <h5>सामग्री विश्लेषण</h5>
                            <p class="small text-muted">वीडियो प्रदर्शन पर अंतर्दृष्टि प्राप्त करें</p>
                        </div>
                    </div>
                </div>
                <div class="input-group mb-3 mx-auto" style="max-width: 500px;">
                    <input type="text" class="form-control form-control-lg" placeholder="खोज के लिए कीवर्ड दर्ज करें..." id="mainSearchInput">
                    <button class="btn btn-danger btn-lg" type="button" id="mainSearchButton">
                        <i class="fas fa-search me-2"></i>खोज
                    </button>
                </div>
                <div class="small text-muted">
                    <strong>लोकप्रिय कीवर्ड:</strong>
                    <a href="#" class="keyword-suggestion">पठानकोट न्यूज़</a> • 
                    <a href="#" class="keyword-suggestion">पठानकोट पर्यटन स्थल</a> • 
                    <a href="#" class="keyword-suggestion">पठानकोट भोजन</a> • 
                    <a href="#" class="keyword-suggestion">पठानकोट मंदिर</a>
                </div>
            </div>
            
            <!-- Loading state -->
            <div id="loadingState" style="display: none;">
                <div class="text-center py-5">
                    <div class="spinner-border text-danger mb-3" role="status" style="width: 3rem; height: 3rem;">
                        <span class="visually-hidden">लोड हो रहा है...</span>
                    </div>
                    <h4 class="mt-3">यूट्यूब खोज जारी है...</h4>
                    <p class="text-muted" id="loadingMessage">आपके कीवर्ड के लिए वीडियो प्राप्त किए जा रहे हैं</p>
                    <div class="progress mt-4" style="height: 10px; max-width: 500px; margin: 0 auto;">
                        <div class="progress-bar progress-bar-striped progress-bar-animated bg-danger" role="progressbar" id="searchProgress" style="width: 0%"></div>
                    </div>
                </div>
            </div>
            
            <!-- Results state (initially hidden) -->
            <div id="resultsState" style="display: none;">
                <!-- Results header with metrics -->
                <div class="d-flex justify-content-between align-items-center mb-4 flex-wrap">
                    <h3 id="resultsTitle">"<span id="searchTermDisplay"></span>" के लिए परिणाम</h3>
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
                            <option value="relevance">प्रासंगिकता</option>
                            <option value="date">अपलोड तिथि (नवीनतम)</option>
                            <option value="viewCount">व्यू काउंट (अधिकतम)</option>
                            <option value="rating">रेटिंग (अधिकतम)</option>
                        </select>
                    </div>
                </div>
                
                <!-- Results metrics -->
                <div class="row mb-4">
                    <div class="col-md-3 col-sm-6">
                        <div class="metric-card">
                            <div class="metric-value" id="totalVideosMetric">0</div>
                            <div class="metric-label">कुल वीडियो</div>
                        </div>
                    </div>
                    <div class="col-md-3 col-sm-6">
                        <div class="metric-card">
                            <div class="metric-value" id="totalViewsMetric">0</div>
                            <div class="metric-label">कुल व्यूज़</div>
                        </div>
                    </div>
                    <div class="col-md-3 col-sm-6">
                        <div class="metric-card">
                            <div class="metric-value" id="avgViewsMetric">0</div>
                            <div class="metric-label">औसत व्यूज़</div>
                        </div>
                    </div>
                    <div class="col-md-3 col-sm-6">
                        <div class="metric-card">
                            <div class="metric-value" id="avgEngagementMetric">0%</div>
                            <div class="metric-label">औसत एन्गेजमेंट</div>
                        </div>
                    </div>
                </div>
                
                <!-- Results tabs -->
                <ul class="nav nav-pills mb-4" id="resultsTabs" role="tablist">
                    <li class="nav-item" role="presentation">
                        <button class="nav-link active" id="videos-tab" data-bs-toggle="pill" data-bs-target="#videos-tab-pane" type="button" role="tab">वीडियो</button>
                    </li>
                    <li class="nav-item" role="presentation">
                        <button class="nav-link" id="analytics-tab" data-bs-toggle="pill" data-bs-target="#analytics-tab-pane" type="button" role="tab">विश्लेषण</button>
                    </li>
                    <li class="nav-item" role="presentation">
                        <button class="nav-link" id="trending-tab" data-bs-toggle="pill" data-bs-target="#trending-tab-pane" type="button" role="tab">ट्रेंडिंग विषय</button>
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
                                    <h5 class="mb-3">कीवर्ड द्वारा व्यूज</h5>
                                    <canvas id="keywordViewsChart"></canvas>
                                </div>
                            </div>
                            
                            <!-- Video duration distribution chart -->
                            <div class="col-md-6 mb-4">
                                <div class="analytics-card">
                                    <h5 class="mb-3">वीडियो अवधि वितरण</h5>
                                    <canvas id="durationDistributionChart"></canvas>
                                </div>
                            </div>
                            
                            <!-- Upload time analysis -->
                            <div class="col-md-6 mb-4">
                                <div class="analytics-card">
                                    <h5 class="mb-3">अपलोड समय विश्लेषण</h5>
                                    <canvas id="uploadTimeChart"></canvas>
                                </div>
                            </div>
                            
                            <!-- Engagement vs Views scatter chart -->
                            <div class="col-md-6 mb-4">
                                <div class="analytics-card">
                                    <h5 class="mb-3">एन्गेजमेंट बनाम व्यूज</h5>
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
                                    <h5 class="mb-3">ट्रेंडिंग विषय</h5>
                                    <div id="topicCloud" style="height: 300px; position: relative;"></div>
                                </div>
                            </div>
                            
                            <!-- Top performing topics -->
                            <div class="col-md-6 mb-4">
                                <div class="analytics-card">
                                    <h5 class="mb-3">शीर्ष प्रदर्शन विषय</h5>
                                    <div class="table-responsive">
                                        <table class="table table-striped table-hover" id="topTopicsTable">
                                            <thead>
                                                <tr>
                                                    <th>विषय</th>
                                                    <th>वीडियो</th>
                                                    <th>औसत व्यूज</th>
                                                    <th>एन्गेजमेंट</th>
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
                                    <h5 class="mb-3">हाल ही में ट्रेंडिंग वीडियो</h5>
                                    <div class="table-responsive">
                                        <table class="table table-hover" id="trendingVideosTable">
                                            <thead>
                                                <tr>
                                                    <th>वीडियो</th>
                                                    <th>चैनल</th>
                                                    <th>व्यूज</th>
                                                    <th>प्रकाशित</th>
                                                
