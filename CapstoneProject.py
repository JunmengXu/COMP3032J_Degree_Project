import os

from app import create_app, db
from app.models import User,Agent,Community,Property

app=create_app(os.environ.get("FLASK_CONFIG") or "default")
@app.shell_context_processor
def make_shell_context():
    return {"app": app, "db": db, "User": User, "Agent": Agent,"Community":Community,"Property":Property}
    # updated simultaneously with database model, not necessary,
    # but follow this guridance will provdie convenience for development


if __name__=="__main__":
    app.run(debug=True)
    # with debug=run, execute 'flask run' in Terminal,
    # then everytime you change code you can see it immediately when refreshing webpage.
