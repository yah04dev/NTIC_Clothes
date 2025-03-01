NTIC_Clothes is a web app for clothing store contains a lot of features like CIB DAHABIA paiment , bill printing , real email to send the password  and a lot of other things
NTIC_Clothes is based on python so you need to have python installed and install
Flask And sqlite3 And chargily_pay And smtplib
Using
```bash
pip install flask
```
```bash
pip install sqlite3
```
```bas
pip install smtplib
```
```bash
pip install chargily_pay
```
After installing dependencies 
start the server by going to the path folder location in cmd or terminal and run
```bash
python app.py
```
the terminal will show you the server link
## Login
the server link will redirect always to the login page to login the first time and you can signup if not admin<br />
username:admin / password:admin<br />
you can change who is the admin from the sqlite db using a program like "DB BROWSER FOR sqlite"
unfortunatly you cant host sqlite into shared hosting but in a vps using gunicorn as an example
this code contains my email and my paiment api keys for test 
