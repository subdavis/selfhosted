# rootless docker selfhosted services

> with docker-compose and traefik

![Uptime Robot ratio (30 days)](https://img.shields.io/uptimerobot/ratio/m784171038-19b52e00f52a8d916ba46346)
[![Build Status](https://drone.subdavis.com/api/badges/subdavis/selfhosted/status.svg)](https://drone.subdavis.com/subdavis/selfhosted)

This repo contains my production **rootless** docker services accessible from anywhere over HTTPS using [traefik](https://traefik.io).  These services (and others) run on a single server.

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
* [Expand LVM to fill remaining disk](docs/ubuntu-expand-lvm.md)

More great documentation.

* https://www.smarthomebeginner.com/traefik-2-docker-tutorial/
* https://github.com/isaacrlevin/HomeNetworkSetup
* https://github.com/htpcBeginner/docker-traefik

## Prerequisites

* A recent version of ubuntu server with rootless `Docker CE` and `docker-compose` installed (see below)
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
* You'll need to modify `.env` with your domain info, ACME email, and cloudflare API tokens.

## Installation

1. start with ubuntu lts
1. [Enable Unattended Upgrades](https://help.ubuntu.com/community/AutomaticSecurityUpdates)
1. clone this repo
1. Sign into any private docker registries
  a. [Seafile Pro](https://www.seafile.com/en/product/private_server/) is free for 3 users
  a. [Seafile Pro Docker Docs](https://download.seafile.com/published/seafile-manual/docker/pro-edition/)
1. install [rootless docker](https://docs.docker.com/engine/security/rootless/)
  a [Understanding UID remapping](https://medium.com/@tonistiigi/experimenting-with-rootless-docker-416c9ad8c0d6)
  a. ignore the env exports it says to set, see below
1. [install docker compose](https://docs.docker.com/compose/install/)
1. make sure `UsePAM yes` is set in `/etc/ssh/sshd_config` [read more](https://superuser.com/questions/1561076/systemctl-use-failed-to-connect-to-bus-no-such-file-or-directory-debian-9)

```bash
cd selfhosted
cp .env.example .env # edit this

# make mount points
mkdir /media/local /media/primary /media/secondary

# install mounts
systemctl link media-primary.mount
systemctl link media-secondary.mount

# enable traefik logrotate
cp etc/traefik-logrotate.conf /etc/logrotate.d/traefik

# Add to .profile
# export DOCKER_HOST=unix://$XDG_RUNTIME_DIR/docker.sock
nano .profile
```

[Set up docker daemon.json](https://forums.docker.com/t/rootless-docker-ip-range-conflicts/103341).  Otherwise, you may end up with subnet ranges inside your containers that overlap with the real LAN and make hosts unreachable.

``` json
{
    "default-address-pools": [
        {"base":"172.16.0.0/16","size":24},
        {"base":"172.20.0.0/16","size":24}
    ]
}
```

Edit `/lib/systemd/system/user@.service` to include dependencies on mounts

```conf
[Unit]
Requires=user-runtime-dir@%i.service media-primary.mount media-secondary.mount
```

## Automatic deployments and drone

* Create a github api app. Follow drone setup instructions.
* Make sure the user filtering config is set correctly so other users can't log in
* Add secrets `ssh_key`, `ssh_host`, `ssh_user` for your deploy user.
* Open `drone.yourdomain.com` and finish configuring your repo.

## Adguard DNS

You may need to disable ubuntu's default dns service and remove resolf.conf [read more](https://www.smarthomebeginner.com/run-pihole-in-docker-on-ubuntu-with-reverse-proxy/).

After disabling `systemd-resolved.service`, I ususally set a different DNS server in `/etc/resolv.conf` so that DNS doesn't break when I screw up the stack.

`systemd-resolve --help` is your friend.

## WireGurad and subnet overlap

* use `wg-quick` for simplicity
* May need to [install or symlink resolvconf](https://superuser.com/questions/1500691/usr-bin-wg-quick-line-31-resolvconf-command-not-found-wireguard-debian)
* Need to avoid [overlapping subnets](https://www.reddit.com/r/WireGuard/comments/bp01ci/connecting_to_services_through_vpn_when_the/).
* Set MTU down to 1280 for issues with cellular networks, on BOTH sides of the connection.

* My subnet is `192.168.48.0/20`
* The mask is `255.255.240.0`
* The default LAN will be `192.168.52.0`
* The gateway is `192.168.52.1`

```
Gateway: 11000000.10101000.0011 | 0100.00000001
Mask:    11111111.11111111.1111 | 0000.00000000
```

* The upper 4 bits will be used for VLANs (16).
* The lower 8 shoud belong to a single VLAN.

Using wireguard:

```bash
sudo systemctl enable wg-quick@peerN --now
```

## IPv6

Some references I encountered while rolling out ipv6.

[My full edgerouter config](docs/config.boot)

* [Docker IPV6](https://docs.docker.com/config/daemon/ipv6/)
* [Kernel modules lazy-load ip6tables](https://github.com/moby/moby/issues/33605#issuecomment-307361421)
  * `SYS_MODULE` capability doesn't seemt to do it. issuing an `ip6tables` dummy rule worked
* [IPv6 Firewall Rules](https://community.ui.com/questions/Can-someone-let-us-know-the-added-default-IPv6-firewall-rule-mentioned-in-the-new-Edge-OS-2-01/9683f591-6cd2-4677-83c9-e90d2b7c3fbe)
* Must [Block LAN to WLAN Multicast and Broadcast Data for ipv6 over wifi](https://community.ui.com/questions/IPv6-for-UniFi-WiFi/fa7109bb-c33f-4af4-9d98-dc82f0e31d99)
* [You might have to disable some firewall stuff on the upstream ISP gateway](https://community.ui.com/questions/Allow-HTTPs-over-IPv6-in-firewall-Edgemax/c5f00707-4476-4b1b-91d4-7391f73aafa6)
* [Disable ISP IPv6 DNS](https://kazoo.ga/dhcpv6-pd-for-native-ipv6/#)
  * `no-dns` in `interface` config for `rdnss`

## Other useful nonsense

```bash
# set own IP, delete set
ifconfig eth0 192.168.1.5 netmask 255.255.255.0 up
ifconfig en1 delete 192.168.1.5
```


