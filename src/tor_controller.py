import requests
from stem import Signal
from stem.control import Controller

# Set up Tor proxy
def set_tor_proxy():
    session = requests.Session()
    session.proxies = {
        'http': 'socks5h://127.0.0.1:9050',
        'https': 'socks5h://127.0.0.1:9050'
    }
    return session

# Renew IP address through Tor
def renew_tor_ip():
    with Controller.from_port(port=9051) as controller:
        controller.authenticate()
        controller.signal(Signal.NEWNYM)
        print("New Tor IP address assigned!")