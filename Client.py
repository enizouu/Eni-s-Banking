import socket
import json
import tkinter
import os

User = {}

Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    Socket.connect(("0.0.0.0", 2330))
except ConnectionRefusedError:
    print("The server isn't reachable, please try again later.")
    exit()

Folder = os.path.dirname(os.path.abspath(__file__))
ApiKeysFile = os.path.join(Folder, "ApiKeys.json")
ApiKeys = {}

if os.path.isfile(ApiKeysFile):
    with open(ApiKeysFile, "r") as f:
        ApiKeys = json.loads(f)
else:
    with open(ApiKeysFile, "w") as f:
        json.dump({"apikeys": []}, f)

def ErrorWindow(Error):
    ErrorTopLevel = tkinter.Toplevel()
    ErrorTopLevel.geometry(f"{len(Error)*10}x100")
    ErrorTopLevel.grid_rowconfigure(0, weight=3)
    ErrorTopLevel.grid_rowconfigure(1, weight=1)
    ErrorTopLevel.grid_columnconfigure(0, weight=1)

    ErrorMessageLabel = tkinter.Label(ErrorTopLevel, text=f"An error occured: {Error}")
    ErrorMessageLabel.grid(row=0, column=0, sticky="nsew")

    OkButton = tkinter.Button(ErrorTopLevel, text="OK", command=lambda:ErrorTopLevel.destroy())
    OkButton.grid(row=1, column=0, sticky="nsew")

def RegisterFrameButtonFunction():
    SignInFrame.pack_forget()
    RegisterFrame.pack(fill="both", expand=True)

def LoginFrameButtonFunction():
    SignInFrame.pack_forget()
    LoginFrame.pack(fill="both", expand=True)

def AgreeTOSCheckButtonFunction():
    if AgreeTOSVar.get() == 1:
        RegisterButton.config(state=tkinter.NORMAL)
    else:
        RegisterButton.config(state=tkinter.DISABLED)

def RegisterButtonFunction():
    if RegisterUsernameEntry.get() != "" and len(RegisterUsernameEntry.get()) > 3 and RegisterPasswordEntry.get() != "":
        Socket.sendall(json.dumps({"type": "register", "username": RegisterUsernameEntry.get(), "password": RegisterPasswordEntry.get()}).encode("utf-8"))

        Data = json.loads(Socket.recv(1024))

        if Data["type"] == "success":
            ErrorWindow(f"Your account is successfully registered, please login now.")
            RegisterFrame.pack_forget()
            SignInFrame.pack(fill="both", expand=True)
        elif Data["type"] == "error":
            ErrorWindow({Data["error"]})

    elif RegisterUsernameEntry.get() == "":
        ErrorWindow("Username can't be empty.")

    elif len(RegisterUsernameEntry.get()) < 3:
        ErrorWindow("Username has to be atleast 4 characters long.")

    elif RegisterPasswordEntry.get() == "":
        ErrorWindow("Password can't be empty.")

def LoginButtonFunction():
    Socket.sendall(json.dumps({"type": "login", "username": LoginUsernameEntry.get(), "password": LoginPasswordEntry.get()}).encode("utf-8"))
    Data = json.loads(Socket.recv(1024))

    global User

    if Data["type"] == "success":
        User = Data["user"]
        print(f"Welcome {User["username"]}, the amount on your account is {User["amount"]}.")
        LoginFrame.pack_forget()
        MainFrame.pack(fill="both", expand=True)

        if os.path.isfile(ApiKeysFile):
            ApiKeys["apikeys"].append(json.dumps(f"{User["apikey"]}"))
        else:
            with open(ApiKeysFile, "w") as f:
                json.dump({"apikeys": []}, f)
    elif Data["type"] == "error":
        ErrorWindow(Data["error"])

def LoadFrame(Frame):
    HomeFrame.pack_forget()

    Frame.pack(side="bottom", fill="both", expand=True)

def ShowProfileFrame():
    if ProfileFrame.winfo_ismapped() == False:
        ProfileFrame.place(relx=0.75, rely=0.08, relwidth=0.25, relheight=0.5)
    else:
        ProfileFrame.place_forget()

def SignOutFunction():
    Socket.sendall(json.dumps({"type": "signout", "username": User["username"], "apikey": ApiKey}).encode("utf-8"))
    Data = json.loads(Socket.recv(1024))

    if Data["type"] == "success":
        MainFrame.pack_forget()
        SignInFrame.pack(fill="both", expand=True)
    elif Data["type"] == "error":
        ErrorWindow(Data["error"])

Window = tkinter.Tk()
Window.title("Eni's Banking")
Window.geometry("1440x810")

SignInFrame = tkinter.Frame(Window)
SignInFrame.pack(fill="both", expand=True)

RegisterFrameButton = tkinter.Button(SignInFrame, text="Register", command=RegisterFrameButtonFunction)
RegisterFrameButton.pack()

RegisterFrame = tkinter.Frame(Window)
RegisterFrame.grid_rowconfigure(0, weight=1)
RegisterFrame.grid_rowconfigure(1, weight=1)
RegisterFrame.grid_columnconfigure(0, weight=1)
RegisterFrame.grid_columnconfigure(1, weight=1)

RegisterUsernameEntryLabel = tkinter.Label(RegisterFrame, text="Username:")
RegisterUsernameEntryLabel.grid(row=0, column=0, sticky="nsew", pady=2)

RegisterUsernameEntry = tkinter.Entry(RegisterFrame)
RegisterUsernameEntry.grid(row=0, column=1, sticky="nsew", pady=2)

RegisterPasswordEntryLabel = tkinter.Label(RegisterFrame, text="Password:")
RegisterPasswordEntryLabel.grid(row=1, column=0, sticky="nsew", pady=2)

RegisterPasswordEntry = tkinter.Entry(RegisterFrame)
RegisterPasswordEntry.grid(row=1, column=1, sticky="nsew", pady=2)

AgreeTOSVar = tkinter.IntVar()
AgreeTOSCheckButton = tkinter.Checkbutton(RegisterFrame, text="Do you agree to the TOS?", variable=AgreeTOSVar, onvalue=1, offvalue=0, command=AgreeTOSCheckButtonFunction)
AgreeTOSCheckButton.grid(row=2, column=0, sticky="nsew", pady=2)

RegisterButton = tkinter.Button(RegisterFrame, text="Register", command=RegisterButtonFunction)
RegisterButton.grid(row=2, column=1, sticky="nsew", pady=2)
RegisterButton.config(state=tkinter.DISABLED)

LoginFrameButton = tkinter.Button(SignInFrame, text="Login", command=LoginFrameButtonFunction)
LoginFrameButton.pack()

LoginFrame = tkinter.Frame(Window)
LoginFrame.grid_rowconfigure(0, weight=1)
LoginFrame.grid_rowconfigure(1, weight=1)
LoginFrame.grid_columnconfigure(0, weight=1)
LoginFrame.grid_columnconfigure(1, weight=1)

LoginUsernameEntryLabel = tkinter.Label(LoginFrame, text="Full Name:")
LoginUsernameEntryLabel.grid(row=0, column=0, sticky="nsew", pady=2)

LoginUsernameEntry = tkinter.Entry(LoginFrame)
LoginUsernameEntry.grid(row=0, column=1, sticky="nsew", pady=2)

LoginPasswordEntryLabel = tkinter.Label(LoginFrame, text="Password:")
LoginPasswordEntryLabel.grid(row=1, column=0, sticky="nsew", pady=2)

LoginPasswordEntry = tkinter.Entry(LoginFrame)
LoginPasswordEntry.grid(row=1, column=1, sticky="nsew", pady=2)

LoginButton = tkinter.Button(LoginFrame, text="Login", command=LoginButtonFunction)
LoginButton.grid(row=2, column=1, sticky="nsew", pady=2)

MainFrame = tkinter.Frame(Window, bd=5, relief="ridge")
MainFrame.grid_rowconfigure(0, weight=1)
MainFrame.grid_rowconfigure(1, weight=15)
MainFrame.grid_columnconfigure(0, weight=1)
MainFrame.grid_columnconfigure(1, weight=1)

TopFrame = tkinter.Frame(MainFrame, bd=5, relief="ridge")
TopFrame.pack(side="top", fill="x", ipady=5)

NameLabel = tkinter.Label(TopFrame, text="Banking", font=("Arial", 25))
NameLabel.pack(side="left")

TopButtonsFrame = tkinter.Frame(TopFrame)
TopButtonsFrame.pack(side="right", fill="y")
TopButtonsFrame.grid_rowconfigure(0, weight=1)
TopButtonsFrame.grid_columnconfigure(0, weight=1)
TopButtonsFrame.grid_columnconfigure(1, weight=1)
TopButtonsFrame.grid_columnconfigure(2, weight=1)
TopButtonsFrame.grid_columnconfigure(3, weight=1)
TopButtonsFrame.grid_columnconfigure(4, weight=1)

HomeButton = tkinter.Button(TopButtonsFrame, text="Home", command=lambda: LoadFrame(HomeFrame))
HomeButton.grid(row=0, column=0, sticky="nsew")

HomeFrame = tkinter.Frame(MainFrame, bd=5, relief="ridge")
HomeFrame.pack(side="bottom", fill="both", expand=True)

SecondButton = tkinter.Button(TopButtonsFrame, text="Second")
SecondButton.grid(row=0, column=1, sticky="nsew")

ThirdButton = tkinter.Button(TopButtonsFrame, text="Third")
ThirdButton.grid(row=0, column=2, sticky="nsew")

FourthButton = tkinter.Button(TopButtonsFrame, text="Fourth")
FourthButton.grid(row=0, column=3, sticky="nsew")

ProfileButton = tkinter.Button(TopButtonsFrame, text="Profile", command=ShowProfileFrame)
ProfileButton.grid(row=0, column=4, sticky="nsew")

ProfileFrame = tkinter.Frame(MainFrame, bd=5, relief="ridge")
ProfileFrame.grid_rowconfigure(0, weight=1)
ProfileFrame.grid_rowconfigure(1, weight=1)
ProfileFrame.grid_rowconfigure(2, weight=1)
ProfileFrame.grid_columnconfigure(0, weight=1)

SignOutButton = tkinter.Button(ProfileFrame, text="Sign Out", command=lambda: print(User))
SignOutButton.grid(row=2, column=0, sticky="nsew")

Window.mainloop()