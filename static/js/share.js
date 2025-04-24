/**
 * WikiTruth - Social Sharing Functionality
 * Handles sharing comparison results through various platforms
 */

document.addEventListener('DOMContentLoaded', function() {
    // Get all share buttons
    const shareButtons = document.querySelectorAll('.share-btn');
    
    // Add click event listeners
    shareButtons.forEach(button => {
        button.addEventListener('click', function() {
            const platform = this.dataset.platform;
            const mode = this.dataset.mode;
            shareResult(platform, mode);
        });
    });
    
    /**
     * Share comparison results through various platforms
     * @param {string} platform - Sharing platform (twitter, linkedin, etc.)
     * @param {string} mode - Comparison mode (summary, full, funny)
     */
    function shareResult(platform, mode) {
        // Make sure we have content to share
        if (!WikiTruth.comparisonResults[mode]) {
            WikiTruth.showNotification('No content available to share', 'error');
            return;
        }
        
        // Get mode title
        const modeTitle = {
            'summary': 'Key Factual Discrepancies',
            'full': 'Complete Article Comparison',
            'funny': 'Sarcastic Roast of Differences'
        }[mode];
        
        // Create share text (truncated for social media)
        const shareText = `WikiTruth - ${modeTitle} | Find the truth across language barriers`;
        
        // Current URL for sharing
        const shareUrl = window.location.href;
        
        // Handle different platforms
        switch (platform) {
            case 'twitter':
                // Twitter/X sharing
                window.open(`https://twitter.com/intent/tweet?text=${encodeURIComponent(shareText)}&url=${encodeURIComponent(shareUrl)}`, '_blank');
                break;
                
            case 'linkedin':
                // LinkedIn sharing
                window.open(`https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(shareUrl)}`, '_blank');
                break;
                
            case 'reddit':
                // Reddit sharing
                window.open(`https://www.reddit.com/submit?url=${encodeURIComponent(shareUrl)}&title=${encodeURIComponent(shareText)}`, '_blank');
                break;
                
            case 'telegram':
                // Telegram sharing
                window.open(`https://t.me/share/url?url=${encodeURIComponent(shareUrl)}&text=${encodeURIComponent(shareText)}`, '_blank');
                break;
                
            case 'whatsapp':
                // WhatsApp sharing
                window.open(`https://api.whatsapp.com/send?text=${encodeURIComponent(shareText + ' ' + shareUrl)}`, '_blank');
                break;
                
            case 'email':
                // Email sharing
                const emailSubject = `WikiTruth - ${modeTitle}`;
                const emailBody = `Check out this comparison of Wikipedia articles across different languages:\n\n${shareUrl}`;
                window.location.href = `mailto:?subject=${encodeURIComponent(emailSubject)}&body=${encodeURIComponent(emailBody)}`;
                break;
                
            case 'copy':
                // Copy link to clipboard
                navigator.clipboard.writeText(shareUrl)
                    .then(() => {
                        WikiTruth.showNotification('Link copied to clipboard', 'success');
                    })
                    .catch(err => {
                        console.error('Clipboard error:', err);
                        WikiTruth.showNotification('Failed to copy link', 'error');
                    });
                break;
                
            default:
                console.error('Unknown sharing platform:', platform);
                WikiTruth.showNotification('Sharing option not supported', 'error');
        }
    }
});
