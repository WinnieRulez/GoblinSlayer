#!/usr/bin/env python3
"""Costruisce la mappa ASCII del livello 1 (levels/level_1.gd). Puoi anche modificare direttamente quel file."""
W, H = 172, 14
g = [[' '] * W for _ in range(H)]

def fill(x0, x1, top, ch='#', bottom=H - 1):
    for x in range(x0, x1 + 1):
        for y in range(top, bottom + 1):
            g[y][x] = ch

def put(x, y, ch):
    g[y][x] = ch

def row(x0, x1, y, ch):
    for x in range(x0, x1 + 1):
        g[y][x] = ch

# 1) Cimitero di partenza
fill(0, 20, 11)
fill(0, 1, 0, 'B', 10)               # muro a sinistra
for x in (5, 9, 13, 18): put(x, 10, 't')
put(11, 10, 'x')
put(4, 10, 'P')
put(17, 10, 'g')
# fossa con punte
fill(21, 23, 13); row(21, 23, 12, '^')
# 2) Prima collina con generatore di goblin
fill(24, 45, 11)
fill(38, 45, 10)
row(28, 31, 8, '=')
put(33, 10, 'S')
put(26, 10, 't'); put(42, 9, 't')
put(44, 9, 'g')
# burrone senza fondo
# 46..48 vuoto
# 3) Rovine di pietra con il forziere
fill(49, 72, 11, 'B')
fill(49, 52, 9, 'B')
row(55, 58, 8, '=')
row(60, 63, 6, '=')
put(62, 5, 'C')
fill(66, 68, 8, 'B', 10)
put(57, 10, 'g'); put(70, 10, 'g')
put(53, 10, 'x')
put(73, 10, 'K')                     # checkpoint
# 4) Colline dei goblin
fill(73, 100, 11)
fill(84, 90, 10); fill(86, 88, 9)
put(80, 10, 'S'); put(95, 10, 'S')
put(76, 10, 't'); put(92, 10, 'x'); put(98, 10, 't')
put(87, 8, 'g')
# fossa con punte
fill(101, 103, 13); row(101, 103, 12, '^')
# 5) Ponte di assi sopra il campo di punte
fill(104, 110, 11, 'B')
fill(111, 125, 13); row(111, 125, 12, '^')
row(112, 114, 9, '='); row(117, 119, 9, '='); row(122, 124, 9, '=')
fill(126, 132, 11, 'B')
put(108, 10, 'g')
# 6) Avvicinamento alla tana
fill(133, W - 1, 11)
fill(140, 146, 10)
row(149, 152, 8, '=')
put(137, 10, 'S'); put(145, 9, 'g'); put(155, 10, 'g')
put(135, 10, 't'); put(152, 10, 'x'); put(158, 10, 'x')
put(164, 10, 'E')
# lupi dei goblin e cuore (+1 vita)
put(93, 10, 'w'); put(160, 10, 'w'); put(150, 7, 'H')
put(7, 10, 'x'); put(30, 10, 'x'); put(126, 10, 't'); put(131, 10, 'x')
fill(W - 2, W - 1, 0, 'B', 10)       # muro a destra

lines = [''.join(r).rstrip() for r in g]
out = ['## Livello 1: "La collina dei goblin". Mappa ASCII, una cella = 16x16 pixel.',
       '## Legenda:  # terra  B pietra  = asse (attraversabile dal basso)  ^ punte',
       '##           t decorazione piccola (teschi, funghi...)  x decorazione grande  P partenza  K checkpoint  g goblin',
       '##           S buca da cui spuntano goblin  C armatura  H cuore (+1 vita)  w lupo  E uscita',
       'const MAP := [']
out += ['\t"%s",' % l for l in lines]
out.append(']')
open('levels/level_1.gd', 'w').write('\n'.join(out) + '\n')
print('\n'.join(lines))
