import os

from flask import Flask

from .flask_config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    gui_dir = os.path.join(os.path.dirname(__file__), "templates")  # development path
    if not os.path.exists(gui_dir):  # frozen executable path
        gui_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")

    app.static_folder = gui_dir
    app.template_folder = gui_dir

    from .ha_websocket_manager import WebSocketManager
    from .routes import register_routes

    register_routes(app)

    @app.teardown_appcontext
    def cleanup(exception=None):
        # Get the manager instance without creating a new one if it doesn't exist
        manager = WebSocketManager._instance
        if manager:
            manager.shutdown()

    return app
