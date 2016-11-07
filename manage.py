import os, sys
from flask_script import Manager

sys.path.append(os.path.join(os.path.dirname(__file__), "extra"))

from root import create_app

app = create_app()
manager = Manager(app)


@manager.command
def run():
    """Run in local machine."""
    app.run()


if __name__ == "__main__":
    manager.run()
