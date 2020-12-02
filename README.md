# Self-Host Anything 

> with docker-compose and traefik

![Uptime Robot ratio (30 days)](https://img.shields.io/uptimerobot/ratio/m784171033-0a5b0fa97302da182e304db8)

This repo contains my production systemd services.  When you're done, you will be able to access your services from anywhere over HTTPS, using [traefik](https://traefik.io)

* Plex Media
* TheLounge IRC
* Minio
* Calibre Web
* Samba Fileshare
* Torrent server with OpenVPN over NordVPN
* Multiple PiHole DNS Servers (primary and backup)
* Seafile Pro with Elasticache

# Documentation

I've also written some intermediate to advanced generic usage docs for traefik, docker, pihole, and home networking.  These articles are generally applicable, but some may be more useful than others.

* [Configuring Wildcard Certs for Traefik](docs/wildcard-certs.md)
* [LAN-only Traefik Routing with ACME SSL](docs/lan-only-routes.md)
* [Configuring PiHole with dnsmasq](docs/pihole-dnsmasq.md)
* [EdgeRouter Backups over SSH (SCP)](docs/edgerouter-backups.md)

## Prerequisites

* A linux server on your local network (CoreOS, Ubuntu >= 15.04, whatever...) with `Docker CE` and `docker-compose` installed.
* A router or firewall capable of dnsmasq. I use a Ubiquiti EdgeRouter X.
* A domain name.
* A cloudflare account.

## Home network prep

* You need to make sure that ports 80 and/or 443 are port-forwarded through your router to whatever host this will be on.
* I also recommend setting your server to be assigned a static private IP by your router.  `ifconfig` will list your interfaces.
* Refer to the [docker-pi-hole](https://github.com/pi-hole/docker-pi-hole) docs and [my docs](docs/pihole-dnsmasq.md) for further network setup related to that service.

### DNS Configuration

In this setup, each container's service will serve from a different subdomain of your Cloudflare hosted zone dyndns subdomain.

* Modify `docker/.env.prod` and set `DNS_DOMAIN=mydomain.com`
* Create an `A` record for `core.mydomain.com` to point to your public IP.
* For each service, you'll need to create CNAME records for each `service.mydomain.com` to point to `core.mydomain.com` because all of your services are running on the same host but the host needs to be able to do virtual host routing based on domain name.
* Your services will be publically available on `https://servicename.mydomain.com`.

## Dynamic DNS (recommended)

Resolving the IP address of your home network is annoying because most DNS providers change your IP every now and again.  Services like No-IP combat this, but they aren't the most reliable.  However, setting DNS programatically is pretty easy with Cloudflare API.

* Follow the instructions in [Configuring Wildcard Certs for Traefik](docs/wildcard-certs.md) to get this part set up.
* You'll need to modify `docker/.env.prod` with your domain info, ACME email, and cloudflare API tokens.

### Volume Mounts

Some of my services, like `media-primary.service`, may not apply to you, and you might have to disable them.  My server has several separate storage volumes that I spread my volume mounts across.  Some containers share mounts, like plex and samba.  You can change the container mount points in `docker/.env.prod` without having to modify service files.

* Most of my mounts are on a Raid 1 mirror at `/media/primary`.
* Backups and lower-redundancy data (like plex movies) go on `/media/secondary`.
* High-iops, low-redundancy data like access logs go on `/media/local` where data loss will be tolerated.

## Installation

Don't do this until you have your CNAMEs and Dynamic DNS working.

* Start with a fresh install of Ubuntu server
* Fork or Clone this repo. `git clone git@github.com:subdavis/selfhosted git/usr/local/lib/systemd/system`
* `mkdir /media/local` to create a mount point on the OS disk.
* create `docker/.env.prod` from the `docker/.env` template
* create `passwords.txt` with the `htpasswd` command in `./etc`
* Sign into any private docker registries
  * [Seafile Pro](https://www.seafile.com/en/product/private_server/) is free for 3 users
  * [Seafile Pro Docker Docs](https://download.seafile.com/published/seafile-manual/docker/pro-edition/Deploy%20Seafile-pro%20with%20Docker.md) are hard to find.
* Reload systemd: `systemctl daemon-reload`. This must be run **ANY TIME** any of your `.service` or `.conf` files change.
* Enable all the services: `systemctl enable <name>.service`
* You may need to disable ubuntu's default dns service and remove resolf.conf  [read more](https://www.smarthomebeginner.com/run-pihole-in-docker-on-ubuntu-with-reverse-proxy/).
* Start all the services: `systemctl start <name>.service`
* Start all the containers: `cd docker && docker-compose --env-file .env.prod up -d`
* [Enable Unattended Upgrades](https://help.ubuntu.com/community/AutomaticSecurityUpdates)

# Automatic deployments and drone


* Create a github app. Follow drone setup instructions
* Make sure the user filtering config is set correctly so other users can't log in
* Create a `deploy` user with SSH authentication
* Add the user to the `docker` group
* Add your public key key to `/home/deploy/.ssh/authorized_keys`
* Add the private key to `ssh_key` secret in drone.
* In drone, add your repository.

# Troubleshooting

```bash
# Handy commands
docker ps
docker logs <name>

# Systemctl
systemctl daemon-reload
systemctl status name.service
systemctl disable name.service

# systemctl restart name.service
docker stop name.service # use docker stop, it's quicker

# journalctl
journalctl -u name.service --since yesterday
docker logs -f name.service
```
