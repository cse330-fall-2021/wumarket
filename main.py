import os
import re
import datetime
import secrets
from flask import Flask, render_template, request, redirect, url_for, abort, send_from_directory, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
# from flask_pymongo import PyMongo
from pymongo import MongoClient
from flask_login import LoginManager, current_user, login_user, logout_user
from forms import NewProductForm, LoginForm, SignUpForm, ValidateForm, editProductForm, editProfileForm
from models import User, AnonymousUser, permission_required, admin_required, CustomJSONEncoder, login_required, Product
from bson.json_util import ObjectId
from flask_mail import Mail, Message
from flask_socketio import SocketIO
from flask_socketio import emit, join_room, leave_room
import time
from flask_wtf.csrf import CSRFProtect


class Config:
	SECRET_KEY = '7d441f27d441f27567d441f2b6176a'
	MAIL_SERVER = 'smtp.gmail.com'
	MAIL_PORT = 587
	MAIL_USE_TLS = True
	MAIL_USERNAME = 'wumarket889@gmail.com'
	MAIL_PASSWORD = 'wumarket!'
	RESUME_LINK = os.environ.get("RESUME_LINK")
	MAIL_DEFAULT_SENDER = 'wumarket889@gmail.com'
	TESTING = False

mail = Mail()
app = Flask(__name__)
app.config.from_object(Config)
app.json_encoder = CustomJSONEncoder
mail.init_app(app)

# Login stuff
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.session_protection = 'strong'
login_manager.login_view = 'login'
login_manager.anonymous_user = AnonymousUser

# socketio
socketio = SocketIO()
socketio.init_app(app, cors_allowed_origins='*')

#csrf
# csrf = CSRFProtect()
# csrf.init_app(csrf)
# @csrf.error_handler
# def csrf_error(reason):
# 	return 'not allowed'

@login_manager.user_loader
def load_user(id):
	id = ObjectId(id)
	queried_user = db.Users.find_one({"_id":id})
	user = User(queried_user)
	return user

# initialize mongo db
uri = "mongodb://wumarket-shard-00-00.k8wsz.mongodb.net:27017,wumarket-shard-00-01.k8wsz.mongodb.net:27017,wumarket-shard-00-02.k8wsz.mongodb.net:27017/myFirstDatabase?ssl=true&replicaSet=atlas-b73qmr-shard-0&authSource=%24external&authMechanism=MONGODB-X509&retryWrites=true&w=majority"
certificate_path = './X509-cert-5700102249016803480.pem'
client = MongoClient(uri,
										 tls=True,
										 tlsCertificateKeyFile=certificate_path)
db = client['WUmarket']


# views
@app.route('/', methods=['GET'])
@login_required
def index():
	products = db.Products.find(None)
	return render_template('main.html', items=products, db=db)


@app.route('/my_products', methods=['GET'])
@login_required
def my_products():
	products = db.Products.find({"seller_id": ObjectId(current_user.id)})
	return render_template('my_products.html', items=products, db=db)

@app.route('/favorites', methods=['GET'])
@login_required
def favorites():
	user = load_user(current_user.id)
	products = db.Products.find({"_id": {"$in": user.favorites}})
	return render_template('main.html', items=products, db=db)

@app.route('/login', methods=['GET', 'POST'])
def login():
	form = LoginForm()
	if request.method == "POST":
		email = request.form['email']
		password = request.form['password']
		queried_user = db['Users'].find_one({"email":email})
		hashed_pw = queried_user['password_hash']
		if check_password_hash(hashed_pw, password):
			user = User(queried_user)
			if user.permission == 0:
				print("must verify email")
				return redirect(url_for('login'))
			else:
				login_user(user)
				print("Login successfully")
				return redirect(url_for('index'))
		else:
			print("Wrong credentials")
			return redirect(url_for('login'))
	return render_template('login.html', form=form)


@app.route('/logout', methods=['GET'])
@login_required
def logout():
		logout_user()
		return redirect(url_for('index'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
	form = SignUpForm()
	if request.method == "POST":
		firstName = request.form['firstName']
		lastName = request.form['lastName']
		password = request.form['password']
		email = request.form['email']
		email_regex = re.compile(r"^[\w!#$%&'*+/=?^_`{|}~-]+@([\w\-]+(?:\.[\w\-]+)+)$")
		domain_from_email = None
		match = email_regex.match(email)
		if match is not None:
			domain_from_email = match.group(1)
		if (domain_from_email is not None) and (domain_from_email != 'wustl.edu'):
			return "<h1> Email is not a valid WashU email </h1>", 400
		token = secrets.token_hex(10)
		pw_hash = generate_password_hash(password)
		new_user = {
					 'firstName': firstName,
					 'lastName': lastName,
					 'password_hash': pw_hash,
					 'email': email,
			# the permission is 0 until confirmed
					 'permission': 0,
					 'img_link': 'https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/f/271deea8-e28c-41a3-aaf5-2913f5f48be6/de7834s-6515bd40-8b2c-4dc6-a843-5ac1a95a8b55.jpg?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1cm46YXBwOjdlMGQxODg5ODIyNjQzNzNhNWYwZDQxNWVhMGQyNmUwIiwiaXNzIjoidXJuOmFwcDo3ZTBkMTg4OTgyMjY0MzczYTVmMGQ0MTVlYTBkMjZlMCIsIm9iaiI6W1t7InBhdGgiOiJcL2ZcLzI3MWRlZWE4LWUyOGMtNDFhMy1hYWY1LTI5MTNmNWY0OGJlNlwvZGU3ODM0cy02NTE1YmQ0MC04YjJjLTRkYzYtYTg0My01YWMxYTk1YThiNTUuanBnIn1dXSwiYXVkIjpbInVybjpzZXJ2aWNlOmZpbGUuZG93bmxvYWQiXX0.BopkDn1ptIwbmcKHdAOlYHyAOOACXW0Zfgbs0-6BY-E',
					 'score': 0,
					 'vote_counts': 0,
					 'token': token,
					 'favorites': [],
					 'bio': '',
					 'title': 'student'
					}
		users = db.Users
		if users.find_one({"email":email}):
			return "<h1> Email already used </h1>", 400
		new_user_id = users.insert_one(new_user).inserted_id
		msg = Message("Verify your WashU email", recipients=[email])
		base_url = request.url_root[:-1]
		msg.body = "Your verification code is: " + token + "\nVisit " +  base_url + url_for('validate') + " to validate."
		mail.send(msg)
		print("create new user with id", new_user_id)
		return redirect(url_for('validate'))
	return render_template('signup.html', form=form)

@app.route('/validate', methods=['GET', 'POST'])
def validate():
	form = ValidateForm()
	if request.method == "POST":
		user_token = request.form['token']
		email = request.form['email']
		if email is not None:
			queried_user = db['Users'].find_one({"email":email})
			user = User(queried_user)
			if user_token == user.token:
				db.Users.update_one({'_id': user.id}, {'$set': {'permission': 1}})
		else:
			return  "<h1> Email invalid </h1>", 400
		return redirect(url_for('index'))
	return render_template('validate.html', form=form)



@app.route('/add_product', methods=['GET', 'POST'])
@login_required
def add_product():
	form = NewProductForm()
	if request.method == "POST":
		print("form submitted")
		cur_time = str(datetime.datetime.now())
		# to get datetime object, datetime.datetime.strptime(cur_time, '%Y-%m-%d %H:%M:%S.%f')
		new_product = {
					 'title': request.form['title'],
					 'price': request.form['price'],
					 'image_link': request.form['image_link'],
					 'description': request.form['description'],
					 'tags': [],
					 'seller_id': current_user.id,
					 'sold': False,
					 'post_date': cur_time
					}

		new_product_id = db.Products.insert_one(new_product).inserted_id
		print("create new product with id", new_product_id)
		return redirect(url_for('index'))

	return render_template('new_post.html', form=form)

@app.route('/add_favorite/<item_id>')
def add_favorite(item_id):
	print("received: ", item_id)
	print(type(item_id))
	item_id = ObjectId(item_id)
	user = load_user(current_user.id)
	if (item_id in user.favorites):
		db.Users.update_one({'_id': current_user.id}, {'$pullAll': {'favorites': [item_id]}})
	else:
		db.Users.update_one({'_id': current_user.id}, {'$push': {'favorites': item_id}})
	return redirect(url_for('index'))

@app.route('/view_profile/<profile_id>', methods=['GET'])
def view_profile(profile_id):
	profile_id = ObjectId(profile_id)
	profile = db.Users.find_one({"_id": profile_id})
	user = User(profile)
	products = db.Products.find({"seller_id": profile_id})
	current_id = current_user.id
	return render_template('view_profile.html', profile=user, items=products, current_id=current_id, db=db)

@app.route('/delete_product/<item_id>')
def delete_product(item_id):
	print("received: ", item_id)
	item_id = ObjectId(item_id)
	db.Products.delete_one({'_id': item_id})
	return redirect(url_for('my_products'))

@app.route('/edit_product/<item_id>', methods=['GET', 'POST'])
def edit_product(item_id):
	form = editProductForm()
	item_id = ObjectId(item_id)
	product = db.Products.find_one({"_id": item_id})

	if request.method == "POST":
		print("form submitted")
		sold = request.form['sold']
		if (sold == 'True'):
			sold = True
		else:
			sold = False
		updated_data = {
		'title': request.form['title'],
		'price': request.form['price'],
		'image_link': request.form['image_link'],
		'description': request.form['description'],
		'sold': sold
		}
		db.Products.update_one({'_id': item_id}, {'$set': updated_data})
		return redirect(url_for('my_products'))
	else:
		product = Product(product)
		form.title.data = product.title
		form.price.data = product.price
		form.image_link.data = product.image_link
		form.description.data = product.description
		return render_template('edit_product.html', form=form)

@app.route('/edit_profile/<user_id>', methods=['GET', 'POST'])
def edit_profile(user_id):
	form = editProfileForm()
	user_id = ObjectId(user_id)
	profile = db.Users.find_one({"_id": user_id})
	if request.method == "POST":
		print("form submitted")
		updated_data = {
		'firstName': request.form['firstName'],
		'lastName': request.form['lastName'],
		'img_link': request.form['img_link'],
		'bio': request.form['bio'],
		'title' : request.form['title']
		}
		db.Users.update_one({'_id': user_id}, {'$set': updated_data})
		return redirect(url_for('view_profile', profile_id=user_id))
	else:
		user = User(profile)
		form.firstName.data = user.firstName
		form.lastName.data = user.lastName
		form.img_link.data = user.img_link
		form.bio.data = user.bio
		form.title.data = user.title
		return render_template('edit_profile.html', form=form)

	print("received: ", item_id)
	print(type(item_id))
	item_id = ObjectId(item_id)
	db.Users.update_one({'_id': current_user.id}, {'$push': {'favorites': item_id}})
	return redirect(url_for('index'))

@app.route('/chats')
def chats():
	cur_id = current_user.id
	chat_history = list(db.Chats.find({'user1_id': cur_id})) + list(db.Chats.find({'user2_id': cur_id}))
	chat_history.sort(key=lambda x: x['timestamp'])

	chat_heads = []
	for chat in chat_history:
		other_user_id = chat['user1_id']
		if cur_id == other_user_id:
			other_user_id = chat['user2_id']
		other_user = db.Users.find_one({'_id': other_user_id})
		other_user_name = '{} {}'.format(other_user['firstName'], other_user['lastName'])
		other_user_img_link = other_user['img_link']
		chat_heads.append({'name': other_user_name,
							'img_link': other_user_img_link,
							'id': str(other_user_id)})

	return render_template('chats.html', chat_heads=chat_heads)


@app.route('/change_chathead', methods=['POST'])
def change_chathead():
	print("change chathead called")
	session['other_id'] = request.form['other_user_id']

	other_user_id = ObjectId(request.form['other_user_id'])
	cur_id = current_user.id
	if str(cur_id) >= str(other_user_id):
		chat_history = db.Chats.find_one({'user1_id': cur_id,
											'user2_id': other_user_id})
	else:
		chat_history = db.Chats.find_one({'user1_id': other_user_id,
											'user2_id': cur_id})
	messages = chat_history['messages']
	cur_id = str(current_user.id)
	other_id = session['other_id']
	room_id = str(cur_id) + str(other_user_id)
	session['room_id'] = room_id

	# join_room(room_id)
	return jsonify({'messages': messages,
					'cur_user_id': str(cur_id)})

@app.route('/add_message', methods=['POST'])
def add_message():
	# a = request.args.get('a', 0, type=int)
	# print(a)
	print('add_message called')
	if request.method == "POST":
		print("post received")
		cur_id = current_user.id
		other_id = ObjectId(session['other_id'])
		newMes = request.form['message']
		newMesObj = {'message': newMes,
					'sender_id': cur_id}

		user1_id = other_id
		user2_id = cur_id
		if str(cur_id) >= session['other_id']:
			user1_id = cur_id
			user2_id = other_id

		if db.Chats.find_one({'user1_id': user1_id, 'user2_id': user2_id}) is not None:
			db.Chats.update_one({'user1_id': user1_id,
									'user2_id': user2_id},
										{'$push': {'messages': newMesObj},
										 '$set': {'timestamp': time.time()}
								})
		else:
			db.Chats.insert_one({	'user1_id': user1_id,
									'user2_id': user2_id,
									'messages': [newMesObj],
									'timestamp': time.time()
								})

	return jsonify(status='Done')


@app.route('/redicrect_new_message/<seller_id>', methods=['GET'])
def redicrect_new_message(seller_id):
	cur_id = current_user.id
	other_id = ObjectId(seller_id)

	if cur_id == other_id:
		return redirect(url_for('index'));

	user1_id = other_id
	user2_id = cur_id
	if str(cur_id) >= str(other_id):
		user1_id = cur_id
		user2_id = other_id

	if db.Chats.find_one({'user1_id': user1_id, 'user2_id': user2_id}) is None:
		db.Chats.insert_one({	'user1_id': user1_id,
								'user2_id': user2_id,
								'messages': [],
								'timestamp': time.time()
							})
	return redirect(url_for('chats'))


@app.route('/private/<path:filename>')
def private(filename):
	file_folder = os.path.join(os.getcwd(), 'private')
	# print("sending", filename, "form", file_folder)
	return send_from_directory(
			file_folder,
			filename
		)

clients = dict()
@socketio.on('joined', namespace='/chats')
def joined(message):
	print("joined called")
	cur_id = str(current_user.id)
	other_id = session['other_id']
	clients[cur_id] = request.sid
	if cur_id >= other_id:
		room_id =(cur_id + other_id)
	else:
		room_id = other_id + cur_id
	session['room_id'] = room_id
	print("cur_room: ", room_id)
	join_room(room_id)

@socketio.on('broadcastMessage', namespace='/chats')
def incomingMessage(message):
	other_sid = clients.get(session['other_id'])
	if other_sid is not None:
		room_id = session.get('room_id')
		print("broadcasting message to {} room. Content: {}".format(room_id, message['msg']))
		emit('incomingMessage', {'msg': message['msg'], 'sender_id': str(current_user.id)}, room=room_id)
	else:
		print("Nothing to broadcast, the other user is not online.")


# @app.route('/<anything>')
# def abort_404(anything):
# 	return abort(404)



if __name__ == "__main__":
		socketio.run(app, host='0.0.0.0', port=5000)
