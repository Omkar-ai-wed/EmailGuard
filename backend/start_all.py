"""
EmailGuard — Quick Start Script
Starts both the backend API AND the frontend static server.

Run this ONE script to start everything:
  python start_all.py

Then open:
  Dashboard: http://localhost:3000
  API Docs:  http://localhost:8000/docs
"""

import os
import sys
import subprocess
import threading
import time
import webbrowser
import http.server
import socketserver

BACKEND_PORT = 8000
FRONTEND_PORT = 3000
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), '..', 'Dashboard_UI')


def run_backend():
    """Seed DB (first run only) then start FastAPI."""
    backend_dir = os.path.dirname(__file__)
    db_path = os.path.join(backend_dir, 'emailguard.db')

    # Seed only if fresh database
    if not os.path.exists(db_path):
        print("🌱 Seeding database for the first time...")
        subprocess.run([sys.executable, os.path.join(backend_dir, 'seed_data.py')], cwd=backend_dir)

    print(f"🚀 Starting EmailGuard API on http://localhost:{BACKEND_PORT}")
    subprocess.run([sys.executable, '-m', 'uvicorn', 'main:app', '--host', '0.0.0.0',
                    '--port', str(BACKEND_PORT)], cwd=backend_dir)


def run_frontend():
    """Serve the Dashboard_UI folder as a static website."""
    os.chdir(os.path.abspath(FRONTEND_DIR))
    handler = http.server.SimpleHTTPRequestHandler

    with socketserver.TCPServer(("", FRONTEND_PORT), handler) as httpd:
        print(f"🌐 Serving dashboard at  http://localhost:{FRONTEND_PORT}")
        httpd.serve_forever()


def main():
    print("=" * 55)
    print("  EmailGuard — Email Detection System")
    print("=" * 55)

    # Start frontend in background thread
    t_frontend = threading.Thread(target=run_frontend, daemon=True)
    t_frontend.start()
    time.sleep(1)

    # Open browser after a short delay
    def open_browser():
        time.sleep(3)
        url = f"http://localhost:{FRONTEND_PORT}/Overview_Dashboard.html"
        print(f"\n🌍 Opening dashboard in browser: {url}\n")
        webbrowser.open(url)

    threading.Thread(target=open_browser, daemon=True).start()

    # Run backend in main thread (blocking)
    run_backend()


if __name__ == "__main__":
    main()
