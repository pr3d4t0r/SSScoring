# See: https://github.com/pr4d4t0r/SSSCoring/blob/master/LICENSE.txt

# launch_gui.py
# Bootstrap entry point for the frozen SSScoring desktop app.
# Imported by PyInstaller as the analysis target; spawns Streamlit in-process
# on a daemon thread, then opens a native PyWebView window pointed at it.
# Closing the window exits the process (taking the daemon thread with it).

from __future__ import annotations
from pathlib import Path

from webview.menu import Menu
from webview.menu import MenuAction


import socket
import sys
import threading
import time

import webview
import ssscoring


SERVER_HOST = '127.0.0.1'
SERVER_READY_TIMEOUT_SEC = 30.0
PORT_POLL_INTERVAL_SEC = 0.2
SOCKET_CONNECT_TIMEOUT_SEC = 0.5

WINDOW_TITLE = 'SSScore'
WINDOW_SCREEN_H_FRACTION = 0.8
WINDOW_SCREEN_V_FRACTION = 0.9
WINDOW_MIN_WIDTH = 1100
WINDOW_MIN_HEIGHT = 700


def _bundleRoot() -> Path:
    '''Bundle root when frozen, repo root in dev.'''
    if getattr(sys, 'frozen', False):
        return Path(sys._MEIPASS)  # type: ignore[attr-defined]
    return Path(__file__).resolve().parent


def _freePort() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((SERVER_HOST, 0))
        return sock.getsockname()[1]


def _waitForServerReady(port: int, timeout: float = SERVER_READY_TIMEOUT_SEC) -> bool:
    '''Poll the port until the Streamlit server accepts a connection.
    Returns True if reachable before timeout, False otherwise.
    '''
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection((SERVER_HOST, port), timeout=SOCKET_CONNECT_TIMEOUT_SEC):
                return True
        except OSError:
            time.sleep(PORT_POLL_INTERVAL_SEC)
    return False


# def _runStreamlit(scriptPath: str) -> None:
#     '''Daemon-thread target: run Streamlit's bootstrap. Server config is set
#     in main() before this is invoked; bootstrap picks up the headless port
#     and address from the global Streamlit config.
#     '''
#     from streamlit.web import bootstrap
#     bootstrap.run(scriptPath, is_hello=False, args=[], flag_options={})

def _runStreamlit(scriptPath: str) -> None:
    '''Daemon-thread target: run Streamlit's bootstrap. Server config is set
    in main() before this is invoked; bootstrap picks up the headless port
    and address from the global Streamlit config.

    NOTE: Streamlit's run_server() unconditionally registers a SIGTERM handler
    via signal.signal(), which raises ValueError on non-main threads. We
    no-op the handler before invoking bootstrap because in our architecture
    PyWebView owns the user-facing exit path and the daemon thread dies with
    the process — Streamlit doesn't need its own signal handling here.
    '''
    from streamlit.web import bootstrap

    bootstrap._set_up_signal_handler = lambda server: None
    bootstrap.run(scriptPath, is_hello=False, args=[], flag_options={})


def _screenLogicalSizeMac() -> tuple[int, int]:
    '''Primary screen size in logical points (what PyWebView wants for window
    dimensions). Retina/HiDPI is handled correctly: NSScreen.frame() returns
    points, not physical pixels, which matches PyWebView's coordinate space.
    '''
    try:
        from AppKit import NSScreen
        frame = NSScreen.mainScreen().frame()
        return int(frame.size.width), int(frame.size.height)
    except Exception:
        return 1920, 1080 # fallback


def _screenLogicalSizeWin() -> tuple[int, int]:
    try:
        screens = webview.screens
        if screens:
            s = screens[0]  # primary monitor
            return int(s.width), int(s.height)
    except Exception:
        pass
    # fallback
    return 1920, 1080


def _getPrimaryScreenSize() -> tuple[int, int]:
    if sys.platform == 'darwin':
        return _screenLogicalSizeMac()
    else:
        # Windows (and Linux fallback)
        return _screenLogicalSizeWin()


def _showAbout(window):
    content = f'''
    <h2>SSScore {ssscoring.__VERSION__}</h2>
    <p>A modern desktop application for analyzing FlySight speed skydiving data.</p>
    <hr>
    <p>© 2026 Eugene Ciurana / pr3d4t0r</p>
    '''
    window.load_html(content, title=f'About SSScore {ssscoring.__VERSION__}')


def main() -> None:
    from streamlit import config as streamlitConfig

    scriptPath = str(_bundleRoot() / 'ssscrunner.py')
    port = _freePort()

    # Headless server config — no auto-browser-open (PyWebView owns the window),
    # no telemetry, no file watcher (frozen bundle's source files don't change
    # at runtime), no developer mode (suppresses dev-only UI affordances).
    streamlitConfig.set_option('server.headless', True)
    streamlitConfig.set_option('server.port', port)
    streamlitConfig.set_option('server.address', SERVER_HOST)
    streamlitConfig.set_option('server.fileWatcherType', 'none')
    streamlitConfig.set_option('server.runOnSave', False)
    streamlitConfig.set_option('browser.gatherUsageStats', False)
    streamlitConfig.set_option('global.developmentMode', False)
    streamlitConfig.set_option('runner.magicEnabled', False)
    streamlitConfig.set_option('runner.fastReruns', True)

    # Streamlit on a daemon thread; main thread is reserved for PyWebView,
    # which on macOS must own the main thread for Cocoa event-loop reasons.
    threading.Thread(
        target=_runStreamlit,
        args=(scriptPath,),
        daemon=True,
    ).start()

    # Don't open the window until the server is actually serving — avoids a
    # brief connection-refused error inside the embedded webview.
    if not _waitForServerReady(port):
        sys.stderr.write(
            f'SSScore: Streamlit server did not become ready within {SERVER_READY_TIMEOUT_SEC:.0f}s\n'
        )
        sys.exit(1)

    screenW, screenH = _getPrimaryScreenSize()
    windowW = max(WINDOW_MIN_WIDTH,  int(screenW * WINDOW_SCREEN_H_FRACTION))
    windowH = max(WINDOW_MIN_HEIGHT, int(screenH * WINDOW_SCREEN_V_FRACTION))
    windowX = (screenW - windowW) // 2
    windowY = (screenH - windowH) // 2

    window = webview.create_window(
        title=WINDOW_TITLE,
        url=f'http://{SERVER_HOST}:{port}',
        width=windowW,
        height=windowH,
        x=windowX,
        y=windowY,
        min_size=(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT),
        resizable=True,
    )

    def aboutHandler(window):
        _showAbout(window)

    helpMenu = Menu(
            'Help',
            [
                MenuAction('About SSScore...', aboutHandler),
            ],)
    window.menu = [ helpMenu, ]

    webview.start()
    sys.exit(0)


if __name__ == '__main__':
    main()

