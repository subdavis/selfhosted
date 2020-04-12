# Self-Host Anything with systemd, docker, and traefik

![Uptime Robot ratio (30 days)](https://img.shields.io/uptimerobot/ratio/m784171033-0a5b0fa97302da182e304db8)

This repository consists of a list of services I run on a headless Lenovo ThinkCentre workstation.  You should be able to run this on any reasonably powerful computer (pentium 4 or greater??).  This probably won't work on a Raspberry Pi.

This repo contains my examples for these services and others:

* Plex Media
* TheLounge IRC
* Minio
* Calibre Web
* Samba Fileshare
* Torrent server with OpenVPN over NordVPN
* PiHole DNS
* ElasticSearch and Kibana

When you're done, you will be able to access your services from anywhere over HTTPS, using [traefik](https://traefik.io)

## Prerequisites

* A linux server on your local network (CoreOS, Ubuntu >= 15.04, whatever...) with `Docker CE` and `systemd` installed.
* A domain name.
* A cloudflare account.
* A build of https://github.com/subdavis/systemd-docker

### Volume Mounts

**IMPORTANT** - Some of my services, like `media-sdb.service`, may or may NOT apply to you, and you might have to disable them.  My server has 3 separate storage volumes that I spread my volume mounts across.  I mount my secondary disks at `/media/secondary`.  All these containers bind-mount volumes at `/media/primary/<containername>`.  Some containers share mounts, like plex and samba.  You can change the container mount points in `profile.env` without having to modify service files.

## Setup

* Start with a fresh install of Ubuntu server
* Install `systemd-docker`. You can [get my build of systemd-docker](https://github.com/subdavis/systemd-docker/releases/tag/1.0.0) for linux amd64.  I've tested it on ubuntu 18.04.

## Home network prep

You need to make sure that ports 80 and/or 443 are port-forwarded through your router to whatever host this will be on.  I also recommend setting your server to be assigned a static private IP by your router.  You can usually do this by interface MAC address.  `ifconfig` will list your interfaces.  Refer to the [docker-pi-hole](https://github.com/pi-hole/docker-pi-hole) docs for further network setup related to that service.

### DNS Configuration

In this setup, each container's service will serve from a different subdomain of your Cloudflare hosted zone dyndns subdomain. Set `DNS_DOMAIN=example.com`, then create an `A` record for `core.example.com`, the value of `LOCAL_DOMAIN` in `profile.env`. Your services will be publically available on `https://servicename.example.com`.

For each service, you'll need to create CNAME records for each `service.example.com` to point to `core.example.com` because all of your services are running on the same host but the host needs to be able to do virtual host routing based on domain name.

## Dynamic DNS (recommended)

Resolving the IP address of your home network is annoying because most DNS providers change your IP every now and again.  Services like No-IP combat this, but they aren't the most reliable.  However, setting DNS programatically is pretty easy with Cloudflare API.

Follow the instructions at https://github.com/oznu/docker-cloudflare-ddns to get this part set up.

For Traefik SSL, you can use the same token provided that you give it `DNS:Edit` and `Zone:Read` permissions as detailed in [the traefik letsencrypt docs](https://go-acme.github.io/lego/dns/cloudflare/).  Set these in `profile.env`.

## Installation

Don't do this until you have your CNAMEs and Dynamic DNS working.

* Clone this repo in `/usr/local/lib/systemd/system/` on your newly provisioned server.
* For any overrides, like `torrent.service.d`, copy the template to a new `override.conf` file with the correct values.
* create `profile.env` from template: `cp /usr/local/lib/systemd/system/profile.env.example /usr/local/lib/systemd/system/profile.env`
* edit `profile.env` for your needs
* create `passwords.txt` with the `htpasswd` command in `./etc`
* If you're using Lambda Dynamic DNS, go complete that section below!
* Reload systemd: `systemctl daemon-reload`. This must be run ANY TIME any of your `.service` or `.conf` files change.
* Enable all the services and timers: `systemctl enable <name>.<service|timer>`
* You may need to disable ubuntu's default dns service and remove resolf.conf.  [read more](https://www.smarthomebeginner.com/run-pihole-in-docker-on-ubuntu-with-reverse-proxy/).

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
