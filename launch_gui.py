import os
import subprocess
import threading
import webbrowser

def start_streamlit():
    os.environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
    subprocess.Popen(["streamlit", "run", "SSScore_app.py"])

if __name__ == "__main__":
    threading.Thread(target=start_streamlit).start()
    webbrowser.open("http://localhost:8509")

