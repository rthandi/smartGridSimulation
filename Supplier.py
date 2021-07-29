from Pyfhel import Pyfhel, PyPtxt, PyCtxt

class Supplier:
    def __init__(self):
        self.encryption = Pyfhel()
        self.encryption.contextGen(p=65537)
        self.encryption.keyGen()
        self.userDict = {}

    def load_users(self, users):
        for user in users:
            self.userDict[user.name] = {'name': user.name, 'bill': self.encryption.encryptFrac(0)}
            print("supplier loaded: " + str(self.userDict[user.name]['name']))

    def get_pub_key(self):
        return self.encryption.to_bytes_publicKey()

    def get_user_bill_decrypted(self, user_name):
        return round(self.encryption.decryptFrac(self.userDict[user_name]['bill']), 2)

    def get_user_bill_encrypted(self, user_name):
        return self.userDict[user_name]

    def update_bill(self, user_name, period_bill):
        self.userDict[user_name]['bill'] += period_bill

    def print_bills(self):
        for user in self.userDict:
            print("From Supplier: User: " + self.userDict[user]['name'] + " bill: " +
                  str(round(self.encryption.decryptFrac(self.userDict[user]['bill']), 2)))
