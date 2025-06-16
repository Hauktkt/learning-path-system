import os
import sys
import time
import platform
from datetime import datetime

# Import necessary modules
from init_db import init_db
from unified_api import app as flask_app
from swagger_ui import setup_swagger

def print_colored(text, color):
    """Print colored text based on platform"""
    colors = {
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'magenta': '\033[95m',
        'cyan': '\033[96m',
        'white': '\033[97m',
        'end': '\033[0m'
    }
    
    if platform.system() == "Windows":
        # Check if running in a terminal that supports ANSI colors
        if os.environ.get('TERM') or 'WT_SESSION' in os.environ:
            print(f"{colors[color]}{text}{colors['end']}")
        else:
            print(text)
    else:
        print(f"{colors[color]}{text}{colors['end']}")

def main():
    """Main function to initialize database and run the API server"""
    print_colored("=== RAG Learning Path API Service ===", "cyan")
    print_colored(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", "blue")
    print("")
    
    # Step 1: Initialize database
    print_colored("Step 1: Initializing Database...", "yellow")
    success = init_db()
    
    if not success:
        print_colored("Error initializing database.", "red")
        input("Press Enter to exit...")
        return
    
    print_colored("✓ Database initialized successfully.", "green")
    print("")
    
    # Step 2: Setup Swagger UI
    print_colored("Step 2: Setting up Swagger UI...", "yellow")
    try:
        setup_swagger(flask_app)
        print_colored("✓ Swagger UI set up successfully.", "green")
        print("")
    except Exception as e:
        print_colored(f"Warning: Could not set up Swagger UI: {str(e)}", "yellow")
        print("")
    
    # Step 3: Start API server
    print_colored("Step 3: Starting API server...", "yellow")
    
    print_colored("✓ API server running at:", "green")
    print_colored("   http://localhost:5000", "magenta")
    print_colored("✓ Swagger UI accessible at:", "green")
    print_colored("   http://localhost:5000/api/docs", "magenta")
    print("")
    print_colored("Login information:", "cyan")
    print_colored("   Username: admin", "white")
    print_colored("   Password: admin123", "white")
    print("")
    print_colored("Press Ctrl+C to stop the server.", "yellow")
    
    try:
        # On Windows, set the window title
        if platform.system() == "Windows":
            os.system('title RAG Learning Path API Server')
        
        # Run Flask app
        flask_app.run(debug=True, port=5000, host='0.0.0.0')
        
    except KeyboardInterrupt:
        print("")
        print_colored("API server stopped by user.", "yellow")
    except Exception as e:
        print_colored(f"Error running API server: {str(e)}", "red")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main() 