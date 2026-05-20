#!/bin/bash

SERVER="100.101.108.31"
USER="crash_user"

LOCKFILE="/tmp/postgres_failover.lock"

state=$(systemctl is-active postgresql)

if [ "$state" = "inactive" ]; then

    if [ ! -f "$LOCKFILE" ]; then
        echo "PostgreSQL caído, ejecutando failover..."

        ssh $USER@$SERVER "sudo failover"

        touch "$LOCKFILE"
    fi

else
    rm -f "$LOCKFILE"
fi
