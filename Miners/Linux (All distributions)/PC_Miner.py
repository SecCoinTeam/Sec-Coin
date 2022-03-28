import hashlib
import os
import socket
import sys  # Only python3 included libraries
import time
import ssl
import select

AVAILABLE_PORTS = [2811]
soc = None

username = input('Username?\n> ')
diff_choice = input(
    'Usar uma dificuldade baixa?[Use caso tiver um pc fraco]\n> ')
if diff_choice.lower == "n":
    NoDif = False
else:
    NoDif = True


def get_fastest_connection(server_ip: str):
    connection_pool = []
    available_connections = []
    for i in range(len(AVAILABLE_PORTS)):
        connection_pool.append(socket.socket())
        connection_pool[i].setblocking(0)
        try:
            connection_pool[i].connect((server_ip,
                                        AVAILABLE_PORTS[i]))
        except BlockingIOError as e:
            pass

    ready_connections, _, __ = select.select(connection_pool, [], [])

    while True:
        for connection in ready_connections:
            try:
                server_version = connection.recv(100)
            except:
                continue
            if server_version == b'':
                continue

            available_connections.append(connection)
            connection.send(b'PING')

        ready_connections, _, __ = select.select(available_connections, [], [])
        ready_connections[0].recv(100)
        ready_connections[0].settimeout(10)
        return ready_connections[0]


while True:
    try:
        print('Searching for fastest connection to the server')
        soc = get_fastest_connection(str("159.65.220.57"))
        print('Fastest connection found')

        # Mining section
        while True:
            if NoDif:
                # Send job request for lower diff
                soc.send(bytes(
                    "JOB,"
                    + str(username)
                    + ",MEDIUM",
                    encoding="utf8"))
            else:
                soc.send(bytes(
                    "JOB,"
                    + str(username),
                    encoding="utf8"))

            job = soc.recv(1024).decode().rstrip("\n")
            job = job.split(",")
            difficulty = job[2]

            hashingStartTime = time.time()
            base_hash = hashlib.sha1(str(job[0]).encode('ascii'))
            temp_hash = None

            for result in range(100 * int(difficulty) + 1):
                temp_hash = base_hash.copy()
                temp_hash.update(str(result).encode('ascii'))
                algo = temp_hash.hexdigest()

                if job[1] == algo:
                    hashingStopTime = time.time()
                    timeDifference = hashingStopTime - hashingStartTime
                    hashrate = result / timeDifference

                    soc.send(bytes(
                        str(result)
                        + ","
                        + str(hashrate)
                        + ",SecCoin Miner",
                        encoding="utf8"))

                    feedback = soc.recv(1024).decode().rstrip("\n")
                    if feedback == "GOOD":
                        print("Hashrate",
                              int(hashrate/1000),
                              "kH/s",)
                        break
                    elif feedback == "BAD":
                        print("Hashrate",
                              int(hashrate/1000),
                              "kH/s")
                        break
        

    except Exception as e:
        print("Error: " + str(e) + ", restarting in 5s.")
        time.sleep(5)
        os.execl(sys.executable, sys.executable, *sys.argv)
