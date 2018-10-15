# Self-Host Anything

This repository consists of a list of services I run on a headless Lenovo ThinkCentre workstation.  You should be able to run this on any reasonably powerful computer (pentium 4 or greater??).  This probably won't work on a Raspberry Pi.

This repo contains my examples for:

* Plex Media Server
* Shout IRC client
* NextCloud
* Syncthing
* Samba Fileshare Server
* Torrent server with OpenVPN over NordVPN

When you're done, you will be able to access your home services from anywhere over HTTPS, using

* Nginx Proxy: https://github.com/jwilder/nginx-proxy
* LetsEncrypt companion: https://github.com/JrCs/docker-letsencrypt-nginx-proxy-companion

## Prerequisites

* A linux server on your local network running CoreOS, Ubuntu >= 15.04, or really whatever.
  * systemd installed
  * docker CE installed
* Your own domain name
* An AWS Account for Dynamic DNS -- will be (mostly) contrained to free tier usage.

**IMPORTANT** - `media-sdb.service` may or may NOT apply to you, and you might have to disable it.  My server has a secondary spinning disk that I mount all my docker container's shared volumes to.  I mount this disk at `/media/sdb`, then symlink that directory to `/dockmount`.  All these containers mount shared volumes at `/dockmount/<containername>`.  Some containers share a filespace.  I'm then free to completely wipe my boot disk without losing any data.

# Setup

I won't walk you through [setting up CoreOS (guide here)](https://coreos.com/os/docs/latest/installing-to-disk.html), so you should be able to do this.  Ubuntu will probably work too, but I like CoreOS because of how lightweight it is.  The [CoreOS ISO image](https://coreos.com/os/docs/latest/booting-with-iso.html) has everything you need to compile `ignition.yml`.  Be sure to replace that ssh public key with your own!

## Home network prep

You need to make sure that ports 80 and 443 are port-forwarded through your router to whatever host this will be on.  I also recommend setting your server to be assigned a static IP by your router.  You can usually do this by interface MAC address.  `ifconfig` will list your interfaces.

## When you get an OS installed: (run as root)

* Clone this repo in `/etc/systemd/system`
* For any overrides, like `torrent.service.d`, copy the template to a new `override.conf` file with the correct values.
* Create a symlink: `ln -s /etc/systemd/system/profile.env /etc/profile.env`, and edit `profile.env` for your needs (see DNS section)
* If you're using Lambda Dynamic DNS, go complete that section below!
* Reload systemd: `systemctl daemon-reload`  -- this must be run ANY TIME any of your `.service` or `.conf` files change.
* Enable all the services: `systemctl enable <name>.service` -- you'll need to do this for any additional services you add in the future.

## Dynamic DNS (recommended)

Resolving the IP address of your home network is annoying because most DNS providers change your IP every now and again.  Services like No-IP combat this, but they aren't the most reliable.  However, setting DNS programatically is (conceptually) trivial with AWS, Route53, and Lambda.  I've found it to be quite reliable.

### AWS Stuff

1. [Setup a Hosted Zone with Route53](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/CreatingHostedZone.html). **Costs $0.50 per month**
2. Deploy [Route53 Dynamic DNS Lambda](https://github.com/awslabs/route53-dynamic-dns-with-lambda) as directed.  Note that the cloudformation stack name **must be lowercase**.  Use `route53ZoneId` option to specify the ID of the hosted zone in step 1.  `route53ZoneName` must match the zone name.
3. Pay attention to the [stack outputs](https://github.com/awslabs/route53-dynamic-dns-with-lambda#cloudformation-stack-outputs) - you'll need these later.

### Docker Stuff

Now that we have a DNS provider setup, we need to create the container service that will keep it up to date.

* In `cd dockerfiles/lambda-dns`, run `docker build -t dyndns-local .` -- the trailing `.` is IMPORTANT :)
* In `dyndns.service.d`, create a copy of the example config called `override.conf` and set the `APIKEY`, `SECRET`, and `APIURL` to the values from step 3 above.

Test it by running:

```bash
export APIURL=YOURURL
export APIKEY=YOURKEY
export DNS_DOMAIN=YOURDOMAIN
export SECRET=YOURSECRET
/usr/bin/docker run --name dyndns --rm -it \
    -e APIURL="${APIURL}" \
    -e APIKEY="${APIKEY}" \
    -e HOSTNAME="${DNS_DOMAIN}" \
    -e SECRET="${SECRET}" \
    -e CRON_SCHEDULE="@hourly" \
    dyndns-local
```

### Manual stuff

In this setup, each container's service will serve from a different subdomain of your Route53 hosted zone dyndns subdomain.  If you set up a hosted zone at `route53.example.com`, then set `DNS_DOMAIN=myserver.route53.example.com`, your services would be publically available on `https://service.myserver.route53.example.com`.

For each service, you'll need to create CNAME records for each `service.myserver.route53.example.com` to point to `myserver.route53.example.com` because all of your services are running on the same hostm but the host needs to be able to do virtual host routing based on domain name.

# Troubleshooting

```bash
# Handy commands
docker ps
docker logs <name>

# Systemctl
systemctl status name.service
systemctl restart name.service
systemctl disable name.service
```