from classes.user import User
from classes.pongCLI import PongCLI
import time

import json
import httpx
import re


# regix = re.compile(r'event: ([a-z\-]+)\ndata: (.+)\n\n')
#
# def SSE():
#     with httpx.Client(verify=User.SSLCertificate) as client:
#         headers = {
#             'Content-Type': 'text/event-stream',
#             'Authorization': f'Bearer {User.accessToken}',
#         }
#         try: #server down url ==prout
#             with client.stream('GET', f"{User.server}/sse/users/", headers=headers) as response:
#                 if (response.status_code == 200):
#                     for line in response.iter_text():
#                         try:
#                             events = regix.findall(line)
#                             for event, data in events:
#                                 if event == "game-start":# game start
#                                     dataJSON =json.loads(data)
#                                     #send id ws
#                                     with #mutex lock
#                                 #User.gameWaitingForMe = true
#                         except (IndexError, ValueError) as error:
#                             continue
#                 elif (response.status_code >= 400):
#                     raise (Exception("SSE connection prout!"))
#         except Exception as error:
#             print(error)

# def main():
#     url = "https://localhost:4443/"
#     headers = {
#         "Content-Type": "application/json",
#         "User-Agent": "pong-CLI",
#     }
#
#     User.server = "https://localhost:4443/"
#     User.SSLCertificate = "ft_transcendence.crt"
#     User.username = "xcharra"
#     User.password = "!@#$(90-9875tr"
#     try:
#         print("Try login\n")
#         User.loginUser()
#         print("Login successful\n")
#     except Exception as error:
#         if (User.response.status_code >= 300):
#             print(error)
#         if (User.response.status_code == 401):
#             try:
#                 print("Try register\n")
#                 User.registerUser()
#                 print("Register successful\n")
#             except Exception as errorr:
#                 print(errorr)
#         elif (User.response.status_code >= 300):
#             print(User.response)


def main():
    app = PongCLI()
    app.run()


if __name__ == '__main__':
    main()





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

