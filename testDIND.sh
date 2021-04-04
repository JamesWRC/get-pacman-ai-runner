docker buildx build --platform linux/arm64 -t dindtest .

docker run --privileged dindtest