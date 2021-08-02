from Cryptodome.Signature import pss
from Pyfhel import Pyfhel, PyPtxt, PyCtxt
from Cryptodome.Hash import SHA256
from Cryptodome.PublicKey import RSA
from Cryptodome.Cipher import AES, PKCS1_OAEP


class Supplier:
    def __init__(self):
        self.encryption = Pyfhel()
        self.encryption.contextGen(p=65537)
        self.encryption.keyGen()
        self.userDict = {}
        self.rsa_private_key = RSA.generate(2048)

    def load_users(self, users):
        for user in users:
            self.userDict[user.name] = {'name': user.name, 'bill': self.encryption.encryptFrac(0),
                                        'pub_key': user.get_public_key()}
            print("supplier loaded: " + str(self.userDict[user.name]['name']))

    def get_homo_pub_key(self):
        return self.encryption.to_bytes_publicKey()

    def get_user_bill_decrypted(self, user_name):
        return round(self.encryption.decryptFrac(self.userDict[user_name]['bill']), 2)

    def get_user_bill_encrypted(self, user_name):
        return self.userDict[user_name]

    def get_rsa_pub_key(self):
        return self.rsa_private_key.publickey().exportKey()

    def update_bill(self, user_name, period_bill):
        self.userDict[user_name]['bill'] += period_bill

    def print_bills(self):
        for user in self.userDict:
            print("From Supplier: User: " + self.userDict[user]['name'] + " bill: " +
                  str(round(self.encryption.decryptFrac(self.userDict[user]['bill']), 2)))

    def verify_receive(self, user_name, enc_session_key, nonce, tag, ciphertext, signature):
        user = self.userDict[user_name]

        cipher_rsa = PKCS1_OAEP.new(self.rsa_private_key)
        session_key = cipher_rsa.decrypt(enc_session_key)

        # Decrypt the data with the AES session key
        cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
        hashed_bill = cipher_aes.decrypt_and_verify(ciphertext, tag)

        user_pub_key = RSA.importKey(user['pub_key'])
        verifier = pss.new(user_pub_key)
        verifier.verify(hashed_bill, signature)



