// UI Management for Research Agent
class UIManager {
    constructor() {
        this.loadingOverlay = document.getElementById('loadingOverlay');
        this.loadingTitle = document.getElementById('loadingTitle');
        this.loadingMessage = document.getElementById('loadingMessage');
        this.toastContainer = document.getElementById('toastContainer');
        this.statusDot = document.getElementById('statusDot');
        this.statusText = document.getElementById('statusText');
        
        // Progress tracking
        this.progressSection = document.getElementById('progressSection');
        this.progressFill = document.getElementById('progressFill');
        this.progressStatus = document.getElementById('progressStatus');
        this.toolsList = document.getElementById('toolsList');
        this.sessionId = document.getElementById('sessionId');
        
        // Results
        this.resultsSection = document.getElementById('resultsSection');
        this.answerText = document.getElementById('answerText');
        this.processingTime = document.getElementById('processingTime');
        this.tokenCount = document.getElementById('tokenCount');
        this.toolsSummary = document.getElementById('toolsSummary');
        this.sessionInfo = document.getElementById('sessionInfo');
        
        // History
        this.historyList = document.getElementById('historyList');
        
        // Loading steps
        this.loadingSteps = {
            step1: document.getElementById('step1'),
            step2: document.getElementById('step2'),
            step3: document.getElementById('step3')
        };
        // Floating ask button
        this.floatingAskBtn = document.getElementById('floatingAskBtn');
        
        this.currentStep = 1;
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Character counter for query input
        const queryInput = document.getElementById('queryInput');
        const charCount = document.getElementById('charCount');
        
        queryInput.addEventListener('input', () => {
            const length = queryInput.value.length;
            charCount.textContent = `${length} characters`;
            
            // Auto-resize textarea
            queryInput.style.height = 'auto';
            queryInput.style.height = queryInput.scrollHeight + 'px';
        });

        // Keyboard shortcuts
        queryInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
                e.preventDefault();
                document.getElementById('researchForm').dispatchEvent(new Event('submit'));
            }
        });

        // Floating ask button click
        this.floatingAskBtn.addEventListener('click', () => {
            this.scrollToInput();
        });

        // Scroll listener for floating button visibility
        window.addEventListener('scroll', () => {
            this.handleFloatingButtonVisibility();
        });

        // Initial check for floating button
        this.handleFloatingButtonVisibility();
    }

    // Status Management
    updateStatus(status, text) {
        this.statusDot.className = `status-dot ${status}`;
        this.statusText.textContent = text;
    }

    // Loading Overlay
    showLoading(title = 'Processing Research...', message = 'AI is analyzing your query') {
        this.loadingTitle.textContent = title;
        this.loadingMessage.textContent = message;
        this.loadingOverlay.style.display = 'flex';
        document.body.style.overflow = 'hidden';
        this.currentStep = 1;
        this.updateLoadingStep(1);
    }

    hideLoading() {
        this.loadingOverlay.style.display = 'none';
        document.body.style.overflow = 'auto';
    }

    updateLoadingStep(step) {
        // Remove active class from all steps
        Object.values(this.loadingSteps).forEach(stepEl => {
            stepEl.classList.remove('active');
        });
        
        // Add active class to current step
        if (this.loadingSteps[`step${step}`]) {
            this.loadingSteps[`step${step}`].classList.add('active');
        }
        
        // Update messages based on step
        const messages = {
            1: 'Analyzing your query and selecting appropriate tools...',
            2: 'Using research tools to gather information...',
            3: 'Generating comprehensive answer from collected data...'
        };
        
        if (messages[step]) {
            this.loadingMessage.textContent = messages[step];
        }
    }

    // Progress Tracking
    showProgress(sessionId) {
        this.sessionId.textContent = sessionId;
        this.progressSection.style.display = 'block';
        this.progressFill.style.width = '10%';
        this.progressStatus.textContent = 'Research initiated...';
        this.toolsList.innerHTML = '';
        
        // Scroll to progress section
        this.progressSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    updateProgress(percentage, status, toolsUsed = []) {
        this.progressFill.style.width = `${percentage}%`;
        this.progressStatus.textContent = status;
        
        // Update loading step based on percentage
        if (percentage < 30) {
            this.updateLoadingStep(1);
        } else if (percentage < 70) {
            this.updateLoadingStep(2);
        } else {
            this.updateLoadingStep(3);
        }
        
        // Update tools list
        this.updateToolsList(toolsUsed);
    }

    updateToolsList(toolsUsed) {
        // Clear existing tools
        this.toolsList.innerHTML = '';
        
        // Add tool tags
        toolsUsed.forEach(tool => {
            const toolTag = document.createElement('div');
            toolTag.className = 'tool-tag active';
            toolTag.innerHTML = `<i class="fas fa-cog"></i> ${this.formatToolName(tool)}`;
            this.toolsList.appendChild(toolTag);
        });
    }

    formatToolName(toolName) {
        // Convert snake_case to Title Case
        return toolName
            .split('_')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ');
    }

    hideProgress() {
        this.progressSection.style.display = 'none';
    }

    // Results Display
    showResults(data) {
        // Hide progress
        this.hideProgress();
        
        // Show results section
        this.resultsSection.style.display = 'block';
        
        // Display answer
        this.answerText.innerHTML = this.formatAnswer(data.answer);
        
        // Display metadata
        this.processingTime.textContent = `${data.processing_time.toFixed(2)}s`;
        this.tokenCount.textContent = data.token_estimate ? `~${data.token_estimate} tokens` : 'N/A';
        
        // Tools summary
        this.toolsSummary.innerHTML = `
            <h4><i class="fas fa-tools"></i> Tools Used</h4>
            <div class="tools-list">
                ${data.tools_used.map(tool => 
                    `<span class="tool-tag">${this.formatToolName(tool)}</span>`
                ).join('')}
            </div>
        `;
        
        // Session info
        this.sessionInfo.innerHTML = `
            <h4><i class="fas fa-info-circle"></i> Session Info</h4>
            <div style="font-family: var(--font-mono); font-size: 0.9rem; color: var(--text-muted);">
                <div>Session: ${data.session_id}</div>
                <div>Timestamp: ${new Date(data.timestamp).toLocaleString()}</div>
                <div>Tools: ${data.tools_used.length}</div>
            </div>
        `;
        
        // Scroll to results
        this.resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    formatAnswer(text) {
        if (!text) return 'No answer available';
        
        // Basic markdown-like formatting
        return text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`(.*?)`/g, '<code style="background: var(--bg-tertiary); padding: 2px 4px; border-radius: 3px; font-family: var(--font-mono);">$1</code>')
            .replace(/\n\n/g, '</p><p>')
            .replace(/\n/g, '<br>')
            .replace(/^(.*)$/, '<p>$1</p>');
    }

    clearResults() {
        this.resultsSection.style.display = 'none';
        this.hideProgress();
    }

    // History Management
    addToHistory(query, result) {
        const historyData = this.getHistory();
        
        const historyItem = {
            id: Date.now(),
            query: query,
            timestamp: new Date().toISOString(),
            tools_used: result.tools_used,
            processing_time: result.processing_time,
            session_id: result.session_id
        };
        
        historyData.unshift(historyItem);
        
        // Keep only last 10 items
        if (historyData.length > 10) {
            historyData.splice(10);
        }
        
        localStorage.setItem('research_history', JSON.stringify(historyData));
        this.renderHistory();
    }

    getHistory() {
        try {
            return JSON.parse(localStorage.getItem('research_history') || '[]');
        } catch {
            return [];
        }
    }

    renderHistory() {
        const history = this.getHistory();
        
        if (history.length === 0) {
            this.historyList.innerHTML = '<div class="history-empty">No recent queries</div>';
            return;
        }
        
        this.historyList.innerHTML = history.map(item => `
            <div class="history-item" onclick="ui.loadHistoryItem('${item.id}')">
                <div class="history-query">${this.truncateText(item.query, 80)}</div>
                <div class="history-meta">
                    <span>${new Date(item.timestamp).toLocaleDateString()}</span>
                    <span>${item.tools_used.length} tools • ${item.processing_time.toFixed(1)}s</span>
                </div>
            </div>
        `).join('');
    }

    loadHistoryItem(id) {
        const history = this.getHistory();
        const item = history.find(h => h.id == id);
        
        if (item) {
            document.getElementById('queryInput').value = item.query;
            this.showToast('Query loaded from history', 'info');
        }
    }

    clearHistory() {
        localStorage.removeItem('research_history');
        this.renderHistory();
        this.showToast('History cleared', 'success');
    }

    // Button State Management
    setButtonLoading(button, loading = true) {
        const icon = button.querySelector('i');
        const span = button.querySelector('span');
        
        if (loading) {
            button.disabled = true;
            if (icon) {
                button.setAttribute('data-original-icon', icon.className);
                icon.className = 'fas fa-spinner fa-spin';
            }
            if (span) {
                button.setAttribute('data-original-text', span.textContent);
                span.textContent = 'Processing...';
            }
        } else {
            button.disabled = false;
            if (icon) {
                const originalIcon = button.getAttribute('data-original-icon');
                if (originalIcon) {
                    icon.className = originalIcon;
                }
            }
            if (span) {
                const originalText = button.getAttribute('data-original-text');
                if (originalText) {
                    span.textContent = originalText;
                }
            }
        }
    }

    // Toast Notifications
    showToast(message, type = 'success', duration = 5000) {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        const icons = {
            success: 'check-circle',
            error: 'exclamation-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        
        toast.innerHTML = `
            <div style="display: flex; align-items: center; gap: 8px;">
                <i class="fas fa-${icons[type] || 'info-circle'}"></i>
                <span>${message}</span>
            </div>
        `;

        this.toastContainer.appendChild(toast);

        // Auto remove
        setTimeout(() => {
            if (toast.parentNode) {
                toast.style.animation = 'slideOut 0.3s ease forwards';
                setTimeout(() => {
                    if (toast.parentNode) {
                        this.toastContainer.removeChild(toast);
                    }
                }, 300);
            }
        }, duration);

        // Click to dismiss
        toast.addEventListener('click', () => {
            if (toast.parentNode) {
                this.toastContainer.removeChild(toast);
            }
        });
    }

    // Form Validation
    validateForm(formId) {
        const form = document.getElementById(formId);
        const inputs = form.querySelectorAll('input[required], textarea[required]');
        let isValid = true;

        inputs.forEach(input => {
            if (!input.value.trim()) {
                input.style.borderColor = 'var(--error)';
                isValid = false;
            } else {
                input.style.borderColor = 'var(--border-color)';
            }
        });

        return isValid;
    }

    // Utility Functions
    truncateText(text, maxLength = 100) {
        if (!text || text.length <= maxLength) return text || '';
        return text.slice(0, maxLength) + '...';
    }

    formatBytes(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    formatDuration(seconds) {
        if (seconds < 60) return `${seconds.toFixed(1)}s`;
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = seconds % 60;
        return `${minutes}m ${remainingSeconds.toFixed(0)}s`;
    }

    // Set Example Query
    setExampleQuery(element) {
        const query = element.textContent;
        const queryInput = document.getElementById('queryInput');
        
        // Set the query with a nice animation
        queryInput.style.transform = 'scale(0.98)';
        queryInput.style.transition = 'transform 0.2s ease';
        
        setTimeout(() => {
            queryInput.value = query;
            queryInput.style.transform = 'scale(1)';
            
            // Update character count
            const charCount = document.getElementById('charCount');
            charCount.textContent = `${query.length} characters`;
            
            // Auto-resize textarea
            queryInput.style.height = 'auto';
            queryInput.style.height = queryInput.scrollHeight + 'px';
            
            // Focus on the input
            queryInput.focus();
            
            // Show toast
            this.showToast('Example query loaded! Press Ctrl+Enter to research.', 'info', 3000);
            
            // Scroll to input after setting example
            this.scrollToInput();
        }, 100);
    }

    // Floating Button Management
    scrollToInput() {
        const queryInput = document.getElementById('queryInput');
        queryInput.scrollIntoView({ 
            behavior: 'smooth', 
            block: 'center' 
        });
        
        // Focus after scroll completes
        setTimeout(() => {
            queryInput.focus();
        }, 800);
    }

    handleFloatingButtonVisibility() {
        const queryInput = document.getElementById('queryInput');
        const rect = queryInput.getBoundingClientRect();
        const isVisible = rect.top < window.innerHeight && rect.bottom > 0;
        
        if (isVisible) {
            this.floatingAskBtn.classList.add('hidden');
        } else {
            this.floatingAskBtn.classList.remove('hidden');
        }
    }

    // Export Results
    exportResults(data) {
        const exportData = {
            query: document.getElementById('queryInput').value,
            answer: data.answer,
            session_id: data.session_id,
            tools_used: data.tools_used,
            processing_time: data.processing_time,
            token_estimate: data.token_estimate,
            timestamp: data.timestamp,
            exported_at: new Date().toISOString()
        };

        const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `research_results_${data.session_id}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        this.showToast('Results exported successfully', 'success');
    }
}

// Create global UI manager instance
const ui = new UIManager();

// Export for use in other scripts
window.UIManager = ui;

// Add CSS for slideOut animation
const style = document.createElement('style');
style.textContent = `
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);