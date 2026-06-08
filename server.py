import socket
import json
import os
import threading
import secrets

Folder = os.path.dirname(os.path.abspath(__file__))
UsersFile = os.path.join(Folder, "users.json")
Users = {}

if not os.path.isfile(UsersFile):
    with open(UsersFile, "w") as f:
        json.dump({"users": []}, f)

with open(UsersFile, "r") as f:
    Users = json.load(f)

Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
Socket.bind(("0.0.0.0", 2330))
Socket.listen()

def User(Conn, Addr):
    with Conn:
        print(f"{Conn} connected with {Addr}")
        while True:
            Data = Conn.recv(1024)
            if not Data:
                break

            Data = json.loads(Data)
            
            if Data["type"] == "register":
                Exists = False
                User = {}
                for i in Users["users"]:
                    if i["username"] == Data["username"]:
                        Exists = True
                        User = i
                        break

                if Exists == False:
                    Conn.sendall(json.dumps({"type": "success"}).encode("utf-8"))

                    Users["users"].append({"username": Data["username"], "password": Data["password"], "amount": 0, "apikey": []})
                else:
                    Conn.sendall(json.dumps({"type": "error", "error": "Username already exists."}).encode("utf-8"))

            elif Data["type"] == "login":
                Exists = False
                User = {}
                for i in Users["users"]:
                    if i["username"] == Data["username"]:
                        Exists = True
                        User = i
                        break

                if Exists == True:
                    if Data["password"] == User["password"]:
                        ApiKey = secrets.token_urlsafe(16)
                        print(ApiKey)
                        User["apikey"].append(ApiKey)
                        Conn.sendall(json.dumps({"type": "success", "user": {"username": User["username"], "password": User["password"], "amount": User["amount"], "apikey": ApiKey}}).encode("utf-8"))
                    else:
                        Conn.sendall(json.dumps({"type": "error", "error": "Wrong password, please try again."}).encode("utf-8"))
                else:
                    Conn.sendall(json.dumps({"type": "error", "error": "User doesn't exist."}).encode("utf-8"))

            elif Data["type"] == "signout":
                Exists = False
                User = {}
                for i in Users["users"]:
                    if i["username"] == Data["username"]:
                        Exists = True
                        User = i
                        break

                if Exists == True:
                    Conn.sendall(json.dumps({"type": "success"}).encode("utf-8"))
                    ApiKey = Data["apikey"]
                    User["apikey"].pop(ApiKey)
                else:
                    Conn.sendall(json.dumps({"type": "error", "error": "User doesn't exist."}).encode("utf-8"))
            
            elif Data["type"] == "send":
                FromExists = False
                From = {}
                ToExists = False
                To = {}
                for i in Users["users"]:
                    if i["username"] == Data["from"]:
                        FromExists = True
                        From = i
                        break
                for i in Users["users"]:
                    if i["username"] == Data["to"]:
                        ToExists = True
                        To = i
                        break

                if FromExists:
                    if ToExists:
                        if From != To:
                            if From["amount"] >= int(Data["amount"]):
                                From["amount"] = From["amount"] - int(Data["amount"])
                                To["amount"] = To["amount"] + int(Data["amount"])
                                Conn.sendall(json.dumps({"type": "success", "user": From}).encode("utf-8"))
                            else:
                                Conn.sendall(json.dumps({"type": "error", "error": "Insufficient funds."}).encode("utf-8"))
                        else:
                            Conn.sendall(json.dumps({"type": "error", "error": "Unable to send money to yourself."}).encode("utf-8"))
                    else:
                        Conn.sendall(json.dumps({"type": "error", "error": "The user you are sending money to doesn't exist."}).encode("utf-8"))
                else:
                    Conn.sendall(json.dumps({"type": "error", "error": "There was a problem with the transaction, please try again later."}).encode("utf-8"))

try:
    while True:
        Conn, Addr = Socket.accept()
        UserThread = threading.Thread(target=User, args=(Conn, Addr))
        UserThread.start()
except KeyboardInterrupt:
    with open(UsersFile, "w") as f:
        json.dump(Users, f)
    Socket.close()
    exit()