from flask import Flask, request,render_template, redirect,session,url_for,send_from_directory
from flask_sqlalchemy import SQLAlchemy
import bcrypt
import mysql.connector
import stripe

#stripe, api keys, revel test key
stripe.api_key='sk_test_51Orj7ZSE5GvLBPytzSkmp3v8MMXYDpLDdRqPj9H3kmqFufCpByHpvd4Y8WTX4IcyodMpkLoOm3gZ2h9w68cMPoCT00t9mQlMZH'
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
app.secret_key = 'secret_key'
mydb = mysql.connector.connect(host="localhost",user="root",password="password@489",db='trans')

'''class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

    def __init__(self,email,password,name):
        self.name = name
        self.email = email
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self,password):
        return bcrypt.checkpw(password.encode('utf-8'),self.password.encode('utf-8'))
    

with app.app_context():
    db.create_all()'''


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')




@app.route('/templates/<path:path>')
def send_static(path):
    return send_from_directory('templates', path)

@app.route('/images/<path:path>')
def send_image(path):
    return send_from_directory('images', path)

@app.route('/register',methods=['GET','POST'])
def register():
    if request.method == 'POST':
        # handle request
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        # new_user = User(name=name,email=email,password=password)
        # print(new_user)
        # db.session.add(new_user)
        # db.session.commit()
        cursor = mydb.cursor(buffered=True) 
        cursor.execute('SELECT COUNT(*) FROM users WHERE email = %s',[email])
        data1=cursor.fetchone()
        if int(data1[0])==0:
            cursor.execute('insert into users(name,email,password) values(%s,%s,%s)',(name,email,password))
        else:
            return redirect('/unsuccessful')
        cursor.execute('select * from users')
        data=cursor.fetchall()
        print(data)
        mydb.commit()
        return redirect('/successful')

    return render_template('register.html')


@app.route('/successful')
def successful():
    return render_template('successful.html')

@app.route('/unsuccessful')
def unsuccessful():
    return render_template('unsuccessful.html')

@app.route('/forgot',methods=['GET','POST'])
def forget():
    if request.method == 'POST':
        email=request.form['email']
        cursor = mydb.cursor(buffered=True) 
        cursor.execute('SELECT COUNT(*) FROM users WHERE email = %s',[email])
        data1=cursor.fetchone()
        count=int(data1[0])
        print(count,email)
        session['email'] = email
        if count==0:
            return redirect('/invalid')
        else:
            return redirect('/changepwd')
        
    return render_template('forgot.html')
    

@app.route('/invalid')
def invalid():
    return render_template('invalid.html')

@app.route('/changepwd',methods=['GET','POST'])
def changepwd():
    if request.method == 'POST':
        #email=request.args.get('email')
        email = session.get('email')
        password = request.form['password']
        cursor = mydb.cursor(buffered=True)
        print(password)
        print(email)
        update_query = 'UPDATE users SET password = %s WHERE email = %s'

        # Define the values to be substituted into the query
        

# Execute the query with the values
        cursor.execute(update_query, (password,email ))

# Get the number of rows affected by the update operation
        data = cursor.rowcount

# Print the number of rows affected
        print(data)

        #data=cursor.execute('UPDATE users SET password = %s WHERE email=%s',[password,email])
        
        return redirect('/wow')

    return render_template('changepwd.html')
@app.route('/wow')
def wow():
    return render_template('wow.html')


@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        user = request.form['email']
        password = request.form['password']
        cursor = mydb.cursor(buffered=True)
        cursor.execute('select email,password from users where email=%s',[user])
        data = cursor.fetchone()
        if data==None:
            return render_template('login.html',error='Invalid user')
        if data[0] ==  user and data[1] == password:
            print(data[0],data[1])
            session['email'] = user
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html',error='Invalid user')

    return render_template('login.html')

@app.route('/login2',methods=['GET','POST'])
def login2():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        cursor3 = mydb.cursor(buffered=True)
        cursor3.execute('select name,password from main where name=%s',[name])
        datanew = cursor3.fetchone()
        if datanew==None:
            return render_template('login2.html',error='Invalid user')
        if datanew[0] ==  name and datanew[1] == password:
            print(datanew[0],datanew[1])
            session['name'] = name
            return redirect(url_for('manage'))
        else:
            return render_template('login2.html',error='Invalid user')

    return render_template('login2.html')



@app.route('/dashboard',methods=['GET','POST'])
def dashboard():
    if session['email']:
        if request.method == 'POST':
        #user = User.query.filter_by(email=session['email']).first()
        #create ta ticket table and dump it to database
            name = request.form['name']
            email=request.form['email']
            tickettype='bus ticket'
            start=request.form['from']
            end=request.form['to']
            quantity=request.form['quantity']
            cursor1= mydb.cursor(buffered=True)
            cursor1.execute('select price from fares where start=%s and end=%s',[start,end])
            data2=cursor1.fetchone()
            fare=int(quantity)*int(data2[0])
            mydb.commit()
            data_to_send = email
            #return redirect(url_for('generate',data=data_to_send,quantity=quantity,name=name,fare=fare))
            return redirect(url_for('pay',price=int(data2[0]),name=name,q=int(quantity),email=email,start=start,end=end,ticket_type=tickettype))
    
    return render_template('dashboard.html')



@app.route('/logout')
def logout():
    session.pop('email',None)
    return redirect('/login')

@app.route('/generate')
def generate():
    name = request.args.get('name')
    data_received = request.args.get('data')
    cursor2 = mydb.cursor(buffered=True)
    cursor2.execute('select start,end from tickets where email=%s ORDER BY id DESC LIMIT 1',[data_received])
    data1 = cursor2.fetchone()
    start=data1[0]
    end=data1[1]
    cursor2.execute('select price from fares where start=%s and end=%s',[start,end])
    data2=cursor2.fetchone()
    print(start,end)
    print(data1)
    print(data2)
    quantity=int(request.args.get('quantity'))
    fare=quantity*int(data2[0])
    return render_template('generate.html',d1=start,d2=end,total=fare,name=name,quantity=quantity,price=int(data2[0]))
#def paying(name,fare):
    #if fare>=1:
        #return redirect(url_for('pay',price=fare,name=name))


@app.route('/pay/<name>/<int:price>/<int:q>/<email>/<start>/<end>/<ticket_type>',methods=['POST','GET'])
def pay(name,price,q,email,start,end,ticket_type):
    q=q
    total=q*price
    checkout_session=stripe.checkout.Session.create(
        success_url=url_for('success',name=name,quantity=q,total=total,email=email,start=start,end=end,ticket_type=ticket_type,_external=True),
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

@app.route('/success/<name>/<int:quantity>/<total>/<email>/<start>/<end>/<ticket_type>')
def success(name,quantity,total,email,start,end,ticket_type):
    cursor1= mydb.cursor(buffered=True)
    cursor1.execute('insert into tickets(name,email,ticket_type,start,end,quantity) values(%s,%s,%s,%s,%s,%s)',(name,email,ticket_type,start,end,quantity))
    cursor1.execute('select * from tickets')
    data=cursor1.fetchall()
    cursor1.execute('select price from fares where start=%s and end=%s',[start,end])
    data2=cursor1.fetchone()
    fare=int(quantity)*int(data2[0])
    print(data)
    mydb.commit()
    data_to_send = email

    return redirect(url_for('generate',data=data_to_send,quantity=quantity,name=name,fare=fare))
    

@app.route('/ptog')
def ptog():
    cursor4 = mydb.cursor(buffered=True)
    cursor4.execute('SELECT SUM(quantity) FROM tickets where end="Munipalle"')
    d1=cursor4.fetchone()
    d1c=d1[0]
    cursor4.execute('SELECT SUM(quantity) FROM tickets where end="Manchala"')
    d2=cursor4.fetchone()
    d2c=d2[0]
    cursor4.execute('SELECT SUM(quantity) FROM tickets where end="Chebrolu"')
    d3=cursor4.fetchone()
    d3c=d3[0]
    cursor4.execute('SELECT SUM(quantity) FROM tickets where end="Nara Koduru"')
    d4=cursor4.fetchone()
    d4c=d4[0]
    cursor4.execute('SELECT SUM(quantity) FROM tickets where end="Budampadu"')
    d5=cursor4.fetchone()
    d5c=d5[0]
    cursor4.execute('SELECT SUM(quantity) FROM tickets where end="Guntur"')
    d6=cursor4.fetchone()
    d6c=d6[0]

    return render_template('ptog.html',c1=d1c,c2=d2c,c3=d3c,c4=d4c,c5=d5c,c6=d6c)


@app.route('/gtop')
def gtop():
    cursor4 = mydb.cursor(buffered=True)
    cursor4.execute('SELECT SUM(quantity) FROM tickets where end="Budampadu"')
    d1=cursor4.fetchone()
    d1c=d1[0]
    cursor4.execute('SELECT SUM(quantity) FROM tickets where end="Nara Koduru"')
    d2=cursor4.fetchone()
    d2c=d2[0]
    cursor4.execute('SELECT SUM(quantity) FROM tickets where end="Chebrolu"')
    d3=cursor4.fetchone()
    d3c=d3[0]
    cursor4.execute('SELECT SUM(quantity) FROM tickets where end="Manchala"')
    d4=cursor4.fetchone()
    d4c=d4[0]
    cursor4.execute('SELECT SUM(quantity) FROM tickets where end="Munipalle"')
    d5=cursor4.fetchone()
    d5c=d5[0]
    cursor4.execute('SELECT SUM(quantity) FROM tickets where end="Ponnur"')
    d6=cursor4.fetchone()
    d6c=d6[0]

    return render_template('gtop.html',c1=d1c,c2=d2c,c3=d3c,c4=d4c,c5=d5c,c6=d6c)

@app.route('/manage')
def manage():
    cursor4 = mydb.cursor(buffered=True)
    cursor4.execute('SELECT SUM(QUANTITY) FROM tickets')
    datanew = cursor4.fetchone()
    count=datanew[0]
    return render_template('manage.html',count=count)
@app.route('/clear')
def clear():
    cursor5 = mydb.cursor(buffered=True)
    cursor5.execute('DELETE FROM tickets')
    return render_template('clear.html')

if __name__ == '__main__':
    app.run(debug=True,use_reloader=True)