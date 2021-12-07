from flask import url_for, redirect
from flask_login import UserMixin, AnonymousUserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from flask import abort

import json
from bson.json_util import ObjectId


class Tags():
	def __init__(self, tags_dict=None):
		if tags_dict == None:
			self.tags = {
				'clothes': 0,
				'electronics': 0,
				'school supply': 0,
				'miscellaneous': 0
			}
		else:
			self.tags = tags_dict
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super(MyEncoder, self).default(obj)

class Permission:
	guest = 0
	verified = 1
	mod = 2
	admin = 3

class Product():
  def __init__(self, product_info):
    self.id = product_info['_id']
    self.title = product_info['title']
    self.price = float(product_info['price'])
    self.image_link = product_info['image_link']
    self.description = product_info['description']
    self.tags = product_info['tags']
    self.seller_id = product_info['seller_id']
    self.sold = product_info['sold']
    self.post_date = product_info['post_date']
class User(UserMixin):

	def __init__(self, user_info):
		self.id = user_info['_id']
		self.password_hash = user_info['password_hash']
		self.firstName = user_info['firstName']
		self.lastName = user_info['lastName']
		self.email = user_info['email']
		self.permission = user_info['permission']
		self.score = user_info['score']
		self.vote_counts = user_info['vote_counts']
		self.favorites = user_info['favorites']
		self.token = user_info['token']
		self.img_link = user_info['img_link']
		self.bio = user_info['bio']
		self.title = user_info['title']

	def __repr__(self):
		return '<User {} {}>'.format(self.firstName, self.lastName)

	@property
	def password(self):
		raise AttributeError('Password is not a readable attribute.')

	@password.setter
	def password(self, password):
		self.password_hash = generate_password_hash(password)

	def verify_password(self, password):
		return check_password_hash(self.password_hash, password)

	def is_admin(self):
		return self.permission == Permission.admin

	def is_authenticated(self):
		return True
	def is_active(self):
		return True
	def is_anonymous(self):
		return False
	def get_id(self):
		return self.id


class AnonymousUser(AnonymousUserMixin):

	def __init__(self):
		self.permission = 0

	def is_admin(self):
		return False
	def is_authenticated(self):
		return False
	def is_active(self):
		return False
	def is_anonymous(self):
		return True
	def get_id(self):
		return 'None'





'''
Authentication decorators
'''

def permission_required(permission): 
	def decorator(f):
		@wraps(f)
		def decorated_function(*args, **kwargs):
			if not current_user.permission >= permission:
				abort(403)
			return f(*args, **kwargs)
		return decorated_function
	return decorator

def login_required(f): 
	@wraps(f)
	def decorated_function(*args, **kwargs):
		if current_user.is_anonymous():
			return redirect(url_for('login'))
		return f(*args, **kwargs)
	return decorated_function

def admin_required(f):
	return permission_required(Permission.admin)(f)