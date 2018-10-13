## Self-hosted Services

A list of services I run.

## Setup

1. https://coreos.com/os/docs/latest/installing-to-disk.html
2. Clone this repo in `/etc/systemd/system`
3. Symlink `/etc/profile.env`

For any overrides, like `torrent.service.d`, copy the template to a new `override.conf` file with the correct values.

## DynDNS

Deploy https://github.com/awslabs/route53-dynamic-dns-with-lambda