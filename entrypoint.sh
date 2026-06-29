#!/bin/sh

echo "Starting app.py (Flask web server)..."
python app.py &
APP_PID=$!

sleep 1

echo "Starting bot.py (Telegram bot)..."
python bot.py &
BOT_PID=$!

echo "Both services started. PIDs: app=$APP_PID bot=$BOT_PID"

cleanup() {
    echo "Shutting down..."
    kill $APP_PID $BOT_PID 2>/dev/null
    wait $APP_PID $BOT_PID 2>/dev/null
    echo "Done."
}
trap cleanup EXIT TERM INT

while true; do
    sleep 5
done
