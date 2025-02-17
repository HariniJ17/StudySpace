from flask import Blueprint, request, session, redirect, url_for, render_template

payment_bp = Blueprint('payment', __name__)

@payment_bp.route('/payment', methods=['GET', 'POST'])
def payment():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        course_id = request.form['course_id']
        # Store dummy payment entry in the database (Future implementation)
        return "Payment Successful!"
    
    return render_template('payment.html')
