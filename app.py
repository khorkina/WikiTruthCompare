import os
import logging
import json
import requests
from urllib.parse import quote
from flask import Flask, render_template, request, jsonify, session, redirect, url_for

# Import utility functions
from utils import get_wikipedia_text_content, get_language_name

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
        
        response = requests.get(api_endpoint, params=params)
        response.raise_for_status()  # Raise exception for 4XX/5XX responses
        data = response.json()
        
        # Extract and format search results
        results = []
        if 'query' in data and 'search' in data['query']:
            search_results = data['query']['search']
            
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
        
        return jsonify(results)
    
    except Exception as e:
        logger.error(f"Error searching Wikipedia: {str(e)}")
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
        
        # Store article contents in session for the comparison page
        session['article_contents'] = article_contents
        
        # Store any warnings to show on the comparison page
        if errors:
            session['comparison_warnings'] = errors
        
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
    article_contents = session.get('article_contents', {})
    
    if not article_contents:
        return redirect(url_for('index'))
    
    # Get any warnings to display
    warnings = session.pop('comparison_warnings', [])
    
    return render_template('comparison.html', 
                          article_contents=article_contents,
                          warnings=warnings)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
