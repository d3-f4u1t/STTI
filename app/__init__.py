from flask import Flask, render_template

def create_app():
    app = Flask(__name__)

    # Load config, initialize extensions, etc.
    app.config.from_object('config.Config')

    from app.extentions import db, login_manager
    db.init_app(app)
    login_manager.init_app(app)

    # Import and register Blueprints (auth, main, etc.)
    from app.auth.routes import auth_bp
    from app.main.routes import main_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    # Add your additional routes here
    @app.route("/")
    def home():
        return render_template("home.html")

    @app.route("/dashboard")
    def dashboard():
        return render_template("dashboard.html")

    @app.route("/notifications")
    def notifications():
        return render_template("notifications.html")

    @app.route("/timetable")
    def timetable():
        return render_template("timetable.html")  # You can create this later

    return app
