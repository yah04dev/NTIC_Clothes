from flask import redirect,url_for,Flask, request,render_template,make_response
import sqlite3
import random
import string
import smtplib
from email.mime.text import MIMEText
from chargily_pay import ChargilyClient
from chargily_pay.settings import CHARGILIY_TEST_URL
from chargily_pay import ChargilyClient
from chargily_pay.entity import Checkout
key = "test_pk_m4MHp1rTSghTJhDFSHjQfIjTZc9eWq6CpveQ5pHD"
secret = "test_sk_jCQlbggug05xeAi2eH2tAaJGzU13YxRjTlc2dqsA"

chargily = ChargilyClient(key, secret, CHARGILIY_TEST_URL)
def pass_gen(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def emailo(password, recipient, fname):
    sender = "clothestore25@zohomail.com"
    app_password = "S6tZK9MqFE61" 

    msg = MIMEText(f"Welcome Mr {fname} to our store. Your password is {password}")
    msg["Subject"] = "Your Password"
    msg["From"] = sender
    msg["To"] = recipient

    try:
        server = smtplib.SMTP_SSL("smtp.zoho.com", 465)  
        server.login(sender, app_password)
        server.sendmail(sender, recipient, msg.as_string())
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error: {e}")
app = Flask(__name__)
@app.route('/')
def dhome():
    CID = request.cookies.get('CID')
    if not CID or CID == "0":
        return redirect(url_for("login"))
    else:
        name = request.args.get('name')
        types = request.args.get('types')
        con = sqlite3.connect("db.db")
        cur = con.cursor()

        if not name and not types:
         cur.execute("SELECT * FROM prod ORDER BY pid DESC LIMIT 50")
        elif types:
         cur.execute("SELECT * FROM prod WHERE type = ? ORDER BY pid DESC LIMIT 50", (types,))
        else:
         cur.execute("SELECT * FROM prod WHERE LOWER(name) LIKE LOWER(?) OR LOWER(disc) LIKE LOWER(?)", (f"%{name}%", f"%{name}%"))
        prods = list(cur.fetchall())
        con.close() 
        return render_template('index.html',prods=prods)
@app.route('/addcart') 
def addcart():
 CID = request.cookies.get('CID')
 if not CID or CID == "0":
        return redirect(url_for("login"))
 else:
     pid = request.args.get('pid')
     pid=int(pid)
     size = request.args.get('size')
     qty = request.args.get('qty')
     color = request.args.get('color')
     name = request.args.get('name')
     price = request.args.get('price')
     conn = sqlite3.connect("db.db")  
     cursor = conn.cursor()
     cursor.execute("INSERT INTO cart (cid,pid,qty,color,size,name,price)VALUES (?,?,?,?,?,?,?)",(CID,pid,qty,color,size,name,price) )
     conn.commit()
     return redirect(url_for("dhome"))
@app.route('/cart')
def cart():
 CID = request.cookies.get('CID')
 if not CID or CID == "0":
        return redirect(url_for("login"))
 else:
     con = sqlite3.connect("db.db")
     cur = con.cursor()
     cur.execute("SELECT * FROM cart WHERE cid = ?", (CID,))

     prods = list(cur.fetchall())
     con.close() 
     total = 0
     for i in prods:
        total=total+(i[2]*i[6])
     return(render_template('cart.html',prods=prods,total=total))  
@app.route('/pay')
def pay():
     total=request.args.get('total')
     success_url = url_for('buy', _external=True)
     failure_url = url_for('errpay', _external=True)
     total = float(total)  
     qtp = str(int(total / 50))
     checkout = chargily.create_checkout(Checkout(items=[{"price": '01jn8d3dkh8sxmcaw1416tb4k8', "quantity": qtp}],success_url=success_url,failure_url=failure_url))
     print(checkout)
     return redirect(checkout["checkout_url"])
     
@app.route('/delcar') 
def delcar():
 CID = request.cookies.get('CID')
 if not CID or CID == "0":
        return redirect(url_for("login"))
 else:
   
   pid = int(request.args.get('pid'))
   size = request.args.get('size')
   qty = int(request.args.get('qty'))
   color = request.args.get('color')
   if color and qty and pid:
        conn = sqlite3.connect("db.db") 
        cursor = conn.cursor()
        cursor.execute("DELETE FROM cart WHERE cid = ? AND color = ? AND qty = ? AND pid = ? ", (int(CID), color, qty, pid))
        conn.commit()
        cursor.close()
        return redirect(url_for('cart'))
@app.route('/details') 
def details():
 CID = request.cookies.get('CID')
 if not CID or CID == "0":
        return redirect(url_for("login"))
 else:
     pid = request.args.get('pid')
     pid=int(pid)
     conn = sqlite3.connect("db.db")  
     cursor = conn.cursor()
     cursor.execute("SELECT * FROM prod WHERE pid = ?", (pid,))
     row = cursor.fetchone()
     if row is None:  return("""
            <html>
            <body >
              📢 اك غالط 
              
              <a href="/admin">ارجع</a></body>
            </html>
            """)
     else: 
        row=list(row)
        return render_template('details.html',row=row,CID=CID)
@app.route('/delprod') 
def delprod():
 CID = request.cookies.get('CID')
 if CID != "admin":
        return redirect(url_for("login"))
 else:
     pid = request.args.get('pid')
     pid=int(pid)
     conn = sqlite3.connect("db.db")  
     cursor = conn.cursor()
     cursor.execute("DELETE FROM prod WHERE pid = ?", (pid,))
     conn.commit()
     conn.close()
     return redirect(url_for("admin"))
@app.route('/login') 
def login():
     resp = make_response(render_template('login.html'))
     resp.delete_cookie('CID')
     return resp
@app.route('/checko') 
def checko():
    email = request.args.get('email')
    passe = request.args.get('pass')

    if passe == "admin" and email == "admin": 
        resp = make_response(render_template('admino.html'))
        resp.set_cookie("CID", "admin")
        return resp

    con = sqlite3.connect("db.db")
    cur = con.cursor()

    cur.execute("SELECT * FROM cli WHERE email=?", (email,))
    sdata = cur.fetchone()  

    con.close()  

    if sdata:  
        if sdata[2] == passe: 
            resp = make_response(redirect(url_for("dhome")))
            resp.set_cookie("CID", str(sdata[0]))
            return resp

   
    return render_template('login.html', X="incorrect")
@app.route('/admin') 
def admin():
    CID = request.cookies.get('CID')  

    if CID != "admin":
        return redirect(url_for("login"))
    else:
     return render_template('admin.html')  
@app.route('/insc') 
def insc():
 email=request.args.get('email')
 passw = str(pass_gen(8))

 addr=request.args.get('add')
 tel=int(request.args.get('tel'))
 fname=request.args.get('fname')
 emailo(passw, email,fname)
 con = sqlite3.connect("db.db")
 cur = con.cursor() 
 cur.execute("INSERT INTO cli (fname,email,passw,addr,tel,totals)VALUES (?,?,?,?,?,?)",(fname,email,passw,addr,tel,0.0) )
 con.commit()
 
 return render_template('login.html',X="signup completed password was sent to the email")
@app.route('/ajp') 
def ajp():
    CID = request.cookies.get('CID')  
    if CID != "admin":
        return redirect(url_for("login"))
    else:
     name = request.args.get('name')
     disc = request.args.get('disc')
     prix=float(request.args.get('prix'))
     type=request.args.get('type')
     con = sqlite3.connect("db.db")
     cur = con.cursor()
     cur.execute("INSERT INTO prod (name,disc,prix,type)VALUES (?,?,?,?)",(name,disc,prix,type) )
     con.commit()
     return redirect(url_for("admin"))
@app.route('/buy')
def buy():
    CID = request.cookies.get('CID')  
    if not CID or CID==0:
        return redirect(url_for("login"))
    else:
     con = sqlite3.connect("db.db")
     cur = con.cursor()
     cur.execute("SELECT * FROM cart WHERE cid = ?", (CID,))

     prods = list(cur.fetchall())
     totalss=0
     for item in prods :
        totalss=totalss+(item[6]*item[2])
        cur.execute(""" INSERT INTO com (cid, pid, qty, size, color,name,price) VALUES (?, ?, ?, ?, ?,?,?)""", (item[0], item[1], item[2], item[3], item[4],item[5],item[6]))
        con.commit()
     cur.execute("DELETE FROM cart WHERE cid = ?", (int(CID),))
     
     con.commit()
     cur.execute("SELECT totals FROM cli WHERE clid=(?)",(CID,))
     totals = totalss+float(list(cur.fetchone())[0])
     print(totals)
     cur.execute("UPDATE cli SET totals = ? WHERE clid = ?", (totals, int(CID)))
     
     con.commit()
     con.close()
     return redirect(render_template('succespay.html'))
@app.route('/errpay')
def errpay():
   return render_template('unsecpay.html')
def get_clients_with_total():
    CID = request.cookies.get('CID')  
    if not CID or CID==0:
        return redirect(url_for("login"))
    else:
     conn = sqlite3.connect("db.db")  
     cur = conn.cursor()
    
     cur.execute("""
         SELECT clid, totals FROM cli WHERE totals > 0
     """)
    
     clients = cur.fetchall()
     conn.close()
     return clients

@app.route("/commandes")
def commandes():
    CID = request.cookies.get('CID')  
    if not CID or CID==0:
        return redirect(url_for("login"))
    else:
     clients = get_clients_with_total()
     return render_template("commandes.html", clients=clients)


def get_user_info(clid):
 
    conn = sqlite3.connect("db.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM cli WHERE clid = ?", (clid,))
    user = cursor.fetchone()
    
    cursor.execute("SELECT * FROM com WHERE cid = ?", (clid,))
    purchases = cursor.fetchall()
    
    conn.close()
    return user, purchases

@app.route("/fact")

def user_profile():
 CID = request.cookies.get('CID')
 if CID != "admin":
        return redirect(url_for("login"))
 else:
    clid = request.args.get('clid')
    user, purchases = get_user_info(clid)
    
    if not user:
        return "Utilisateur non trouvé", 404
    
    return render_template("fact.html", user=user, purchases=purchases)

@app.route("/factimp")

def user_profileimp():
 CID = request.cookies.get('CID')
 if CID != "admin":
        return redirect(url_for("login"))
 else:
    clid = request.args.get('clid')
    user, purchases = get_user_info(clid)
    
    if not user:
        return "Utilisateur non trouvé", 404
    
    return render_template("factimp.html", user=user, purchases=purchases)
@app.route("/delefact")
def delefact():
 CID = request.cookies.get('CID')
 if CID != "admin":
        return redirect(url_for("login"))
 else:
   clid = request.args.get('clid')
   con = sqlite3.connect("db.db")
   cur = con.cursor()
   cur.execute("DELETE FROM com WHERE cid = ?", (int(clid),))
   con.commit()
   cur.execute("UPDATE cli SET totals = ? WHERE clid = ?", (0.0, int(clid)))
     
   con.commit()
   return redirect(url_for('commandes'))
@app.route('/userf')
def userf():
 CID = request.cookies.get('CID')
 if CID != "admin":
        return redirect(url_for("login"))
 else:
   tel=request.args.get('tel')
   con = sqlite3.connect("db.db")
   cur=con.cursor()
   try:
        cur.execute("SELECT clid FROM cli WHERE tel=?", (tel,))  # Pas de int()
        x = cur.fetchone()

        if x is None:  
            return """
            <html>
            <body >
              📢 عطاك نومرو غالط 
              
              <a href="/admin">ارجع</a></body>
            </html>
            """
       

        clid = x[0]  
        return redirect(f"/fact?clid={clid}")

   finally:
        con.close() 
@app.route('/rst')
def rst():
    con = sqlite3.connect("db.db")
    cur = con.cursor()
    
    email = request.args.get('email')
    cur.execute("SELECT passw FROM cli WHERE email=?", (email,))
    result = cur.fetchone()
    
    con.close()

    if result:  

        emailo(result[0], email,"")
        X="password is sent to your email"
        return render_template('login.html',X=X)
    else:
        X="Email non trouvé"
        return render_template('login.html',X=X)
@app.route('/changepass')
def changepass():
 CID = request.cookies.get('CID')
 if not CID :
        return redirect(url_for("login"))
 else: 
    pas = request.args.get('pas')
    conn = sqlite3.connect('db.db')
    cursor = conn.cursor()
    
    query = "UPDATE cli SET passw = ? WHERE clid = ?"
    cursor.execute(query, (pas, CID))
    
    conn.commit()
    conn.close()
    return redirect(url_for('dhome'))
 
  
@app.errorhandler(404)
def page_not_found(e):
    return redirect(url_for("dhome")), 404
    
if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0")