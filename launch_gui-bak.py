# launch_gui.py
# Bootstrap entry point for the frozen SSScoring desktop app.
# Imported by PyInstaller as the analysis target; spawns Streamlit in-process.

from __future__ import annotations

import socket
import sys
import threading
import time
import webbrowser
from pathlib import Path

# Importing ssscoring here ensures PyInstaller's import-graph analyzer
# picks up the package even though the actual Streamlit script is loaded
# at runtime as a data file.
import ssscoring  # noqa: F401


SERVER_HOST = "127.0.0.1"
BROWSER_OPEN_TIMEOUT_SEC = 30.0
PORT_POLL_INTERVAL_SEC = 0.2
SOCKET_CONNECT_TIMEOUT_SEC = 0.5


def _bundleRoot() -> Path:
    """Bundle root when frozen, repo root in dev."""
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)  # type: ignore[attr-defined]
    return Path(__file__).resolve().parent


def _freePort() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((SERVER_HOST, 0))
        return sock.getsockname()[1]


def _openBrowserWhenReady(port: int, timeout: float = BROWSER_OPEN_TIMEOUT_SEC) -> None:
    """Poll the port until the server accepts a connection, then launch browser."""
    deadline = time.time() + timeout
    targetURL = f"http://{SERVER_HOST}:{port}"
    while time.time() < deadline:
        try:
            with socket.create_connection((SERVER_HOST, port), timeout=SOCKET_CONNECT_TIMEOUT_SEC):
                webbrowser.open(targetURL)
                return
        except OSError:
            time.sleep(PORT_POLL_INTERVAL_SEC)
    # Fallback — server slow; open anyway so the user sees something.
    webbrowser.open(targetURL)


def main() -> None:
    # Streamlit's bootstrap is the supported in-process entry point.
    # It does what `streamlit run` does, minus the CLI shell-out.
    from streamlit import config as streamlitConfig
    from streamlit.web import bootstrap

    scriptPath = str(_bundleRoot() / "ssscrunner.py")
    port = _freePort()

    # Headless server config — no auto-browser-open by Streamlit, no telemetry,
    # no file watcher (frozen bundle's source files don't change at runtime),
    # no developer mode (suppresses dev-only UI affordances).
    streamlitConfig.set_option("server.headless", True)
    streamlitConfig.set_option("server.port", port)
    streamlitConfig.set_option("server.address", SERVER_HOST)
    streamlitConfig.set_option("server.fileWatcherType", "none")
    streamlitConfig.set_option("server.runOnSave", False)
    streamlitConfig.set_option("browser.gatherUsageStats", False)
    streamlitConfig.set_option("global.developmentMode", False)
    streamlitConfig.set_option("runner.magicEnabled", False)
    streamlitConfig.set_option("runner.fastReruns", True)

    threading.Thread(
        target=_openBrowserWhenReady,
        args=(port,),
        daemon=True,
    ).start()

    # Blocks until the server exits (Ctrl-C / window close on console builds,
    # or until the OS terminates the .app/.exe).
    bootstrap.run(scriptPath, is_hello=False, args=[], flag_options={})


if __name__ == "__main__":
    main()
