#!/usr/bin/env bash
# Avvia HTTP server (porta 8000) + WebSocket bus relay (porta 8090).
# Serve l'intera cartella 00_demo/ via HTTP, così puoi aprire control/ e 00_HAND/
# dal browser locale + iPad / altri laptop sulla LAN.
#
# 00_ENV/ e 00_NECK/ sono pensate per essere pubblicate su GitHub Pages
# (richiedono HTTPS per accedere al microfono dell'iPad), ma puoi aprirle
# anche da qui per test rapidi *sul Mac stesso* via localhost.
#
# Uso:  ./control/start.sh
# Stop: Ctrl+C  (chiude entrambi)

set -e
cd "$(dirname "$0")/.."          # spostati in 00_demo/

HTTP_PORT=8000
BUS_PORT=8090

IP=$(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null || echo "?.?.?.?")

echo "============================================================"
echo "  Demo · server"
echo "------------------------------------------------------------"
echo "  HTTP : http://${IP}:${HTTP_PORT}/"
echo "         http://${IP}:${HTTP_PORT}/control/      (control page)"
echo "         http://${IP}:${HTTP_PORT}/00_HAND/      (proiezione HAND)"
echo "  BUS  : ws://${IP}:${BUS_PORT}/"
echo ""
echo "  00_ENV e 00_NECK: prendili dai loro URL GitHub Pages"
echo "============================================================"

python3 control/bus_relay.py --port "$BUS_PORT" &
BUS_PID=$!
trap 'kill $BUS_PID 2>/dev/null || true' EXIT INT TERM

python3 -m http.server "$HTTP_PORT"
