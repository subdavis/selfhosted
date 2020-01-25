# Self-Host Anything with systemd and docker

![Uptime Robot ratio (30 days)](https://img.shields.io/uptimerobot/ratio/m784171033-0a5b0fa97302da182e304db8)  [Uptime Robot Monitoring](https://status.aws.subdavis.com/)

This repository consists of a list of services I run on a headless Lenovo ThinkCentre workstation.  You should be able to run this on any reasonably powerful computer (pentium 4 or greater??).  This probably won't work on a Raspberry Pi.

This repo contains my examples for these services and others:

* Plex Media
* Shout IRC
* NextCloud
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
* An AWS Account for Dynamic DNS.  Our use will be constrained to permanent free-tier except for a single Route53 Hosted Zone, which is $0.50 a month.

### Volume Mounts

**IMPORTANT** - Some of my services, like `media-sdb.service`, may or may NOT apply to you, and you might have to disable them.  My server has 3 separate storage volumes that I spread my volume mounts across.  I mount my secondary disks at `/media/sdX`, then symlink that directory to `/dockmount`.  All these containers bind-mount volumes at `/media/sdX/<containername>`.  Some containers share mounts, like plex and samba.  You can change the container mount points in `profile.env` without having to modify service files.

# Setup

I won't walk you through [setting up CoreOS (guide here)](https://coreos.com/os/docs/latest/installing-to-disk.html), so you should be able to do this.  Ubuntu will probably work too, but I like CoreOS because of how lightweight it is.  The [CoreOS ISO image](https://coreos.com/os/docs/latest/booting-with-iso.html) has everything you need to compile `ignition.yml`.  Be sure to replace that ssh public key with your own!

## Home network prep

You need to make sure that ports 80 and/or 443 are port-forwarded through your router to whatever host this will be on.  I also recommend setting your server to be assigned a static private IP by your router.  You can usually do this by interface MAC address.  `ifconfig` will list your interfaces.  Refer to the [docker-pi-hole](https://github.com/pi-hole/docker-pi-hole) docs for further network setup related to that service.

## Dynamic DNS (recommended)

Resolving the IP address of your home network is annoying because most DNS providers change your IP every now and again.  Services like No-IP combat this, but they aren't the most reliable.  However, setting DNS programatically is (conceptually) trivial with AWS, Route53, and Lambda.  I've found it to be quite reliable.


1. [Setup a Hosted Zone with Route53](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/CreatingHostedZone.html). **Costs $0.50 per month**
2. Deploy [Route53 Dynamic DNS Lambda](https://github.com/awslabs/route53-dynamic-dns-with-lambda) as directed.  Note that the cloudformation stack name **must be lowercase**.  Use `route53ZoneId` option to specify the ID of the hosted zone in step 1.  `route53ZoneName` must match the zone name.
3. Pay attention to the [stack outputs](https://github.com/awslabs/route53-dynamic-dns-with-lambda#cloudformation-stack-outputs) - you'll need these later.
4. In `dyndns.service.d`, create a copy of the example config called `override.conf` and set the `APIKEY`, `SECRET`, and `APIURL` to the values from step 3 above.

Test it by running:

```bash
APIURL=YOURURL
APIKEY=YOURKEY
DNS_DOMAIN=YOURDOMAIN
SECRET=YOURSECRET
/usr/bin/docker run --name dyndns --rm -it \
    --env APIURL="${APIURL}" \
    --env APIKEY="${APIKEY}" \
    --env HOSTNAME="${DNS_DOMAIN}" \
    --env SECRET="${SECRET}" \
    dyndns-local
```

### Manual stuff

In this setup, each container's service will serve from a different subdomain of your Route53 hosted zone dyndns subdomain.  If you set up a hosted zone at `route53.example.com`, then set `DNS_DOMAIN=myserver.route53.example.com`, your services would be publically available on `https://service.myserver.route53.example.com`.

For each service, you'll need to create CNAME records for each `service.myserver.route53.example.com` to point to `myserver.route53.example.com` because all of your services are running on the same host but the host needs to be able to do virtual host routing based on domain name.

## Installation

Don't do this until you have your CNAMEs and Dynamic DNS working.

* Clone this repo in `/etc/systemd/system` on your newly provisioned server.
* For any overrides, like `torrent.service.d`, copy the template to a new `override.conf` file with the correct values.
* Create a symlink: `ln -s /etc/systemd/system/profile.env /etc/profile.env`, and edit `profile.env` for your needs.
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
```
