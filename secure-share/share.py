from flask import Flask, request, render_template, redirect, url_for, send_file
import secrets
import time
import os
import sys
import argparse
import threading
from pyngrok import ngrok, conf

app = Flask(__name__)

# Dictionary to store our "sends"
sends = {}

# Parse command-line arguments
parser = argparse.ArgumentParser(description='File sharing Flask app')
parser.add_argument('filename', help='The file to share')
parser.add_argument('--expiration', type=int, default=3600, help='Expiration time in seconds (default: 3600)')
parser.add_argument('--max-downloads', type=int, default=1, help='Maximum number of downloads (default: 1)')
parser.add_argument('--ngrok-token', help='Ngrok auth token')
args = parser.parse_args()

# Check if the file exists
if not os.path.exists(args.filename):
    print(f"Error: File '{args.filename}' not found.")
    sys.exit(1)

# Create a send for the file
file_send_id = secrets.token_urlsafe(16)
sends[file_send_id] = {
    'filename': args.filename,
    'expiration': time.time() + args.expiration,
    'downloads': 0,
    'max_downloads': args.max_downloads
}

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

@app.route('/')
def index():
    return render_template('file_link.html', send_id=file_send_id)

@app.route('/send/<send_id>')
def get_send(send_id):
    send = sends.get(send_id)
    if send and time.time() < send['expiration'] and send['downloads'] < send['max_downloads']:
        send['downloads'] += 1
        if send['downloads'] >= send['max_downloads']:
            # Schedule server shutdown after sending the file
            threading.Thread(target=lambda: time.sleep(1) or shutdown_server()).start()
        return send_file(send['filename'], as_attachment=True)
    elif send and send['downloads'] >= send['max_downloads']:
        return "Maximum number of downloads reached", 403
    return "Send not found or expired", 404

@app.route('/stats/<send_id>')
def get_stats(send_id):
    send = sends.get(send_id)
    if send:
        remaining_time = max(0, int(send['expiration'] - time.time()))
        remaining_downloads = max(0, send['max_downloads'] - send['downloads'])
        return render_template('stats.html', downloads=send['downloads'], 
                               remaining_time=remaining_time, 
                               remaining_downloads=remaining_downloads)
    return "Send not found", 404

if __name__ == '__main__':
    use_ngrok = input("Do you want to use ngrok? (y/n): ").lower() == 'y'
    if use_ngrok:
        # Get ngrok token from command line argument or environment variable
        ngrok_token = args.ngrok_token or os.environ.get('NGROK_AUTH_TOKEN')
        if not ngrok_token:
            print("Ngrok token not provided. Please provide it using --ngrok-token or set NGROK_AUTH_TOKEN environment variable.")
            sys.exit(1)
        
        # Configure ngrok
        conf.get_default().auth_token = ngrok_token
        
        try:
            public_url = ngrok.connect(5000)
            print(f" * Ngrok tunnel URL: {public_url}")
            base_url = public_url
        except Exception as e:
            print(f"Ngrok error: {e}")
            print("Falling back to local URL")
            base_url = "http://localhost:5000"
    else:
        base_url = "http://localhost:5000"

    print(f" * File share link: {base_url}/")
    print(f" * Stats link: {base_url}/stats/{file_send_id}")
    app.run(debug=True)