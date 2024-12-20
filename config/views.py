from . import bp
from dashboard.navigate import load_dashboard
from flask import render_template, request, redirect, url_for, current_app
from .config_handler import get_saved_config, save_to_config
import time
import webview

CONFIG_FILE = "config.ini"


@bp.route("/", methods=["GET"])
def config():
    saved_config = get_saved_config()
    if "HomeAssistant" in saved_config:
        current_app.config["assist_entity"] = saved_config.get("HomeAssistant", "assist_entity", fallback=None)
        current_app.config["default_dashboard"] = saved_config.get("HomeAssistant", "default_dashboard_path", fallback=None)
        current_app.config["url"] = saved_config.get("HomeAssistant", "url", fallback=None)
        if current_app.config["assist_entity"] and current_app.config["default_dashboard"]:
            return redirect(url_for("dashboard.dashboard"))
        else:
            return render_template("config.html")
    return redirect(url_for("config.hass_login"))

@bp.route("/save", methods=["POST"])
def save_config():
    assist_entity = request.form.get("assistEntity")
    default_dashboard = request.form.get("defaultDashboard")

    save_to_config("HomeAssistant", "assist_entity", assist_entity)
    save_to_config("HomeAssistant", "default_dashboard_path", default_dashboard)

    # Also set the values on the server object so they can be accessed later
    current_app.config["assist_entity"] = assist_entity
    current_app.config["default_dashboard"] = default_dashboard

    return redirect(url_for("dashboard.dashboard"))

@bp.route("/hass-login", methods=["GET"])
def hass_login():
    return render_template("login.html")

def save_url(url):
    save_to_config("HomeAssistant", "url", url)

    # Also save the URL on the Server object
    current_app.config["url"] = url

    print(f"URL saved: {url}")

@bp.route("/connect", methods=["POST"])
def connect():

    url = request.form.get("haUrl")

    load_dashboard(url)

    while True:
        result = webview.windows[0].evaluate_js("""
            localStorage.getItem('hassTokens')
        """)
        if result:
            save_url(url)
            load_dashboard(url_for("config.config"))
            break

        time.sleep(1)

    return redirect(url_for("dashboard.dashboard"))
