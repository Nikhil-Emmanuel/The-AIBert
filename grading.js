// AI-Assisted Grading System JavaScript

class GradingSystem {
    constructor() {
        this.apiBaseUrl = 'http://localhost:5000';
        this.uploadedFiles = [];
        this.currentReviewItem = null;
        
        this.initializeEventListeners();
        this.checkSystemStatus();
    }

    initializeEventListeners() {
        // Navigation
        document.getElementById('backToDashboard').addEventListener('click', () => {
            window.location.href = 'index.html';
        });

        document.getElementById('analyticsBtn').addEventListener('click', () => {
            this.showSection('analyticsSection');
        });

        document.getElementById('reviewQueueBtn').addEventListener('click', () => {
            this.showSection('reviewQueueSection');
            this.loadReviewQueue();
        });

        // File upload
        const dropZone = document.getElementById('dropZone');
        const fileInput = document.getElementById('fileInput');
        const browseBtn = document.getElementById('browseBtn');

        browseBtn.addEventListener('click', () => fileInput.click());
        fileInput.addEventListener('change', (e) => this.handleFileSelect(e.target.files));

        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('dragover');
        });

        dropZone.addEventListener('dragleave', () => {
            dropZone.classList.remove('dragover');
        });

        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('dragover');
            this.handleFileSelect(e.dataTransfer.files);
        });

        // Manual grading
        document.getElementById('gradeAnswerBtn').addEventListener('click', () => {
            this.gradeManualAnswer();
        });

        // Batch processing
        document.getElementById('processBatchBtn').addEventListener('click', () => {
            this.processBatch();
        });

        document.getElementById('exportResultsBtn').addEventListener('click', () => {
            this.exportResults();
        });

        // Analytics
        document.getElementById('generateReportBtn').addEventListener('click', () => {
            this.generateReport();
        });

        // Review queue
        document.getElementById('refreshQueueBtn').addEventListener('click', () => {
            this.loadReviewQueue();
        });

        // Modal
        document.getElementById('closeModal').addEventListener('click', () => {
            this.closeModal();
        });

        document.getElementById('approveBtn').addEventListener('click', () => {
            this.submitReview('approved');
        });

        document.getElementById('rejectBtn').addEventListener('click', () => {
            this.submitReview('rejected');
        });

        document.getElementById('needsRevisionBtn').addEventListener('click', () => {
            this.submitReview('needs_revision');
        });
    }

    async checkSystemStatus() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/status`);
            const status = await response.json();
            
            if (!status.models_initialized) {
                this.showNotification('System is initializing models. Some features may be limited.', 'warning');
            }
        } catch (error) {
            console.error('Error checking system status:', error);
            this.showNotification('Unable to connect to AI backend', 'error');
        }
    }

    showSection(sectionId) {
        // Hide all sections
        const sections = ['ocrSection', 'manualGradingSection', 'resultsSection', 
                         'batchSection', 'analyticsSection', 'reviewQueueSection'];
        
        sections.forEach(id => {
            const section = document.getElementById(id);
            if (section) section.style.display = 'none';
        });

        // Show selected section
        const targetSection = document.getElementById(sectionId);
        if (targetSection) {
            targetSection.style.display = 'block';
        }
    }

    handleFileSelect(files) {
        const fileArray = Array.from(files);
        const validFiles = fileArray.filter(file => file.type.startsWith('image/'));
        
        if (validFiles.length === 0) {
            this.showNotification('Please select valid image files', 'error');
            return;
        }

        this.uploadedFiles = [...this.uploadedFiles, ...validFiles];
        this.updateFileDisplay();
        
        // Process files immediately for OCR
        this.processOCR(validFiles);
    }

    updateFileDisplay() {
        const dropZone = document.getElementById('dropZone');
        const content = dropZone.querySelector('.drop-zone-content p');
        
        if (this.uploadedFiles.length > 0) {
            content.textContent = `${this.uploadedFiles.length} file(s) selected`;
        } else {
            content.textContent = 'Drag and drop exam scripts here or click to browse';
        }
    }

    async processOCR(files) {
        this.showLoading(true);
        const progressContainer = document.getElementById('uploadProgress');
        const progressFill = document.getElementById('progressFill');
        const progressText = document.getElementById('progressText');
        
        progressContainer.style.display = 'block';
        
        const results = [];
        
        for (let i = 0; i < files.length; i++) {
            const file = files[i];
            const progress = ((i + 1) / files.length) * 100;
            
            progressFill.style.width = `${progress}%`;
            progressText.textContent = `Processing ${file.name}...`;
            
            try {
                const base64 = await this.fileToBase64(file);
                const documentType = document.getElementById('documentType').value;
                
                const response = await fetch(`${this.apiBaseUrl}/ocr/process`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        image: base64,
                        document_type: documentType
                    })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    results.push({
                        filename: file.name,
                        result: result.result
                    });
                } else {
                    console.error('OCR processing failed:', result.error);
                }
                
            } catch (error) {
                console.error('Error processing file:', error);
            }
        }
        
        this.displayOCRResults(results);
        progressContainer.style.display = 'none';
        this.showLoading(false);
    }

    displayOCRResults(results) {
        const resultsSection = document.getElementById('resultsSection');
        const resultsContainer = document.getElementById('gradingResults');
        
        resultsContainer.innerHTML = '<h3>📄 OCR Extraction Results</h3>';
        
        results.forEach(({ filename, result }) => {
            const resultDiv = document.createElement('div');
            resultDiv.className = 'result-item';
            
            let html = `
                <h4>📁 ${filename}</h4>
                <div class="ocr-results">
            `;
            
            if (result.full_text) {
                html += `
                    <div class="ocr-text-region">
                        <div class="region-header">
                            <span class="region-id">Full Document Text</span>
                        </div>
                        <div class="extracted-text">${result.full_text}</div>
                    </div>
                `;
            }
            
            if (result.regions && result.regions.length > 0) {
                html += '<h5>Text Regions:</h5>';
                result.regions.forEach(region => {
                    const confidence = Math.round(region.confidence * 100);
                    html += `
                        <div class="ocr-text-region">
                            <div class="region-header">
                                <span class="region-id">Region ${region.region_id}</span>
                                <span class="confidence-badge">${confidence}% confidence</span>
                            </div>
                            <div class="extracted-text">${region.text}</div>
                        </div>
                    `;
                });
            }
            
            html += '</div>';
            resultDiv.innerHTML = html;
            resultsContainer.appendChild(resultDiv);
        });
        
        resultsSection.style.display = 'block';
    }

    async gradeManualAnswer() {
        const question = document.getElementById('questionInput').value.trim();
        const studentAnswer = document.getElementById('studentAnswerInput').value.trim();
        const correctAnswer = document.getElementById('correctAnswerInput').value.trim();
        const maxScore = parseInt(document.getElementById('maxScoreInput').value) || 100;
        
        if (!question || !studentAnswer || !correctAnswer) {
            this.showNotification('Please fill in all required fields', 'error');
            return;
        }
        
        this.showLoading(true);
        
        try {
            const response = await fetch(`${this.apiBaseUrl}/grading/evaluate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    question,
                    student_answer: studentAnswer,
                    correct_answer: correctAnswer,
                    max_score: maxScore
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.displayGradingResult(result.grading_result);
            } else {
                this.showNotification('Grading failed: ' + result.error, 'error');
            }
            
        } catch (error) {
            console.error('Error grading answer:', error);
            this.showNotification('Error connecting to grading service', 'error');
        }
        
        this.showLoading(false);
    }

    displayGradingResult(result) {
        const resultsSection = document.getElementById('resultsSection');
        const resultsContainer = document.getElementById('gradingResults');
        
        resultsContainer.innerHTML = `
            <h3>🎯 Grading Results</h3>
            <div class="result-item">
                <div class="score-display">
                    ${result.final_score}/${result.max_score} (${result.percentage}%)
                </div>
                
                <div class="breakdown-grid">
                    ${Object.entries(result.breakdown).map(([criterion, data]) => `
                        <div class="breakdown-item">
                            <h4>${criterion.replace(/_/g, ' ')}</h4>
                            <div class="breakdown-score">${data.score}%</div>
                            <small>Weight: ${(data.weight * 100)}%</small>
                        </div>
                    `).join('')}
                </div>
                
                <div class="feedback-section">
                    <h4>📝 Feedback</h4>
                    <div class="feedback-text">${result.feedback}</div>
                </div>
                
                ${result.recommendations ? `
                    <div class="feedback-section">
                        <h4>💡 Recommendations</h4>
                        <ul class="recommendations-list">
                            ${result.recommendations.map(rec => `<li>${rec}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
            </div>
        `;
        
        resultsSection.style.display = 'block';
    }

    async processBatch() {
        if (this.uploadedFiles.length === 0) {
            this.showNotification('No files uploaded for batch processing', 'error');
            return;
        }
        
        this.showNotification('Batch processing started...', 'info');
        // Implementation would process all uploaded files
        // This is a placeholder for the actual batch processing logic
    }

    async exportResults() {
        // Implementation for exporting results
        this.showNotification('Export functionality coming soon', 'info');
    }

    async generateReport() {
        const reportType = document.getElementById('reportType').value;
        const studentId = document.getElementById('studentIdInput').value.trim();
        const examId = document.getElementById('examIdInput').value.trim();
        
        this.showLoading(true);
        
        try {
            // Implementation for generating analytics reports
            // This would call the analytics endpoints
            this.showNotification('Analytics report generation coming soon', 'info');
        } catch (error) {
            console.error('Error generating report:', error);
            this.showNotification('Error generating report', 'error');
        }
        
        this.showLoading(false);
    }

    async loadReviewQueue() {
        this.showLoading(true);
        
        try {
            // Implementation for loading review queue
            // This would call the human verification endpoints
            const queueContainer = document.getElementById('reviewQueue');
            queueContainer.innerHTML = '<p>Review queue functionality coming soon</p>';
        } catch (error) {
            console.error('Error loading review queue:', error);
            this.showNotification('Error loading review queue', 'error');
        }
        
        this.showLoading(false);
    }

    closeModal() {
        document.getElementById('reviewModal').style.display = 'none';
        this.currentReviewItem = null;
    }

    async submitReview(status) {
        // Implementation for submitting human reviews
        this.showNotification('Review submission functionality coming soon', 'info');
        this.closeModal();
    }

    fileToBase64(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.readAsDataURL(file);
            reader.onload = () => resolve(reader.result);
            reader.onerror = error => reject(error);
        });
    }

    showLoading(show) {
        const overlay = document.getElementById('loadingOverlay');
        overlay.style.display = show ? 'flex' : 'none';
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        // Style the notification
        Object.assign(notification.style, {
            position: 'fixed',
            top: '20px',
            right: '20px',
            padding: '15px 20px',
            borderRadius: '8px',
            color: 'white',
            fontWeight: '600',
            zIndex: '9999',
            maxWidth: '400px',
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.2)'
        });
        
        // Set background color based on type
        const colors = {
            info: '#667eea',
            success: '#48bb78',
            warning: '#ed8936',
            error: '#f56565'
        };
        notification.style.backgroundColor = colors[type] || colors.info;
        
        document.body.appendChild(notification);
        
        // Remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 5000);
    }
}

// Initialize the grading system when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new GradingSystem();
});
