# Handoff: station
Written 2026-11-16 09:00. Project: /workspace. Session: aaaa-old.

## Where things stand
The CSV logger runs every minute on the Raspberry Pi.

## Next steps
1. Connect the humidity sensor to station/logger.py.

## Waiting on the user
- Timestamps in UTC or local time? Recommendation: UTC.

## Decisions
- D1 (2026-11-15): the station runs on a Raspberry Pi 4, not an ESP32, because it needs Python. (Also in docs/decisions.md.)

## Facts found (don't re-check)
- The Pi runs Python 3.9.

## Tried or rejected (don't propose again)
- Polling the sensor over Bluetooth: the range was too short in the garden.
