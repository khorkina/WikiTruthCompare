/**
 * WikiTruth - Search Functionality
 * Handles search input, suggestions, and navigation to article languages
 */

document.addEventListener('DOMContentLoaded', function() {
    // Get DOM elements
    const searchInput = document.getElementById('search-input');
    const searchResults = document.getElementById('search-results');
    const languageSelect = document.getElementById('language-select');
    
    // Variables to control search behavior
    let searchTimeout;
    const SEARCH_DELAY = 300; // Milliseconds to wait before triggering search
    
    // Initialize search functionality if elements exist
    if (searchInput && searchResults) {
        // Add event listener for search input
        searchInput.addEventListener('input', function() {
            // Clear previous timeout
            clearTimeout(searchTimeout);
            
            const query = this.value.trim();
            
            if (query.length < 2) {
                // Hide results for short queries
                searchResults.classList.add('d-none');
                searchResults.innerHTML = '';
                return;
            }
            
            // Set a timeout to avoid too many requests
            searchTimeout = setTimeout(() => {
                performSearch(query);
            }, SEARCH_DELAY);
        });
        
        // Hide search results when clicking outside
        document.addEventListener('click', function(event) {
            if (!searchInput.contains(event.target) && !searchResults.contains(event.target)) {
                searchResults.classList.add('d-none');
            }
        });
        
        // Show results when focusing on input field (if there's a query)
        searchInput.addEventListener('focus', function() {
            if (this.value.trim().length >= 2 && searchResults.innerHTML) {
                searchResults.classList.remove('d-none');
            }
        });
    }
    
    /**
     * Perform Wikipedia article search
     * @param {string} query - Search query
     */
    function performSearch(query) {
        // Get selected language
        const selectedLang = languageSelect ? languageSelect.value : 'en';
        
        // Build the search URL
        const searchUrl = `/search?q=${encodeURIComponent(query)}&lang=${selectedLang}`;
        
        // Make the search request
        fetch(searchUrl)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Search failed: ${response.status}`);
                }
                return response.json();
            })
            .then(results => {
                displaySearchResults(results);
            })
            .catch(error => {
                console.error('Search error:', error);
                WikiTruth.showNotification('Failed to fetch search results. Please try again.', 'error');
            });
    }
    
    /**
     * Display search results in the dropdown
     * @param {Array} results - Search results from Wikipedia API
     */
    function displaySearchResults(results) {
        // Clear previous results
        searchResults.innerHTML = '';
        
        if (results.length === 0) {
            searchResults.innerHTML = `
                <div class="search-result-item">No results found</div>
            `;
            searchResults.classList.remove('d-none');
            return;
        }
        
        // Create result items
        results.forEach(result => {
            const resultItem = document.createElement('div');
            resultItem.className = 'search-result-item';
            resultItem.textContent = result.title;
            resultItem.dataset.path = result.path;
            
            // Add click event to navigate to article languages
            resultItem.addEventListener('click', function() {
                window.location.href = `/languages/${this.dataset.path}`;
            });
            
            searchResults.appendChild(resultItem);
        });
        
        // Show the results dropdown
        searchResults.classList.remove('d-none');
    }
});
