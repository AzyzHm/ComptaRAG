import subprocess
import sys
import time
import os

BACKEND_FILE = "main.py" 
FRONTEND_FILE = os.path.join("frontend", "main.py")

def run_services():
    # 1. Start the FastAPI Backend
    backend_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
        cwd=".",  # Run from root so it finds main.py
        stdout=sys.stdout,
        stderr=sys.stderr
    )
    print(f"🚀 Backend running on PID {backend_process.pid}")

    # 2. Start the Streamlit Frontend
    time.sleep(2)
    
    frontend_process = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", FRONTEND_FILE, "--server.headless", "true"],
        cwd=".",
        stdout=sys.stdout,
        stderr=sys.stderr
    )
    print(f"🎈 Frontend running on PID {frontend_process.pid}")

    try:
        while True:
            time.sleep(1)
            if backend_process.poll() is not None:
                print("Backend process terminated unexpectedly.")
                break
            if frontend_process.poll() is not None:
                print("Frontend process terminated unexpectedly.")
                break

    except KeyboardInterrupt:
        print("\n🛑 Shutting down services...")
        backend_process.terminate()
        frontend_process.terminate()
        
        backend_process.wait()
        frontend_process.wait()
        print("✅ Services stopped.")

if __name__ == "__main__":
    run_services()