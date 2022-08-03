from flask import Flask, render_template, request, redirect, url_for, flash
from flask import session as login_session
import pyrebase

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = 'super-secret-key'

config = {
  "apiKey": "AIzaSyCaezKQWTK2Y5Hl8NRbTV9_ympFrvgwLwk",
  "authDomain": "cs-personal-project.firebaseapp.com",
  "databaseURL": "https://cs-personal-project-default-rtdb.europe-west1.firebasedatabase.app",
  "projectId": "cs-personal-project",
  "storageBucket": "cs-personal-project.appspot.com",
  "messagingSenderId": "507433844433",
  "appId": "1:507433844433:web:0472d6d5acbc2a6f278ff0",
  "measurementId":"G-7CVSDVSDHV",
}
firebase=pyrebase.initialize_app(config)
auth=firebase.auth()
db=firebase.database()
#Code goes below here

@app.route('/', methods=['GET', 'POST'])
def signin():
	if request.method=='POST':
		email=request.form['email']
		password=request.form['password']
		try:
			login_session['user']=auth.sign_in_with_email_and_password(email,password)
			return redirect(url_for('home'))
		except:
			print("signin error")
	return render_template("signin.html")

@app.route('/signup', methods=['GET', 'POST'])
def signup():
	if request.method=='POST':
		email=request.form['email']
		password=request.form['password']
		verify_password=request.form['verify_password']
		username=request.form['username']
		try:
			if password==verify_password:
				login_session['user']=auth.create_user_with_email_and_password(email,password)
				user = {'email':email,'password':password,'username':username}
				db.child('Users').child(login_session['user']['localId']).set(user)
				return redirect(url_for('home'))
			return render_template("signup.html",failed_verify=True)
		except:
			print("sign up error")
	return render_template("signup.html",failed_verify=False)

@app.route('/signout')
def signout():
	login_session['user']=None
	auth.current_user=None
	return redirect(url_for('signin')) 

@app.route('/add_video', methods=['GET', 'POST'])
def add_video():
	if request.method=='POST':
		videoLink=request.form["videoLink"]
		title=request.form['title']
		description=request.form['description']
		try:
			video = {"title":title,"description":description,"uid":login_session['user']['localId'],"videoLink":videoLink,"username":db.child('Users').child(login_session['user']['localId']).child("username").get().val()}
			db.child('Videos').push(video)
			return redirect(url_for("all_tweets"))
		except:
			print("adding error")
	return render_template("add_video.html")

@app.route("/home")
def home():
	videos=db.child('Videos').get().val()
	users=db.child('users').get().val()
	return render_template("home.html",videos=videos,users=users)

@app.route("/search",methods=['GET', 'POST'])
def search():
	videos=db.child('Videos').get().val()
	users=db.child('users').get().val()
	if request.method=="POST":
		videos_list=""
		search=request.form['search']
		for i in videos:
			if search==videos[i]["title"] or search in videos[i]["description"] or search==videos[i]["videoLink"] or search==videos[i]["username"]:
				videos_list.append(videos[i])
		return render_template("search.html",videos=videos,users=users,videos_list=videos_list)
	return render_template("search.html",videos=videos,users=users)

@app.route("/profile")
def profile():
	users=db.child("users").get().val()
	videos=db.child("videos").get().val()
	return render_template("profile.html",videos=videos,users=users)

@app.route("/profile/settings",methods=['GET', 'POST'])
def profile_settings():
	user=db.child("Users").child(login_session['user']['localId']).get().val()
	if request.method=="POST":
		changed={'password':"",'username':""}
		for i in changed:
			if request.form[i]!=changed[i]:
				update={i:request.form[i]}
				db.child("Users").child(login_session['user']['localId']).update(update)
				login_session['user'][i]=request.form[i]
		return redirect(url_for('profile'))
	return render_template("profile_settings.html",username=user['username'],password=user['password'])


#Code goes above here

if __name__ == '__main__':
	app.run(debug=True)