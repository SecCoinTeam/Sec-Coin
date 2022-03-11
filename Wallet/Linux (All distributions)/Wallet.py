#!/usr/bin/env python3
import configparser
import datetime
import getpass
import json
import os
import platform
import socket
import sys
import time
from pathlib import Path
from signal import SIGINT, signal
from base64 import b64decode, b64encode

try:
    from base64 import urlsafe_b64decode as b64d
    from base64 import urlsafe_b64encode as b64e
except ModuleNotFoundError:
    print("Base64 is not installed. "
          + "Please manually install \"base64\""
          + "\nExiting in 15s.")
    sleep(15)
    _exit(1)

try:
    from cryptography.fernet import Fernet, InvalidToken
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
except:
    now = datetime.datetime.now()
    print(now.strftime("%H:%M:%S ")
          + "Cryptography is not installed. "
          + "Please install it using: python3 -m pip install cryptography."
          + "\nExiting in 15s.")
    time.sleep(15)
    os._exit(1)

try:
    import secrets
except:
    now = datetime.datetime.now()
    print(now.strftime("%H:%M:%S ")
          + "Secrets is not installed. "
          + "Please install it using: python3 -m pip install secrets."
          + "\nExiting in 15s.")
    time.sleep(15)
    os._exit(1)

try:
    import websocket
except:
    now = datetime.datetime.now()
    print(now.strftime("%H:%M:%S ")
          + "Websocket-client is not installed. "
          + "Please install it using: python3 -m pip install websocket-client."
          + "\nExiting in 15s.")
    time.sleep(15)
    os._exit(1)

try:
    from base64 import urlsafe_b64decode as b64d
    from base64 import urlsafe_b64encode as b64e
except:
    now = datetime.datetime.now()
    print(now.strftime("%H:%M:%S ")
          + "Base64 is not installed. "
          + "Please install it using: python3 -m pip install base64."
          + "\nExiting in 15s.")
    time.sleep(15)
    os._exit(1)

try:  # Check if requests is installed
    import requests
except:
    now = datetime.datetime.now()
    print(now.strftime("%H:%M:%S ")
          + "Requests is not installed. "
          + "Please install it using: python3 -m pip install requests."
          + "\nExiting in 15s.")
    time.sleep(15)
    os._exit(1)

try:  # Check if colorama is installed
    from colorama import Back, Fore, Style, init
except:
    now = datetime.datetime.now()
    print(now.strftime("%H:%M:%S ")
          + "Colorama is not installed. "
          + "Please install it using: python3 -m pip install colorama."
          + "\nExiting in 15s.")
    time.sleep(15)
    os._exit(1)

try:
    import tronpy
    from tronpy.keys import PrivateKey
    tronpy_installed = True
except:
    tronpy_installed = False
    now = datetime.datetime.now()
    print(now.strftime("%H:%M:%S ")
          + "Tronpy is not installed. "
          + "Please install it using: python3 -m pip install tronpy."
          + "\nWrapper is disabled because of tronpy is not installed.")

wrong_passphrase = False
backend = default_backend()
iterations = 100_000
timeout = 30  
VER = 2.45
use_wrapper = False
WS_URI = "ws://159.65.220.57:14808"

config = configparser.ConfigParser()


def title(title):
    if os.name == 'nt':
        os.system(
            "title "
            + title)
    else:
        print(
            '\33]0;'
            + title
            + '\a',
            end='')
        sys.stdout.flush()


def _derive_key(
        password: bytes,
        salt: bytes,
        iterations: int = iterations) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=iterations,
        backend=backend)
    return b64e(kdf.derive(password))


def print_command(name, desc):
    print(" " + Style.RESET_ALL + Fore.WHITE +
          Style.BRIGHT + name + Style.RESET_ALL + desc)


def print_commands_norm():
    with open('cli_wallet_commands.json') as f:
        data = json.load(f)
        for key, value in data.items():
            if key == "wrapper_commands":
                break
            print_command(key, value)


def password_encrypt(
        message: bytes,
        password: str,
        iterations: int = iterations) -> bytes:
    salt = secrets.token_bytes(16)
    key = _derive_key(
        password.encode(),
        salt,
        iterations)
    return b64e(
        b'%b%b%b' % (
            salt,
            iterations.to_bytes(4, 'big'),
            b64d(Fernet(key).encrypt(message))))

def password_decrypt(
        token: bytes,
        password: str) -> bytes:
    decoded = b64d(token)
    salt, iterations, token = decoded[:16], decoded[16:20], b64e(decoded[20:])
    iterations = int.from_bytes(iterations, 'big')
    key = _derive_key(
        password.encode(),
        salt,
        iterations)
    return Fernet(key).decrypt(token)

def handler(signal_received, frame):
    print(Style.RESET_ALL
          + Style.BRIGHT
          + Fore.YELLOW
          + "See you soon!")
    try:
        s.send(bytes("CLOSE", encoding="utf8"))
    except:
        pass
    os._exit(0)


signal(SIGINT, handler)  # Enable signal handler


while True:
    try:  # Try to connect
        s = websocket.create_connection(WS_URI)
        s.settimeout(timeout)
        SERVER_VER = s.recv().rstrip("\n")

        break  # If connection was established, continue

    except Exception as e:  # If it wasn't, display a message
        print(e)
        print(Style.RESET_ALL
                + Fore.RED
                + "Cannot connect to the server. "
                + "It is probably under maintenance or temporarily down."
                + "\nRetrying in 15 seconds.")
        time.sleep(15)
        os.execl(sys.executable, sys.executable, *sys.argv)

    except:
        print(Style.RESET_ALL
              + Fore.RED +
              " Cannot receive pool address and IP."
              + "\nExiting in 15 seconds.")
        time.sleep(15)
        os._exit(1)


def reconnect():
    while True:
        try:  # Try to connect
            s = websocket.create_connection(WS_URI)
            s.settimeout(timeout)
            SERVER_VER = s.recv().rstrip("\n")

        except:  # If it wasn't, display a message
            print(Style.RESET_ALL + Fore.RED
                    + "Cannot connect to the server. "
                    + "It is probably under maintenance or temporarily down."
                    + "\nRetrying in 15 seconds.")
            time.sleep(15)
            os.execl(sys.executable, sys.executable, *sys.argv)
        else:
            return s


while True:
    title("Sec-Coin CLI Wallet")
    if not Path("CLIWallet_config.cfg").is_file():

        print(Style.RESET_ALL
              + Style.BRIGHT
              + Fore.YELLOW
              + "Sec-Coin CLI Wallet first-run\n")
        print(Style.RESET_ALL + "Select an option")

        choice = input("  1 - Login\n  2 - Register\n  3 - Exit\n")
        try:
            int(choice)
        except ValueError:
            print("Error, value must be numeric")

        if int(choice) <= 1:
            username = input(
                Style.RESET_ALL
                + Fore.YELLOW
                + "Enter your username: "
                + Style.BRIGHT)

            password = getpass.getpass(prompt=Style.RESET_ALL
                                       + Fore.YELLOW
                                       + "Enter your password: "
                                       + Style.BRIGHT,
                                       stream=None)

            server_timeout = True
            while server_timeout:
                try:
                    s.send(bytes(
                        "LOGI,"
                        + str(username)
                        + ","
                        + str(password)
                        + str(",placeholder"),
                        encoding="utf8"))
                    loginFeedback = s.recv().rstrip("\n").split(",")
                    server_timeout = False

                    if loginFeedback[0] == "OK":
                        print(Style.RESET_ALL
                              + Fore.YELLOW
                              + "Successfull login")

                        config['wallet'] = {
                            "username": username,
                            "password": b64encode(bytes(password, encoding="utf8")).decode("utf-8")}
                        config['wrapper'] = {"use_wrapper": "false"}

                        with open("CLIWallet_config.cfg", "w") as configfile:  # Write data to file
                            config.write(configfile)
                    else:
                        print(Style.RESET_ALL
                              + Fore.RED
                              + "Couldn't login, reason: "
                              + Style.BRIGHT
                              + str(loginFeedback[1]))
                        time.sleep(15)
                        os._exit(1)
                except socket.timeout:
                    server_timeout = True

        if int(choice) == 2:
            print(Style.RESET_ALL
                  + Fore.YELLOW
                  + "By registering a new account you agree to the"
                  + " terms of service and privacy policy available at "
                  + Fore.WHITE
                  + ""
                  + Fore.YELLOW)

            username = input(
                Style.RESET_ALL
                + Fore.YELLOW
                + "Enter your username: "
                + Style.BRIGHT)

            password = getpass.getpass(prompt=Style.RESET_ALL
                                       + Fore.YELLOW
                                       + "Enter your password: "
                                       + Style.BRIGHT,
                                       stream=None)

            pconfirm = getpass.getpass(prompt=Style.RESET_ALL
                                       + Fore.YELLOW
                                       + "Confirm your password: "
                                       + Style.BRIGHT,
                                       stream=None)

            email = input(
                Style.RESET_ALL
                + Fore.YELLOW
                + "Enter your e-mail address: "
                + Style.BRIGHT)

            if password == pconfirm:
                while True:
                    s.send(bytes(
                        "REGI,"
                        + str(username)
                        + ","
                        + str(password)
                        + ","
                        + str(email),
                        encoding="utf8"))

                    regiFeedback = s.recv().rstrip("\n").split(",")

                    if regiFeedback[0] == "OK":
                        print(Style.RESET_ALL
                              + Fore.YELLOW
                              + Style.BRIGHT
                              + "Successfully registered new account")
                        break

                    elif regiFeedback[0] == "NO":
                        print(Style.RESET_ALL
                              + Fore.RED
                              + "Couldn't register new user, reason: "
                              + Style.BRIGHT
                              + str(regiFeedback[1]))
                        time.sleep(15)
                        os._exit(1)

        if int(choice) >= 3:
            os._exit(0)

    else:
        config.read("CLIWallet_config.cfg")
        while True:
            config.read("CLIWallet_config.cfg")
            username = config["wallet"]["username"]
            password = b64decode(config["wallet"]["password"]).decode("utf8")
            s.send(bytes(
                "LOGI,"
                + str(username)
                + ","
                + str(password)
                + str(",placeholder"),
                encoding="utf8"))

            loginFeedback = s.recv().rstrip("\n").split(",")
            if loginFeedback[0] == "OK":
                break
            else:
                print(Style.RESET_ALL
                      + Fore.RED
                      + "Couldn't login, reason: "
                      + Style.BRIGHT
                      + str(loginFeedback[1]))
                time.sleep(15)
                os._exit(1)

        while True:
            print(Style.RESET_ALL
                  + Style.BRIGHT
                  + Fore.YELLOW
                  + "\nSec-Coin CLI Wallet")

            print(Style.RESET_ALL
                  + Fore.YELLOW
                  + "Type `help` to list available commands")

            command = input(Style.RESET_ALL
                            + Fore.WHITE
                            + "Sec Console: "
                            + Style.BRIGHT)

            if command == "refresh":
                continue
  
            elif command == "send":
                recipient = input(Style.RESET_ALL
                                  + Fore.WHITE
                                  + "Enter recipients' username: "
                                  + Style.BRIGHT)
                try:
                    amount = float(input(
                        Style.RESET_ALL
                        + Fore.WHITE
                        + "Enter amount to transfer: "
                        + Style.BRIGHT))
                except ValueError:
                    print("Amount should be numeric... aborting")
                    continue

                s.send(bytes(
                    "SEND,-,"
                    + str(recipient)
                    + ","
                    + str(amount),
                    encoding="utf8"))
                while True:
                    message = s.recv().rstrip("\n")
                    print(Style.RESET_ALL
                          + Fore.BLUE
                          + "Server message: "
                          + Style.BRIGHT
                          + str(message))
                    break

            elif command == "changepass":
                oldpassword = input(
                    Style.RESET_ALL
                    + Fore.WHITE
                    + "Enter your current password: "
                    + Style.BRIGHT)

                newpassword = input(
                    Style.RESET_ALL
                    + Fore.WHITE
                    + "Enter new password: "
                    + Style.BRIGHT)

                s.send(bytes(
                    "CHGP,"
                    + str(oldpassword)
                    + ","
                    + str(newpassword),
                    encoding="utf8"))

                while True:
                    message = s.recv().rstrip("\n")
                    print(Style.RESET_ALL
                          + Fore.BLUE
                          + "Server message: "
                          + Style.BRIGHT
                          + str(message))
                    break

            elif command == "exit":
                print(Style.RESET_ALL
                      + Style.BRIGHT
                      + Fore.YELLOW
                      + "\nSIGINT detected - Exiting gracefully."
                      + Style.NORMAL
                      + " See you soon!" 
                      + Style.RESET_ALL)
                try:
                    s.send(bytes("CLOSE", encoding="utf8"))
                except:
                    pass
                os._exit(0)

            elif command == "logout":
                os.remove("CLIWallet_config.cfg")
                os.execl(sys.executable, sys.executable, *sys.argv)

            else:
                print(Style.RESET_ALL
                      + Fore.YELLOW
                      + " Sec commands:")
                print_commands_norm()

