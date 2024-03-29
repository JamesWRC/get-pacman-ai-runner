org = ""
org_key = ""
non_root_user=""
update_system=False
patch_os=False

import os
import json
import requests
import zipfile, io
import base64
import time
from pwd import getpwnam
import sys
import subprocess
from util import Util


CODEBASE_RESOURCE_URL = "https://getresources.pacman.ai"            # Codebase to install server
GAME_CODEBASE_RESOURCE_URL = CODEBASE_RESOURCE_URL + "/runner"    # Codebase to get the code to run the games.
COMPLETED_JOB_HISTORY = "./codebase/history.json"

#Get the Personal Access Token (PAT) to fetch the Pacman-ai-runner prebuilt amd64(x86) and aarch64(arm), default aarch64 container.
PACMAN_AI_CONTAINER_PAT = 'https://api.pacman.ai/auth/generatePAT'


def setVariables():
    #.
    from dotenv import load_dotenv
    load_dotenv()

    if(os.getenv('ORG_KEY') != ""):
        try:
            global org
            global org_key
            global non_root_user
            global update_system
            global patch_os

            org = os.getenv('ORG')
            org_key = os.getenv('ORG_KEY')
            non_root_user = os.getenv('NON_ROOT_USER')
            update_system = os.getenv('UPDATE_SYSTEM').lower() in ('true', '1', 't', 'True', 'TRUE')
            patch_os = os.getenv('PATCH_OS').lower() in ('true', '1', 't', 'True', 'TRUE')
            return True
        except:
            return False
    else:
        return False
    # gets values from this script, .env file or params when running this file.



def getResources():
    # use userKey to send key
    # Only update and sent to KV if logMsg array length is different, and gameResults are diff README
#    os.system("wget ")
    headers = {'userKey': org_key}
    request = requests.get(CODEBASE_RESOURCE_URL, headers=headers, stream=True)
    with open('pacman-ai-runner', 'wb') as fd:
        for chunk in request.iter_content(chunk_size=128):
            fd.write(chunk)
    
    z = zipfile.ZipFile('pacman-ai-runner')
    
    # Get the code from (private) GitHub Repo.
    z.extractall(".")

    print("\n \t[+] Moving files.\n")
    print(request.headers['X-PACMAN-ZIPNAME'])
    print(request.headers['X-GITHUB-RELEASE-VERSION'])
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

    print("\n \t[+] Cleaning up.\n")
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

    os.system('sudo chown ' + non_root_user + ' *')

    os.system('sudo chmod +x docker/runner/runner.py')
    os.system('sudo chown ' + non_root_user + ' docker/runner/runner.py')

    # Set the directory to codebase
    currentDirectory = os.getcwd()
    os.system('sudo -u ' + non_root_user + ' touch history.json')

    os.chdir('./codebase')

    os.system('sudo chown ' + non_root_user + ' *')

    # Start server
    # os.system('sudo -u ' + NON_ROOT_USER + ' touch history.json')
    

    print("\n \t[+] Running server!.\n")

    # !! Note: Driver will run as root so that it can remove left over folders.
    os.system('sudo python3 driver.py')

    # Set the directory back to the parent directory
    os.chdir(currentDirectory)




def cleanUp():
    print("\n \t[+] Cleaning up server files.\n")
    os.system("rm -Rfv ./codebase ./docker build.sh") 

    print("\n \t[+] Cleaning up game files in ramdisk.\n")
    os.system("rm -Rfv /tmp/ramdisk/*")

    
   

    # print("\n [+] Cleaning pacman docker image.\n")
    # os.system('docker image prune --force') 

    # print("\n [+] Cleaning pacman build cache.\n")
    # os.system('docker builder prune --force')

    # print("\n [+] Cleaning unused docker images.\n")
    # os.system('docker image rm --force pacman:latest')

    # print("\n [+] Cleaning unused Docker volumes.\n")
    # os.system('docker system prune -f --volumes')

def cleanContainerVolumes():
    from codebase.util import Util
    print(" \t[+] Removing volume for runners...")
    for runner in range(0, Util().getNumRunners()):
        os.system('docker rm -v runner' + str(runner))
        os.system('docker stop runner' + str(runner))
        os.system('docker rm runner' + str(runner))
        print(" \t\t[-] Removed volume for runner" + str(runner) + ".")

def checkKeys():
    while True:
        print(" \t[+] Checking private certificate and key...")
        if not (os.path.isfile('./codebase/driver.py') and \
            os.path.isfile('./codebase/private.cert') and \
            os.path.isfile('./codebase/private.key')):
            print(" \t[!] Could not find 'private.cert' and/or private.key, ensure the 'codebase' \
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
            print(" \t[!] Error there was an issue with the certificates. This is either due to an issue with the request itself or the certificate and/or key are corrupted / not valid. Terminating with FAILURE.")
            exit(403)
        # If the the 
        elif response.status_code == 200:
            print(" \t[+] Certifcate and key have been successfully validated...")
        else:
            print(" \t[!] Some unknown error occurred...")
            print(" \t[!] Dumping request: \n\n")
            print(response.json())
            print("\n\n \t[+] Please contact me with the error shown above if needed.")
            exit(1)

def installRequirements():
    # Install all required dependencies to tun the server and the Docker containers that the runners use.
    # Passing in the non root user to run docker as a non root user to reduce any escelated privileges when running the un trusted code in the secure containers.
    currentDirectory = os.getcwd()
    os.chdir('./codebase')

    os.system('sudo sh install.sh ' + non_root_user)

    # Set the directory back to the parent directory
    os.chdir(currentDirectory)

def getGameResources():
    # use userKey to send key
    # Only update and sent to KV if logMsg array length is different, and gameResults are diff README
#    os.system("wget ")
    headers = {'userKey': org_key}
    request = requests.get(GAME_CODEBASE_RESOURCE_URL, headers=headers)

    z = zipfile.ZipFile(io.BytesIO(request.content))
    
    # Get the code from (private) GitHub Repo.
    z.extractall(".")

    print("\n \t[+] Creating directory 'codebase' in ramdisk.\n")
    os.system('mkdir /tmp/ramdisk/codebase')

    time.sleep(5)
    print("\n \t[+] Moving files.\n")

    os.system("mv ./" + request.headers['X-PACMAN-ZIPNAME'] + "-" + request.headers['X-GITHUB-RELEASE-VERSION'] + "/* /tmp/ramdisk/codebase")

    time.sleep(5)

    print("\n \t[+] Cleaning up.\n")
    os.system("rm -Rfv " + request.headers['X-PACMAN-ZIPNAME'] + "-" + request.headers['X-GITHUB-RELEASE-VERSION']) 



def buildDockerImage(cleanBuild, dev):
    # Get the docker container needed to run cross platform
    os.system('docker run --privileged --rm tonistiigi/binfmt --install all')
    
    from util import Util
    headers = { 'userKey': org_key, }
    print("### Cleaning up unused Docker Containers, Images, Volumes, Networks & Build cache.")
    os.system('docker system prune --volumes -f')

    tokenResponse = Util().makeRequest(PACMAN_AI_CONTAINER_PAT, 'GET', headers)
    print(tokenResponse.content)
    tokenResponse = tokenResponse.json()
    #Gets the value of the success in the response, if its true then pull, 
    # if its false or does not exist then try and build manually.

    if dev:
        print("\n \t[+] Building fresh docker image.\n")
        os.system('docker buildx build --platform linux/aarch64 --force-rm=true -t pacman:latest -f ./docker/Dockerfile .')
        return

    if tokenResponse.get('success', False) and tokenResponse.get('token'):
        pullFromGitHubPackageRegistry = 'echo '+ str(tokenResponse.get('token')) + ' | docker login ghcr.io -u JamesWRC --password-stdin'
        os.system(pullFromGitHubPackageRegistry)
        os.system('docker pull ghcr.io/jameswrc/pacman-ai-runner:aarch64-latest')
    elif cleanBuild:
        print("\n \t[+] Building fresh docker image.\n")
        os.system('docker buildx build --platform linux/amd64 --force-rm=true -t pacman:aarch64-latest -f ./docker/Dockerfile . --no-cache')
    else:
        print("\n \t[+] Semi-building using older docker image.\n")
        os.system('docker buildx build --platform linux/amd64 --force-rm=true -t pacman:aarch64-latest -f ./docker/Dockerfile .')
        pass    

def backupHistoryFile():
    # Open and backup the history file
    tempHistoryFile = None
    print(" \t[+] BACKING UP FILE")
    if os.path.isfile(COMPLETED_JOB_HISTORY):
        with open(COMPLETED_JOB_HISTORY, 'r') as jsonFile:
            tempHistoryFile = json.load(jsonFile)
            jsonFile.close()
    return tempHistoryFile


def restoreJobHistory(tempHistory):
    # Save history file
    print(" \t[+] RESTORING FILE")
    print(tempHistory)
    if tempHistory is not None:
        with open(COMPLETED_JOB_HISTORY, 'w+') as jsonFile:

            json.dump(tempHistory, jsonFile)
            jsonFile.close()

def detectAndPatchOSForDocker():
    # Need to apply the right patched to the OS Kernel to ensure that Docker
    # Can isolate memory (RAM) to each container and disable swap memory.

    print(" \t[+] Patching OS")

    # Detect OS 
    raspberryPiOS = False
    ubuntu = False
    raspianCheck = subprocess.check_output(['cat', '/etc/os-release']).decode('utf-8')
    if raspianCheck.lower().find("raspian"):
        raspberryPiOS = True
    else:
        print(raspianCheck.lower())

        print("error")
        exit(0)
    



    # Apply patch
    if raspberryPiOS and os.path.isfile('/boot/cmdline.txt'):
        bootFileData = None
        with open('/boot/cmdline.txt') as f:
            bootFileData = f.read()
            f.close()

        if "cgroup_enable=cpuset" in bootFileData and \
            "cgroup_enable=memory" in bootFileData and "cgroup_memory=1" in bootFileData:

            print(" \t[+] RaspberryPi OS is already patched.")
        else:
            print(" \t[+] Disabling memory swap space!")
            os.system('sudo dphys-swapfile swapoff')

            print(" \t[+] RaspberryPi OS needs to be patched!")

            with open("/boot/cmdline.txt", "w+") as bootFile:
                bootFile.seek(0)
                patchToWrite = ""
                if "cgroup_enable=cpuset" not in bootFileData:
                    patchToWrite += "cgroup_enable=cpuset "
                if "cgroup_enable=memory" not in bootFileData:
                    patchToWrite += "cgroup_enable=memory "

                if "cgroup_memory=1" not in bootFileData:
                    patchToWrite += "cgroup_memory=1 "

                bootFile.write(str(bootFileData.replace('\n',' ') + patchToWrite))

            with open('/boot/cmdline.txt') as f:
                if "cgroup_enable=cpuset" in f.read() and \
                "cgroup_enable=memory" in f.read() and "cgroup_memory=1" in f.read():
                    print(" \t[+] RaspberryPi OS has been successfully patched!")
                    time.sleep(5)
                    print(" \t[+] RaspberryPi OS needs to be rebooted for patch to take effect.")
                f.close()
                print(" \t[+] RaspberryPi System rebooting in 5 seconds...")
                time.sleep(5)
                os.system('sudo reboot now')

print(setVariables())
print(org_key)
if not setVariables():
    print(".env file is not set up correctly. See README about how to set it up.")

if patch_os:
    detectAndPatchOSForDocker()    

# Back up the history file that stores previously run jobs
tempHistory = backupHistoryFile()

# Clean up if needed. (Just ensuring there are no left over files that may interfear with updating files etc.)
cleanUp()

# Get the codebase
getResources()

# Install and set up environment
installRequirements()

# Removes containers volumes since they dont get updated
cleanContainerVolumes()

# Install the code to run games (by BERKELY Uni and updated by Sebastian RMIT)
getGameResources()

# Build the image
buildClean = True
dev = False
if len(sys.argv) > 1:
    if sys.argv[1] == "--no-clean-build" or sys.argv[1] == "-ncb":
        buildClean = False
    if sys.argv[1] == "--dev" or sys.argv[1] == "-d":
        dev = True
buildDockerImage(buildClean, dev)

# Restore hostory file
restoreJobHistory(tempHistory)

# Run server 
run()

# Removes containers volumes since they dont get updated
cleanContainerVolumes()

# Clean up
# cleanUp()
