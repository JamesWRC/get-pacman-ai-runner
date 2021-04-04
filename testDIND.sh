docker buildx build --platform linux/arm64 -t dindtest .

docker run -v "/var/run/docker.sock:/var/run/docker.sock" dindtest