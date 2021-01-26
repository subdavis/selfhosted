firewall {
    all-ping enable
    broadcast-ping disable
    group {
    }
    ipv6-name WANv6_IN {
        default-action drop
        description "WAN inbound traffic forwarded to LAN"
        enable-default-log
        rule 10 {
            action accept
            description "Allow established/related sessions"
            state {
                established enable
                related enable
            }
        }
        rule 20 {
            action drop
            description "Drop invalid state"
            state {
                invalid enable
            }
        }
    }
    ipv6-name WANv6_LOCAL {
        default-action drop
        description "WAN inbound traffic to the router"
        enable-default-log
        rule 10 {
            action accept
            description "Allow established/related sessions"
            state {
                established enable
                related enable
            }
        }
        rule 20 {
            action drop
            description "Drop invalid state"
            state {
                invalid enable
            }
        }
        rule 30 {
            action accept
            description "Allow IPv6 icmp"
            protocol ipv6-icmp
        }
        rule 40 {
            action accept
            description "allow dhcpv6"
            destination {
                port 546
            }
            protocol udp
            source {
                port 547
            }
        }
    }
    ipv6-receive-redirects disable
    ipv6-src-route disable
    ip-src-route disable
    log-martians enable
    name WAN_IN {
        default-action drop
        description "WAN to internal"
        rule 10 {
            action accept
            description "Allow established/related"
            state {
                established enable
                related enable
            }
        }
        rule 20 {
            action drop
            description "Drop invalid state"
            state {
                invalid enable
            }
        }
    }
    name WAN_LOCAL {
        default-action drop
        description "WAN to router"
        rule 10 {
            action accept
            description "Allow established/related"
            state {
                established enable
                related enable
            }
        }
        rule 20 {
            action drop
            description "Drop invalid state"
            state {
                invalid enable
            }
        }
    }
    receive-redirects disable
    send-redirects enable
    source-validation disable
    syn-cookies enable
}
interfaces {
    ethernet eth0 {
        address dhcp
        description Internet
        dhcp-options {
            default-route update
            default-route-distance 210
            name-server no-update
        }
        dhcpv6-pd {
            pd 0 {
                interface switch0 {
                    service slaac
                }
                prefix-length /64
            }
            rapid-commit enable
        }
        duplex auto
        firewall {
            in {
                ipv6-name WANv6_IN
                name WAN_IN
            }
            local {
                ipv6-name WANv6_LOCAL
                name WAN_LOCAL
            }
            out {
            }
        }
        ipv6 {
            address {
                autoconf
            }
            dup-addr-detect-transmits 1
        }
        pppoe 0 {
            default-route auto
            ipv6 {
                address {
                    autoconf
                }
                dup-addr-detect-transmits 1
                enable {
                }
            }
            mtu 1492
            name-server auto
        }
        speed auto
    }
    ethernet eth1 {
        description Local
        duplex auto
        speed auto
    }
    ethernet eth2 {
        description Local
        duplex auto
        speed auto
    }
    ethernet eth3 {
        description Local
        duplex auto
        speed auto
    }
    ethernet eth4 {
        description Local
        duplex auto
        poe {
            output off
        }
        speed auto
    }
    loopback lo {
    }
    switch switch0 {
        address 192.168.52.1/20
        description Local
        mtu 1500
        switch-port {
            interface eth1 {
            }
            interface eth2 {
            }
            interface eth3 {
            }
            vlan-aware disable
        }
    }
}
port-forward {
    auto-firewall enable
    hairpin-nat enable
    lan-interface switch0
    rule 1 {
        description http
        forward-to {
            address 192.168.52.175
            port 80
        }
        original-port http
        protocol tcp
    }
    rule 2 {
        description https
        forward-to {
            address 192.168.52.175
            port 443
        }
        original-port https
        protocol tcp
    }
    rule 3 {
        description wireguard
        forward-to {
            address 192.168.52.175
            port 51820
        }
        original-port 51820
        protocol tcp_udp
    }
    wan-interface eth0
}
service {
    dhcp-server {
        disabled false
        hostfile-update disable
        shared-network-name lan {
            authoritative disable
            subnet 192.168.52.0/24 {
                default-router 192.168.52.1
                lease 86400
                start 192.168.52.38 {
                    stop 192.168.52.243
                }
                static-mapping Draynor {
                    ip-address 192.168.52.112
                    mac-address b8:27:eb:b3:9f:ce
                }
                static-mapping MainAP {
                    ip-address 192.168.52.185
                    mac-address e0:63:da:3c:68:be
                }
                static-mapping PhilipsHue {
                    ip-address 192.168.52.230
                    mac-address 00:17:88:6d:95:69
                }
                static-mapping lumbridge {
                    ip-address 192.168.52.175
                    mac-address 8c:89:a5:3b:3b:41
                }
                static-mapping varrock {
                    ip-address 192.168.52.40
                    mac-address 54:bf:64:6c:91:e9
                }
                static-mapping wildy {
                    ip-address 192.168.52.45
                    mac-address 00:23:24:64:4b:98
                }
                unifi-controller 192.168.52.175
            }
        }
        static-arp disable
        use-dnsmasq enable
    }
    dns {
        dynamic {
            interface eth0 {
                service dyndns {
                    host-name subdavis
                    login nouser
                    password ************
                    protocol dyndns2
                    server www.duckdns.org
                }
                web dyndns
            }
        }
        forwarding {
            cache-size 150
            listen-on switch0
            name-server 1.1.1.2
            name-server 1.0.0.2
            options dhcp-option=6,192.168.52.1
            options bind-interfaces
            options listen-address=127.0.0.1
            options listen-address=192.168.52.1
        }
    }
    gui {
        http-port 80
        https-port 443
        older-ciphers enable
    }
    nat {
        rule 5010 {
            description "masquerade for WAN"
            outbound-interface eth0
            type masquerade
        }
    }
    ssh {
        port 22
        protocol-version v2
    }
    unms {
        disable
    }
}
system {
    config-management {
        commit-archive {
        }
    }
    domain-name lan
    host-name ubnt
    login {
        user ubnt {
            authentication {
                encrypted-password *************
                plaintext-password ""
            }
            full-name ""
            level admin
        }
    }
    name-server 127.0.0.1
    ntp {
        server 0.ubnt.pool.ntp.org {
        }
        server 1.ubnt.pool.ntp.org {
        }
        server 2.ubnt.pool.ntp.org {
        }
        server 3.ubnt.pool.ntp.org {
        }
    }
    offload {
        hwnat enable
    }
    package {
        repository stretch {
            components "main contrib non-free"
            distribution stretch
            password ""
            url http://http.us.debian.org/debian
            username ""
        }
    }
    syslog {
        global {
            facility all {
                level notice
            }
            facility protocols {
                level debug
            }
        }
    }
    task-scheduler {
    }
    time-zone America/New_York
}
