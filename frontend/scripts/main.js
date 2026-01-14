// Main Application Logic for Research Agent
class ResearchAgentApp {
    constructor() {
        this.api = window.ResearchAPI;
        this.ui = window.UIManager;
        this.admin = window.AdminManager;
        this.currentSession = null;
        this.init();
    }

    async init() {
        console.log('🤖 Research Agent Frontend initialized');
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Check initial health status
        await this.checkHealth();
        
        // Load history
        this.ui.renderHistory();
        
        // Start periodic health checks
        this.startHealthChecks();
    }

    setupEventListeners() {
        // Research form submission
        const researchForm = document.getElementById('researchForm');
        researchForm.addEventListener('submit', (e) => this.handleResearchSubmission(e));

        // Export results button
        document.getElementById('exportBtn').addEventListener('click', () => {
            if (this.lastResult) {
                this.ui.exportResults(this.lastResult);
            }
        });

        // Clear history button
        document.getElementById('clearHistoryBtn').addEventListener('click', () => {
            this.ui.clearHistory();
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            // Escape key to cancel/close
            if (e.key === 'Escape') {
                this.ui.hideLoading();
                this.ui.clearResults();
            }
            
            // Ctrl+Shift+A for admin panel
            if (e.ctrlKey && e.shiftKey && e.key === 'A') {
                e.preventDefault();
                this.admin.toggleAdmin();
            }
        });

        // Window beforeunload to warn about ongoing research
        window.addEventListener('beforeunload', (e) => {
            if (this.isResearching) {
                e.preventDefault();
                e.returnValue = 'Research is in progress. Are you sure you want to leave?';
            }
        });
    }

    async handleResearchSubmission(event) {
        event.preventDefault();
        
        const queryInput = document.getElementById('queryInput');
        const researchBtn = document.getElementById('researchBtn');
        
        try {
            // Validate form
            if (!this.ui.validateForm('researchForm')) {
                this.ui.showToast('Please enter a research query', 'error');
                return;
            }

            const query = queryInput.value.trim();
            
            if (query.length < 10) {
                this.ui.showToast('Please enter a more detailed query (at least 10 characters)', 'warning');
                return;
            }

            // Set research state
            this.isResearching = true;
            
            // Generate session ID
            this.currentSession = `session_${Date.now()}`;
            
            // Show loading and progress
            this.ui.setButtonLoading(researchBtn, true);
            this.ui.showLoading('Initiating Research...', 'Preparing to analyze your query');
            this.ui.showProgress(this.currentSession);
            
            // Simulate progress updates (since we don't have real-time updates from backend)
            this.simulateProgress();
            
            // Make API call
            const result = await this.api.submitResearch(query, this.currentSession);
            
            // Handle success
            this.handleResearchSuccess(result, query);
            
        } catch (error) {
            console.error('Research error:', error);
            this.handleResearchError(error);
        } finally {
            // Reset state
            this.isResearching = false;
            this.ui.setButtonLoading(researchBtn, false);
            this.ui.hideLoading();
        }
    }

    simulateProgress() {
        let progress = 10;
        const progressInterval = setInterval(() => {
            if (!this.isResearching) {
                clearInterval(progressInterval);
                return;
            }
            
            progress += Math.random() * 15;
            if (progress > 90) progress = 90;
            
            const statuses = [
                'Analyzing query structure...',
                'Selecting appropriate research tools...',
                'Searching web sources...',
                'Fetching academic papers...',
                'Reading content from URLs...',
                'Processing retrieved information...',
                'Generating comprehensive answer...'
            ];
            
            const statusIndex = Math.floor((progress / 100) * statuses.length);
            const status = statuses[Math.min(statusIndex, statuses.length - 1)];
            
            this.ui.updateProgress(progress, status, this.getSimulatedTools(progress));
            
            if (progress >= 90) {
                clearInterval(progressInterval);
            }
        }, 800);
        
        // Clear interval after 30 seconds max
        setTimeout(() => clearInterval(progressInterval), 30000);
    }

    getSimulatedTools(progress) {
        const allTools = [
            'tavily_search',
            'fetch_url_content', 
            'wikipedia_search',
            'arxiv_search',
            'pubmed_search'
        ];
        
        const toolCount = Math.min(Math.floor(progress / 20), allTools.length);
        return allTools.slice(0, toolCount);
    }

    handleResearchSuccess(result, query) {
        console.log('Research completed:', result);
        
        // Store result for export
        this.lastResult = result;
        
        // Update progress to 100%
        this.ui.updateProgress(100, 'Research completed successfully!', result.tools_used);
        
        // Show results after a brief delay
        setTimeout(() => {
            this.ui.showResults(result);
            
            // Add to history
            this.ui.addToHistory(query, result);
            
            // Show success toast
            this.ui.showToast(
                `Research completed in ${result.processing_time.toFixed(2)}s using ${result.tools_used.length} tools`, 
                'success',
                6000
            );
        }, 1000);
    }

    handleResearchError(error) {
        console.error('Research failed:', error);
        
        this.ui.hideProgress();
        
        // Show specific error messages
        let errorMessage = 'Research failed. Please try again.';
        
        if (error.message.includes('connect')) {
            errorMessage = 'Cannot connect to Research Agent API. Please ensure the backend server is running on port 8001.';
        } else if (error.message.includes('timeout')) {
            errorMessage = 'Research request timed out. The query might be too complex or the server is overloaded.';
        } else if (error.message.includes('500')) {
            errorMessage = 'Internal server error. Please check the server logs for more details.';
        } else {
            errorMessage = `Research failed: ${error.message}`;
        }
        
        this.ui.showToast(errorMessage, 'error', 10000);
    }

    async checkHealth() {
        try {
            this.ui.updateStatus('', 'Checking...');
            
            const health = await this.api.checkHealth();
            
            if (health.status === 'healthy' && health.agent_ready) {
                this.ui.updateStatus('connected', 'Ready');
                console.log('✅ Research Agent is ready:', health);
            } else {
                this.ui.updateStatus('warning', 'Issues detected');
                this.ui.showToast('Research Agent has some issues. Check admin panel for details.', 'warning');
            }

        } catch (error) {
            console.error('❌ Health check failed:', error);
            this.ui.updateStatus('error', 'Disconnected');
            this.ui.showToast(
                'Cannot connect to Research Agent API. Please ensure the backend server is running on port 8001.', 
                'error', 
                10000
            );
        }
    }

    startHealthChecks() {
        // Check health every 30 seconds
        setInterval(() => {
            this.checkHealth();
        }, 30000);
    }

    // Utility methods for external access
    getCurrentSession() {
        return this.currentSession;
    }

    getLastResult() {
        return this.lastResult;
    }

    isCurrentlyResearching() {
        return this.isResearching;
    }

    // Manual research trigger (for testing)
    async triggerResearch(query) {
        document.getElementById('queryInput').value = query;
        document.getElementById('researchForm').dispatchEvent(new Event('submit'));
    }

    // Clear all data
    clearAllData() {
        this.ui.clearResults();
        this.ui.clearHistory();
        this.currentSession = null;
        this.lastResult = null;
        document.getElementById('queryInput').value = '';
        this.ui.showToast('All data cleared', 'info');
    }
}

// Initialize application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.researchApp = new ResearchAgentApp();
});

// Global utility functions for console access
window.research = {
    query: (q) => window.researchApp.triggerResearch(q),
    clear: () => window.researchApp.clearAllData(),
    health: () => window.researchApp.checkHealth(),
    session: () => window.researchApp.getCurrentSession(),
    result: () => window.researchApp.getLastResult(),
    admin: () => window.admin.toggleAdmin()
};

// Console welcome message
console.log(`
🤖 Research Agent Frontend v1.0

Available console commands:
- research.query("your question")  // Submit a research query
- research.clear()                 // Clear all data
- research.health()                // Check system health
- research.session()               // Get current session ID
- research.result()                // Get last research result
- research.admin()                 // Toggle admin panel

Keyboard shortcuts:
- Ctrl+Enter in query box         // Submit research
- Ctrl+Shift+A                    // Toggle admin panel
- Escape                          // Cancel/close overlays
`);

// Performance monitoring
if ('performance' in window) {
    window.addEventListener('load', () => {
        setTimeout(() => {
            const perfData = performance.getEntriesByType('navigation')[0];
            console.log(`⚡ Page loaded in ${perfData.loadEventEnd - perfData.loadEventStart}ms`);
        }, 0);
    });
}