docker run -d --name gitlab-runner --restart always \
  -v $PWD/config:/etc/gitlab-runner \
  -v /var/run/docker.sock:/var/run/docker.sock \
  --network="gitlab-network" \
  gitlab/gitlab-runner:latest
