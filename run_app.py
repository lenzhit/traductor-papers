import os
import sys
import time
import webbrowser
import threading
import streamlit.web.cli as stcli

def get_base_dir():
    """Retorna el directorio base tanto en ejecución normal como empaquetada con PyInstaller."""
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))

def open_browser_delayed(url: str, delay_seconds: float = 1.5):
    """Abre el navegador tras un breve retraso para que el servidor Streamlit esté listo."""
    time.sleep(delay_seconds)
    try:
        webbrowser.open_new(url)
    except Exception:
        pass

def main():
    base_dir = get_base_dir()
    app_path = os.path.join(base_dir, "app.py")
    
    # Asegurar que el directorio base y utils estén en sys.path
    if base_dir not in sys.path:
        sys.path.insert(0, base_dir)

    port = "8501"
    url = f"http://localhost:{port}"

    # Iniciar hilo para abrir el navegador automáticamente
    threading.Thread(target=open_browser_delayed, args=(url, 1.8), daemon=True).start()

    # Argumentos de Streamlit para modo aplicación de escritorio local
    sys.argv = [
        "streamlit",
        "run",
        app_path,
        "--global.developmentMode=false",
        "--server.headless=true",
        "--browser.gatherUsageStats=false",
        f"--server.port={port}",
        "--server.address=localhost",
        "--theme.base=dark"
    ]

    # Ejecutar el CLI de Streamlit
    sys.exit(stcli.main())

if __name__ == "__main__":
    main()
