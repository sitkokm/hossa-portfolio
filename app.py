from flask import Flask
import src.update_script as us

app = Flask(__name__)

@app.route("/")
def update_plots():
    try:
        us.run_update() 
        return "Plots updated successfully!"
    except Exception as e:
        return f"ERROR: {e}"

# WSGI callable for SEOHost
application = app
