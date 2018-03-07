from ksproj import app
from ksproj import model

from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

migrate = Migrate(app.app, model.db)

manager = Manager(app.app)
manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()
