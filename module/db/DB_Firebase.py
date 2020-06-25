from firebase_admin import credentials
from firebase_admin import firestore
import firebase_admin

# Private_key
#private_key = credentials.Certificate("./module/db/key/service-account.json")
private_key = credentials.Certificate("/app/module/db/key/service-account.json")


# 初始化firebase
firebase_admin.initialize_app(private_key)


class DBHelper():
    def __int__(self):
        self.db = None


    def connect(self):
        self.db = firestore.client()

    def set_create_user(self,Line_userid,token):
        self.connect()
        doc_ref = self.db.collection(u'Users').document(f'{Line_userid}')
        doc_ref.set({
            u'mc_token' : f'{token}'
        })


    def get_check_exists(self,Line_userid):
        self.connect()
        # [START get_check_exists]
        doc_ref = self.db.collection(u'Users').document(f'{Line_userid}')

        try:
            doc = doc_ref.get().to_dict()
            if doc != None:
                #print(u'Document data: {}'.format(doc.to_dict()))
                return doc
            else:
                return False
        except:
            print(u'No such document!')

        # [END get_check_exists]


    def get_allusers(self):

        self.connect()
        docs = self.db.collection('Users').stream()
        return docs



