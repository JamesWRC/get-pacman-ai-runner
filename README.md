ORG="DEFAULT"
ORG_KEY=""
NON_ROOT_USER="Pacman"
UPDATE_SYSTEM="false"
PATCH_OS="false"


```
sudo apt-get install qemu binfmt-support qemu-user-static
docker run --rm --privileged multiarch/qemu-user-static --reset -p yes
docker run --privileged --rm tonistiigi/binfmt --install all
```