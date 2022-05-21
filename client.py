import os
import socket
from hashlib import md5
from termcolor import colored

SERVER_ADDRESS = '127.0.0.1'
SERVER_PORT = 8070


def main():
    commands = {'song_url%%<song_name>': 'returns a YouTube URL for song_name', 'get_albums': 'returns all albums',
                'get_album_songs%%<album_name>': 'returns all songs in an album', 'get_lyrics%%<song_name>':
                    'returns the lyrics of a song', 'get_song_album%%<song_name>': 'returns the album name of the song',
                'search_lyrics%%<lyric>': 'return the song with the same lyrics', 'shutdown_server': 'read the command'}
    data = "no data"

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        server_soc = (SERVER_ADDRESS, SERVER_PORT)
        try:
            s.connect(server_soc)
        except ConnectionRefusedError:
            print("couldn't connect to server")
        else:
            print(colored("you are connected to the", "green"), colored("Pink Floyd", "magenta"),
                  colored("lyrics server!", "green"))
            print(colored("to end your connection with the server enter 'exit' ", "green"))
            print(colored("to get a list of all possible commands and description enter 'help' ", "green"))
            while True:
                command = input("please enter a command \n").lower()
                if command == 'help':
                    print(colored(str(list(commands.keys())).replace(',', '\n'), "green"))
                    key = input('for a description of a command please enter the command name, else press enter \n')
                    if key in commands.keys():
                        print(colored(commands[key], "green"))
                else:
                    if '%%' in command:
                        command = command.split('%%')
                        s.sendall(f"{command[0]}%%{command[1]}%%{md5(command[1].encode()).hexdigest()}".encode())
                    else:
                        s.sendall(f"{command}".encode())
                    try:
                        data = s.recv(2048)
                    except ConnectionResetError:
                        break

                    if not data:
                        print('no data received from server!')
                        break
                    elif data.decode() == 'md5 does not match!':
                        print('md5 does not match!')
                        break
                    else:
                        data = data.decode().split('%%')
                        data_md5 = md5(data[1].encode()).hexdigest()
                        if data_md5 != data[2]:
                            print("md5 doesnt match!")
                            break
                        else:
                            print(colored("the servers response is:", "blue"))
                            print(colored(data[1], "green"))
                            if 'https://www.youtube.com' in data[1]:
                                answer = input(colored('do you want to play the song? (y/n)\n', "green")).lower()
                                if answer == 'y':
                                    os.startfile(data[1])
                    if command == 'exit' or command == 'shutdown_server':
                        break


if __name__ == "__main__":
    main()
