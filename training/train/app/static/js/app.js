// DOM Elements
const commentInput = document.getElementById('commentInput');
const analyzeBtn = document.getElementById('analyzeBtn');
const loading = document.getElementById('loading');
const result = document.getElementById('result');
const error = document.getElementById('error');
const errorMessage = document.getElementById('errorMessage');
const charCount = document.getElementById('charCount');
const emojiCounter = document.getElementById('emojiCounter');
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
const processingTime = document.getElementById('processingTime');
const emojiImpact = document.getElementById('emojiImpact');

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    console.log("AI Sentiment Analyzer initialized");
    checkServerStatus();
    
    // Count characters and emojis
    commentInput.addEventListener('input', function() {
        const text = this.value;
        charCount.textContent = text.length;
        
        // Count emojis
        const emojiCount = countEmojis(text);
        emojiCounter.textContent = emojiCount + ' emoji';
        
        // Update color based on length
        if (text.length > 500) {
            charCount.style.color = '#ff4757';
        } else if (text.length > 300) {
            charCount.style.color = '#ffa502';
        } else {
            charCount.style.color = '#2ed573';
        }
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
    
    // Close error button
    document.querySelector('.error-close')?.addEventListener('click', hideError);
    
    // Emoji guide click
    document.querySelectorAll('.guide-emoji-item').forEach(item => {
        item.addEventListener('click', function() {
            const emoji = this.getAttribute('data-emoji');
            addEmojiToInput(emoji);
        });
    });
    
    // Shortcut hint top click
    document.querySelector('.shortcut-hint-top')?.addEventListener('click', showShortcuts);
    
    // Shortcut watermark click
    document.querySelector('.shortcuts-watermark')?.addEventListener('click', showShortcuts);
    
    // Initialize floating effects
    setTimeout(addFloatingEffects, 1000);
    
    // Auto focus on input
    setTimeout(() => {
        commentInput.focus();
    }, 500);
});

// ========== KEYBOARD SHORTCUTS FUNCTIONS ==========

// Hiển thị modal phím tắt
function showShortcuts() {
    const modal = document.getElementById('shortcutsModal');
    if (modal) {
        modal.style.display = 'flex';
        document.body.style.overflow = 'hidden';
        
        // Animation
        setTimeout(() => {
            modal.style.opacity = '1';
            modal.querySelector('.shortcuts-modal-content').style.transform = 'translateY(0)';
        }, 10);
        
        console.log("Shortcuts modal opened");
    }
}

// Ẩn modal phím tắt
function hideShortcuts() {
    const modal = document.getElementById('shortcutsModal');
    if (modal) {
        modal.style.opacity = '0';
        modal.querySelector('.shortcuts-modal-content').style.transform = 'translateY(30px)';
        
        setTimeout(() => {
            modal.style.display = 'none';
            document.body.style.overflow = '';
        }, 300);
    }
}

// Đóng modal khi click ra ngoài
document.addEventListener('click', (e) => {
    const modal = document.getElementById('shortcutsModal');
    if (modal && modal.style.display === 'flex' && e.target === modal) {
        hideShortcuts();
    }
});

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Alt + C to clear
    if (e.altKey && e.key === 'c') {
        e.preventDefault();
        commentInput.value = '';
        commentInput.dispatchEvent(new Event('input'));
        hideError();
        hideResult();
        commentInput.focus();
        console.log("Cleared input with Alt+C");
    }
    
    // Alt + L to focus input
    if (e.altKey && e.key === 'l') {
        e.preventDefault();
        commentInput.focus();
        console.log("Focused input with Alt+L");
    }
    
    // Escape to clear errors/close modals
    if (e.key === 'Escape') {
        hideError();
        hideShortcuts();
    }
    
    // Alt + E to add random emoji
    if (e.altKey && e.key === 'e') {
        e.preventDefault();
        const emojis = ['😊', '❤️', '😂', '😍', '👍', '👏', '🎉', '😭', '😡', '👎'];
        const randomEmoji = emojis[Math.floor(Math.random() * emojis.length)];
        addEmojiToInput(randomEmoji);
        console.log("Added random emoji with Alt+E:", randomEmoji);
    }
    
    // ? to show shortcuts
    if (e.key === '?' && !e.ctrlKey && !e.shiftKey) {
        e.preventDefault();
        showShortcuts();
    }
    
    // Alt + S to simulate server check
    if (e.altKey && e.key === 's') {
        e.preventDefault();
        checkServerStatus();
        console.log("Manual server check with Alt+S");
    }
});

// Function to add emoji to input
function addEmojiToInput(emoji) {
    const input = commentInput;
    const cursorPos = input.selectionStart;
    const text = input.value;
    
    // Insert emoji at cursor position
    const newText = text.substring(0, cursorPos) + emoji + text.substring(cursorPos);
    input.value = newText;
    
    // Update cursor position
    input.selectionStart = input.selectionEnd = cursorPos + emoji.length;
    
    // Trigger input event to update counters
    input.dispatchEvent(new Event('input'));
    
    // Show visual feedback
    const item = document.querySelector(`.guide-emoji-item[data-emoji="${emoji}"]`);
    if (item) {
        item.style.transform = 'scale(1.3)';
        item.style.transition = 'transform 0.2s';
        
        setTimeout(() => {
            item.style.transform = '';
        }, 300);
    }
    
    // Focus back to input
    input.focus();
    
    console.log("Added emoji:", emoji);
}

// Count emojis in text
function countEmojis(text) {
    const emojiRegex = /[\p{Emoji_Presentation}\p{Emoji}\uFE0F]/gu;
    const matches = text.match(emojiRegex);
    return matches ? matches.length : 0;
}

// Check server status
async function checkServerStatus() {
    try {
        console.log("Checking server status...");
        const response = await fetch('/health');
        const data = await response.json();
        
        console.log("Server health response:", data);
        
        if (data.status === 'healthy') {
            serverStatus.innerHTML = '<span style="color: #10b981">ĐANG HOẠT ĐỘNG</span>';
            statusDot.style.background = '#10b981';
            statusDot.style.animation = 'none';
            
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
                
                // Update emoji count
                const emojiCount = document.getElementById('emojiCount');
                if (emojiCount && data.model_info.emoji_count) {
                    emojiCount.textContent = data.model_info.emoji_count;
                }
            }
            
            // Update emoji status
            const emojiStatus = document.getElementById('emojiStatus');
            if (emojiStatus) {
                if (data.emoji_processor_loaded) {
                    emojiStatus.textContent = 'Emoji AI: ĐÃ TẢI';
                    emojiStatus.style.color = '#10b981';
                } else {
                    emojiStatus.textContent = 'Emoji AI: CHƯA TẢI';
                    emojiStatus.style.color = '#ef4444';
                }
            }
        } else {
            serverStatus.innerHTML = '<span style="color: #ef4444">LỖI HỆ THỐNG</span>';
            statusDot.style.background = '#ef4444';
            statusDot.style.animation = 'statusPulse 2s infinite';
        }
    } catch (err) {
        console.error("Server check error:", err);
        serverStatus.innerHTML = '<span style="color: #ef4444">MẤT KẾT NỐI</span>';
        statusDot.style.background = '#ef4444';
        statusDot.style.animation = 'statusPulse 2s infinite';
    }
}

// ========== UI FUNCTIONS ==========

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
    
    // Update loading text
    const loadingText = document.getElementById('loadingText');
    if (loadingText) {
        const texts = [
            'Đang phân tích ngôn ngữ...',
            'Đang xử lý emoji...',
            'Đang tổng hợp kết quả...',
            'AI đang suy nghĩ...'
        ];
        const randomText = texts[Math.floor(Math.random() * texts.length)];
        loadingText.textContent = randomText;
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
    
    console.error("Displayed error:", message);
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
            const actualPercent = Math.min(Math.max(percent, 0), 100);
            bar.style.width = actualPercent + '%';
            bar.style.opacity = '1';
            value.textContent = actualPercent.toFixed(1) + '%';
            console.log(`Set ${barId} to ${actualPercent}%`);
        }, 300);
    }
}

// Update confidence bar
function updateConfidenceBar(percent) {
    if (confidenceBar) {
        confidenceBar.style.width = '0%';
        setTimeout(() => {
            const actualPercent = Math.min(Math.max(percent, 0), 100);
            confidenceBar.style.width = actualPercent + '%';
            console.log(`Confidence bar: ${actualPercent}%`);
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
        intensityLevel.style.color = '#2ed573';
    } else if (sentiment === 1) {
        resultBadge.classList.add('neutral');
        resultLabel.textContent = 'TRUNG TÍNH';
        intensityLevel.textContent = 'TRUNG BÌNH';
        intensityLevel.style.color = '#ffa502';
    } else if (sentiment === 0) {
        resultBadge.classList.add('negative');
        resultLabel.textContent = 'TIÊU CỰC';
        intensityLevel.textContent = confidencePercent > 80 ? 'RẤT CAO' : confidencePercent > 60 ? 'CAO' : 'TRUNG BÌNH';
        intensityLevel.style.color = '#ff4757';
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

// ========== MAIN ANALYSIS FUNCTION ==========

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

    console.log("Starting analysis for text:", text);

    try {
        const response = await fetch('/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ text: text })
        });

        const data = await response.json();
        console.log("API Response:", data);

        if (!response.ok || !data.success) {
            throw new Error(data.error || 'Lỗi không xác định từ hệ thống AI');
        }

        // Success - display result
        displayResult(data);

    } catch (err) {
        console.error("Analysis error:", err);
        showError(err.message || 'Lỗi kết nối với server AI. Vui lòng thử lại!');
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

// ========== DISPLAY RESULT ==========

function displayResult(data) {
    console.log("Displaying result:", data);
    
    // Update confidence
    if (data.confidence) {
        const confValue = typeof data.confidence === 'number' ? data.confidence : parseFloat(data.confidence);
        confidence.textContent = confValue.toFixed(1) + '%';
        updateConfidenceBar(confValue);
    }
    
    // Update processing time
    if (processingTime && data.processing_time_ms) {
        processingTime.textContent = data.processing_time_ms + 'ms';
    }
    
    // Update result appearance
    updateResultAppearance(data.sentiment, data.confidence || 0);
    
    // Update probabilities
    if (data.probabilities_formatted) {
        console.log("Probabilities formatted:", data.probabilities_formatted);
        
        // Parse percentages từ string
        const parsePercent = (str) => {
            if (!str) return 0;
            const num = parseFloat(str.replace('%', '').replace(',', '.'));
            return isNaN(num) ? 0 : num;
        };
        
        const positive = parsePercent(data.probabilities_formatted['Tích cực']);
        const neutral = parsePercent(data.probabilities_formatted['Trung tính']);
        const negative = parsePercent(data.probabilities_formatted['Tiêu cực']);
        
        console.log(`Parsed probabilities: Positive=${positive}, Neutral=${neutral}, Negative=${negative}`);
        
        // Animate probability bars with staggered delay
        setTimeout(() => updateProbability('probNegative', 'valNegative', negative), 100);
        setTimeout(() => updateProbability('probNeutral', 'valNeutral', neutral), 300);
        setTimeout(() => updateProbability('probPositive', 'valPositive', positive), 500);
    } else if (data.probabilities) {
        console.log("Raw probabilities:", data.probabilities);
        
        // Use raw probabilities
        const positive = data.probabilities.positive || 0;
        const neutral = data.probabilities.neutral || 0;
        const negative = data.probabilities.negative || 0;
        
        setTimeout(() => updateProbability('probNegative', 'valNegative', negative), 100);
        setTimeout(() => updateProbability('probNeutral', 'valNeutral', neutral), 300);
        setTimeout(() => updateProbability('probPositive', 'valPositive', positive), 500);
    } else {
        console.log("No probabilities data");
        // Set default values
        setTimeout(() => updateProbability('probNegative', 'valNegative', 0), 100);
        setTimeout(() => updateProbability('probNeutral', 'valNeutral', 0), 300);
        setTimeout(() => updateProbability('probPositive', 'valPositive', 0), 500);
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
    
    // Update emoji details
    updateEmojiDetails(data);
    
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
        
        console.log("Result displayed successfully");
    }, 800);
}

// Update emoji details in result
function updateEmojiDetails(data) {
    console.log("Updating emoji details:", data);
    
    const emojiEffectNotice = document.getElementById('emojiEffectNotice');
    const emojiCountResult = document.getElementById('emojiCountResult');
    const emojiScoreResult = document.getElementById('emojiScoreResult');
    const emojiDetailsContainer = document.getElementById('emojiDetailsContainer');
    const emojiDetailsGrid = document.getElementById('emojiDetailsGrid');
    
    if (data.emoji_count && data.emoji_count > 0) {
        // Show emoji effect notice
        emojiEffectNotice.style.display = 'flex';
        emojiCountResult.textContent = data.emoji_count + ' emoji';
        emojiScoreResult.textContent = 'Score: ' + (data.emoji_score || 0).toFixed(2);
        
        // Update emoji impact
        if (emojiImpact) {
            emojiImpact.textContent = data.has_emoji_effect ? 'Có' : 'Không';
            emojiImpact.style.color = data.has_emoji_effect ? '#8b5cf6' : '#6b7280';
        }
        
        // Show emoji details container
        emojiDetailsContainer.style.display = 'block';
        
        // Clear existing emoji details
        emojiDetailsGrid.innerHTML = '';
        
        // Add emoji details if available
        if (data.emoji_details && data.emoji_details.length > 0) {
            console.log("Creating emoji detail cards:", data.emoji_details);
            
            data.emoji_details.forEach(detail => {
                const emojiCard = document.createElement('div');
                emojiCard.className = 'emoji-detail-card';
                
                let sentimentClass = '';
                let sentimentLabel = '';
                
                // Xác định class dựa trên label
                if (detail.label === 2) {
                    sentimentClass = 'positive';
                    sentimentLabel = 'Tích cực';
                } else if (detail.label === 1) {
                    sentimentClass = 'neutral';
                    sentimentLabel = 'Trung tính';
                } else {
                    sentimentClass = 'negative';
                    sentimentLabel = 'Tiêu cực';
                }
                
                // Tạo HTML đúng với CSS
                emojiCard.innerHTML = `
                    <div class="emoji-detail-display">${detail.emoji}</div>
                    <div class="emoji-detail-name">${detail.description || detail.emoji}</div>
                    <div class="emoji-detail-score">Score: ${detail.score.toFixed(3)}</div>
                    <div class="emoji-detail-label ${sentimentClass}">${sentimentLabel}</div>
                `;
                
                emojiDetailsGrid.appendChild(emojiCard);
            });
        } else {
            // Just show emoji count if no details
            console.log("No emoji details, only count");
            const noDetailsMsg = document.createElement('div');
            noDetailsMsg.className = 'no-emoji-message';
            noDetailsMsg.innerHTML = `
                <i class="fas fa-smile"></i>
                <p>Phát hiện ${data.emoji_count} emoji trong bình luận</p>
            `;
            emojiDetailsGrid.appendChild(noDetailsMsg);
        }
    } else {
        // Hide emoji sections if no emoji
        console.log("No emoji found");
        emojiEffectNotice.style.display = 'none';
        emojiDetailsContainer.style.display = 'none';
        
        // Update emoji impact
        if (emojiImpact) {
            emojiImpact.textContent = 'Không';
            emojiImpact.style.color = '#6b7280';
        }
    }
}

// ========== VISUAL EFFECTS ==========

// Add confetti effect for positive results
function addConfettiEffect() {
    console.log("Adding confetti effect");
    
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
    console.log("Adding floating effects");
    
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
    
    // Add hover effects to emoji guide items
    const emojiItems = document.querySelectorAll('.guide-emoji-item');
    emojiItems.forEach(item => {
        item.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
            this.style.boxShadow = '0 10px 20px rgba(0,0,0,0.2)';
        });
        
        item.addEventListener('mouseleave', function() {
            this.style.transform = '';
            this.style.boxShadow = '';
        });
    });
    
    // Add hover effects to shortcut items
    const shortcutItems = document.querySelectorAll('.shortcut-item');
    shortcutItems.forEach(item => {
        item.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-3px)';
        });
        
        item.addEventListener('mouseleave', function() {
            this.style.transform = '';
        });
    });
}

// ========== UTILITY FUNCTIONS ==========

// Debounce function for performance
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Format number with commas
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

// Copy text to clipboard
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        console.log("Copied to clipboard:", text);
    }).catch(err => {
        console.error("Failed to copy:", err);
    });
}

// ========== EXPORT FUNCTIONS FOR GLOBAL USE ==========

// Make functions available globally for inline event handlers
window.showShortcuts = showShortcuts;
window.hideShortcuts = hideShortcuts;
window.hideError = hideError;
window.analyzeSentiment = analyzeSentiment;

console.log("AI Sentiment Analyzer JavaScript loaded successfully!");