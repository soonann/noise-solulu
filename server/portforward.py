from dotenv import load_dotenv
import os
import subprocess
import time
import requests

load_dotenv()
PORT=os.getenv('PORT')

class NgrokManager:
    def __init__(self):
        self.process = None

    def start_ngrok(self, port):
        # Start ngrok process
        self.process = subprocess.Popen(["ngrok", "http", str(port)])
        
        # Give it some time to actually start and establish the connection
        time.sleep(2)
        
        # Fetch the ngrok API to retrieve the public URL
        ngrok_details = requests.get("http://localhost:4040/api/tunnels").json()
        
        # Extract the public URL (you can also extract the HTTPS URL if needed)
        public_url = ngrok_details['tunnels'][0]['public_url']
        
        return public_url

    def terminate_ngrok(self):
        if self.process:
            self.process.terminate()
            self.process = None


if __name__ == "__main__":
    # Usage
    manager = NgrokManager()
    url = manager.start_ngrok(PORT)
    print(url)

    # When you want to terminate
    # manager.terminate_ngrok()