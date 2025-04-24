import os
import logging
import json
import requests
from urllib.parse import quote
from flask import Flask, render_template, request, jsonify, session, redirect, url_for

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
    """API endpoint for searching Wikipedia articles"""
    query = request.args.get('q', '')
    lang = request.args.get('lang', 'en')
    
    if not query:
        return jsonify([])
    
    try:
        # Build the API URL for Wikipedia search
        params = {
            'action': 'opensearch',
            'search': query,
            'limit': 10,
            'namespace': 0,
            'format': 'json',
        }
        
        # Use the appropriate language-specific Wikipedia API endpoint
        api_endpoint = f"https://{lang}.wikipedia.org/w/api.php"
        
        response = requests.get(api_endpoint, params=params)
        data = response.json()
        
        # Format results: data[0] is the search term, data[1] is article titles,
        # data[2] is descriptions, data[3] is URLs
        results = []
        for i in range(len(data[1])):
            article_title = data[1][i]
            article_url = data[3][i]
            
            # Extract the article's path from URL for later use
            article_path = article_url.split('/wiki/')[1] if '/wiki/' in article_url else article_title
            
            results.append({
                'title': article_title,
                'url': article_url,
                'path': article_path
            })
        
        return jsonify(results)
    
    except Exception as e:
        logger.error(f"Error searching Wikipedia: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/languages/<article_path>')
def get_languages(article_path):
    """Get available language versions for a specific article"""
    try:
        # Build the API URL for Wikipedia langlinks
        params = {
            'action': 'query',
            'titles': article_path.replace('_', ' '),
            'prop': 'langlinks',
            'lllimit': 500,
            'format': 'json',
        }
        
        response = requests.get(WIKIPEDIA_API_ENDPOINT, params=params)
        data = response.json()
        
        # Store the article information in the session
        session['article'] = {
            'title': article_path.replace('_', ' '),
            'path': article_path
        }
        
        # Extract language links
        pages = data.get('query', {}).get('pages', {})
        if not pages:
            return jsonify({'error': 'Article not found'}), 404
        
        # Get the first (and only) page
        page_id = list(pages.keys())[0]
        page = pages[page_id]
        
        # Include English (source language) in the list
        languages = [{'lang': 'en', 'title': page.get('title', article_path.replace('_', ' '))}]
        
        # Add other languages
        langlinks = page.get('langlinks', [])
        for lang in langlinks:
            languages.append({
                'lang': lang.get('lang', ''),
                'title': lang.get('*', '')
            })
        
        # Return the template with languages
        return render_template('languages.html', 
                              article_title=article_path.replace('_', ' '),
                              languages=languages)
    
    except Exception as e:
        logger.error(f"Error getting language versions: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/compare', methods=['POST'])
def compare_articles():
    """Compare selected language versions of an article"""
    try:
        selected_languages = request.form.getlist('languages')
        
        if len(selected_languages) < 2:
            return jsonify({'error': 'Please select at least two languages to compare'}), 400
        
        # Get article content for each selected language
        article_contents = {}
        
        for lang_info in selected_languages:
            lang, title = lang_info.split('|', 1)
            
            # Build API URL for fetching article content
            params = {
                'action': 'query',
                'prop': 'extracts',
                'exintro': 1,
                'explaintext': 1,
                'titles': title,
                'format': 'json',
            }
            
            api_endpoint = f"https://{lang}.wikipedia.org/w/api.php"
            response = requests.get(api_endpoint, params=params)
            data = response.json()
            
            # Extract content
            pages = data.get('query', {}).get('pages', {})
            if pages:
                page_id = list(pages.keys())[0]
                extract = pages[page_id].get('extract', '')
                
                # Store content with language info
                article_contents[lang] = {
                    'title': title,
                    'content': extract,
                    'lang_code': lang
                }
        
        # Store article contents in session for the comparison page
        session['article_contents'] = article_contents
        
        # Redirect to the comparison page
        return redirect(url_for('show_comparison'))
    
    except Exception as e:
        logger.error(f"Error comparing articles: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/comparison')
def show_comparison():
    """Show the comparison page with the selected articles"""
    article_contents = session.get('article_contents', {})
    
    if not article_contents:
        return redirect(url_for('index'))
    
    return render_template('comparison.html', 
                          article_contents=article_contents)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
