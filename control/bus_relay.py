#!/usr/bin/env python3
"""
Tiny WebSocket bus relay for the CPS demo.

Every text message received from any connected client is forwarded to every
OTHER connected client. Binary frames are dropped. No persistence, no auth,
no topics — same fan-out semantics as the browser's BroadcastChannel but
across machines on the LAN (laptop + iPad + extra screens).

Usage:
  pip3 install websockets
  python3 bus_relay.py            # listens on 0.0.0.0:8090
  python3 bus_relay.py --port 9000 --verbose

All HTML pages then point their NetBus to ws://<this-machine-ip>:8090/.
The default discovery in netbus.js uses the same hostname that served the
page, so if you serve everything from this Mac there is nothing to configure.
"""
import argparse
import asyncio
import logging
import websockets

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [bus] %(message)s",
                    datefmt="%H:%M:%S")
log = logging.getLogger()

clients: set = set()

async def handler(ws):
    clients.add(ws)
    peer = f"{ws.remote_address[0]}:{ws.remote_address[1]}"
    log.info(f"+ {peer}  (tot={len(clients)})")
    try:
        async for msg in ws:
            if not isinstance(msg, str):
                continue                       # ignore binary
            if log.isEnabledFor(logging.DEBUG):
                log.debug(f"{peer} -> {msg[:120]}")
            # fan-out to everyone except the sender
            await asyncio.gather(
                *(c.send(msg) for c in clients if c is not ws),
                return_exceptions=True,
            )
    except websockets.ConnectionClosed:
        pass
    finally:
        clients.discard(ws)
        log.info(f"- {peer}  (tot={len(clients)})")

async def main(host: str, port: int):
    log.info(f"listening on ws://{host}:{port}/")
    async with websockets.serve(handler, host, port, max_size=64 * 1024):
        await asyncio.Future()      # run forever

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="0.0.0.0")
    ap.add_argument("--port", type=int, default=8090)
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()
    if args.verbose:
        log.setLevel(logging.DEBUG)
    try:
        asyncio.run(main(args.host, args.port))
    except KeyboardInterrupt:
        pass
