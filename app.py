from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Initialize the SQLAlchemy instance (without passing the app yet)
db = SQLAlchemy()

# Initialize Flask-Migrate
migrate = Migrate()


def create_app():
    app = Flask(__name__)

    # Configure the app with the database URI and other settings
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize SQLAlchemy with the Flask app
    db.init_app(app)

    # Initialize Flask-Migrate with the Flask app and SQLAlchemy instance
    migrate.init_app(app, db)

    # Define the Task model
    class Task(db.Model):
        __tablename__ = 'task'  # Explicitly set the table name

        id = db.Column(db.Integer, primary_key=True)
        description = db.Column(db.String(255), nullable=False)
        is_completed = db.Column(db.Boolean, default=False)
        created_at = db.Column(db.DateTime, default=db.func.now())
        updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

        def __repr__(self):
            return f'<Task {self.description}>'

    # Route for home page
    @app.route('/')
    def home():
        return render_template('index.html')

    # Route to view all tasks
    @app.route('/tasks')
    def view_tasks():
        tasks = Task.query.all()
        return render_template('tasks.html', tasks=tasks)

    # Route to add a new task
    @app.route('/tasks/add', methods=['GET', 'POST'])
    def add_task():
        if request.method == 'POST':
            description = request.form['description']
            new_task = Task(description=description)
            db.session.add(new_task)
            db.session.commit()
            return redirect(url_for('view_tasks'))
        return render_template('add_task.html')

    # Route to update an existing task
    @app.route('/tasks/update/<int:id>', methods=['GET', 'POST'])
    def update_task(id):
        task = Task.query.get_or_404(id)
        if request.method == 'POST':
            task.description = request.form['description']
            task.is_completed = 'is_completed' in request.form
            db.session.commit()
            return redirect(url_for('view_tasks'))
        return render_template('update_task.html', task=task)

    # Route to delete a task
    @app.route('/tasks/delete/<int:id>', methods=['POST'])
    def delete_task(id):
        task = Task.query.get_or_404(id)
        db.session.delete(task)
        db.session.commit()
        return redirect(url_for('view_tasks'))

    return app

# Create an app instance


app = create_app()

# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True)
