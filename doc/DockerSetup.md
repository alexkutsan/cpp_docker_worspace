# Prepare Linux for work with SDL docker registry.

## Install docker:

[Docker installation help](https://docs.docker.com/install/linux/docker-ce/ubuntu/)

```
curl -fsSL get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

<b>Note:</b> Don't forget to logout and login for the changes to take effect.

Test docker installation:

```
docker run hello-world
```
