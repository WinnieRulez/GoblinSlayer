#!/usr/bin/env python3
"""Costruisce la mappa ASCII del livello 1 (levels/level_1.gd). Puoi anche modificare direttamente quel file.

Il percorso segue il primo livello di Ghosts'n Goblins: cimitero, colline a due piani con le scale,
rovine, campo di punte e la tana dei goblin in fondo."""
W, H = 184, 14
g = [[' '] * W for _ in range(H)]
FLOOR = 11   # prima riga di terreno: i personaggi stanno sulla riga 10


def fill(x0, x1, top, ch='#', bottom=H - 1):
    for x in range(x0, x1 + 1):
        for y in range(top, bottom + 1):
            g[y][x] = ch


def put(x, y, ch):
    g[y][x] = ch


def row(x0, x1, y, ch):
    for x in range(x0, x1 + 1):
        g[y][x] = ch


def hill(x0, x1, top, ladders):
    """Collina alla Ghosts'n Goblins: cima attraversabile dal basso, fianco di terra solo grafico,
    scale a pioli dal terreno alla cima."""
    row(x0, x1, top, 'h')
    for lx in ladders:
        put(lx, top, 'l')
        for y in range(top + 1, FLOOR):
            put(lx, y, 'L')


# 1) Cimitero di partenza
fill(0, 58, FLOOR)
fill(0, 1, 0, 'B', FLOOR - 1)        # muro a sinistra
put(4, 10, 'P')
put(10, 10, 'Y')
for x in (8, 13, 19, 25): put(x, 10, 'T')
put(16, 10, 'S'); put(22, 10, 'S')
put(6, 10, 't'); put(28, 10, 't')
# 2) Prima collina con due scale
hill(31, 52, 6, (33, 49))
put(36, 5, 'T'); put(46, 5, 'T')
put(40, 5, 'Y'); put(41, 5, 'g'); put(44, 5, '1')   # alabarda in cima
put(38, 10, 'T'); put(42, 10, 'S'); put(55, 10, 'T')
put(57, 10, '5')                     # machete
put(45, 4, 'G')
# fossa con punte
fill(59, 61, 13); row(59, 61, 12, '^')
# 3) Rovine di pietra con l'armatura
fill(62, 85, FLOOR, 'B')
fill(62, 65, 9, 'B')
row(68, 71, 8, '=')
row(73, 76, 6, '=')
put(75, 5, 'C')
put(69, 7, '4')                      # bastone sull'asse
fill(79, 81, 8, 'B', 10)
put(70, 10, 'g'); put(83, 10, 'g')
put(66, 8, 'x')
put(86, 10, 'K')                     # checkpoint
# 4) Seconda collina, con un'asse sopra e il cuore
fill(86, 118, FLOOR)
hill(90, 112, 7, (92, 108))
row(98, 101, 4, '='); put(99, 3, 'H')
put(95, 6, 'T'); put(103, 6, 'g'); put(110, 6, '2')   # martello in cima
put(104, 10, 'w')
put(96, 10, 'S'); put(114, 10, 'S')
put(100, 10, 'T'); put(116, 10, 'Y')
put(88, 10, 't')
put(100, 2, 'G')
# fossa con punte
fill(119, 121, 13); row(119, 121, 12, '^')
# 5) Ponte di assi sopra il campo di punte
fill(122, 128, FLOOR, 'B')
fill(129, 143, 13); row(129, 143, 12, '^')
row(130, 132, 9, '='); row(135, 137, 9, '='); row(140, 142, 9, '=')
fill(144, 150, FLOOR, 'B')
put(126, 10, 'g'); put(147, 10, 'x')
# 6) Ultimo cimitero e tana dei goblin
fill(151, W - 1, FLOOR)
hill(156, 170, 7, (158, 168))
put(163, 6, '3')                     # arco in cima
put(161, 6, 'T'); put(166, 6, 'g')
for x in (153, 172, 176): put(x, 10, 'T')
put(160, 10, 'S'); put(174, 10, 'w')
put(165, 2, 'G')
put(178, 10, 'Y')
put(180, 10, 'E')
fill(W - 2, W - 1, 0, 'B', FLOOR - 1)  # muro a destra

lines = [''.join(r).rstrip() for r in g]
out = ['## Livello 1: "Il cimitero dei goblin". Mappa ASCII, una cella = 16x16 pixel.',
       '## Legenda:  # terra  B pietra  = asse (attraversabile dal basso)  ^ punte',
       '##           h cima di collina (attraversabile dal basso, sotto c\'è il fianco di terra)',
       '##           l cima di una scala  L scala a pioli  T lapide  Y albero morto',
       '##           t decorazione piccola (teschi, funghi...)  x decorazione grande  P partenza  K checkpoint',
       '##           g goblin  S buca da cui spuntano goblin  w lupo  G spettri in volo',
       '##           C armatura  H cuore (+1 vita)  1 alabarda  2 martello  3 arco  4 bastone  5 machete  E uscita',
       'const MAP := [']
out += ['\t"%s",' % l for l in lines]
out.append(']')
open('levels/level_1.gd', 'w').write('\n'.join(out) + '\n')
print('\n'.join(lines))
