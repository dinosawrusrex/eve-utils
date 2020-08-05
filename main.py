import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate("./english-vocabulary-exercises-firebase-adminsdk-mjz1s-3da7e79e6c.json")
app = firebase_admin.initialize_app(cred)

store = firestore.client(app)

for doc in store.collection('top-level-categories').list_documents():
    print(doc.get().get('name'))
