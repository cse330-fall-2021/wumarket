from pymongo import MongoClient
uri = "mongodb+srv://wumarket.k8wsz.mongodb.net/myFirstDatabase?authSource=%24external&authMechanism=MONGODB-X509&retryWrites=true&w=majority"
certificate_path = './X509-cert-5700102249016803480.pem'
client = MongoClient(uri,
                     tls=True,
                     tlsCertificateKeyFile=certificate_path)
db = client['WUmarket']
users = db['Users']

user = {"username": "bob",
		"password": "123",
		"firstname": "bob",
		"lastname": "ben" }

queried_user = users.find_one({"username":"hoang"})
print(queried_user)