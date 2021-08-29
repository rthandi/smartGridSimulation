from time import process_time
from Pyfhel import Pyfhel, PyPtxt, PyCtxt
from phe import paillier
print(paillier.__file__)

encryption = Pyfhel()
encryption.contextGen(p=65537, m=8192, base=2, intDigits=64, fracDigits = 32)
encryption.keyGen()
encryption.relinKeyGen(bitCount=60, size=5)

public_key, private_key = paillier.generate_paillier_keypair()

integer1 = 2.367
integer2 = 3.7858
ctxt1 = public_key.encrypt(integer1) # Encryption makes use of the public key
ctxt2 = public_key.encrypt(integer2) # For integers, encryptInt function is used.

committed_amount = encryption.encryptFrac(40)
trading_price = 2.756
real_amount = encryption.encryptFrac(35)
tariff = encryption.encryptFrac(10)

# summ = ctxt1 * ctxt2
# summ2 = summ * ctxt2
total = 0
sum = encryption.encryptFrac(0)
for i in range(500):
      # Start the stopwatch / counter
      t1_start = process_time()
      sum += (committed_amount * trading_price - ((real_amount - committed_amount) * tariff))
      encryption.relinearize(sum)
      # ctxt2 = public_key.encrypt(integer2) # For integers, encryptInt function is used.
      # hi = integer1 * 10000
      # summ2 = summ * summ2

      # Stop the stopwatch / counter
      t1_stop = process_time()
      print(encryption.decryptFrac(sum))

      print("Elapsed time:", t1_stop, t1_start)

      print("Elapsed time during the whole program in seconds:",
            t1_stop-t1_start)
      total += (t1_stop-t1_start)
print(str(total/500))