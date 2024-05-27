from flask import Flask,request,redirect,url_for,render_template
import stripe
app=Flask(__name__)
stripe.api_key='yourkey'
@app.route('/')
def index():
    return render_template('item1.html')
@app.route('/pay/<name>/<int:price>',methods=['POST'])
def pay(name,price):
    q=int(request.form['qty'])
    total=price*q
    checkout_session=stripe.checkout.Session.create(
        success_url=url_for('success',item=name,qty=q,total=total,_external=True),
        line_items=[
                {
                    'price_data': {
                        'product_data': {
                            'name': name,
                        },
                        'unit_amount': price*100,
                        'currency': 'inr',
                    },
                    'quantity': q,
                },
                ],
        mode="payment",)
    return redirect(checkout_session.url)
@app.route('/success/<item>/<qty>/<total>')
def success(item,qty,total):
    return {'item':item,'quantity':qty,'total':total}

app.run(use_reloader=True,debug=True)