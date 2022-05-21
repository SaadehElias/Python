import os
import socket
from bs4 import BeautifulSoup, Comment
from hashlib import md5
import requests
import urllib.request
import re
import pickle
import time

# Internet URLs
URL = 'https://www.azlyrics.com/p/pinkfloyd.html'
URL_LYRICS = 'https://www.azlyrics.com/lyrics/pinkfloyd/'
YOUTUBE_URL = 'https://www.youtube.com/results?search_query='
SERVER_ADDRESS = '127.0.0.1'
SERVER_PORT = 8070


def song_url(song_name):
    """

    :param song_name: the desired song
    :return:  a string representing a youtube url
    """
    search_keywords = "Pink floyd " + song_name
    html = urllib.request.urlopen(YOUTUBE_URL + search_keywords.replace(' ', '+'))
    video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
    return 'https://www.youtube.com/watch?v=' + video_ids[0]


def get_song_url(album_dict, data):
    """returns a youtube url for song"""
    result = ''
    if len(data) == 1:
        result = 'missing arguments'
    else:
        song = data[1]
        for song_list in album_dict.values():
            if song in song_list:
                result = str(song_url(song))
                break
            else:
                result = 'song not found!'
    return result


def _get_lyrics_by_song(song_name):
    """

    :param song_name: the desired song name
    :return: a string representing the song lyrics from the web
    """
    div_comment = "Usage of azlyrics.com"
    song_name = song_name.lower()
    source = requests.get(URL_LYRICS + ''.join(e for e in song_name if e.isalnum()) + '.html').text
    soup = BeautifulSoup(source, 'lxml')
    comments = soup.find_all(string=lambda text: isinstance(text, Comment))
    for comment in comments:
        if div_comment in comment:
            return str(comment.parent.text).lower()


def get_albums_list():
    """

    :return: a list of all the albums
    """
    albums = []
    source = requests.get(URL).text

    soup = BeautifulSoup(source, 'lxml')

    for album in soup.find_all("div", {"class": "album"}):
        albums.append(str(album.find('b').text.replace('"', '').replace(':', '')).lower())
    return soup, albums


def get_album_dict():
    """

    :return:a dictionary that the keys contain the album names and the values are the songs in said album
    """
    soup, albums = get_albums_list()

    songs = []
    album_dict = {}

    current_album = ''

    for song in soup.find_all("div", {"class": ["listalbum-item", "album"]}):
        if song.find('b'):
            album = str(song.find('b').text.replace('"', '').replace(':', ''))
        else:
            album = ''

        if album not in albums:
            songs.append(song.text)
        else:
            if not current_album == '':
                album_dict[current_album] = songs
            current_album = album
            songs = []
    album_dict[current_album] = songs
    album_dict = _lowercase(album_dict)
    with open('./data/album_dict.pkl', 'wb') as pickle_file:
        pickle.dump(album_dict, pickle_file)
    return album_dict


def get_album_songs(album_dict, data):
    """

    :param data:
    :param album_dict:
    :return: returns all songs in an album
    """
    result = ''
    returned_type = 'str'
    if len(data) == 1:
        result = 'missing arguments'
    else:
        album = data[1]
        print(data[1])
        if album in album_dict.keys():
            result = str(album_dict[album])
            returned_type = 'list'
        else:
            result = 'album not found!'
    return f'{returned_type}%%{result}%%{md5(result.encode()).hexdigest()}'.encode()


def get_lyrics(song_dict, data):
    """
        :param data: the desired song name
        :param song_dict:
        :return: a string representing the song lyrics
        """
    result = ''
    returned_type = 'str'
    if len(data) == 1:
        result = 'missing arguments'
    else:
        song = data[1]
        if song in song_dict.keys():
            result = song_dict[song]
        else:
            result = 'song not found!'
    return f'{returned_type}%%{result}%%{md5(result.encode()).hexdigest()}'.encode()


def get_song_album(album_dict, data):
    """

    :param album_dict:
    :param data:
    :return:returns the album name of the song
    """
    result = 'song not found!'
    returned_type = 'str'
    if len(data) == 1:
        result = 'missing arguments'
    else:
        song = data[1]
        for song_list in album_dict.values():
            if song in song_list:
                result = list(album_dict.keys())[list(album_dict.values()).index(song_list)]
                returned_type = 'str'
    return f'{returned_type}%%{result}%%{md5(result.encode()).hexdigest()}'.encode()


def search_lyrics(album_dict, song_dict, data):
    result = 'lyrics not found!'
    returned_type = 'str'
    if len(data) == 1:
        result = 'missing arguments'
    else:
        lyrics = data[1]
        for song_list in album_dict.values():
            for song in song_list:
                song_lyrics = song_dict[song]
                if song_lyrics is None:
                    break
                elif lyrics in song_lyrics:
                    result = song
                    return f'{returned_type}%%{result}%%{md5(result.encode()).hexdigest()}'.encode()
    return f'{returned_type}%%{result}%%{md5(result.encode()).hexdigest()}'.encode()


def _lowercase(obj):
    """ Make dictionary lowercase """
    if isinstance(obj, dict):
        return {k.lower(): _lowercase(v) for k, v in obj.items()}
    elif isinstance(obj, (list, set, tuple)):
        t = type(obj)
        return t(_lowercase(o) for o in obj)
    elif isinstance(obj, str):
        return obj.lower()
    else:
        return obj


def request_data():
    album_dict_path = './data/album_dict.pkl'
    song_dict_path = './data/song_dict.pkl'
    if os.path.exists(album_dict_path):
        with open('./data/album_dict.pkl', 'rb') as handle:
            album_dict = pickle.load(handle)

    else:
        album_dict = get_album_dict()
    if os.path.exists(song_dict_path):
        with open('./data/song_dict.pkl', 'rb') as handle:
            song_dict = pickle.load(handle)
    else:
        song_dict = get_songs_dict(album_dict)
    return album_dict, song_dict


def get_songs_dict(album_dict):
    """

    :param album_dict:
    :return: a dictunary that contains song names as the key and the lyrics as the value
    """
    songs_dict = {}
    for album in album_dict:
        for song in album_dict[album]:
            songs_dict[song] = _get_lyrics_by_song(song)
            time.sleep(3)
            print("Song " + song + " Added successfully!")
    with open('./data/song_dict.pkl', 'wb') as pickle_file:
        pickle.dump(songs_dict, pickle_file)
    return songs_dict


def boot_up_server(album_dict, song_dict):
    is_up = True
    while is_up:
        print('server is up')
        # create socket
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # bind the socket to a public host, and a well-known port
        server_socket.bind((SERVER_ADDRESS, SERVER_PORT))
        # become a server socket
        server_socket.listen(5)
        # accept connections from outside
        conn, addr = server_socket.accept()
        with conn:
            print('Connected by', addr)
            while True:
                try:
                    data = conn.recv(2048)
                except ConnectionResetError:
                    break
                if not data:
                    break
                data = data.decode()
                # data[0] will contain the command and data[1] will contain the data if provided
                data = data.split('%%')
                print(data)
                if len(data) > 1:
                    data_md5 = str(md5(data[1].encode()).hexdigest())
                    if data_md5 != data[2]:  # checksum
                        conn.sendall("md5 does not match!".encode())
                        break

                if data[0] == 'song_url':
                    result = get_song_url(album_dict, data)
                    conn.sendall(f'str%%{result}%%{md5(result.encode()).hexdigest()}'.encode())
                elif data[0] == 'get_albums':
                    #  returns all albums
                    result = str(list(album_dict.keys())).replace(',', '\n').replace('[', '').replace(']', '')
                    conn.sendall(f'str%%{result}%%{md5(result.encode()).hexdigest()}'.encode())

                elif data[0] == 'get_album_songs':
                    #  returns all songs in a given album
                    conn.sendall(get_album_songs(album_dict, data))

                elif data[0] == 'get_lyrics':
                    #  returns the lyrics of a song
                    conn.sendall(get_lyrics(song_dict, data))

                elif data[0] == 'get_song_album':
                    #  returns the album name of the song
                    conn.sendall(get_song_album(album_dict, data))

                elif data[0] == 'search_lyrics':
                    #  return the song with the same lyrics
                    conn.sendall(search_lyrics(album_dict, song_dict, data))

                elif data[0] == 'exit':
                    result = 'session ended'
                    conn.sendall(f'str%%{result}%%{md5(result.encode()).hexdigest()}'.encode())
                    break

                elif data[0] == 'shutdown_server':
                    result = 'shutting down server...'
                    conn.sendall(f'str%%{result}%%{md5(result.encode()).hexdigest()}'.encode())
                    is_up = False
                    break

                else:
                    result = 'invalid command!'
                    conn.sendall(f'str%%{result}%%{md5(result.encode()).hexdigest()}'.encode())


def main():
    album_dict, song_dict = request_data()
    boot_up_server(album_dict, song_dict)


if __name__ == "__main__":
    main()
