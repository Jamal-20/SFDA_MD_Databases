"""
SFDA Products Database - Complete Working Version
With working graphics, charts, and all features
"""

from flask import Flask, render_template_string, request, jsonify
import pandas as pd
import sqlite3
import os
import socket
import webbrowser
from threading import Timer
import sys
import json

app = Flask(__name__)

#==============================================================================
# HELPER FUNCTIONS
#==============================================================================

def get_resource_path(relative_path):
    """Get absolute path to resource"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def get_database_path():
    """Get database path"""
    possible_paths = [
        'sfda_products.db',
        os.path.join(os.path.dirname(sys.executable), 'sfda_products.db') if getattr(sys, 'frozen', False) else 'sfda_products.db',
        get_resource_path('sfda_products.db')
    ]
    
    for path in possible_paths:
        if path and os.path.exists(path):
            return path
    return 'sfda_products.db'

def get_excel_path():
    """Get Excel file path"""
    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(sys.executable)
        excel_path = os.path.join(exe_dir, 'sfda_products.xlsx')
        if os.path.exists(excel_path):
            return excel_path
    return get_resource_path('sfda_products.xlsx')

def get_local_ip():
    """Get local IP address"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def load_database():
    """Load or verify database"""
    db_path = get_database_path()
    
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            count = pd.read_sql_query("SELECT COUNT(*) as count FROM products", conn)['count'][0]
            conn.close()
            print(f"✅ Database found with {count:,} products")
            return True
        except:
            pass
    
    excel_path = get_excel_path()
    if os.path.exists(excel_path):
        print("📂 Creating database from Excel...")
        try:
            df = pd.read_excel(excel_path)
            conn = sqlite3.connect(db_path)
            df.to_sql('products', conn, if_exists='replace', index=False)
            conn.close()
            print(f"✅ Created database with {len(df):,} products")
            return True
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    else:
        print(f"❌ Excel file not found")
        return False

#==============================================================================
# HTML TEMPLATE - COMPLETE WITH WORKING GRAPHICS
#==============================================================================

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>SFDA Products Database</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        /* Header */
        .header {
            background: white;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 25px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
        }
        .header h1 {
            color: #333;
            font-size: 2em;
        }
        .header p {
            color: #666;
            margin-top: 5px;
        }
        .developer-name {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 10px 20px;
            border-radius: 10px;
            color: white;
            font-weight: bold;
        }
        
        /* Stats Cards */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 25px;
        }
        .stat-card {
            background: white;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            text-align: center;
            transition: transform 0.3s ease;
        }
        .stat-card:hover {
            transform: translateY(-5px);
        }
        .stat-value {
            font-size: 2.2em;
            font-weight: bold;
            color: #667eea;
            margin: 10px 0;
        }
        .stat-label {
            color: #666;
            font-size: 0.9em;
            text-transform: uppercase;
        }
        
        /* Charts */
        .charts-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 25px;
            margin-bottom: 25px;
        }
        .chart-card {
            background: white;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        .chart-title {
            font-size: 1.2em;
            margin-bottom: 15px;
            color: #333;
            font-weight: bold;
        }
        .chart-container {
            height: 300px;
            position: relative;
        }
        
        /* Search Section */
        .search-section {
            background: white;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 25px;
        }
        .search-box {
            display: flex;
            gap: 10px;
            margin-top: 15px;
            flex-wrap: wrap;
        }
        .search-input {
            flex: 1;
            padding: 12px 15px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 16px;
            min-width: 250px;
        }
        .search-input:focus {
            outline: none;
            border-color: #667eea;
        }
        .search-field {
            padding: 12px 20px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 16px;
            background: white;
            min-width: 150px;
        }
        .search-btn {
            padding: 12px 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
        }
        .search-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102,126,234,0.4);
        }
        
        /* Filters */
        .filters-section {
            background: white;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 25px;
        }
        .filters-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }
        .filter-item {
            display: flex;
            flex-direction: column;
            gap: 5px;
        }
        .filter-item select {
            padding: 10px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            background: white;
        }
        .apply-filters-btn {
            padding: 10px 20px;
            background: #28a745;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            margin-top: 15px;
        }
        .apply-filters-btn:hover {
            background: #218838;
        }
        
        /* Results */
        .results-section {
            background: white;
            border-radius: 15px;
            padding: 25px;
        }
        .results-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }
        .results-count {
            font-size: 16px;
            color: #667eea;
            font-weight: bold;
        }
        .info-box {
            background: #e8f0fe;
            padding: 10px 15px;
            border-radius: 8px;
            margin-bottom: 15px;
            color: #1a73e8;
            font-size: 14px;
            text-align: center;
        }
        
        /* Table */
        .table-container {
            overflow-x: auto;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px;
            text-align: left;
        }
        td {
            padding: 10px 12px;
            border-bottom: 1px solid #e0e0e0;
        }
        tr:hover { background: #f5f5f5; }
        
        /* Status Badges */
        .status-badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
        }
        .status-active { background: #d4edda; color: #155724; }
        .status-inactive { background: #f8d7da; color: #721c24; }
        .status-pending { background: #fff3cd; color: #856404; }
        
        /* Loading */
        .loading {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(255,255,255,0.9);
            display: none;
            justify-content: center;
            align-items: center;
            z-index: 9999;
        }
        .loading.show { display: flex; }
        .loading-spinner {
            border: 5px solid #f3f3f3;
            border-top: 5px solid #667eea;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
        }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        
        /* Pagination */
        .pagination {
            display: flex;
            justify-content: center;
            gap: 5px;
            margin-top: 20px;
            flex-wrap: wrap;
        }
        .page-btn {
            padding: 8px 12px;
            border: 1px solid #e0e0e0;
            background: white;
            border-radius: 5px;
            cursor: pointer;
        }
        .page-btn:hover {
            background: #667eea;
            color: white;
        }
        .page-btn.active {
            background: #667eea;
            color: white;
            border-color: #667eea;
        }
        
        /* Footer */
        .footer {
            margin-top: 30px;
        }
        .network-info {
            text-align: center;
            background: #f5f5f5;
            padding: 10px;
            border-radius: 8px;
            color: #666;
            font-size: 12px;
            margin-bottom: 15px;
        }
        .signature {
            text-align: center;
            padding: 15px;
            background: white;
            border-radius: 10px;
        }
        .signature-text {
            color: #667eea;
            font-size: 12px;
            margin-bottom: 8px;
        }
        .social-links a {
            color: #333;
            text-decoration: none;
            margin: 0 8px;
            font-size: 12px;
        }
        .social-links a:hover {
            color: #667eea;
        }
        
        @media (max-width: 768px) {
            .header { flex-direction: column; text-align: center; gap: 15px; }
            .stats-grid { grid-template-columns: 1fr 1fr; }
            .charts-grid { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header with Developer Name -->
        <div class="header">
            <div>
                <h1>🏥 SFDA Products Database</h1>
                <p>Saudi Food and Drug Authority - Classified Products</p>
            </div>
            <div class="developer-name">
                👨‍💻 Developed by <strong>JAMALUDDIN | R&D | MarketAccess</strong>
            </div>
        </div>

        <!-- Stats Cards -->
        <div class="stats-grid" id="statsCards">
            <div class="stat-card">
                <div class="stat-value" id="totalProducts">-</div>
                <div class="stat-label">Total Products</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="totalClassifications">-</div>
                <div class="stat-label">Classifications</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="totalManufacturers">-</div>
                <div class="stat-label">Manufacturers</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="activeProducts">-</div>
                <div class="stat-label">Active Products</div>
            </div>
        </div>

        <!-- Charts -->
        <div class="charts-grid">
            <div class="chart-card">
                <div class="chart-title">📊 Products by Classification</div>
                <div class="chart-container">
                    <canvas id="classificationChart"></canvas>
                </div>
            </div>
            <div class="chart-card">
                <div class="chart-title">📈 Products by Status</div>
                <div class="chart-container">
                    <canvas id="statusChart"></canvas>
                </div>
            </div>
        </div>

        <!-- Search Section -->
        <div class="search-section">
            <h3>🔍 Search Products</h3>
            <div class="search-box">
                <input type="text" class="search-input" id="searchInput" placeholder="Enter SN, brand, classification, manufacturer, or status...">
                <select class="search-field" id="searchField">
                    <option value="all">All Fields</option>
                    <option value="SN">SN</option>
                    <option value="Brand Name">Brand Name</option>
                    <option value="Classification">Classification</option>
                    <option value="Manufacturer Name">Manufacturer</option>
                    <option value="Status">Status</option>
                </select>
                <button class="search-btn" onclick="search()">Search</button>
            </div>
        </div>

        <!-- Filters -->
        <div class="filters-section">
            <h3>⚙️ Advanced Filters</h3>
            <div class="filters-grid">
                <div class="filter-item">
                    <label>Classification:</label>
                    <select id="filterClassification">
                        <option value="">All Classifications</option>
                    </select>
                </div>
                <div class="filter-item">
                    <label>Manufacturer:</label>
                    <select id="filterManufacturer">
                        <option value="">All Manufacturers</option>
                    </select>
                </div>
                <div class="filter-item">
                    <label>Status:</label>
                    <select id="filterStatus">
                        <option value="">All Statuses</option>
                    </select>
                </div>
            </div>
            <button class="apply-filters-btn" onclick="applyFilters()">Apply Filters</button>
        </div>

        <!-- Results -->
        <div class="results-section">
            <div class="results-header">
                <span class="results-count" id="resultsCount">Loading products...</span>
            </div>
            <div class="info-box">
                💡 Tip: Use the search box above to find specific products. You can search by SN, brand name, classification, manufacturer, or status.
            </div>
            <div class="table-container">
                <div id="results">Loading...</div>
            </div>
            <div class="pagination" id="pagination"></div>
        </div>

        <!-- Footer with Network Info and Signature -->
        <div class="footer">
            <div class="network-info" id="networkInfo">
                Loading network info...
            </div>
            <div class="signature">
                <div class="signature-text">
                    ⚕️ SFDA Classified Products Database
                </div>
                <div class="social-links">
                    <a href="https://github.com/Jamal-20" target="_blank">📦 GitHub</a>
                    |
                    <a href="https://www.linkedin.com/in/jamaluddin-microbiology-qa" target="_blank">🔗 LinkedIn</a>
                </div>
            </div>
        </div>
    </div>

    <!-- Loading -->
    <div class="loading" id="loading">
        <div class="loading-spinner"></div>
    </div>

    <script>
        let currentResults = [];
        let currentPage = 1;
        let totalPages = 1;
        let classificationChart = null;
        let statusChart = null;

        window.onload = function() {
            loadNetworkInfo();
            loadStats();
            loadFilters();
            loadAllProducts();
            loadCharts();
        };

        function showLoading() {
            document.getElementById('loading').classList.add('show');
        }

        function hideLoading() {
            document.getElementById('loading').classList.remove('show');
        }

        async function loadNetworkInfo() {
            try {
                const response = await fetch('/api/network/info');
                const data = await response.json();
                document.getElementById('networkInfo').innerHTML = 
                    `🌐 Network Access: ${data.network_url} &nbsp;|&nbsp; 📱 Local Access: ${data.local_url}`;
            } catch (error) {
                document.getElementById('networkInfo').innerHTML = 'Network info unavailable';
            }
        }

        async function loadStats() {
            try {
                const response = await fetch('/api/stats');
                const data = await response.json();
                document.getElementById('totalProducts').textContent = data.total.toLocaleString();
                document.getElementById('totalClassifications').textContent = data.classification_count;
                document.getElementById('totalManufacturers').textContent = data.manufacturer_count;
                document.getElementById('activeProducts').textContent = data.active_count.toLocaleString();
            } catch (error) {
                console.error('Error loading stats:', error);
            }
        }

        async function loadCharts() {
            try {
                const response = await fetch('/api/charts/data');
                const data = await response.json();
                
                // Classification Chart
                const classCtx = document.getElementById('classificationChart').getContext('2d');
                if (classificationChart) classificationChart.destroy();
                classificationChart = new Chart(classCtx, {
                    type: 'pie',
                    data: {
                        labels: data.classifications.map(c => c.Classification),
                        datasets: [{
                            data: data.classifications.map(c => c.count),
                            backgroundColor: ['#667eea', '#764ba2', '#28a745', '#ffc107', '#17a2b8', '#dc3545', '#fd7e14', '#6c757d']
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: true,
                        plugins: { legend: { position: 'right', labels: { boxWidth: 10, font: { size: 10 } } } }
                    }
                });
                
                // Status Chart
                const statusCtx = document.getElementById('statusChart').getContext('2d');
                if (statusChart) statusChart.destroy();
                statusChart = new Chart(statusCtx, {
                    type: 'bar',
                    data: {
                        labels: data.statuses.map(s => s.Status),
                        datasets: [{
                            label: 'Number of Products',
                            data: data.statuses.map(s => s.count),
                            backgroundColor: 'rgba(102, 126, 234, 0.6)',
                            borderColor: '#667eea',
                            borderWidth: 1
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: true,
                        scales: { y: { beginAtZero: true, grid: { display: false } } }
                    }
                });
            } catch (error) {
                console.error('Error loading charts:', error);
            }
        }

        async function loadFilters() {
            try {
                const response = await fetch('/api/filters');
                const data = await response.json();
                
                const classSelect = document.getElementById('filterClassification');
                data.classifications.forEach(c => {
                    if (c) {
                        const option = document.createElement('option');
                        option.value = c;
                        option.textContent = c;
                        classSelect.appendChild(option);
                    }
                });
                
                const manSelect = document.getElementById('filterManufacturer');
                data.manufacturers.slice(0, 100).forEach(m => {
                    if (m) {
                        const option = document.createElement('option');
                        option.value = m;
                        option.textContent = m;
                        manSelect.appendChild(option);
                    }
                });
                
                const statusSelect = document.getElementById('filterStatus');
                data.statuses.forEach(s => {
                    if (s) {
                        const option = document.createElement('option');
                        option.value = s;
                        option.textContent = s;
                        statusSelect.appendChild(option);
                    }
                });
            } catch (error) {
                console.error('Error loading filters:', error);
            }
        }

        async function loadAllProducts() {
            showLoading();
            try {
                const response = await fetch('/api/products/all');
                const data = await response.json();
                currentResults = data.products;
                displayResults();
                document.getElementById('resultsCount').innerHTML = `Showing ${data.products.length} of ${data.total.toLocaleString()} products`;
            } catch (error) {
                document.getElementById('results').innerHTML = 'Error loading products';
            } finally {
                hideLoading();
            }
        }

        async function search(page = 1) {
            const term = document.getElementById('searchInput').value;
            const field = document.getElementById('searchField').value;
            
            if (!term) {
                loadAllProducts();
                return;
            }
            
            showLoading();
            try {
                const response = await fetch(`/api/search?term=${encodeURIComponent(term)}&field=${encodeURIComponent(field)}&page=${page}`);
                const data = await response.json();
                
                currentResults = data.results;
                totalPages = data.total_pages;
                currentPage = data.page;
                
                displayResults();
                document.getElementById('resultsCount').innerHTML = `Found ${data.total_count} results (Page ${currentPage}/${totalPages})`;
            } catch (error) {
                console.error('Search error:', error);
            } finally {
                hideLoading();
            }
        }

        async function applyFilters() {
            const classification = document.getElementById('filterClassification').value;
            const manufacturer = document.getElementById('filterManufacturer').value;
            const status = document.getElementById('filterStatus').value;
            
            showLoading();
            try {
                const response = await fetch(`/api/filter?classification=${encodeURIComponent(classification)}&manufacturer=${encodeURIComponent(manufacturer)}&status=${encodeURIComponent(status)}`);
                const data = await response.json();
                
                currentResults = data.results;
                displayResults();
                document.getElementById('resultsCount').innerHTML = `Found ${data.total} products`;
            } catch (error) {
                console.error('Filter error:', error);
            } finally {
                hideLoading();
            }
        }

        function displayResults() {
            if (currentResults.length === 0) {
                document.getElementById('results').innerHTML = '<p style="text-align: center; padding: 40px;">No products found</p>';
                document.getElementById('pagination').innerHTML = '';
                return;
            }
            
            let html = '<table><thead><tr>';
            html += '<th>SN</th><th>Brand Name</th><th>Classification</th><th>Manufacturer</th><th>Status</th>';
            html += '</tr></thead><tbody>';
            
            currentResults.forEach(item => {
                let statusClass = 'status-badge';
                if (item.Status && item.Status.toLowerCase().includes('active')) statusClass += ' status-active';
                else if (item.Status && item.Status.toLowerCase().includes('inactive')) statusClass += ' status-inactive';
                else if (item.Status && item.Status.toLowerCase().includes('pending')) statusClass += ' status-pending';
                
                html += '<tr>';
                html += `<td>${item.SN || '-'}</td>`;
                html += `<td>${item['Brand Name'] || '-'}</td>`;
                html += `<td>${item.Classification || '-'}</td>`;
                html += `<td>${item['Manufacturer Name'] || '-'}</td>`;
                html += `<td><span class="${statusClass}">${item.Status || '-'}</span></td>`;
                html += '</tr>';
            });
            
            html += '</tbody></table>';
            document.getElementById('results').innerHTML = html;
            
            if (totalPages > 1) {
                let pageHtml = '';
                for (let i = 1; i <= totalPages && i <= 10; i++) {
                    pageHtml += `<button class="page-btn ${i === currentPage ? 'active' : ''}" onclick="search(${i})">${i}</button>`;
                }
                document.getElementById('pagination').innerHTML = pageHtml;
            }
        }

        document.getElementById('searchInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') search();
        });
    </script>
</body>
</html>
'''

#==============================================================================
# FLASK ROUTES
#==============================================================================

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/network/info')
def network_info():
    ip = get_local_ip()
    return jsonify({
        'local_url': f'http://127.0.0.1:5000',
        'network_url': f'http://{ip}:5000'
    })

@app.route('/api/stats')
def get_stats():
    db_path = get_database_path()
    conn = sqlite3.connect(db_path)
    
    total = pd.read_sql_query("SELECT COUNT(*) as count FROM products", conn)['count'][0]
    class_count = pd.read_sql_query("SELECT COUNT(DISTINCT Classification) as count FROM products", conn)['count'][0]
    man_count = pd.read_sql_query('SELECT COUNT(DISTINCT "Manufacturer Name") as count FROM products', conn)['count'][0]
    active = pd.read_sql_query("SELECT COUNT(*) as count FROM products WHERE Status LIKE '%Active%'", conn)['count'][0]
    
    conn.close()
    
    return jsonify({
        'total': int(total),
        'classification_count': int(class_count),
        'manufacturer_count': int(man_count),
        'active_count': int(active)
    })

@app.route('/api/charts/data')
def chart_data():
    db_path = get_database_path()
    conn = sqlite3.connect(db_path)
    
    class_data = pd.read_sql_query("""
        SELECT Classification, COUNT(*) as count 
        FROM products 
        WHERE Classification IS NOT NULL 
        GROUP BY Classification 
        ORDER BY count DESC 
        LIMIT 8
    """, conn)
    
    status_data = pd.read_sql_query("""
        SELECT Status, COUNT(*) as count 
        FROM products 
        WHERE Status IS NOT NULL 
        GROUP BY Status 
        ORDER BY count DESC
    """, conn)
    
    conn.close()
    
    return jsonify({
        'classifications': class_data.to_dict('records'),
        'statuses': status_data.to_dict('records')
    })

@app.route('/api/filters')
def get_filters():
    db_path = get_database_path()
    conn = sqlite3.connect(db_path)
    
    classifications = pd.read_sql_query("SELECT DISTINCT Classification FROM products WHERE Classification IS NOT NULL ORDER BY Classification", conn)
    manufacturers = pd.read_sql_query('SELECT DISTINCT "Manufacturer Name" FROM products WHERE "Manufacturer Name" IS NOT NULL ORDER BY "Manufacturer Name"', conn)
    statuses = pd.read_sql_query("SELECT DISTINCT Status FROM products WHERE Status IS NOT NULL ORDER BY Status", conn)
    
    conn.close()
    
    return jsonify({
        'classifications': classifications['Classification'].tolist(),
        'manufacturers': manufacturers['Manufacturer Name'].tolist(),
        'statuses': statuses['Status'].tolist()
    })

@app.route('/api/products/all')
def get_all_products():
    db_path = get_database_path()
    conn = sqlite3.connect(db_path)
    
    total = pd.read_sql_query("SELECT COUNT(*) as count FROM products", conn)['count'][0]
    df = pd.read_sql_query("SELECT * FROM products LIMIT 500", conn)
    
    conn.close()
    
    return jsonify({
        'products': df.to_dict('records'),
        'total': int(total)
    })

@app.route('/api/search')
def search_products():
    term = request.args.get('term', '')
    field = request.args.get('field', 'all')
    page = int(request.args.get('page', 1))
    per_page = 50
    
    db_path = get_database_path()
    conn = sqlite3.connect(db_path)
    
    if field == 'all':
        query = """
            SELECT * FROM products 
            WHERE SN LIKE ? OR "Brand Name" LIKE ? OR 
                  Classification LIKE ? OR "Manufacturer Name" LIKE ? OR Status LIKE ?
            LIMIT ? OFFSET ?
        """
        count_query = """
            SELECT COUNT(*) as count FROM products 
            WHERE SN LIKE ? OR "Brand Name" LIKE ? OR 
                  Classification LIKE ? OR "Manufacturer Name" LIKE ? OR Status LIKE ?
        """
        params = [f'%{term}%'] * 5
        data_params = params + [per_page, (page-1)*per_page]
    else:
        query = f'SELECT * FROM products WHERE "{field}" LIKE ? LIMIT ? OFFSET ?'
        count_query = f'SELECT COUNT(*) as count FROM products WHERE "{field}" LIKE ?'
        params = [f'%{term}%']
        data_params = params + [per_page, (page-1)*per_page]
    
    count_df = pd.read_sql_query(count_query, conn, params=params)
    total_count = int(count_df['count'].iloc[0]) if not count_df.empty else 0
    
    df = pd.read_sql_query(query, conn, params=data_params)
    conn.close()
    
    return jsonify({
        'results': df.to_dict('records'),
        'total_count': total_count,
        'page': page,
        'total_pages': (total_count + per_page - 1) // per_page if total_count > 0 else 1
    })

@app.route('/api/filter')
def filter_products():
    classification = request.args.get('classification', '')
    manufacturer = request.args.get('manufacturer', '')
    status = request.args.get('status', '')
    
    db_path = get_database_path()
    conn = sqlite3.connect(db_path)
    
    conditions = []
    params = []
    
    if classification:
        conditions.append('Classification = ?')
        params.append(classification)
    if manufacturer:
        conditions.append('"Manufacturer Name" = ?')
        params.append(manufacturer)
    if status:
        conditions.append('Status = ?')
        params.append(status)
    
    if conditions:
        query = 'SELECT * FROM products WHERE ' + ' AND '.join(conditions) + ' LIMIT 1000'
        df = pd.read_sql_query(query, conn, params=params)
    else:
        df = pd.read_sql_query("SELECT * FROM products LIMIT 1000", conn)
    
    conn.close()
    
    return jsonify({
        'results': df.to_dict('records'),
        'total': len(df)
    })

#==============================================================================
# MAIN
#==============================================================================

def open_browser():
    webbrowser.open_new('http://127.0.0.1:5000')

if __name__ == '__main__':
    print("="*60)
    print("🚀 SFDA Products Database")
    print("="*60)
    
    if load_database():
        ip = get_local_ip()
        print(f"\n📱 Local: http://127.0.0.1:5000")
        print(f"🌐 Network: http://{ip}:5000")
        print("\n⏱️  Opening browser...")
        print("="*60)
        
        Timer(1.5, open_browser).start()
        app.run(host='0.0.0.0', port=5000, debug=False)
    else:
        print("\n❌ Failed to load database")
        print("Please make sure 'sfda_products.xlsx' is in the same folder")
        input("\nPress Enter to exit...")