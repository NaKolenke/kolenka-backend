from src.main import app

@app.route("/users")
def users():
    return "Testing update"
