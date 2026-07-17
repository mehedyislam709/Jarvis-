import socket

def check_internet(host="8.8.8.8", port=53, timeout=3):
    """
    Check if there is an internet connection
    by attempting to connect to a reliable host.
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error as ex:
        return False

if __name__ == "__main__":
    if check_internet():
        print("Internet connected. Online mode is active.")
    else:
        print("No internet connection. Offline mode is active.")
