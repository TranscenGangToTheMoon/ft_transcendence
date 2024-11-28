import subprocess
import re


find_regex_port = re.compile(r'^Port:\s(\d+)\n?')


def get_port(server):
    for line in server.stdout:
        line = line.decode('utf-8')
        result = find_regex_port.findall(line)
        if result and result[0].isdigit():
            server.stdout.close()
            return int(result[0])
    return 0


def launch_server(match):
    server = subprocess.Popen(["python", "game_server/main.py", match.code], stdout=subprocess.PIPE)
    return get_port(server)
