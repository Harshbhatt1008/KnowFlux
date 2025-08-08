from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import sys
import requests
from groq import Groq
from dotenv import load_dotenv
import json
import traceback

# Load environment variables
load_dotenv()

# Add parent directory to path to import your existing modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import prompts
except ImportError:
    # If prompts.py is in the same directory
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    import prompts

app = Flask(__name__, static_folder='static', static_url_path='/static')
CORS(app)  # Enable CORS for frontend requests

# Initialize Groq client
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

@app.route('/')
def index():
    """Serve the main HTML file"""
    return send_from_directory('.', 'index.html')

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'Code Reviewer API is running'})

@app.route('/api/review', methods=['POST'])
def review_code():
    """
    API endpoint to review code from GitHub repository
    Expected JSON payload: {"github_url": "https://github.com/user/repo"}
    """
    try:
        # Get JSON data from request
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'No JSON data provided',
                'success': False
            }), 400
        
        github_url = data.get('github_url', '').strip()
        
        if not github_url:
            return jsonify({
                'error': 'GitHub URL is required',
                'success': False
            }), 400
        
        # Validate GitHub URL format
        if not github_url.startswith('https://github.com/'):
            return jsonify({
                'error': 'Invalid GitHub URL format. Must start with https://github.com/',
                'success': False
            }), 400
        
        # Transform URL to UIthub API (same as your main.py)
        api_url = github_url.replace(
            "https://github.com/", 
            "https://uithub.com/"
        ) + "?accept=text%2Fplain&maxTokens=5000"
        
        print(f"Fetching repository content from: {api_url}")
        
        # Fetch repository content
        try:
            repo_response = requests.get(api_url, timeout=30)
            repo_response.raise_for_status()
        except requests.exceptions.RequestException as e:
            return jsonify({
                'error': f'Failed to fetch repository content: {str(e)}',
                'success': False
            }), 400
        
        repo_code = repo_response.text
        
        if not repo_code or len(repo_code.strip()) == 0:
            return jsonify({
                'error': 'Repository appears to be empty or inaccessible',
                'success': False
            }), 400
        
        print(f"Repository content fetched successfully. Length: {len(repo_code)} characters")
        
        # Check if Groq API key is available
        if not client.api_key:
            return jsonify({
                'error': 'Groq API key not configured. Please set GROQ_API_KEY environment variable.',
                'success': False
            }), 500
        
        # Get AI review using Groq (same as your main.py)
        try:
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": prompts.system_prompt_reviewer,
                    },
                    {
                        "role": "user",
                        "content": f"Please provide the review as mentioned for the code repository given below:\n{repo_code}",
                    }
                ],
                model="llama-3.3-70b-versatile",
            )
            
            review_result = chat_completion.choices[0].message.content
            
            print("AI review completed successfully")
            
            return jsonify({
                'review': review_result,
                'success': True,
                'repository_url': github_url,
                'content_length': len(repo_code)
            })
            
        except Exception as groq_error:
            print(f"Groq API error: {str(groq_error)}")
            return jsonify({
                'error': f'AI review failed: {str(groq_error)}',
                'success': False
            }), 500
        
    except Exception as e:
        # Log the full traceback for debugging
        print(f"Unexpected error in review_code: {str(e)}")
        print(traceback.format_exc())
        
        return jsonify({
            'error': f'Internal server error: {str(e)}',
            'success': False
        }), 500

@app.route('/api/test-connection', methods=['GET'])
def test_connection():
    """Test endpoint to verify API connectivity"""
    try:
        # Test if prompts module is accessible
        hasattr(prompts, 'system_prompt_reviewer')
        
        # Test if Groq client is configured
        api_key_configured = bool(client.api_key)
        
        return jsonify({
            'success': True,
            'prompts_available': True,
            'groq_configured': api_key_configured,
            'message': 'All connections are working'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Connection test failed'
        }), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Endpoint not found',
        'success': False
    }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors"""
    return jsonify({
        'error': 'Method not allowed',
        'success': False
    }), 405

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'error': 'Internal server error',
        'success': False
    }), 500

def validate_environment():
    """Validate that all required environment variables are set"""
    required_vars = ['GROQ_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"Warning: Missing environment variables: {', '.join(missing_vars)}")
        print("Please ensure your .env file is properly configured.")
        return False
    
    return True

if __name__ == '__main__':
    # Validate environment before starting
    if not validate_environment():
        print("Environment validation failed. Please check your configuration.")
        sys.exit(1)
    
    print("Starting Code Reviewer Flask Application...")
    print("Environment validation passed.")
    print(f"Server will be available at: http://localhost:5000")
    print("API endpoints:")
    print("  - GET  /              : Frontend interface")
    print("  - POST /api/review    : Code review endpoint")
    print("  - GET  /api/test-connection : Test connectivity")
    print("  - GET  /health        : Health check")
    
    # Run the Flask application
    app.run(
        debug=True, 
        port=5000, 
        host='0.0.0.0',  # Allow external connections
        threaded=True     # Handle multiple requests
    )