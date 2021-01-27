KEY = "43f4127ddffe3d40fd6a5271eb0140a20e0f77890e66d9e5183a1ba0fb02ef56"
NON_ROOT_USER="pacman"
UPDATE_SYSTEM=False

import os
import json
import requests
import zipfile, io
import base64
import time
from pwd import getpwnam  

CODEBASE_RESOURCE_URL = "https://getresources.pacman.ai"            # Codebase to install server
GAME_CODEBASE_RESOURCE_URL = CODEBASE_RESOURCE_URL + "/runner"    # Codebase to get the code to run the games.


def setVariables():
    # gets values from this script, .env file or params when running this file.
    pass

def getResources():
    # use userKey to send key
    # Only update and sent to KV if logMsg array length is different, and gameResults are diff README
#    os.system("wget ")
    headers = {'userKey': KEY}
    request = requests.get(CODEBASE_RESOURCE_URL, headers=headers)

    z = zipfile.ZipFile(io.BytesIO(request.content))
    
    # Get the code from (private) GitHub Repo.
    z.extractall(".")

    print("\n\t [+] Moving files.\n")
    print("mv ./" + request.headers['X-PACMAN-ZIPNAME'] + "-" + request.headers['X-GITHUB-RELEASE-VERSION'] + "/* .")
    os.system("mv ./" + request.headers['X-PACMAN-ZIPNAME'] + "-" + request.headers['X-GITHUB-RELEASE-VERSION'] + "/* .")
    ########################################################################
    #                                                                      #
    #           TSL/SSL Certificates For Mutual Authentication             #
    #                                                                      #
    ########################################################################
    time.sleep(5)
    # Get and save the private certificate
    cert = base64.b64decode(request.headers['X-PACMAN-PRIVATE-CERT']).decode('utf-8')
    setStatus("private.cert", cert)

    # Get and save the private key
    key = base64.b64decode(request.headers['X-PACMAN-PRIVATE-KEY']).decode('utf-8')
    setStatus("private.key", key)

    print("\n\t [+] Cleaning up.\n")
    os.system("rm -Rfv " + request.headers['X-PACMAN-ZIPNAME'] + "-" + request.headers['X-GITHUB-RELEASE-VERSION']) 

    # Check the key and certificate files exist.
    checkKeys()

    # Validate that a request using mutual authentication is accepted by Cloudflares WAF.
    validateAuthentication()

def setStatus(filename , dataToSave):
    f = open('./codebase/' + filename, "w+")
    f.write(dataToSave)
    f.close()
    
def run():
    # Set the directory to codebase
    currentDirectory = os.getcwd()
    os.chdir('./codebase')

    # Start server
    os.system('touch history.json')

    print("\n [+] Running server!.\n")

    os.system('sudo -u ' + NON_ROOT_USER + ' python3 driver.py')

    # Set the directory back to the parent directory
    os.chdir(currentDirectory)




def cleanUp():
    print("\n [+] Cleaning up server files.\n")
    os.system("rm -Rfv ./codebase ./docker build.sh") 

    print("\n [+] Cleaning up game files in ramdisk..\n")
    os.system("rm -Rfv /tmp/ramdisk/codebase") 


def checkKeys():
    while True:
        print(" [+] Checking private certificate and key...")
        if not (os.path.isfile('./codebase/driver.py') and \
            os.path.isfile('./codebase/private.cert') and \
            os.path.isfile('./codebase/private.key')):
            print(" [!] Could not find 'private.cert' and/or private.key, ensure the 'codebase' \
                folder exists and is populated with the 'private.cert' AND the 'private.key... \n\t Trying again..." )
            time.sleep(5)
        else:
            return

def validateAuthentication():
        headers = {
        'Content-Type': 'application/json',
        }
        response = requests.request('GET', "https://certificate.pacman.ai", headers=headers, cert=("./codebase/private.cert", "./codebase/private.key"))
        # If the response is 403 (forbidden, blocked by cloudflares WAF rules for a bad certificate for mutual authentication)
        if response.status_code == 403:
            print(" [!] Error there was an issue with the certificates. This is either due to an issue with the request itself or the certificate and/or key are corrupted / not valid. Terminating with FAILURE.")
            exit(403)
        # If the the 
        elif response.status_code == 200:
            print(" [+] Certifcate and key have been successfully validated...")
        else:
            print(" [!] Some unknown error occurred...")
            print(" [!] Dumping request: \n\n")
            print(response.json())
            print("\n\n [+] Please contact me with the error shown above if needed.")
            exit(1)

def installRequirements():
    # Install all required dependencies to tun the server and the Docker containers that the runners use.
    # Passing in the non root user to run docker as a non root user to reduce any escelated privileges when running the un trusted code in the secure containers.
    currentDirectory = os.getcwd()
    os.chdir('./codebase')

    os.system('sudo sh install.sh ' + NON_ROOT_USER)

    # Set the directory back to the parent directory
    os.chdir(currentDirectory)

def getGameResources():
    # use userKey to send key
    # Only update and sent to KV if logMsg array length is different, and gameResults are diff README
#    os.system("wget ")
    headers = {'userKey': KEY}
    request = requests.get(GAME_CODEBASE_RESOURCE_URL, headers=headers)

    z = zipfile.ZipFile(io.BytesIO(request.content))
    
    # Get the code from (private) GitHub Repo.
    z.extractall(".")

    print("\n\t [+] Creating directory 'codebase' in ramdisk.\n")
    os.system('mkdir /tmp/ramdisk/codebase')

    time.sleep(5)
    print("\n\t [+] Moving files.\n")

    os.system("mv ./" + request.headers['X-PACMAN-ZIPNAME'] + "-" + request.headers['X-GITHUB-RELEASE-VERSION'] + "/* /tmp/ramdisk/codebase")

    time.sleep(5)

    print("\n\t [+] Cleaning up.\n")
    os.system("rm -Rfv " + request.headers['X-PACMAN-ZIPNAME'] + "-" + request.headers['X-GITHUB-RELEASE-VERSION']) 

# Clean up if needed. (Just ensuring there are no left over files that may interfear with updating files etc.)
cleanUp()

# Get the codebase
getResources()

# Install and set up environment
installRequirements()

# Install the code to run games (by BERKELY Uni and updated by Sebastian RMIT)
getGameResources()

# Run server 
run()

# Clean up
# cleanUp()

