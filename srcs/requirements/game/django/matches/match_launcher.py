import subprocess
import re

# from matches.models import Matches
find_regex_port = re.compile(r'^Port:\s(\d+)\n?')


def get_port(server):
    for line in server.stdout:
        line = line.decode('utf-8')
        result = find_regex_port.findall(line)
        if result and result[0].isdigit():
            return int(result[0])
    return 0


def launch_server(match):
    user_ids = [str(player.user_id) for player in match.players.all()]
    print(user_ids)
    server = subprocess.Popen(["python", "game_server/main.py", match.code], stdout=subprocess.PIPE)
    return get_port(server)
