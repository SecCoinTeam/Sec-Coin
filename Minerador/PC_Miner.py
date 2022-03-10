import os
import socket
import sys  
import time
import xxhash  

soc = socket.socket()
soc.settimeout(10)

username = input("Enter your SecCoin name: ")

while True:
    try:

        soc.connect((str("159.65.220.57"), int("2811")))
        server_version = soc.recv(3).decode()  
        print("Server is on version", server_version)

        
        while True:
            
            soc.send(bytes(
                "JOBXX,"
                + str(username)
                + ",NET",
                encoding="utf8"))
            
            job = soc.recv(1024).decode().rstrip("\n")

            job = job.split(",")
            difficulty = job[2]

            hashingStartTime = time.time()
            for ducos1xxres in range(100 * int(difficulty) + 1):
                
                ducos1xx = xxhash.xxh64(
                    str(job[0])
                    + str(ducos1xxres),
                    seed=2811).hexdigest()

                
                if job[1] == ducos1xx:
                    hashingStopTime = time.time()
                    timeDifference = hashingStopTime - hashingStartTime
                    hashrate = ducos1xxres / timeDifference

                    
                    soc.send(bytes(
                        str(ducos1xxres)
                        + ","
                        + str(hashrate) +
                        ",Minimal PC Miner (XXHASH)",
                        encoding="utf8"))

                    
                    feedback = soc.recv(1024).decode().rstrip("\n")
                    
                    if feedback == "GOOD":
                        print("Accepted share",
                              ducos1xxres,
                              "Hashrate",
                              int(hashrate/1000),
                              "kH/s",
                              "Difficulty",
                              difficulty)
                        break
                    
                    elif feedback == "BAD":
                        print("Rejected share",
                              ducos1xxres,
                              "Hashrate",
                              int(hashrate/1000),
                              "kH/s",
                              "Difficulty",
                              difficulty)
                        break

    except Exception as e:
        print("Error occured: " + str(e) + ", restarting in 5s.")
        time.sleep(5)
        os.execv(sys.argv[0], sys.argv)