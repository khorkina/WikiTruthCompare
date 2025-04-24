# WikiTruth

WikiTruth is a Flask web application designed to compare Wikipedia articles across different languages using AI to identify factual discrepancies and differences in information presentation.

## Features

- Search for Wikipedia articles in multiple languages
- Compare multiple language versions of the same article
- View comparisons in three different modes:
  - **Summary Mode**: Shows key factual discrepancies in a concise format
  - **Full Differences**: Provides a comprehensive comparison of the entire articles
  - **Funny Mode**: Gives a humorous, sarcastic take on the differences
- Export comparison results to various formats
- Share comparisons via social media and email
- Support for 30+ languages

## Technologies Used

- **Backend**: Flask, Python
- **Frontend**: JavaScript, HTML, CSS, Bootstrap
- **Scraping**: Trafilatura for improved text extraction
- **AI**: Puter.js for AI-powered comparisons
- **Data Source**: Wikipedia API

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/your-username/wikitruth.git
   cd wikitruth
   ```

2. Required packages (already installed in this environment):
   - flask
   - flask-sqlalchemy
   - gunicorn
   - psycopg2-binary
   - requests
   - trafilatura
   - email-validator

   See `requirements-reference.txt` for version details.

3. Run the application:
   ```
   python main.py
   ```

4. Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

## How It Works

1. **Search**: Find a Wikipedia article in your preferred language
2. **Select Languages**: Choose which language versions to compare
3. **Compare**: View the AI-generated analysis of discrepancies
4. **Share or Export**: Save or share your findings

## Project Structure

- `app.py`: Main Flask application
- `utils.py`: Utility functions for text extraction and processing
- `article_cache.py`: Caching system for articles
- `static/`: Frontend assets (CSS, JS, images)
- `templates/`: Jinja2 templates for the web pages
- `main.py`: Application entry point

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Wikipedia for providing the API and content
- Flask and its community for the excellent web framework
- Trafilatura for improved content extraction