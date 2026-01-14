# Research Agent Frontend

A sophisticated, dark-themed web interface for the Research Agent AI system with comprehensive admin panel and real-time logging.

## 🎯 Features

### **Advanced Research Interface**
- **Natural Language Queries** - Ask any research question in plain English
- **Real-time Progress Tracking** - See which tools are being used as research progresses
- **Comprehensive Results** - Get detailed answers with source attribution and metadata
- **Query History** - Automatic saving and loading of previous research queries
- **Export Functionality** - Download research results as JSON files

### **Professional Admin Dashboard**
- **System Analytics** - Total queries, processing times, uptime statistics
- **Tool Usage Analytics** - Visual charts showing which research tools are used most
- **Recent Query Analysis** - Detailed table of recent research sessions
- **Real-time Log Monitoring** - Live view of system logs with filtering
- **Log Management** - Download, clear, and backup log files

### **Modern UI/UX**
- **Dark Tech Theme** - Professional dark interface with cyan/blue accents
- **Responsive Design** - Works perfectly on desktop, tablet, and mobile
- **Smooth Animations** - 60fps transitions and loading states
- **Real-time Status** - Connection status and health monitoring
- **Toast Notifications** - User-friendly feedback system

## 🚀 Quick Start

### **Prerequisites**
- Research Agent backend running on `http://localhost:8001`
- Modern web browser with JavaScript enabled

### **Installation**
1. **Serve the frontend files**:
   ```bash
   cd Research_agent/frontend
   python -m http.server 3000
   ```

2. **Open in browser**: http://localhost:3000

### **No Build Process Required**
Pure HTML/CSS/JavaScript - no compilation needed!

## 📁 Project Structure

```
frontend/
├── index.html              # Main HTML structure
├── styles/
│   └── main.css            # Dark theme styling
├── scripts/
│   ├── api.js              # Backend API integration
│   ├── ui.js               # UI management and interactions
│   ├── admin.js            # Admin panel functionality
│   └── main.js             # Application logic
└── README.md               # This file
```

## 🎨 Design Features

### **Color Scheme**
- **Primary**: Cyan (#00d4ff) with glow effects
- **Secondary**: Orange (#ff6b35) for accents
- **Background**: Dark gradient (#0a0e1a to #1a1f2e)
- **Cards**: Dark blue (#2d3548) with subtle borders
- **Text**: White primary, muted grays for secondary

### **Typography**
- **Primary Font**: Inter (clean, modern sans-serif)
- **Monospace**: JetBrains Mono (for code, logs, IDs)
- **Responsive sizing** with proper hierarchy

### **Interactive Elements**
- **Glowing buttons** with hover animations
- **Progress bars** with gradient fills
- **Tool tags** that animate when active
- **Status indicators** with pulsing effects

## 🔧 Configuration

### **API Endpoint**
The frontend connects to `http://localhost:8001/api` by default.

To change this, edit `API_BASE_URL` in `scripts/api.js`:

```javascript
const API_BASE_URL = 'https://your-research-api.com/api';
```

### **Customization**
- **Colors**: Modify CSS variables in `:root` section of `main.css`
- **Fonts**: Change font imports in `index.html`
- **Layout**: Adjust grid and flexbox properties
- **Features**: Extend JavaScript classes in scripts folder

## 📱 Usage Guide

### **1. Research Interface**
1. Enter your research question in the text area
2. Press "Research" or use Ctrl+Enter
3. Watch real-time progress as tools are used
4. View comprehensive results with sources
5. Export results or save to history

### **2. Admin Dashboard**
1. Click the gear icon in the header
2. View system statistics and analytics
3. Monitor tool usage patterns
4. Analyze recent query performance
5. View real-time logs and download/clear them

### **3. Keyboard Shortcuts**
- **Ctrl+Enter**: Submit research query
- **Ctrl+Shift+A**: Toggle admin panel
- **Escape**: Cancel operations or close overlays

## 🛠️ Technical Details

### **API Integration**
- RESTful API calls using modern Fetch API
- Comprehensive error handling with user feedback
- Real-time status monitoring
- File download functionality for logs and results

### **State Management**
- Clean separation between API, UI, and admin logic
- Local storage for query history
- Session tracking for research queries
- Real-time progress simulation

### **Performance**
- Minimal dependencies (only Font Awesome for icons)
- Optimized CSS with efficient selectors
- Lazy loading and auto-refresh capabilities
- Smooth 60fps animations

## 🔍 Admin Features

### **System Analytics**
- **Total Queries**: Count of all research requests
- **Average Processing Time**: Performance metrics
- **System Uptime**: How long the backend has been running
- **Log File Size**: Current log file size with auto-formatting

### **Tool Usage Analytics**
- **Visual Charts**: Bar charts showing tool popularity
- **Usage Counts**: Exact numbers for each research tool
- **Trend Analysis**: See which tools are used most frequently

### **Log Management**
- **Real-time Viewing**: Live log updates every 5 seconds
- **Filtering**: Choose number of lines to display (50-500)
- **Download**: Export complete log files with timestamps
- **Clear**: Safely clear logs with automatic backup

### **Query Analysis**
- **Recent Queries Table**: Detailed view of last 10 research sessions
- **Performance Metrics**: Processing time and tool usage per query
- **Session Tracking**: Unique session IDs for debugging

## 🌐 Browser Support

- **Modern Browsers**: Chrome 80+, Firefox 75+, Safari 13+, Edge 80+
- **Features Used**: ES6+, Fetch API, CSS Grid, CSS Variables
- **Responsive**: Mobile-first design with breakpoints

## 🚀 Deployment Options

### **Static Hosting**
- **Netlify**: Drag and drop the frontend folder
- **Vercel**: Connect to Git repository
- **GitHub Pages**: Push to gh-pages branch
- **AWS S3**: Upload to S3 bucket with static hosting

### **Traditional Hosting**
- Upload files to any web server
- No server-side processing required
- Works with Apache, Nginx, IIS, etc.

## 🔒 Security Considerations

- **CORS**: Backend must allow frontend domain
- **HTTPS**: Use HTTPS in production
- **Input Validation**: Client-side validation with server verification
- **XSS Protection**: Proper HTML escaping for log content

## 🎯 Advanced Features

### **Console Commands**
Open browser console and use these commands:
```javascript
research.query("your question")  // Submit research
research.clear()                 // Clear all data
research.health()                // Check system health
research.admin()                 // Toggle admin panel
```

### **Auto-refresh**
- Admin panel auto-refreshes every 30 seconds
- Logs update every 5 seconds when admin panel is open
- Health checks every 30 seconds

### **Export Capabilities**
- **Research Results**: Export as JSON with full metadata
- **System Logs**: Download complete log files
- **Analytics Data**: Export system statistics and usage data

## 🔧 Development

### **Adding New Features**
1. **API calls**: Extend `ResearchAPI` class in `api.js`
2. **UI components**: Add methods to `UIManager` class in `ui.js`
3. **Admin features**: Extend `AdminManager` class in `admin.js`
4. **App logic**: Modify `ResearchAgentApp` class in `main.js`

### **Styling**
- Use CSS variables for consistent theming
- Follow BEM methodology for class naming
- Maintain responsive design principles
- Test on multiple screen sizes

---

**Ready to research!** 🚀 The interface provides everything you need to interact with the Research Agent AI system, monitor its performance, and analyze its usage patterns.

## 🎉 Key Improvements Over NeuroVault

1. **Better Visual Design** - More sophisticated dark theme with professional styling
2. **Real-time Progress** - See research happening in real-time with tool tracking
3. **Comprehensive Admin Panel** - Full system monitoring and analytics
4. **Advanced Logging** - Real-time log viewing with management capabilities
5. **Better UX** - Smoother animations, better feedback, keyboard shortcuts
6. **Export Features** - Download results, logs, and analytics data
7. **Performance Monitoring** - Track system performance and usage patterns