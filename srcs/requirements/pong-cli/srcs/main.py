from classes.user import User
from classes.pongCLI import PongCLI
import time

SERVER = "https://localhost:4443"

def main():
    app = PongCLI()
    app.run()


if __name__ == '__main__':
    main()

# def main():
#     url = "https://localhost:4443/"
#     headers = {
#         "Content-Type": "application/json",
#         "User-Agent": "pong-CLI",
#     }
#     test = User()
#
#     test.server = SERVER
#     test.SSLCertificate = SSL_CRT
#     test.username = "xcharra1234"
#     test.password = "!@#$(90-9875trgfvcmntr"
#     try:
#         print("Try login\n")
#         test.loginUser()
#         print("Login successful\n")
#     except Exception as error:
#         if (test.response.status_code >= 300):
#             print(error)
#         if (test.response.status_code == 401):
#             try:
#                 print("Try register\n")
#                 test.registerUser()
#                 print("Register successful\n")
#             except Exception as errorr:
#                 print(errorr)
#         elif (test.response.status_code >= 300):
#             print(test.response)




# def connect():
#     print("Connecté au serveur!", flush=True)
#
# def disconnect():
#     print("Déconnecté du serveur!")
#
# def my_event(data):
#     print(f"Événement reçu : {data}")
#
# ssl_context = ssl.create_default_context()
# ssl_context.load_verify_locations("ft_transcendence.crt")
#
# sio = socketio.Client(ssl_verify=False)
# sio.on("connect", handler=connect)
# try:
#     sio.connect("wss://localhost:4443/", socketio_path="/ws/", transports=["websocket"], auth={
#         "token": "debug"
#     })
#     sio.emit("my_event", {"message": "Hello, server!"})
#     sio.wait()  # Maintient la connexion active
# except Exception as e:
#     print(f"Erreur : {e}")
# crt = open(SSL_CRT, "r").read()
# print(crt)
# data = {"username": "test", "password": "test"}
# data_str = json.dumps(data)
#
#
# try:
#     print("Try guest\n")
#     test.guestUser()
#     print("Guest successful\n")
#     print("Try register guest\n")
#     test.registerGuestUser()
#     print("Register guest successful\n")
#     print(test.headers)
# except Exception as error:
#     print(error)
#
#
#
# response = requests.post(url, data='', verify=SSL_CRT, headers=headers)
# print(response.text)

