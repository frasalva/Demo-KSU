# Demo · 00_demo

Versione di produzione della demo, pronta per la presentazione.

## Architettura

```
┌─────────────────────────────────────────────────────────────────────┐
│  GitHub Pages (HTTPS)                                               │
│   • 00_ENV/   → iPad #1  (microfono iPad, libreria audio)           │
│   • 00_NECK/  → iPad #2  (microfono iPad, soglia visiva)            │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│  Mac/laptop sulla LAN CPS-2.4G — ./control/start.sh                 │
│   • control/  → control page (tu)         ws://*.local:81/ → MCU    │
│   • 00_HAND/  → schermo proiettato        ws://server:8090/ ← bus   │
│   • bus_relay.py  (porta 8090)                                      │
└─────────────────────────────────────────────────────────────────────┘
                            │
                            ▼
                  ESP32 hand + ESP32 pump-neck
                      (CPS-2.4G, mDNS .local)
```

## Cosa contiene ogni cartella

| Cartella | Dove gira | Connettività richiesta |
|---|---|---|
| **00_ENV/** | iPad o qualunque browser HTTPS | nessuna (autonoma, mic locale + 3 mp3) |
| **00_NECK/** | iPad o qualunque browser HTTPS | nessuna (autonoma, mic locale) |
| **00_HAND/** | laptop col proiettore in HDMI | bus relay (riceve `hand.signal`) |
| **control/** | tuo laptop (Mac sulla LAN) | bus relay + ws:// agli MCU |
| **control/bus_relay.py** | tuo laptop | – (è il relay stesso) |
| **control/start.sh** | tuo laptop | lancia HTTP + relay |

## Setup iniziale

### 1 · Mac/laptop server
```sh
pip3 install websockets
```

### 2 · Pubblicazione su GitHub Pages
- Crea un repo (es. `cps-demo`).
- Pusha `00_ENV/` e `00_NECK/` (anche dentro lo stesso repo è ok).
- Impostazioni → Pages → branch `main` → cartella root o `/docs`.
- Ottieni URL tipo `https://<user>.github.io/cps-demo/00_ENV/` e
  `https://<user>.github.io/cps-demo/00_NECK/`.

Verifica che i 3 file `.mp3` siano stati committati dentro `00_ENV/`.

### 3 · MCU
Firmware già pronto su `hand` e `pump-neck`: entrambi si connettono al WiFi
`CPS-2.4G` e si annunciano via mDNS come `hand.local` e `pump-neck.local`
su porta 81. Nessun upload extra per la demo.

## Avvio giornaliero

```sh
cd /percorso/a/00_demo
./control/start.sh
```

Stampa l'IP del Mac e gli URL pronti, es.:
```
HTTP : http://192.168.1.42:8000/
       http://192.168.1.42:8000/control/   (control page)
       http://192.168.1.42:8000/00_HAND/   (proiezione HAND)
BUS  : ws://192.168.1.42:8090/
```

## URL da aprire (esempio)

| Dispositivo | URL |
|---|---|
| Mac (tu, control) | `http://192.168.1.42:8000/control/` |
| Laptop proiettore (HAND) | `http://192.168.1.42:8000/00_HAND/` |
| iPad #1 (ENV) | `https://<user>.github.io/cps-demo/00_ENV/` |
| iPad #2 (NECK) | `https://<user>.github.io/cps-demo/00_NECK/` |

## Come funziona la sincronia control → HAND

Click su `LEFT (1)` o `RIGHT (2)` nella control page:
1. Manda `'1'` o `'2'` via `ws://hand.local:81/` → relè TENS scatta sull'Arduino
2. Pubblica `{type:'hand.signal', dir}` sul bus relay → la pagina 00_HAND riceve l'evento e fa partire l'animazione del segnale + cambio direzione

Le 2 cose avvengono nello stesso click, latenza ~20 ms. Non serve niente
sull'iPad/laptop di HAND oltre al browser.

## Caveat operativi

- **iPad e Mac sulla stessa rete CPS-2.4G** (non sulla rete "guest"/"ospiti").
- macOS firewall: al primo avvio chiede di consentire connessioni in entrata
  a `python3` — accetta. Se le altre macchine non si collegano al bus,
  verifica con `nc -zv <mac-ip> 8090` dal device remoto.
- `*.local` non risolto da un device? Nella card della control page clicca
  `edit host` e incolla l'IP del MCU (lo leggi dal monitor seriale al boot:
  riga `[wifi] connected: ip=...`).
- 00_HAND aperta in fullscreen sul proiettore: tasto `F11` (Windows) /
  `Ctrl+Cmd+F` (Mac) in Chrome.
