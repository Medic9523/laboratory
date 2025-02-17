from flask import Flask, render_template, request, redirect, url_for, Response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pandas as pd
from io import StringIO

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///reagents.db'
db = SQLAlchemy(app)

class Reagent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    operation_type = db.Column(db.String(50), nullable=False)  # Kirim yoki Chiqim
    operation_date = db.Column(db.DateTime, default=datetime.utcnow)

@app.route('/')
def index():
    reagents = Reagent.query.all()
    return render_template('index.html', reagents=reagents)

@app.route('/add', methods=['GET', 'POST'])
def add_reagent():
    if request.method == 'POST':
        name = request.form['name']
        type = request.form['type']
        quantity = float(request.form['quantity'])
        operation_type = request.form['operation_type']
        new_reagent = Reagent(name=name, type=type, quantity=quantity, operation_type=operation_type)
        db.session.add(new_reagent)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add.html')

@app.route('/delete/<int:id>')
def delete_reagent(id):
    reagent = Reagent.query.get(id)
    if reagent:
        db.session.delete(reagent)
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/export')
def export_report():
    reagents = Reagent.query.all()
    data = [(r.name, r.type, r.quantity, r.operation_type, r.operation_date) for r in reagents]
    df = pd.DataFrame(data, columns=['Name', 'Type', 'Quantity', 'Operation Type', 'Date'])
    output = StringIO()
    df.to_csv(output, index=False)
    output.seek(0)
    return Response(output.getvalue(), mimetype="text/csv", headers={"Content-Disposition": "attachment; filename=reagents_report.csv"})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
