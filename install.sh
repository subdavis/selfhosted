#!/bin/bash
SYSTEMD_DIR=${SYSTEMD_DIR:-/usr/local/lib/systemd/system}
files=("media-primary.mount" "media-secondary.mount")

systemctl daemon-reload

for file in "${files[@]}"
do
    ln --symbolic --force --no-dereference $(pwd)/${file} ${SYSTEMD_DIR}/${file}
    systemctl enable $file
    systemctl start $file
done

ln --symbolic --force --no-dereference $(pwd)/etc/traefik-logrotate.conf /etc/logrotate.d/traefik
