import logging
import trafilatura
import requests
from urllib.parse import quote

# Setup logging
logger = logging.getLogger(__name__)

def get_wikipedia_text_content(lang_code, article_title):
    """
    Get the full text content of a Wikipedia article using trafilatura for better extraction.
    
    Args:
        lang_code (str): Language code (e.g., 'en', 'es', 'fr')
        article_title (str): Title of the Wikipedia article
        
    Returns:
        str: The extracted article content or empty string if failed
    """
    try:
        # URL encode the article title
        safe_title = quote(article_title.replace(" ", "_"))
        url = f"https://{lang_code}.wikipedia.org/wiki/{safe_title}"
        
        # Use trafilatura to fetch and extract clean text
        downloaded = trafilatura.fetch_url(url)
        
        if not downloaded:
            logger.warning(f"Failed to download content from {url}")
            return ""
            
        # Extract the main content (valid formats are: txt, json, xml, etc.)
        content = trafilatura.extract(downloaded, 
                                      include_comments=False, 
                                      include_tables=True,
                                      include_links=False,
                                      include_images=False)
        
        if not content or len(content.strip()) < 50:
            logger.warning(f"Extracted content from {url} is too short or empty")
            # Fall back to API if trafilatura extraction fails
            return get_wikipedia_content_from_api(lang_code, article_title)
            
        return content
    
    except Exception as e:
        logger.error(f"Error extracting content from Wikipedia: {str(e)}")
        # Fall back to API if trafilatura fails
        return get_wikipedia_content_from_api(lang_code, article_title)


def get_wikipedia_content_from_api(lang_code, article_title):
    """
    Fallback method to get Wikipedia content using the MediaWiki API.
    
    Args:
        lang_code (str): Language code (e.g., 'en', 'es', 'fr')
        article_title (str): Title of the Wikipedia article
        
    Returns:
        str: The extracted article content or empty string if failed
    """
    try:
        api_endpoint = f"https://{lang_code}.wikipedia.org/w/api.php"
        
        # Build API URL for fetching article content
        params = {
            'action': 'query',
            'prop': 'extracts',
            'explaintext': 1,
            'exsectionformat': 'plain',
            'titles': article_title,
            'format': 'json',
        }
        
        response = requests.get(api_endpoint, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Extract content
        pages = data.get('query', {}).get('pages', {})
        if not pages:
            return ""
        
        page_id = list(pages.keys())[0]
        if int(page_id) < 0:  # Negative page ID means article doesn't exist
            return ""
            
        extract = pages[page_id].get('extract', '')
        return extract
        
    except Exception as e:
        logger.error(f"Error fetching Wikipedia content from API: {str(e)}")
        return ""


def get_language_name(lang_code):
    """
    Get the language name from a language code.
    
    Args:
        lang_code (str): Language code (e.g., 'en', 'es', 'fr')
        
    Returns:
        str: The language name or the uppercase code if not found
    """
    lang_map = {
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
        'ko': 'Korean',
        'pl': 'Polish',
        'nl': 'Dutch',
        'tr': 'Turkish',
        'sv': 'Swedish',
        'uk': 'Ukrainian',
        'cs': 'Czech',
        'vi': 'Vietnamese',
        'fa': 'Persian',
        'id': 'Indonesian',
        'th': 'Thai',
        'he': 'Hebrew',
        'no': 'Norwegian',
        'da': 'Danish',
        'fi': 'Finnish',
        'hu': 'Hungarian',
        'ca': 'Catalan',
        'el': 'Greek',
        'ro': 'Romanian',
        'bn': 'Bengali',
        'sr': 'Serbian',
        'bg': 'Bulgarian',
        'ms': 'Malay',
        'sk': 'Slovak',
        'sl': 'Slovenian',
        'et': 'Estonian',
        'lt': 'Lithuanian',
        'lv': 'Latvian',
        'hr': 'Croatian',
    }
    
    return lang_map.get(lang_code, lang_code.upper())