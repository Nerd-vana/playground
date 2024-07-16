import subprocess
import os

# Path to your MP3 file
mp3_file = "141030-YouAreNowReadyToUseKeyvault.mp3"


# Start the afplay process without blocking the current Python script
subprocess.Popen(["afplay", mp3_file])


# Shell command to play the MP3 file
#os.system(f"afplay '{mp3_file}'")

#os.system(f"ffplay '{mp3_file}'")
