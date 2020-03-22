# Self-Host Anything with systemd and docker

![Uptime Robot ratio (30 days)](https://img.shields.io/uptimerobot/ratio/m784171033-0a5b0fa97302da182e304db8)

This repository consists of a list of services I run on a headless Lenovo ThinkCentre workstation.  You should be able to run this on any reasonably powerful computer (pentium 4 or greater??).  This probably won't work on a Raspberry Pi.

This repo contains my examples for these services and others:

* Plex Media
* Shout IRC
* Minio
* Syncthing
* Calibre Web
* Samba Fileshare
* Torrent server with OpenVPN over NordVPN
* PiHole DNS

When you're done, you will be able to access your services from anywhere over HTTPS, using

* Nginx Proxy: https://github.com/jwilder/nginx-proxy
* LetsEncrypt companion: https://github.com/JrCs/docker-letsencrypt-nginx-proxy-companion

## Prerequisites

* A linux server on your local network (CoreOS, Ubuntu >= 15.04, whatever...) with `Docker CE` and `systemd` installed.
* A domain name.
* A cloudflare account.
* A build of https://github.com/subdavis/systemd-docker

### Volume Mounts

**IMPORTANT** - Some of my services, like `media-sdb.service`, may or may NOT apply to you, and you might have to disable them.  My server has 3 separate storage volumes that I spread my volume mounts across.  I mount my secondary disks at `/media/sdX`, then symlink that directory to `/dockmount`.  All these containers bind-mount volumes at `/media/sdX/<containername>`.  Some containers share mounts, like plex and samba.  You can change the container mount points in `profile.env` without having to modify service files.

# Setup

I won't walk you through [setting up CoreOS (guide here)](https://coreos.com/os/docs/latest/installing-to-disk.html), so you should be able to do this.  Ubuntu will probably work too, but I like CoreOS because of how lightweight it is.  The [CoreOS ISO image](https://coreos.com/os/docs/latest/booting-with-iso.html) has everything you need to compile `ignition.yml`.  Be sure to replace that ssh public key with your own!

You can [get my build of systemd-docker](https://github.com/subdavis/systemd-docker/releases/tag/1.0.0) for linux amd64.  I've tested it on ubuntu 18.04 and coreos.

## Home network prep

You need to make sure that ports 80 and/or 443 are port-forwarded through your router to whatever host this will be on.  I also recommend setting your server to be assigned a static private IP by your router.  You can usually do this by interface MAC address.  `ifconfig` will list your interfaces.  Refer to the [docker-pi-hole](https://github.com/pi-hole/docker-pi-hole) docs for further network setup related to that service.

## Dynamic DNS (recommended)

Resolving the IP address of your home network is annoying because most DNS providers change your IP every now and again.  Services like No-IP combat this, but they aren't the most reliable.  However, setting DNS programatically is pretty easy with Cloudflare API

Follow the instructions at https://github.com/oznu/docker-cloudflare-ddns to get this part set up.

### Manual stuff

In this setup, each container's service will serve from a different subdomain of your Cloudflare hosted zone dyndns subdomain.  If you set up a hosted zone at `foo.example.com`, then set `DNS_DOMAIN=example.com`, your services would be publically available on `https://service.example.com`.

For each service, you'll need to create CNAME records for each `service.example.com` to point to `foo.example.com` because all of your services are running on the same host but the host needs to be able to do virtual host routing based on domain name.

## Installation

Don't do this until you have your CNAMEs and Dynamic DNS working.

* Clone this repo in `/etc/systemd/system` on your newly provisioned server.
* For any overrides, like `torrent.service.d`, copy the template to a new `override.conf` file with the correct values.
* create `profile.env` from template: `cp /etc/systemd/system/profile.env.example /etc/systemd/system/profile.env`
* edit `profile.env` for your needs
* If you're using Lambda Dynamic DNS, go complete that section below!
* Reload systemd: `systemctl daemon-reload`. This must be run ANY TIME any of your `.service` or `.conf` files change.
* Enable all the services and timers: `systemctl enable <name>.<service|timer>`

# Troubleshooting

```bash
# Handy commands
docker ps
docker logs <name>

# Systemctl
systemctl daemon-reload
systemctl status name.service
systemctl restart name.service
systemctl disable name.service

# journalctl
journalctl -u name.service --since yesterday
```
