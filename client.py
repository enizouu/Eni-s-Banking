import socket
import json

try:
    def Error(error):
        print(f"An error occured: {error}")

    Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        Socket.connect(("0.0.0.0", 2330))
    except ConnectionRefusedError:
        Error("The server isn't reachable, please try again later.")
        exit()

    SignIn = input("You are not signed in, please input 'Register' to register or 'Login' to login.\nOption:")

    if SignIn == "Register":
        Username = input("Input an username.\nUsername: ")
        Password = input("Input a password.\nPassword: ")

        Socket.sendall(json.dumps({"type": "register", "username": Username, "password": Password}).encode("utf-8"))

        Data = json.loads(Socket.recv(1024))

        if Data["type"] == "success":
            print(f"Your account is successfully registered, please login now.")
            exit()
        elif Data["type"] == "error":
            Error({Data["error"]})
            exit()

    elif SignIn == "Login":
        Username = input("Input your username.\nUsername: ")
        Password = input("Input your password.\nPassword: ")

        Socket.sendall(json.dumps({"type": "login", "username": Username, "password": Password}).encode("utf-8"))

        Data = json.loads(Socket.recv(1024))

        User = {}

        if Data["type"] == "success":
            User = Data["user"]
            print(f"Welcome {User["username"]}, the amount on your account is {User["amount"]}.")
        elif Data["type"] == "error":
            Error(Data["error"])
            exit()
    else:
        exit()

    while True:
        Action = input("Input corresponding words to do specific actions, 'Send' to send or 'Exit' to exit.\nAction: ")
        if Action == "Send":
            To = input("Input the username of the user you want to send to.\nUsername: ")
            Amount = input(f"Input the amount you want to send to {To}.\nAmount: ")

            Socket.sendall(json.dumps({"type": "send", "from": User["username"], "to": To, "amount": Amount}).encode("utf-8"))

            Data = json.loads(Socket.recv(1024))

            if Data["type"] == "success":
                User = Data["user"]
                print(f"Amount transferred successfully, your new amount is {User["amount"]}.")
            elif Data["type"] == "error":
                Error({Data["error"]})

        elif Action == "Exit":
            exit()
        
        else:
            Error("Unrecognized option.")
except KeyboardInterrupt:
    print("")
    exit()