docker buildx build --platform linux/arm64 -t dindtest .
ramAmt=$(python3 util.py getHostRamDisk)
docker run -v "/var/run/docker.sock:/var/run/docker.sock" --tmpfs /run:rw,noexec,nosuid,size="$ramAmt"m dindtest