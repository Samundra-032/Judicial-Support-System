import subprocess
import time

subprocess.run(["python3", "main_script.py"])

time.sleep(100) #change this if needed

print("Running script2.py...")
subprocess.run(["python3", "add_script.py"])
