# Python imports
import os

# Local imports
from classes.PongCLIApp import PongCLI

if __name__ == '__main__':
    os.system('clear')
    os.system('printf "\\e[8;60;150t"')
    app = PongCLI()
    app.run()

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
