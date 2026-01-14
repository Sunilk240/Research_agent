// Research Agent API Client
const API_BASE_URL = 'http://localhost:8001/api';

class ResearchAPI {
    constructor(baseUrl = API_BASE_URL) {
        this.baseUrl = baseUrl;
    }

    // Generic request method
    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };

        try {
            const response = await fetch(url, config);
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            if (error.name === 'TypeError' && error.message.includes('fetch')) {
                throw new Error('Unable to connect to the Research Agent API. Please ensure the backend server is running on port 8001.');
            }
            throw error;
        }
    }

    // Health check
    async checkHealth() {
        return await this.request('/health');
    }

    // Submit research query
    async submitResearch(query, sessionId = null) {
        if (!query || query.trim().length === 0) {
            throw new Error('Query is required and cannot be empty');
        }

        const payload = { query: query.trim() };
        if (sessionId) {
            payload.session_id = sessionId;
        }

        return await this.request('/research', {
            method: 'POST',
            body: JSON.stringify(payload)
        });
    }

    // Get system logs
    async getLogs(lines = 100) {
        return await this.request(`/logs?lines=${lines}`);
    }

    // Get analytics data
    async getAnalytics() {
        return await this.request('/analytics');
    }

    // Download logs
    async downloadLogs() {
        const url = `${this.baseUrl}/download-logs`;
        
        try {
            const response = await fetch(url);
            
            if (!response.ok) {
                throw new Error(`Failed to download logs: ${response.statusText}`);
            }
            
            // Create blob and download
            const blob = await response.blob();
            const downloadUrl = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = downloadUrl;
            a.download = `research_agent_logs_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.log`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(downloadUrl);
            
            return { success: true };
        } catch (error) {
            throw new Error(`Failed to download logs: ${error.message}`);
        }
    }

    // Clear logs
    async clearLogs() {
        return await this.request('/clear-logs', {
            method: 'DELETE'
        });
    }
}

// Create global API instance
const api = new ResearchAPI();

// Export for use in other scripts
window.ResearchAPI = api;