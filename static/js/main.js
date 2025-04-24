/**
 * WikiTruth - Main JavaScript
 * Contains common functionality used across the application
 */

// Set up global variables
const WikiTruth = {
    // Store comparison results
    comparisonResults: {
        summary: '',
        full: '',
        funny: ''
    },
    
    // Track if a comparison is in progress
    isComparing: false,
    
    // Store original tab data
    tabData: {
        title: document.title,
        url: window.location.href
    },
    
    // Translation utility function
    translateText: async function(text, targetLang = 'en') {
        if (!text || targetLang === 'en') {
            return text; // No translation needed
        }
        
        try {
            // Simulate Google Translate API (would be implemented on server-side in production)
            // We're using Puter.js here to simulate translation for demo purposes
            const prompt = `Translate the following text to ${targetLang}:\n\n${text}`;
            
            const translatedText = await puter.ai.chat(prompt, {
                model: "gpt-4o"
            });
            
            return translatedText;
        } catch (error) {
            console.error('Translation error:', error);
            return text; // Return original text on error
        }
    },
    
    // Show notification message
    showNotification: function(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <span>${message}</span>
                <button type="button" class="notification-close">&times;</button>
            </div>
        `;
        
        // Append to body
        document.body.appendChild(notification);
        
        // Show with animation
        setTimeout(() => {
            notification.classList.add('show');
        }, 10);
        
        // Add close button functionality
        notification.querySelector('.notification-close').addEventListener('click', function() {
            notification.classList.remove('show');
            setTimeout(() => {
                notification.remove();
            }, 300);
        });
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            if (document.body.contains(notification)) {
                notification.classList.remove('show');
                setTimeout(() => {
                    if (document.body.contains(notification)) {
                        notification.remove();
                    }
                }, 300);
            }
        }, 5000);
    }
};

// Add CSS for notifications
document.addEventListener('DOMContentLoaded', function() {
    const style = document.createElement('style');
    style.textContent = `
        .notification {
            position: fixed;
            top: 20px;
            right: 20px;
            max-width: 350px;
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            z-index: 9999;
            transform: translateY(-20px);
            opacity: 0;
            transition: transform 0.3s, opacity 0.3s;
        }
        
        .notification.show {
            transform: translateY(0);
            opacity: 1;
        }
        
        .notification-content {
            padding: 15px 20px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        
        .notification-close {
            background: none;
            border: none;
            cursor: pointer;
            font-size: 20px;
            color: #999;
            margin-left: 10px;
        }
        
        .notification-info {
            border-left: 4px solid #87ceeb;
        }
        
        .notification-success {
            border-left: 4px solid #4caf50;
        }
        
        .notification-error {
            border-left: 4px solid #f44336;
        }
    `;
    document.head.appendChild(style);
});
