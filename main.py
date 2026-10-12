import threading
from flask import Flask
from kivy.app import App
from kivy.uix.webview import WebView

# Import your existing Flask app from app.py
# If your app.py already defines 'app', this imports it. 
try:
    from app import app as flask_app
except ImportError:
    # Fallback if app.py doesn't define 'app' properly
    flask_app = Flask(__name__)

    @flask_app.route("/")
    def index():
        return open("index.html").read()

def run_flask():
    # Run Flask in a background thread so it doesn't block Kivy
    # use_reloader=False is CRITICAL, otherwise it crashes on Android
    flask_app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)

class FlaskApp(App):
    def build(self):
        # Start the Flask server in the background
        threading.Thread(target=run_flask, daemon=True).start()
        # Load the local web server into the WebView
        return WebView(url="http://127.0.0.1:5000")

if __name__ == "__main__":
    FlaskApp().run()