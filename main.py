from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import stripe

app = Flask(__name__)

@app.route('/success')
def success():
    return render_template('success.html')

@app.route('/cancel')
def cancel():
    return render_template('cancel.html')

# تكوين مكتبة Stripe
stripe.api_key = 'sk_test_51O2xVYDwh5k7KSXmIjlkMssii4bzNJtUVvwp9rmsFMKpNsdRj6oPfv68l3AMLqLs9Zw2qcYRJzToMYd11PsKaKrF00kYvpDs23'

@app.route('/pay/<int:id>', methods=['GET', 'POST'])
def pay(id):
    employee = Employee.query.get(id)
    if request.method == 'POST':
        amount = request.form['paymentAmount']

        # إنشاء الدفعة باستخدام مكتبة Stripe
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': 'Employee Salary',
                    },
                    'unit_amount': int(amount) * 100,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.url_root + 'success?amount=' + amount,
            cancel_url=request.url_root + 'cancel',
        )

        return render_template('payment.html', employee=employee, amount=amount, session=session)

    return render_template('payment.html', employee=employee)

# تكوين قاعدة البيانات SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///employees.db'
db = SQLAlchemy(app)

# تعريف نموذج الموظف
class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(100), nullable=False)
    performance = db.Column(db.String(100))
    salary = db.Column(db.Float)
    city = db.Column(db.String(100))
    employee_id = db.Column(db.String(20), unique=True)
    image_url = db.Column(db.String(200))

# إعادة إنشاء جداول قاعدة البيانات في حالة عدم وجودها
with app.app_context():
    db.create_all()

# ... (الجزء الباقي من الكود)
@app.route('/')
def index():
    employees = Employee.query.all()
    return render_template('index.html', employees=employees)

@app.route('/add', methods=['GET', 'POST'])
def add_employee():
    if request.method == 'POST':
        name = request.form['name']
        position = request.form['position']
        salary = request.form['salary']
        city = request.form['city']
        employee_id = request.form.get('employee_id')
        image_url = request.form.get('image_url')
        new_employee = Employee(
            name=name,
            position=position,
            salary=salary,
            city=city,
            employee_id=employee_id,
            image_url=image_url
        )
        db.session.add(new_employee)
        db.session.commit()

        return redirect(url_for('index'))
    return render_template('add.html', employee=None)  # تمرير None لـ employee عند عرض الصفحة للمرة الأولى

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_employee(id):
    employee = Employee.query.get(id)
    if request.method == 'POST':
        employee.name = request.form['name']
        employee.position = request.form['position']
        employee.salary = request.form['salary']
        employee.city = request.form['city']
        employee.employee_id = request.form['employee_id']
        employee.image_url = request.form['image_url']
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('edit.html', employee=employee)

@app.route('/delete/<int:id>')
def delete_employee(id):
    employee = Employee.query.get(id)
    db.session.delete(employee)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/add_employee')
def add_employee_page():
    return render_template('add.html')

if __name__ == '__main__':
    app.run(debug=True)
