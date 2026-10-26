# Goblin Slayer – prototipo (Godot 4)

Platform d'azione alla **Ghosts'n Goblins** con l'ambientazione di **Goblin Slayer** e una
grafica pixel art notturna ispirata a **Monkey Island**. Questo è il primo livello giocabile:
"La collina dei goblin".

## Come aprirlo
1. Usa **Godot 4.3 o successivo** (va bene anche la tua 4.7 .NET/"mono": il gioco è in GDScript e non serve installare .NET).
2. Estrai lo zip in una cartella.
3. Apri Godot → **Importa** → seleziona il file `project.godot` nella cartella → **Importa e modifica**.
4. Premi **F5** (o il pulsante ▶ in alto a destra) per giocare.

La prima apertura impiega qualche secondo perché Godot importa le immagini. Con Godot 4.4 o successivo
compare un avviso di conversione del progetto: conferma pure.

## Comandi
| Azione | Tastiera | Gamepad |
|---|---|---|
| Muoversi | A / D oppure frecce | croce / levetta sinistra |
| Abbassarsi | S oppure freccia giù | giù |
| Saltare | Spazio, K oppure Z | A |
| Lanciare il pugnale | J oppure X | X |
| Pausa | Esc oppure P | Start |

## Meccaniche
- **Salto "impegnato"** come in Ghosts'n Goblins: una volta in aria la traiettoria non cambia.
  Per un salto moderno con controllo in aria, seleziona il nodo `Player` e disattiva `Classic Jump`.
- **Armatura**: il primo colpo te la fa volare via in pezzi, il secondo ti uccide. Il **forziere**
  sopra le rovine te la ridà. Le **punte** e i burroni uccidono subito.
- **Goblin**: camminano avanti e indietro e a volte saltano verso di te. Dalle **buche** spuntano
  nuovi goblin quando ti avvicini, come gli zombi del cimitero.
- **Lupi dei goblin**: più resistenti (2 colpi) e ti caricano di corsa quando sei vicino.
- **Cuore**: +1 vita.
- 3 vite, checkpoint a metà livello, punteggio; arrivare alla tana con l'armatura raddoppia il bonus.

## Struttura
```
project.godot          impostazioni (384x216 pixel-perfect, ingrandito 3x)
scenes/                main (livello), player, goblin, dagger, chest, cave_exit, hud...
scripts/               logica in GDScript (player.gd, goblin.gd, level.gd, ...)
levels/level_1.gd      mappa ASCII del livello: modificala per cambiare il percorso
assets/                grafica e suoni usati dal gioco
assets_src/            file originali dei pacchetti grafici (Godot li ignora)
tools/import_packs.py  converte assets_src/ in assets/ (ricolora l'eroe, ritaglia tessere e oggetti)
tools/gen_assets.py    genera goblin, effetti e suoni segnaposto (Python + Pillow)
tools/make_level.py    rigenera la mappa del livello 1
tools/autotest.gd      partita automatica con screenshot (per verifiche)
```

### Modificare il livello
Apri `levels/level_1.gd`: ogni carattere è una cella 16x16. `#` terra, `B` pietra,
`=` asse, `^` punte, `t`/`x` decorazioni, `g` goblin, `w` lupo, `S` buca dei goblin,
`C` armatura, `H` cuore, `K` checkpoint, `E` uscita.

### Grafica e crediti
- Eroe, lupo, tileset, sfondo notturno: **Gothicvania Patreon Collection** di Luis Zuno (@ansimuz),
  pubblico dominio (vedi `assets_src/gothicvania/public-license.txt`). L'eroe è ricolorato come
  Goblin Slayer: elmo e armatura d'acciaio sporco, mantello di cuoio, pennacchio rosso; senza
  armatura diventa un uomo in tunica.
- Oggetti e scenografie (armatura, cuore, pugnale, teschi su picche, funghi, rocce, spada nella roccia):
  dai file `00_items.png` e `misc_scenery.png` che hai caricato. Verifica la loro licenza prima di pubblicare.
- Goblin, punte, ingresso della tana, effetti e suoni: segnaposto generati da `tools/gen_assets.py`
  (i pacchetti non contengono goblin).

Per cambiare grafica: sostituisci i file in `assets_src/` e lancia `python3 tools/import_packs.py`,
oppure sostituisci direttamente i PNG in `assets/` mantenendo le dimensioni dei fotogrammi
(l'ordine delle animazioni è in `ANIMS` dentro `player.gd` e `goblin.gd`).
