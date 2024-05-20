import subprocess
import time

while True:
    quackquack_process = subprocess.Popen(['python', 'quackquackv3.py'])
    time.sleep(100)
    quackquack_process.terminate()
