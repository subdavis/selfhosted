# LAN-only routes with Traefik

> **GOAL:** In this guide, you'll learn how to set up portainer with valid SSL and Host-based routing privately on your LAN.
>
> Turn _this_: `http://myserver.lan:8080`
>
> Into this: `https://portainer.mydomain.com`
>
> ...all while keepoing your private services off the internet.

When running services in traefik, you'll likely want to expose some to the internet (like plex) and keep others accessible only from your local network (like portainer).  This document is mostly about IP whitelisting, but I want to first talk about SSL and security.

## SSL for private routes

There are 2 main ways of creating [routing rules](https://docs.traefik.io/routing/routers/#rule) for apps: Host rules and PathPrefix rules.

* Host rules route based on the hostname of the destination, like `foo.mydomain.com` or `http://192.168.0.10`.
* PathPrefix rules route based on some prefix substring, like `/plex` or `/portainer`.

You may think that, without rolling out some robust DNS on your home network, you're stuck with `http://myserver.lan/portainer` as your best option for routing.  

This has drawbacks:

1. PathPrefix rules are an **enormous pain in the ass** because [nobody understands how they should work](https://github.com/elastic/kibana/issues/6665).
1. Without a legitimate domain name, you're stuck with self-signed certificates.

Instead, I like to use my real domain even for local routes.

1. Create a CNAME or A record for `portainer.mydomain.com` to point to either your server's private IP or even your network's public IP.
1. Set up [Wildcard SSL for your domain](wildcard-certs.md)

Now, you'd be ready to set up a publicly accessible service, except we're going to restrict access.

## IP Whitelisting

### The Traefik Part

With the IPWhitelist middleware, we're going to restrict access to your LAN subnet.  You can run traefik exactly the same as in [the wildcard SSL tutorial](wildcard-certs.md).

> **Note:** the only difference is that you don't actually have to open any ports on your router.

### The Portainer Part

This part will also be almost the same as the wildcard tutorial, with the addition of 1 middleware.  Refer to [CIDR notation](https://en.wikipedia.org/wiki/Classless_Inter-Domain_Routing) if you don't know how to represent your subnet as a CIDR block.

``` bash
export MY_APP_DOMAIN=mydomain.com
export SUBNET="192.168.0.0/24"
docker run --rm --name portainer \
  --label traefik.enable=true \
  --label traefik.http.services.my-service.loadbalancer.server.port="9000" \
  --label traefik.http.middlewares.middleware-redirect-https.redirectscheme.scheme="https" \
  --label traefik.http.routers.my-route.entrypoints=web \
  --label traefik.http.routers.my-route.rule="Host(`portainer.${MY_APP_DOMAIN}`)" \
  --label traefik.http.routers.my-route.middlewares="middleware-redirect-https@docker" \
  --label traefik.http.routers.my-route-secure.entrypoints=websecure \
  --label traefik.http.routers.my-route-secure.rule="Host(`portainer.${MY_APP_DOMAIN}`)" \
  --label traefik.http.routers.my-route-secure.tls.domains[0].main="*.${MY_APP_DOMAIN}" \
  --label traefik.http.routers.my-route-secure.tls.certresolver="myresolver" \
  --label traefik.http.routers.my-route-secure.tls=true \
  --label traefik.http.middlewares.middleware-ipwhitelist.ipwhitelist.sourcerange="127.0.0.1/32,${SUBNET}" \
  --label traefik.http.routers.%N-secure.middlewares="middleware-ipwhitelist@docker" \
  --volume /tmp/portainer/data/:/data \
  --volume /var/run/docker.sock:/var/run/docker.sock  \
  portainer/portainer
```

## Testing it

Visit https://portainer.mydomain.com

It doesn't matter whether your DNS record for `portainer.mydomain.com` points at your network's Public IP or the traefik server's private IP.  When the request hits your Firewall or router, you'll get redirected internally and traefik will examine the origin of the request, which will be your host's private IP.

To verify this, you can:

* Try the request from a host on the subnet.  It will succeed.
* Try the request from a host with a properly configured active VPN running.  It will STILL succeed.
* Try the request from a mobile phone with wifi off. u'll get a 401 Unauthorized response!
* Try whatever else you can think of to trick traefik.  It won't work :)

> **NOTE**: If you run traefik behind another proxy that uses X-Forwarded-For header, you may have to configure other settings to [pick the right IP](https://docs.traefik.io/middlewares/ipwhitelist/#configuration-options)
