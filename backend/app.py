from flask import Flask
from flask_cors import CORS

from agency import agency_bp
from dispatch import dispatch_bp
from login import login_bp
from users import users_bp
from history import history_bp 

app = Flask(__name__)
CORS(app)

# register all modules
app.register_blueprint(agency_bp)
app.register_blueprint(dispatch_bp)
app.register_blueprint(login_bp)
app.register_blueprint(users_bp)
app.register_blueprint(history_bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)