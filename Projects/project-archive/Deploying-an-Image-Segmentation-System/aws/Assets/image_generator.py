import json
import time
import random
import requests
import urllib
import argparse
import socket
import tempfile


def get_args():
    parser = argparse.ArgumentParser(description='Generate and send random images')
    parser.add_argument('--port', '-p', type=str, default='8000', help='port to bind (default 8000)')
    parser.add_argument('--host', '-H', type=str, default='0.0.0.0', help='host to send the image to (default 0.0.0.0)')
    parser.add_argument('--frequency', '-f', type=int, default=10, help='frequency to send images (default 10)')
    args = parser.parse_args()
    return args.port, args.host, args.frequency

def read_urls():
    with open('/home/ec2-user/urls.json', 'rb') as outfile:
        data = json.load(outfile)
    return data

def get_random_url(data):
    elements = list(data.keys())
    category = random.choice(elements)
    img_url = random.choice(data[category])
    return img_url

def download_image(url):
    f = urllib.request.urlopen(url)
    name_file = url.split('/')[-1]
    # Save the file to give it a name to use later
    with tempfile.TemporaryDirectory() as temp_dir:
        with open(f'{temp_dir}/{name_file}', 'wb') as file:
            file.write(f.read())
    
            file_read = open(f'{temp_dir}/{name_file}', 'rb')
    return {'image_encoded': file_read}, name_file

def send_image(image, filename, host, port, frequency):
    
    while True:
        try:
            socket.setdefaulttimeout(frequency)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, int(port)))
        except socket.error as ex:
            print(ex)
            time.sleep(frequency)
        else:
            try:
                requests.get('http://' + host + ':' + port + '/image', timeout=2, headers={"Content-Type":"text"})
            except requests.exceptions.Timeout: 
                print("Request sent to netcat")
                try:
                    payload = {'image_encoded': filename}
                    requests.post('http://' + host + ':' + port + '/image', data=json.dumps(payload), timeout=frequency)
                except:
                    break
            try:
                requests.post('http://' + host + ':' + port + '/image', files=image, timeout=frequency)
                print("Image sent to server")
                time.sleep(frequency)
                break
            except requests.exceptions.Timeout:
                print("Server disconnected while sending image")


if __name__ == '__main__':
    port, host, frequency = get_args()
    urls = read_urls()
    while True:
        path = get_random_url(urls)
        image, filename = download_image(path)
        send_image(image, filename=filename, host=host, port=port, frequency=frequency)