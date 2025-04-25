/**
 * WikiTruth - Comparison Functionality
 * Handles article comparison using Puter.js and result display
 */

document.addEventListener('DOMContentLoaded', function() {
    // Elements for different comparison modes
    const summaryContent = document.getElementById('summary-content');
    const fullContent = document.getElementById('full-content');
    const funnyContent = document.getElementById('funny-content');
    
    // Language selection dropdowns
    const summaryLanguageSelect = document.getElementById('summary-output-language');
    const fullLanguageSelect = document.getElementById('full-output-language');
    const funnyLanguageSelect = document.getElementById('funny-output-language');
    
    // Share option containers
    const summaryShare = document.getElementById('summary-share');
    const fullShare = document.getElementById('full-share');
    const funnyShare = document.getElementById('funny-share');
    
    // Tab elements
    const summaryTab = document.getElementById('summary-tab');
    const fullTab = document.getElementById('full-tab');
    const funnyTab = document.getElementById('funny-tab');
    
    // Get article content from the page
    const articleElements = document.querySelectorAll('.article-card');
    const articles = {};
    
    // Extract article contents
    articleElements.forEach(element => {
        const langTitle = element.querySelector('.article-language').textContent;
        const langCode = langTitle.split(':')[0].trim().toLowerCase();
        const title = langTitle.split(':')[1].trim();
        const content = element.querySelector('.article-preview').textContent;
        
        articles[langCode] = {
            title: title,
            content: content
        };
    });
    
    // If we have articles to compare, start the comparison
    if (Object.keys(articles).length >= 2) {
        // Run comparisons in parallel
        runComparison('summary');
        
        // Set up tab event listeners to load content as needed
        fullTab.addEventListener('click', function() {
            if (!WikiTruth.comparisonResults.full) {
                runComparison('full');
            }
        });
        
        funnyTab.addEventListener('click', function() {
            if (!WikiTruth.comparisonResults.funny) {
                runComparison('funny');
            }
        });
        
        // Set up language change handlers
        if (summaryLanguageSelect) {
            summaryLanguageSelect.addEventListener('change', function() {
                translateOutput('summary', this.value);
            });
        }
        
        if (fullLanguageSelect) {
            fullLanguageSelect.addEventListener('change', function() {
                translateOutput('full', this.value);
            });
        }
        
        if (funnyLanguageSelect) {
            funnyLanguageSelect.addEventListener('change', function() {
                translateOutput('funny', this.value);
            });
        }
    }
    
    /**
     * Run article comparison using Puter.js
     * @param {string} mode - Comparison mode: 'summary', 'full', or 'funny'
     */
    async function runComparison(mode) {
        // Skip if already comparing
        if (WikiTruth.isComparing) {
            return;
        }
        
        WikiTruth.isComparing = true;
        
        try {
            // Prepare the AI prompt based on the mode
            let prompt = '';
            // Using Puter.js models - April 2025 version
            // Available models: gpt-4.1, gpt-4.1-mini, gpt-4.5-preview, gpt-4o, gpt-4o-mini, o1, o1-mini, o3, o3-mini
            let aiModel = 'gpt-4o'; // Using most capable model by default
            
            // Get content container based on mode
            let contentElement;
            let shareElement;
            
            switch (mode) {
                case 'summary':
                    contentElement = summaryContent;
                    shareElement = summaryShare;
                    prompt = `Compare all versions of the article in different languages. Identify their main differences and provide a summary that includes all the most important distinctions between these articles.\n\n`;
                    break;
                case 'full':
                    contentElement = fullContent;
                    shareElement = fullShare;
                    prompt = `Compare all language versions of the article and provide a detailed explanation of the differences between them. You should identify all discrepancies and indicate in which language versions they occur. Then, write a new article that includes all these inconsistencies. You will do this step by step, starting just like a typical Wikipedia article, but along the way, you will note: “In this language version, it states that..., while in this version, it says that...,” clarifying how the person or event is portrayed differently across versions.\n\n`;
                    break;
                case 'funny':
                    contentElement = funnyContent;
                    shareElement = funnyShare;
                    prompt = `Based on the identified differences between the language versions of the article, write a sarcastic roast — Level of Details: 100/10 — that ironically highlights these discrepancies and why they might exist. Subtly point out how Wikipedia content is shaped (read: controlled) by moderators, and how these differences seem almost tailor-made to divide us neatly into our cozy little language-based echo chambers.\n\n`;
                    break;
                default:
                    throw new Error('Invalid comparison mode');
            }
            
            // Add article content to prompt
            Object.entries(articles).forEach(([langCode, article]) => {
                prompt += `${langCode.toUpperCase()} VERSION: "${article.title}"\n${article.content}\n\n`;
            });
            
            // Show loading indicator
            contentElement.innerHTML = `
                <div class="loader text-center">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <p class="mt-2">Analyzing ${Object.keys(articles).length} article versions...</p>
                </div>
            `;
            
            // Make the AI request using Puter.js (April 2025 version)
            // According to documentation, puter.ai.chat() returns text directly
            const response = await puter.ai.chat(prompt, { model: aiModel });
            
            // Handle the response - Puter.js should return a string directly
            let resultText = '';
            if (typeof response === 'string') {
                resultText = response;
            } else {
                // For backward compatibility or unexpected response formats
                console.log('Processing Puter.js response format:', response);
                if (response && typeof response.text === 'string') {
                    resultText = response.text;
                } else if (response && typeof response.content === 'string') {
                    resultText = response.content;
                } else {
                    // Convert to string as a fallback
                    resultText = String(response || 'No response received');
                }
            }
            
            // Store the result
            WikiTruth.comparisonResults[mode] = resultText;
            
            // Display the result
            contentElement.innerHTML = `<div class="result-text">${formatOutput(resultText)}</div>`;
            
            // Show sharing options
            if (shareElement) {
                shareElement.classList.remove('d-none');
            }
            
        } catch (error) {
            console.error(`Error in ${mode} comparison:`, error);
            
            // Get the relevant content element
            const contentElement = (mode === 'summary') ? summaryContent : 
                                  (mode === 'full') ? fullContent : funnyContent;
            
            // Display error message
            contentElement.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-circle me-2"></i>
                    Failed to generate comparison. Please try again.
                    <div class="mt-2 small">${error.message || 'Unknown error'}</div>
                </div>
                <button class="btn btn-outline-primary mt-3 retry-btn" data-mode="${mode}">
                    <i class="fas fa-redo me-2"></i> Retry
                </button>
            `;
            
            // Add retry button functionality
            const retryBtn = contentElement.querySelector('.retry-btn');
            if (retryBtn) {
                retryBtn.addEventListener('click', function() {
                    runComparison(this.dataset.mode);
                });
            }
        } finally {
            WikiTruth.isComparing = false;
        }
    }
    
    /**
     * Format AI output for better readability
     * @param {string} text - Raw comparison text
     * @returns {string} - Formatted HTML
     */
    function formatOutput(text) {
        // Ensure text is a string
        if (typeof text !== 'string') {
            console.warn('formatOutput received non-string input:', text);
            // Convert to string if possible
            text = String(text || '');
        }
        
        // Convert line breaks to HTML
        let formatted = text.replace(/\n\n/g, '</p><p>').replace(/\n/g, '<br>');
        
        // Wrap in paragraph tags if needed
        if (!formatted.startsWith('<p>')) {
            formatted = `<p>${formatted}</p>`;
        }
        
        return formatted;
    }
    
    /**
     * Translate comparison output to selected language
     * @param {string} mode - Comparison mode
     * @param {string} targetLang - Target language code
     */
    async function translateOutput(mode, targetLang) {
        // Skip if already in English or no content
        if (targetLang === 'en' || !WikiTruth.comparisonResults[mode]) {
            return;
        }
        
        // Get content element
        const contentElement = (mode === 'summary') ? summaryContent :
                              (mode === 'full') ? fullContent : funnyContent;
        
        // Show translation in progress
        contentElement.innerHTML = `
            <div class="loader text-center">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-2">Translating to ${getLanguageName(targetLang)}...</p>
            </div>
        `;
        
        try {
            // Get original text
            const originalText = WikiTruth.comparisonResults[mode];
            
            // Translate using WikiTruth utility function
            const translatedText = await WikiTruth.translateText(originalText, targetLang);
            
            // Display translated text
            contentElement.innerHTML = `<div class="result-text">${formatOutput(translatedText)}</div>`;
            
        } catch (error) {
            console.error(`Translation error (${mode}):`, error);
            
            // Show error and restore original content
            contentElement.innerHTML = `
                <div class="alert alert-warning mb-3">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    Translation failed. Showing original English version.
                </div>
                <div class="result-text">${formatOutput(WikiTruth.comparisonResults[mode])}</div>
            `;
        }
    }
    
    /**
     * Get language name from language code
     * @param {string} langCode - Language code (e.g., 'en', 'es')
     * @returns {string} - Language name
     */
    function getLanguageName(langCode) {
        const languages = {
            'en': 'English',
            'es': 'Spanish',
            'fr': 'French',
            'de': 'German',
            'ru': 'Russian',
            'zh': 'Chinese',
            'ja': 'Japanese',
            'ar': 'Arabic',
            'hi': 'Hindi',
            'pt': 'Portuguese',
            'it': 'Italian',
            'ko': 'Korean'
        };
        
        return languages[langCode] || langCode.toUpperCase();
    }
});
