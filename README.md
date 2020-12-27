# selfhosted services

> with docker-compose and traefik

![Uptime Robot ratio (30 days)](https://img.shields.io/uptimerobot/ratio/m784171038-19b52e00f52a8d916ba46346)
[![Build Status](https://drone.subdavis.com/api/badges/subdavis/selfhosted/status.svg)](https://drone.subdavis.com/subdavis/selfhosted)

This repo contains my production docker services accessible from anywhere over HTTPS using [traefik](https://traefik.io).  These services (and others) run on a single server.

* Plex Media
* Seafile Pro with Elasticache
* Minio
* Calibre Web
* Samba Fileshare
* Transmission torrent server with OpenVPN over NordVPN
* AdGuard Home DNS
* Drone CI and runner

# Documentation

I've also written some intermediate to advanced generic usage docs for traefik, docker, pihole, and home networking.  These articles are generally applicable, but some may be more useful than others.

* [Configuring Wildcard Certs for Traefik](docs/wildcard-certs.md)
* [LAN-only Traefik Routing with ACME SSL](docs/lan-only-routes.md)
* [Configuring PiHole with dnsmasq](docs/pihole-dnsmasq.md)
* [EdgeRouter Backups over SSH (SCP)](docs/edgerouter-backups.md)

More great documentation.

* https://www.smarthomebeginner.com/traefik-2-docker-tutorial/
* https://github.com/isaacrlevin/HomeNetworkSetup
* https://github.com/htpcBeginner/docker-traefik

## Prerequisites

* A recent version of ubuntu server with `Docker CE` and `docker-compose` installed.
* A router or firewall capable of dnsmasq. I use a Ubiquiti EdgeRouter X.
* A domain name.
* A cloudflare account.

### Home network prep

* You need to make sure that ports 80 and 443 are port-forwarded through your router to whatever host this will be on.
* Your server should be assigned a static private IP by DNS.  `ifconfig` will list your interfaces.
* Refer to the [docker-pi-hole](https://github.com/pi-hole/docker-pi-hole) docs and [my docs](docs/pihole-dnsmasq.md) for further network setup related to that service.  Even though I use AdGuard Home, those docs are relevant.

### DNS Configuration

In this setup, each container's service will serve from a different subdomain of your Cloudflare hosted zone dyndns subdomain.

* Create an `A` record for `core.mydomain.com` to point to your public IP.
* For each service, you'll need to create CNAME records for each `service.mydomain.com` to point to `core.mydomain.com` because all of your services are running on the same host but the host needs to be able to do virtual host routing based on domain name.
* Your services will be publically available on `https://servicename.mydomain.com`.

### Dynamic DNS (recommended)

Resolving the IP address of your home network is annoying because most DNS providers change your IP every now and again.  Services like No-IP combat this, but they aren't the most reliable.  However, setting DNS programatically is pretty easy with Cloudflare API.

* Follow the instructions in [Configuring Wildcard Certs for Traefik](docs/wildcard-certs.md) to get this part set up.
* You'll need to modify `docker/.env.prod` with your domain info, ACME email, and cloudflare API tokens.

### Systemd Mount Dependencies

Some of my services like `media-primary.mount` may not apply to you, and you might have to disable them.  My server has several separate storage volumes that I spread my volume mounts across.  Some containers share mounts, like plex and samba.  You can change the container mount points in `docker/.env.prod` without having to modify service files.

* Most of my mounts are on a Raid 1 mirror at `/media/primary`.
* Backups and lower-redundancy data (like plex movies) go on `/media/secondary`.
* High-iops, low-redundancy data like access logs go on `/media/local` where data loss will be tolerated.

> **Note**: I've chosen to use systemd mounts rather than `/etc/fstab` to enforce startup behavior.  Dockerd will not be able to start without successful mounts to prevent data corruption from missing mount points.

Modify `Requires` and `After` in `/lib/systemd/system/docker.service` to reference your mount files.

```conf
[Unit]
# ...
After=network-online.target firewalld.service containerd.service media-primary.mount media-secondary.mount
Requires=docker.socket media-primary.mount media-secondary.mount
# ...
```

## Installation

It's best to have a dedicated user for running these services.

* Create a `deploy` user with SSH authentication
* Add the user to the `docker` group
* Add your public key key to `/home/deploy/.ssh/authorized_keys`

Don't do this until you have your CNAMEs and Dynamic DNS working.

* Start with a fresh install of Ubuntu server
* `mkdir /media/local` for host disk mounts
* create `.env.prod` from the `.env` template
* create `etc/passwords.txt` using the `htpasswd` command
* Sign into any private docker registries
  * [Seafile Pro](https://www.seafile.com/en/product/private_server/) is free for 3 users
  * [Seafile Pro Docker Docs](https://download.seafile.com/published/seafile-manual/docker/pro-edition/Deploy%20Seafile-pro%20with%20Docker.md) are hard to find.
* Install and enable `media-*.mount` systemd services.
* You may need to disable ubuntu's default dns service and remove resolf.conf [read more](https://www.smarthomebeginner.com/run-pihole-in-docker-on-ubuntu-with-reverse-proxy/).
  * There's a chicken-and-egg problem here.  You can't use your new DNS resolver until it's running, and you can't get it running without working DNS.  Don't make this change until you get the whole stack up and running and you can `dig @adguard-container-IP somedomain.com` successfully.
* Start all the containers: `docker-compose --env-file .env.prod up -d`
* [Enable Unattended Upgrades](https://help.ubuntu.com/community/AutomaticSecurityUpdates)
* `cp etc/traefik-logrotate.conf /etc/logrotate.d/traefik` to enable log rotation for traefik.

[Configure Authelia](https://www.smarthomebeginner.com/docker-authelia-tutorial/#4_Authelia_Users)

* Make secrets `pushd secrets && ./make-secrets.sh && popd`
* Configure Authelia.  Edit `authelia/configuration.yml` and make a copy of `authelia/users_database.example.yml` with your config

# Automatic deployments and drone

* Create a github api app. Follow drone setup instructions.
* Make sure the user filtering config is set correctly so other users can't log in
* Add the private key to `ssh_key` for your `deploy` user's secret key in drone.
* Open `drone.yourdomain.com` and finish configuring your repo.

# Other notes

* TTRSS icons dir requires permissions for "nobody" 65534
* docker login for watchtower seafile pro should be placed in 
