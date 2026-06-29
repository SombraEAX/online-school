#!/bin/bash
set -m

python seed.py

python bot.py &
BOT_PID=$!

gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120 &
GUNI_PID=$!

while true; do
    if ! kill -0 $BOT_PID 2>/dev/null; then
        echo "bot.py crashed, restarting..."
        python bot.py &
        BOT_PID=$!
    fi
    if ! kill -0 $GUNI_PID 2>/dev/null; then
        echo "gunicorn crashed, exiting..."
        exit 1
    fi
    sleep 5
done
