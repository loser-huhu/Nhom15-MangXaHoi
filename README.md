## Run with Docker

1. Install Docker Desktop(terminal):
https://www.docker.com/products/docker-desktop/

2. Restart PC

3. Build image(terminal):
docker build -t webchat-flask .

4. Run container(terminal):
docker run -p 5000:5000 webchat-flask

5. Open browser:
http://localhost:5000
