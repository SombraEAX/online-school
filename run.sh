#!/bin/bash
cd "$(dirname "$0")"
exec gunicorn app:app --bind 0.0.0.0:5000 --workers 2 --timeout 120
