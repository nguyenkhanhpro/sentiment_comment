// DOM Elements
const commentInput = document.getElementById('commentInput');
const analyzeBtn = document.getElementById('analyzeBtn');
const loading = document.getElementById('loading');
const result = document.getElementById('result');
const error = document.getElementById('error');
const errorMessage = document.getElementById('errorMessage');
const charCount = document.getElementById('charCount');
const serverStatus = document.getElementById('serverStatus');
const statusDot = document.getElementById('statusDot');
const modelName = document.getElementById('modelName');
const modelAccuracy = document.getElementById('modelAccuracy');
const modelDate = document.getElementById('modelDate');

// Result Elements
const resultLabel = document.getElementById('resultLabel');
const resultBadge = document.getElementById('resultBadge');
const resultIcon = document.getElementById('resultIcon');
const sentimentAvatar = document.getElementById('sentimentAvatar');
const confidence = document.getElementById('confidence');
const confidenceBar = document.getElementById('confidenceBar');
const cleanedText = document.getElementById('cleanedText');
const intensityLevel = document.getElementById('intensityLevel');

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    checkServerStatus();
    
    // Count characters
    commentInput.addEventListener('input', function() {
        charCount.textContent = this.value.length;
    });
    
    // Ctrl+Enter to analyze
    commentInput.addEventListener('keydown', function(e) {
        if (e.ctrlKey && e.key === 'Enter') {
            e.preventDefault();
            analyzeSentiment();
        }
    });
    
    // Analyze button click
    analyzeBtn.addEventListener('click', analyzeSentiment);
    
    // Example cards click
    document.querySelectorAll('.example-card').forEach(card => {
        card.addEventListener('click', function() {
            commentInput.value = this.dataset.text;
            commentInput.dispatchEvent(new Event('input'));
            
            // Add click effect
            this.style.transform = 'scale(0.95)';
            setTimeout(() => {
                this.style.transform = '';
            }, 200);
            
            analyzeSentiment();
        });
    });
    
    // Emoticon items click
    document.querySelectorAll('.emoticon-item').forEach(item => {
        item.addEventListener('click', function() {
            const emoji = this.dataset.emoji;
            const currentText = commentInput.value;
            commentInput.value = currentText + (currentText ? ' ' : '') + emoji;
            commentInput.dispatchEvent(new Event('input'));
            commentInput.focus();
            
            // Add click effect
            this.style.transform = 'scale(0.9)';
            setTimeout(() => {
                this.style.transform = '';
            }, 200);
        });
    });
    
    // Close error button
    document.querySelector('.error-close')?.addEventListener('click', hideError);
});

// Check server status
async function checkServerStatus() {
    try {
        const response = await fetch('/health');
        const data = await response.json();
        
        if (data.status === 'healthy') {
            serverStatus.innerHTML = '<span style="color: #10b981">ĐANG HOẠT ĐỘNG</span>';
            statusDot.style.background = '#10b981';
            
            // Update model info
            if (data.model_info) {
                modelName.textContent = data.model_info.model_type || 'Logistic Regression';
                modelAccuracy.textContent = data.model_info.accuracy || 'N/A';
                modelDate.textContent = data.model_info.date || 'N/A';
                
                // Update training samples in footer
                const trainingSamples = document.getElementById('trainingSamples');
                if (trainingSamples && data.model_info.training_samples) {
                    trainingSamples.textContent = data.model_info.training_samples;
                }
            }
        } else {
            serverStatus.innerHTML = '<span style="color: #ef4444">LỖI HỆ THỐNG</span>';
            statusDot.style.background = '#ef4444';
        }
    } catch (err) {
        serverStatus.innerHTML = '<span style="color: #ef4444">MẤT KẾT NỐI</span>';
        statusDot.style.background = '#ef4444';
    }
}

// UI Functions
function showLoading() {
    loading.style.display = 'block';
    // Reset loading bar animation
    const progressBar = loading.querySelector('.loading-progress');
    if (progressBar) {
        progressBar.style.animation = 'none';
        setTimeout(() => {
            progressBar.style.animation = 'loadingProgress 2s infinite ease-in-out';
        }, 10);
    }
}

function hideLoading() {
    loading.style.display = 'none';
}

function showError(message) {
    errorMessage.textContent = message;
    error.style.display = 'flex';
    
    // Auto hide after 8 seconds
    setTimeout(hideError, 8000);
}

function hideError() {
    error.style.display = 'none';
}

function showResult() {
    result.style.display = 'block';
    
    // Add entrance animation
    result.style.animation = 'none';
    setTimeout(() => {
        result.style.animation = 'resultSlideUp 0.5s ease';
    }, 10);
}

function hideResult() {
    result.style.display = 'none';
}

// Update probability bars with animation
function updateProbability(barId, valueId, percent) {
    const bar = document.getElementById(barId);
    const value = document.getElementById(valueId);
    
    if (bar && value) {
        // Reset for animation
        bar.style.width = '0%';
        bar.style.opacity = '0';
        
        // Animate after a small delay
        setTimeout(() => {
            bar.style.width = percent + '%';
            bar.style.opacity = '1';
            value.textContent = percent.toFixed(1) + '%';
        }, 300);
    }
}

// Update confidence bar
function updateConfidenceBar(percent) {
    if (confidenceBar) {
        confidenceBar.style.width = '0%';
        setTimeout(() => {
            confidenceBar.style.width = percent + '%';
        }, 500);
    }
}

// Update result appearance based on sentiment
function updateResultAppearance(sentiment, confidencePercent) {
    // Update badge
    resultBadge.className = 'result-badge';
    if (sentiment === 2) {
        resultBadge.classList.add('positive');
        resultLabel.textContent = 'TÍCH CỰC';
        intensityLevel.textContent = confidencePercent > 80 ? 'RẤT CAO' : confidencePercent > 60 ? 'CAO' : 'TRUNG BÌNH';
    } else if (sentiment === 1) {
        resultBadge.classList.add('neutral');
        resultLabel.textContent = 'TRUNG TÍNH';
        intensityLevel.textContent = 'TRUNG BÌNH';
    } else if (sentiment === 0) {
        resultBadge.classList.add('negative');
        resultLabel.textContent = 'TIÊU CỰC';
        intensityLevel.textContent = confidencePercent > 80 ? 'RẤT CAO' : confidencePercent > 60 ? 'CAO' : 'TRUNG BÌNH';
    }
    
    // Update avatar
    const avatarCircle = sentimentAvatar.querySelector('.avatar-circle');
    avatarCircle.className = 'avatar-circle';
    if (sentiment === 2) {
        avatarCircle.classList.add('positive');
        resultIcon.className = 'fas fa-smile-beam';
    } else if (sentiment === 1) {
        avatarCircle.classList.add('neutral');
        resultIcon.className = 'fas fa-meh';
    } else if (sentiment === 0) {
        avatarCircle.classList.add('negative');
        resultIcon.className = 'fas fa-frown';
    }
    
    // Add avatar animation
    avatarCircle.style.animation = 'none';
    setTimeout(() => {
        avatarCircle.style.animation = 'brainRotate 3s infinite linear';
    }, 100);
}

// Main analysis function
async function analyzeSentiment() {
    const text = commentInput.value.trim();

    if (!text) {
        showError('⚠️ Vui lòng nhập bình luận để phân tích!');
        return;
    }

    // Reset UI
    hideError();
    hideResult();
    showLoading();
    analyzeBtn.disabled = true;
    analyzeBtn.innerHTML = `
        <div class="btn-content">
            <div class="btn-icon">
                <i class="fas fa-cogs fa-spin"></i>
            </div>
            <div class="btn-text">
                <span class="btn-title">AI ĐANG PHÂN TÍCH</span>
                <span class="btn-subtitle">Vui lòng chờ trong giây lát...</span>
            </div>
            <div class="btn-arrow">
                <i class="fas fa-spinner fa-spin"></i>
            </div>
        </div>
    `;

    try {
        const response = await fetch('/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ text: text })
        });

        const data = await response.json();

        if (!response.ok || !data.success) {
            throw new Error(data.error || '❌ Lỗi không xác định từ hệ thống AI');
        }

        // Success - display result
        displayResult(data);

    } catch (err) {
        showError(err.message || '🔌 Lỗi kết nối với server AI. Vui lòng thử lại!');
    } finally {
        hideLoading();
        analyzeBtn.disabled = false;
        analyzeBtn.innerHTML = `
            <div class="btn-content">
                <div class="btn-icon">
                    <i class="fas fa-magic"></i>
                </div>
                <div class="btn-text">
                    <span class="btn-title">PHÂN TÍCH NGAY</span>
                    <span class="btn-subtitle">AI sẽ phân tích trong 2 giây</span>
                </div>
                <div class="btn-arrow">
                    <i class="fas fa-arrow-right"></i>
                </div>
            </div>
        `;
    }
}

// Display result with animations
function displayResult(data) {
    // Update confidence
    if (data.confidence) {
        confidence.textContent = data.confidence.toFixed(1) + '%';
        updateConfidenceBar(data.confidence);
    }
    
    // Update result appearance
    updateResultAppearance(data.sentiment, data.confidence || 0);
    
    // Update probabilities
    if (data.probabilities_formatted) {
        const positive = parseFloat(data.probabilities_formatted['Tích cực']) || 0;
        const neutral = parseFloat(data.probabilities_formatted['Trung tính']) || 0;
        const negative = parseFloat(data.probabilities_formatted['Tiêu cực']) || 0;
        
        // Animate probability bars with staggered delay
        setTimeout(() => updateProbability('probNegative', 'valNegative', negative), 100);
        setTimeout(() => updateProbability('probNeutral', 'valNeutral', neutral), 300);
        setTimeout(() => updateProbability('probPositive', 'valPositive', positive), 500);
    }
    
    // Update cleaned text with typing effect
    if (data.cleaned_text) {
        const text = data.cleaned_text;
        cleanedText.textContent = '';
        let i = 0;
        const typeWriter = () => {
            if (i < text.length) {
                cleanedText.textContent += text.charAt(i);
                i++;
                setTimeout(typeWriter, 10);
            }
        };
        typeWriter();
    } else {
        cleanedText.textContent = '-';
    }
    
    // Show result with delay for animations to be ready
    setTimeout(() => {
        showResult();
        
        // Smooth scroll to result
        result.scrollIntoView({ 
            behavior: 'smooth', 
            block: 'center'
        });
        
        // Add confetti effect for positive sentiment
        if (data.sentiment === 2 && data.confidence > 80) {
            addConfettiEffect();
        }
    }, 800);
}

// Add confetti effect for positive results
function addConfettiEffect() {
    const colors = ['#6366f1', '#8b5cf6', '#10b981', '#f59e0b', '#ec4899'];
    
    for (let i = 0; i < 50; i++) {
        const confetti = document.createElement('div');
        confetti.style.position = 'fixed';
        confetti.style.width = '10px';
        confetti.style.height = '10px';
        confetti.style.background = colors[Math.floor(Math.random() * colors.length)];
        confetti.style.borderRadius = '50%';
        confetti.style.zIndex = '9999';
        confetti.style.left = Math.random() * 100 + 'vw';
        confetti.style.top = '-20px';
        confetti.style.opacity = '0.8';
        confetti.style.pointerEvents = 'none';
        
        document.body.appendChild(confetti);
        
        // Animation
        const animation = confetti.animate([
            { transform: 'translateY(0) rotate(0deg)', opacity: 1 },
            { transform: `translateY(${window.innerHeight + 100}px) rotate(${Math.random() * 360}deg)`, opacity: 0 }
        ], {
            duration: 2000 + Math.random() * 2000,
            easing: 'cubic-bezier(0.215, 0.610, 0.355, 1)'
        });
        
        // Remove after animation
        animation.onfinish = () => {
            document.body.removeChild(confetti);
        };
    }
}

// Add floating effect to some elements
function addFloatingEffects() {
    // Add floating effect to model cards
    const cards = document.querySelectorAll('.model-card');
    cards.forEach((card, index) => {
        card.style.animationDelay = (index * 0.2) + 's';
    });
    
    // Add hover effects to example cards
    const exampleCards = document.querySelectorAll('.example-card');
    exampleCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            const icon = this.querySelector('.example-icon');
            if (icon) {
                icon.style.transform = 'scale(1.2) rotate(10deg)';
            }
        });
        
        card.addEventListener('mouseleave', function() {
            const icon = this.querySelector('.example-icon');
            if (icon) {
                icon.style.transform = '';
            }
        });
    });
}

// Initialize floating effects
setTimeout(addFloatingEffects, 1000);

// Add keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Alt + C to clear
    if (e.altKey && e.key === 'c') {
        commentInput.value = '';
        commentInput.dispatchEvent(new Event('input'));
        hideError();
        hideResult();
        commentInput.focus();
    }
    
    // Alt + L to focus input
    if (e.altKey && e.key === 'l') {
        commentInput.focus();
    }
    
    // Escape to clear errors/close modals
    if (e.key === 'Escape') {
        hideError();
    }
});