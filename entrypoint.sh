#! /bin/bash
set -euxo pipefail

exec uwsgi --http :80 --workers 1 --threads 4 --chdir /usr/src/app/ --mount /=main:app

