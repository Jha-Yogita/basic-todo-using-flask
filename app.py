from flask import Flask, render_template, request, redirect, jsonify, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///todo.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-change-this-in-production'
db = SQLAlchemy(app)


class Todo(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    desc = db.Column(db.String(500), nullable=False)
    category = db.Column(db.String(50), default="Personal")
    priority = db.Column(db.String(20), default="Medium")
    due_date = db.Column(db.DateTime, nullable=True)
    completed = db.Column(db.Boolean, default=False)
    completed_date = db.Column(db.DateTime, nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f"{self.sno} - {self.title}"
    
    @property
    def is_overdue(self):
        if self.due_date and not self.completed:
            return datetime.utcnow() > self.due_date
        return False
    
    @property
    def days_until_due(self):
        if self.due_date and not self.completed:
            delta = self.due_date - datetime.utcnow()
            return delta.days
        return None


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        title = request.form.get('title')
        desc = request.form.get('desc')
        category = request.form.get('category', 'Personal')
        priority = request.form.get('priority', 'Medium')
        due_date_str = request.form.get('due_date')
        
        due_date = None
        if due_date_str:
            try:
                due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
            except ValueError:
                flash('Invalid date format', 'error')
                return redirect("/")
        
        todo = Todo(title=title, desc=desc, category=category, 
                   priority=priority, due_date=due_date)
        db.session.add(todo)
        db.session.commit()
        flash('Todo added successfully!', 'success')
        return redirect("/")
    
    filter_category = request.args.get('category', 'all')
    filter_priority = request.args.get('priority', 'all')
    filter_status = request.args.get('status', 'all')
    search_query = request.args.get('search', '')
    sort_by = request.args.get('sort', 'date_created')
    
    query = Todo.query
    
    if filter_category != 'all':
        query = query.filter_by(category=filter_category)
    
    if filter_priority != 'all':
        query = query.filter_by(priority=filter_priority)
    
    if filter_status == 'completed':
        query = query.filter_by(completed=True)
    elif filter_status == 'active':
        query = query.filter_by(completed=False)
    elif filter_status == 'overdue':
        query = query.filter(Todo.due_date < datetime.utcnow(), Todo.completed == False)
    
    if search_query:
        query = query.filter(
            (Todo.title.contains(search_query)) | 
            (Todo.desc.contains(search_query))
        )
    
    if sort_by == 'priority':
        priority_order = {'High': 1, 'Medium': 2, 'Low': 3}
        allTodo = sorted(query.all(), key=lambda x: priority_order.get(x.priority, 4))
    elif sort_by == 'due_date':
        allTodo = query.order_by(Todo.due_date.asc()).all()
    elif sort_by == 'title':
        allTodo = query.order_by(Todo.title.asc()).all()
    else:
        allTodo = query.order_by(Todo.date_created.desc()).all()
    
    stats = {
        'total': Todo.query.count(),
        'completed': Todo.query.filter_by(completed=True).count(),
        'active': Todo.query.filter_by(completed=False).count(),
        'overdue': Todo.query.filter(Todo.due_date < datetime.utcnow(), Todo.completed == False).count()
    }
    
    categories = db.session.query(Todo.category).distinct().all()
    categories = [cat[0] for cat in categories]
    
    return render_template('index.html', 
                         allTodo=allTodo, 
                         stats=stats,
                         categories=categories,
                         filter_category=filter_category,
                         filter_priority=filter_priority,
                         filter_status=filter_status,
                         search_query=search_query,
                         sort_by=sort_by)


@app.route('/update/<int:sno>', methods=['GET', 'POST'])
def update(sno):
    todo = Todo.query.filter_by(sno=sno).first()
    
    if request.method == 'POST':
        todo.title = request.form.get('title')
        todo.desc = request.form.get('desc')
        todo.category = request.form.get('category', 'Personal')
        todo.priority = request.form.get('priority', 'Medium')
        
        due_date_str = request.form.get('due_date')
        if due_date_str:
            try:
                todo.due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
            except ValueError:
                flash('Invalid date format', 'error')
                return redirect(url_for('update', sno=sno))
        else:
            todo.due_date = None
        
        db.session.commit()
        flash('Todo updated successfully!', 'success')
        return redirect("/")
    
    return render_template('update.html', todo=todo)


@app.route('/delete/<int:sno>')
def delete(sno):
    todo = Todo.query.filter_by(sno=sno).first()
    db.session.delete(todo)
    db.session.commit()
    flash('Todo deleted successfully!', 'success')
    return redirect("/")


@app.route('/toggle/<int:sno>')
def toggle_complete(sno):
    todo = Todo.query.filter_by(sno=sno).first()
    todo.completed = not todo.completed
    if todo.completed:
        todo.completed_date = datetime.utcnow()
    else:
        todo.completed_date = None
    db.session.commit()
    return redirect(request.referrer or "/")


@app.route('/delete_completed')
def delete_completed():
    Todo.query.filter_by(completed=True).delete()
    db.session.commit()
    flash('All completed todos deleted!', 'success')
    return redirect("/")


@app.route('/api/stats')
def get_stats():
    stats = {
        'total': Todo.query.count(),
        'completed': Todo.query.filter_by(completed=True).count(),
        'active': Todo.query.filter_by(completed=False).count(),
        'overdue': Todo.query.filter(Todo.due_date < datetime.utcnow(), Todo.completed == False).count(),
        'high_priority': Todo.query.filter_by(priority='High', completed=False).count(),
    }
    return jsonify(stats)


with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=False, port=8000)