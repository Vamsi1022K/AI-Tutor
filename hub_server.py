import os
from flask import Flask, send_from_directory

# Get absolute paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEB_HUB_DIR = os.path.join(BASE_DIR, 'web_hub')

app = Flask(__name__)

@app.route('/')
def index():
    return send_from_directory(WEB_HUB_DIR, 'index.html')

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(WEB_HUB_DIR, filename)

if __name__ == '__main__':
    print("\n  ============================================")
    print("  AI Compiler Tutor - Unified Hub")
    print("  ============================================")
    print("  Hub running at http://localhost:8080")
    print("  Vamsi's Engine expected at http://localhost:5000")
    print("  Friend's Engine expected at http://localhost:5173")
    print("  Press Ctrl+C to stop the Hub\n")
    # Turn off reloader so it doesn't double-start things
    app.run(debug=False, host='0.0.0.0', port=8080)
