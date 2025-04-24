import os
import logging
import json
import requests
import uuid
from urllib.parse import quote
from flask import Flask, render_template, request, jsonify, session, redirect, url_for

# Import utility functions
from utils import get_wikipedia_text_content, get_language_name
from article_cache import article_cache

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "wikitruth_default_secret")

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# API endpoint for Wikipedia
WIKIPEDIA_API_ENDPOINT = "https://en.wikipedia.org/w/api.php"

# Routes
@app.route('/')
def index():
    """Render the home page"""
    return render_template('index.html')

@app.route('/search')
def search():
    """API endpoint for searching Wikipedia articles with improved handling"""
    query = request.args.get('q', '')
    lang = request.args.get('lang', 'en')
    
    logger.info(f"Search request - Query: '{query}', Language: '{lang}'")
    
    if not query:
        return jsonify([])
    
    try:
        # Build the API URL for Wikipedia search - using more comprehensive search
        params = {
            'action': 'query',
            'list': 'search',
            'srsearch': query,
            'srlimit': 10,
            'format': 'json',
            'srprop': 'snippet|titlesnippet',
        }
        
        # Use the appropriate language-specific Wikipedia API endpoint
        api_endpoint = f"https://{lang}.wikipedia.org/w/api.php"
        logger.info(f"Searching Wikipedia API: {api_endpoint} with query: {query}")
        
        response = requests.get(api_endpoint, params=params)
        response.raise_for_status()  # Raise exception for 4XX/5XX responses
        data = response.json()
        
        # Log the raw response for debugging
        logger.debug(f"Wikipedia API response: {json.dumps(data)[:500]}...")
        
        # Extract and format search results
        results = []
        if 'query' in data and 'search' in data['query']:
            search_results = data['query']['search']
            logger.info(f"Found {len(search_results)} results for '{query}' in {lang}")
            
            for article in search_results:
                title = article.get('title', '')
                
                # Create properly encoded article path
                # Use URL quote to handle special characters properly
                article_path = quote(title.replace(' ', '_'), safe='')
                
                # Get article URL
                article_url = f"https://{lang}.wikipedia.org/wiki/{article_path}"
                
                # Add to results
                results.append({
                    'title': title,
                    'url': article_url,
                    'path': article_path,
                    'snippet': article.get('snippet', ''),
                    'lang': lang
                })
        else:
            # Log why we didn't get results
            logger.warning(f"No results found in API response. Keys in response: {list(data.keys())}")
            if 'query' in data:
                logger.warning(f"Keys in query: {list(data['query'].keys())}")
        
        return jsonify(results)
    
    except Exception as e:
        logger.error(f"Error searching Wikipedia: {str(e)}")
        # Log more detailed error info
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

@app.route('/languages/<path:article_path>')
def get_languages(article_path):
    """Get available language versions for a specific article with improved handling"""
    try:
        # First decode URL-encoded characters in article path
        article_path = article_path.strip()
        article_title = article_path.replace('_', ' ')
        
        # Get source language from query parameter or default to English
        source_lang = request.args.get('lang', 'en')
        
        # Build the API URL for Wikipedia langlinks
        params = {
            'action': 'query',
            'titles': article_title,
            'prop': 'langlinks',
            'lllimit': 500,  # Maximum number of languages to retrieve
            'format': 'json',
        }
        
        # Use the appropriate language-specific Wikipedia API endpoint
        api_endpoint = f"https://{source_lang}.wikipedia.org/w/api.php"
        
        response = requests.get(api_endpoint, params=params)
        response.raise_for_status()  # Raise exception for 4XX/5XX responses
        data = response.json()
        
        # Store the article information in the session
        session['article'] = {
            'title': article_title,
            'path': article_path,
            'source_lang': source_lang
        }
        
        # Extract language links
        pages = data.get('query', {}).get('pages', {})
        if not pages:
            return render_template('error.html', 
                                  error_title="Article Not Found",
                                  error_message=f"Could not find article '{article_title}' in {source_lang.upper()} Wikipedia.")
        
        # Check for negative page ID (indicates article doesn't exist)
        page_id = list(pages.keys())[0]
        if int(page_id) < 0:
            return render_template('error.html', 
                                  error_title="Article Not Found",
                                  error_message=f"Could not find article '{article_title}' in {source_lang.upper()} Wikipedia.")
        
        page = pages[page_id]
        
        # Get the canonical title from the API response
        canonical_title = page.get('title', article_title)
        
        # Include the source language in the list using the utility function
        languages = [{
            'lang': source_lang, 
            'title': canonical_title,
            'name': get_language_name(source_lang)
        }]
        
        # Add other languages
        langlinks = page.get('langlinks', [])
        for lang in langlinks:
            lang_code = lang.get('lang', '')
            languages.append({
                'lang': lang_code,
                'title': lang.get('*', ''),
                'name': get_language_name(lang_code)
            })
        
        # Sort languages by name (with source language first)
        source_lang_obj = languages[0]
        other_langs = sorted(languages[1:], key=lambda x: x['name'])
        languages = [source_lang_obj] + other_langs
        
        # Return the template with languages
        return render_template('languages.html', 
                              article_title=canonical_title,
                              source_lang=source_lang,
                              languages=languages)
    
    except Exception as e:
        logger.error(f"Error getting language versions: {str(e)}")
        return render_template('error.html', 
                              error_title="Error",
                              error_message=f"Failed to retrieve language versions: {str(e)}")

@app.route('/compare', methods=['POST'])
def compare_articles():
    """Compare selected language versions of an article with improved handling"""
    try:
        selected_languages = request.form.getlist('languages')
        
        if len(selected_languages) < 2:
            return render_template('error.html', 
                                 error_title="Selection Error",
                                 error_message="Please select at least two languages to compare.")
        
        # Get article content for each selected language
        article_contents = {}
        errors = []
        
        for lang_info in selected_languages:
            try:
                # Split the language code and title
                parts = lang_info.split('|', 1)
                if len(parts) != 2:
                    logger.warning(f"Invalid language format: {lang_info}")
                    continue
                    
                lang, title = parts
                
                # Get article content using trafilatura for better extraction
                logger.info(f"Getting article content for {title} in {lang}")
                
                # Use the trafilatura extraction function
                extract = get_wikipedia_text_content(lang, title)
                
                # Check if we got content
                if not extract or len(extract.strip()) < 50:
                    errors.append(f"Failed to retrieve meaningful content for {title} ({lang.upper()})")
                    continue
                
                # Get proper language name for display
                lang_name = get_language_name(lang)
                
                # Store content with language info
                article_contents[lang] = {
                    'title': title,
                    'content': extract,
                    'lang_code': lang,
                    'lang_name': lang_name
                }
                
            except Exception as lang_error:
                logger.error(f"Error processing {lang_info}: {str(lang_error)}")
                errors.append(f"Error processing {lang_info}: {str(lang_error)}")
        
        # Check if we have enough content to compare
        if len(article_contents) < 2:
            error_msg = "Couldn't retrieve enough article versions to compare"
            if errors:
                error_msg += ": " + "; ".join(errors)
            return render_template('error.html', 
                                 error_title="Content Retrieval Error",
                                 error_message=error_msg)
        
        # Generate a unique cache key for this set of articles
        lang_codes = list(article_contents.keys())
        titles = [article_contents[lang]['title'] for lang in lang_codes]
        
        # Generate a unique ID for this comparison
        comparison_id = str(uuid.uuid4())
        
        # Store in cache instead of session
        article_cache.set(comparison_id, {
            'contents': article_contents,
            'warnings': errors if errors else []
        })
        
        # Store only the ID in session, not the full content
        session['comparison_id'] = comparison_id
        
        # Redirect to the comparison page
        return redirect(url_for('show_comparison'))
    
    except Exception as e:
        logger.error(f"Error comparing articles: {str(e)}")
        return render_template('error.html', 
                             error_title="Comparison Error",
                             error_message=f"An error occurred while comparing articles: {str(e)}")

@app.route('/comparison')
def show_comparison():
    """Show the comparison page with the selected articles"""
    # Get the comparison ID from session
    comparison_id = session.get('comparison_id')
    
    if not comparison_id:
        # For backward compatibility, check if we have article_contents in session
        article_contents = session.get('article_contents', {})
        warnings = session.get('comparison_warnings', [])
        
        if not article_contents:
            return redirect(url_for('index'))
            
        return render_template('comparison.html', 
                              article_contents=article_contents,
                              warnings=warnings)
    
    # Get cached article contents using the ID
    cached_data = article_cache.get(comparison_id)
    
    if not cached_data:
        return render_template('error.html',
                             error_title="Comparison Expired",
                             error_message="This comparison has expired or was not found. Please try again.")
    
    # Extract data from cache
    article_contents = cached_data.get('contents', {})
    warnings = cached_data.get('warnings', [])
    
    # Render the comparison page
    return render_template('comparison.html', 
                          article_contents=article_contents,
                          warnings=warnings)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
