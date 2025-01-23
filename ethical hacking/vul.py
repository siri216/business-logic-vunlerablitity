from flask import Flask, request, redirect, url_for, session, render_template_string
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from wtforms import StringField, PasswordField, IntegerField, SelectField
from wtforms.validators import DataRequired, InputRequired, NumberRange

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Replace with your actual secret key
csrf = CSRFProtect(app)

# Simulated user database
users = {
    'admin': {'password': 'adminpass', 'role': 'admin'},
    'user': {'password': 'userpass', 'role': 'user'}
}

# Simulated product price database
item_prices = {
    'cheap_item': 10.0,
    'leather_jacket': 100.0
}

# Flask-WTF forms for login and cart management
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

class CartForm(FlaskForm):
    product_id = SelectField('Product ID', choices=[('cheap_item', 'Cheap Item'), ('leather_jacket', 'Leather Jacket')], validators=[InputRequired()])
    quantity = IntegerField('Quantity', validators=[InputRequired(), NumberRange(min=1, message="Quantity must be at least 1")])

@app.route('/')
def home():
    if 'username' in session:
        return redirect(url_for('account'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        if username in users and users[username]['password'] == password:
            session['username'] = username
            return redirect(url_for('account'))
        return "Invalid credentials", 401
    return render_template_string('''
        <form method="post">
            {{ form.hidden_tag() }}
            {{ form.username.label }} {{ form.username() }}<br>
            {{ form.password.label }} {{ form.password() }}<br>
            <input type="submit" value="Login">
        </form>
    ''', form=form)

@app.route('/account', methods=['GET', 'POST'])
def account():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    form = CartForm()
    if 'cart' not in session:
        session['cart'] = []

    if form.validate_on_submit():
        product_id = form.product_id.data
        quantity = form.quantity.data
        
        # Update cart with new quantity or add a new item
        for item in session['cart']:
            if item['product_id'] == product_id:
                item['quantity'] += quantity
                break
        else:
            session['cart'].append({'product_id': product_id, 'quantity': quantity})

        session.modified = True  # Ensure session is marked as modified
        return redirect(url_for('account'))

    return render_template_string('''
        <h2>Welcome {{ session['username'] }}! Manage your cart:</h2>
        <form method="post">
            {{ form.hidden_tag() }}
            {{ form.product_id.label }} {{ form.product_id() }}<br>
            {{ form.quantity.label }} {{ form.quantity() }}<br>
            <input type="submit" value="Add to Cart">
        </form>
        <br>
        <form action="{{ url_for('view_cart') }}">
            <input type="submit" value="View Cart">
        </form>
    ''', form=form)

@app.route('/view_cart', methods=['GET'])
def view_cart():
    if 'username' not in session:
        return redirect(url_for('login'))

    total_price = sum(item_prices[item['product_id']] * item['quantity'] for item in session['cart'])
    
    return render_template_string('''
        <h2>Your Cart:</h2>
        <ul>
            {% for item in session['cart'] %}
                <li>{{ item['product_id'] }} ({{ item['quantity'] }}) - ${{ '%.2f' % (item_prices[item['product_id']] * item['quantity']) }}</li>
            {% endfor %}
        </ul>
        <h3>Total Price: ${{ '%.2f' % total_price }}</h3>
        <a href="{{ url_for('account') }}">Back to Account</a>
    ''', item_prices=item_prices, total_price=total_price)

if __name__ == '__main__':
    app.run(debug=True)
