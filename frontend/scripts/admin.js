// Admin Panel Management for Research Agent
class AdminManager {
    constructor() {
        this.adminSection = document.getElementById('adminSection');
        this.researchSection = document.getElementById('researchSection');
        
        // Analytics elements
        this.totalQueries = document.getElementById('totalQueries');
        this.avgProcessingTime = document.getElementById('avgProcessingTime');
        this.systemUptime = document.getElementById('systemUptime');
        this.logFileSize = document.getElementById('logFileSize');
        this.toolsChart = document.getElementById('toolsChart');
        this.queriesTable = document.getElementById('queriesTable');
        
        // Logs elements
        this.logsContainer = document.getElementById('logsContainer');
        this.logLinesSelect = document.getElementById('logLinesSelect');
        
        this.setupEventListeners();
        this.isVisible = false;
    }

    setupEventListeners() {
        // Admin toggle
        document.getElementById('adminToggle').addEventListener('click', () => {
            this.toggleAdmin();
        });

        // Back to research
        document.getElementById('backToResearch').addEventListener('click', () => {
            this.hideAdmin();
        });

        // Refresh buttons
        document.getElementById('refreshAnalytics').addEventListener('click', () => {
            this.loadAnalytics();
        });

        document.getElementById('refreshLogs').addEventListener('click', () => {
            this.loadLogs();
        });

        // Log controls
        document.getElementById('downloadLogs').addEventListener('click', () => {
            this.downloadLogs();
        });

        document.getElementById('clearLogs').addEventListener('click', () => {
            this.clearLogs();
        });

        // Log lines selector
        this.logLinesSelect.addEventListener('change', () => {
            this.loadLogs();
        });
    }

    toggleAdmin() {
        if (this.isVisible) {
            this.hideAdmin();
        } else {
            this.showAdmin();
        }
    }

    async showAdmin() {
        this.researchSection.style.display = 'none';
        this.adminSection.style.display = 'block';
        this.isVisible = true;

        // Load initial data
        await this.loadAnalytics();
        await this.loadLogs();

        // Auto-refresh every 30 seconds
        this.startAutoRefresh();
    }

    hideAdmin() {
        this.adminSection.style.display = 'none';
        this.researchSection.style.display = 'block';
        this.isVisible = false;

        // Stop auto-refresh
        this.stopAutoRefresh();
    }

    startAutoRefresh() {
        this.stopAutoRefresh(); // Clear any existing interval
        this.refreshInterval = setInterval(() => {
            if (this.isVisible) {
                this.loadAnalytics();
                this.loadLogs();
            }
        }, 30000); // 30 seconds
    }

    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    }

    async loadAnalytics() {
        try {
            const data = await api.getAnalytics();
            this.renderAnalytics(data);
        } catch (error) {
            console.error('Failed to load analytics:', error);
            ui.showToast('Failed to load analytics', 'error');
        }
    }

    renderAnalytics(data) {
        // Update statistics
        this.totalQueries.textContent = data.total_queries.toLocaleString();
        this.avgProcessingTime.textContent = data.average_processing_time 
            ? `${data.average_processing_time.toFixed(2)}s` 
            : '0s';
        this.systemUptime.textContent = data.uptime || '0s';
        this.logFileSize.textContent = ui.formatBytes(data.log_file_size);

        // Render tools chart
        this.renderToolsChart(data.tools_usage);

        // Render recent queries table
        this.renderQueriesTable(data.recent_queries);
    }

    renderToolsChart(toolsUsage) {
        if (!toolsUsage || Object.keys(toolsUsage).length === 0) {
            this.toolsChart.innerHTML = '<div class="chart-empty">No tool usage data</div>';
            return;
        }

        // Sort tools by usage count
        const sortedTools = Object.entries(toolsUsage)
            .sort(([,a], [,b]) => b - a);

        const maxCount = Math.max(...Object.values(toolsUsage));

        this.toolsChart.innerHTML = sortedTools.map(([tool, count]) => {
            const percentage = (count / maxCount) * 100;
            return `
                <div class="tool-usage-item">
                    <div class="tool-info">
                        <span class="tool-name">${ui.formatToolName(tool)}</span>
                        <div class="tool-bar" style="width: ${percentage}%; background: var(--primary); height: 4px; border-radius: 2px; margin-top: 4px;"></div>
                    </div>
                    <span class="tool-count">${count}</span>
                </div>
            `;
        }).join('');
    }

    renderQueriesTable(recentQueries) {
        if (!recentQueries || recentQueries.length === 0) {
            this.queriesTable.innerHTML = '<div class="table-empty">No recent queries</div>';
            return;
        }

        const tableHTML = `
            <table>
                <thead>
                    <tr>
                        <th>Query</th>
                        <th>Tools Used</th>
                        <th>Processing Time</th>
                        <th>Timestamp</th>
                        <th>Session ID</th>
                    </tr>
                </thead>
                <tbody>
                    ${recentQueries.map(query => `
                        <tr>
                            <td class="query-text" title="${query.query}">${ui.truncateText(query.query, 50)}</td>
                            <td class="tools-used-cell">${query.tools_used.join(', ')}</td>
                            <td>${query.processing_time.toFixed(2)}s</td>
                            <td>${new Date(query.timestamp).toLocaleString()}</td>
                            <td style="font-family: var(--font-mono); font-size: 0.8rem;">${query.session_id}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;

        this.queriesTable.innerHTML = tableHTML;
    }

    async loadLogs() {
        try {
            const lines = parseInt(this.logLinesSelect.value);
            const data = await api.getLogs(lines);
            this.renderLogs(data.logs);
        } catch (error) {
            console.error('Failed to load logs:', error);
            this.logsContainer.innerHTML = '<div class="logs-loading">Failed to load logs</div>';
        }
    }

    renderLogs(logs) {
        if (!logs || logs.length === 0) {
            this.logsContainer.innerHTML = '<div class="logs-loading">No logs available</div>';
            return;
        }

        const logsHTML = logs.map(log => `
            <div class="log-entry">
                <div class="log-timestamp">${log.timestamp}</div>
                <div class="log-level ${log.level}">${log.level}</div>
                <div class="log-message">${this.escapeHtml(log.message)}</div>
            </div>
        `).join('');

        this.logsContainer.innerHTML = logsHTML;

        // Auto-scroll to bottom
        this.logsContainer.scrollTop = this.logsContainer.scrollHeight;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    async downloadLogs() {
        try {
            const downloadBtn = document.getElementById('downloadLogs');
            ui.setButtonLoading(downloadBtn, true);

            await api.downloadLogs();
            ui.showToast('Logs downloaded successfully', 'success');

        } catch (error) {
            console.error('Failed to download logs:', error);
            ui.showToast(`Failed to download logs: ${error.message}`, 'error');
        } finally {
            const downloadBtn = document.getElementById('downloadLogs');
            ui.setButtonLoading(downloadBtn, false);
        }
    }

    async clearLogs() {
        // Confirm action
        const confirmed = confirm(
            'Are you sure you want to clear all logs?\n\n' +
            'This action will backup the current logs and create a new log file.\n' +
            'This cannot be undone.'
        );

        if (!confirmed) return;

        try {
            const clearBtn = document.getElementById('clearLogs');
            ui.setButtonLoading(clearBtn, true);

            const result = await api.clearLogs();
            
            ui.showToast(
                `Logs cleared successfully! Backup saved as: ${result.backup_file}`, 
                'success',
                8000
            );

            // Reload logs
            await this.loadLogs();

        } catch (error) {
            console.error('Failed to clear logs:', error);
            ui.showToast(`Failed to clear logs: ${error.message}`, 'error');
        } finally {
            const clearBtn = document.getElementById('clearLogs');
            ui.setButtonLoading(clearBtn, false);
        }
    }

    // Real-time log monitoring (WebSocket would be better, but this works)
    startLogMonitoring() {
        if (this.logMonitorInterval) return;

        this.logMonitorInterval = setInterval(async () => {
            if (this.isVisible) {
                try {
                    const lines = parseInt(this.logLinesSelect.value);
                    const data = await api.getLogs(lines);
                    
                    // Only update if logs have changed
                    const currentLogCount = this.logsContainer.children.length;
                    if (data.logs.length !== currentLogCount) {
                        this.renderLogs(data.logs);
                    }
                } catch (error) {
                    // Silently fail for real-time monitoring
                    console.warn('Log monitoring failed:', error);
                }
            }
        }, 5000); // Check every 5 seconds
    }

    stopLogMonitoring() {
        if (this.logMonitorInterval) {
            clearInterval(this.logMonitorInterval);
            this.logMonitorInterval = null;
        }
    }

    // Export analytics data
    exportAnalytics(data) {
        const exportData = {
            timestamp: new Date().toISOString(),
            system_stats: {
                total_queries: data.total_queries,
                average_processing_time: data.average_processing_time,
                uptime: data.uptime,
                log_file_size: data.log_file_size
            },
            tools_usage: data.tools_usage,
            recent_queries: data.recent_queries
        };

        const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `research_agent_analytics_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        ui.showToast('Analytics exported successfully', 'success');
    }
}

// Create global admin manager instance
const admin = new AdminManager();

// Export for use in other scripts
window.AdminManager = admin;