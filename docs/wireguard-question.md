# Sharing WireGuard network with other containers via docker

I'm trying to do something a little "backwards".  Most WireGuard tutorials show you how to share a WireGuard container's internet connection with peers, forwarding traffic from `wg0` to `eth0`.  For example, the VPN Server configuration [described on ArchWiki](https://wiki.archlinux.org/index.php/WireGuard)

**I want to do the opposite**.  I want containers that share a network with WireGuard to be able to access its peers.

### wg0.conf

My current config is lifted straight from archwiki, and works in the traditional VPN server way.

``` conf
[Interface]
Address = 10.200.200.1/24
ListenPort = 51820
PrivateKey = SERVER_PRIVATE_KEY
PostUp = iptables -A FORWARD -i %i -j ACCEPT; iptables -A FORWARD -o %i -j ACCEPT; iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
PostDown = iptables -D FORWARD -i %i -j ACCEPT; iptables -D FORWARD -o %i -j ACCEPT; iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE

[Peer]
# foo
PublicKey = PEER_FOO_PUBLIC_KEY
PresharedKey = PRE-SHARED_KEY
AllowedIPs = 10.200.200.2/32

[Peer]
# bar
PublicKey = PEER_BAR_PUBLIC_KEY
PresharedKey = PRE-SHARED_KEY
AllowedIPs = 10.200.200.3/32
```

### docker-compose.yml

``` yml
version: '3.8'
services:
  wireguard:
    image: linuxserver/wireguard
    container_name: wireguard
    cap_add:
      - NET_ADMIN
      - SYS_MODULE
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=${TIME_ZONE}
      - SERVERURL="wireguard.${DNS_DOMAIN}"
      - SERVERPORT=51820
      - PEERS=2
      - PEERDNS=192.168.1.10 # DNS on my LAN, not important.
      - INTERNAL_SUBNET=10.200.200.0
    ports:
      - "51820:51820/udp"
    volumes:
      - wireguardconfig:/config
      - /lib/modules:/lib/modules
    sysctls:
      - "net.ipv4.ip_forward=1"
      - "net.ipv4.conf.all.src_valid_mark=1"
    networks:
      - wireguard-net

  ubuntu:
    image: ubuntu
    container_name: ubuntu
    entrypoint: /bin/sleep
    command: 10000000
    networks:
      - wireguard-net

volumes:
  wireguardconfig:

wireguard-net:
  name: wireguard-net
  ipam:
    config:
      - subnet: 10.200.0.0/16
```

## Goal

I want to be able to `docker exec` into ubunut and run `ping 10.200.200.2` when peer 2 is active.  I don't think I'm far off.  What am I missing?