from time import process_time
from Pyfhel import Pyfhel, PyPtxt, PyCtxt

encryption = Pyfhel()
encryption.contextGen(p=65537)
encryption.keyGen()


integer1 = 2
integer2 = 2
ctxt1 = encryption.encryptInt(integer1) # Encryption makes use of the public key
ctxt2 = encryption.encryptInt(integer2) # For integers, encryptInt function is used.


summ = ctxt1 * ctxt2
summ2 = summ * ctxt2

for i in range(100):
      # Start the stopwatch / counter
      t1_start = process_time()


      summ2 = summ * summ2

      # Stop the stopwatch / counter
      t1_stop = process_time()

      print("Elapsed time:", t1_stop, t1_start)

      print("Elapsed time during the whole program in seconds:",
            t1_stop-t1_start)