## Livello 1: "Il cimitero dei goblin". Mappa ASCII, una cella = 16x16 pixel.
## Legenda:  # terra  B pietra  = asse (attraversabile dal basso)  ^ punte
##           h cima di collina (attraversabile dal basso, sotto c'è il fianco di terra)
##           l cima di una scala  L scala a pioli  T lapide  Y albero morto
##           t decorazione piccola (teschi, funghi...)  x decorazione grande  P partenza  K checkpoint
##           g goblin  S buca da cui spuntano goblin  w lupo  G spettri in volo
##           C armatura  H cuore (+1 vita)  1 alabarda  2 martello  3 arco  4 bastone  5 machete  E uscita
const MAP := [
	"BB                                                                                                                                                                                    BB",
	"BB                                                                                                                                                                                    BB",
	"BB                                                                                                  G                                                                G                BB",
	"BB                                                                                                 H                                                                                  BB",
	"BB                                           G                                                    ====                                                                                BB",
	"BB                                  T   Yg  1 T                            C                                                                                                          BB",
	"BB                             hhlhhhhhhhhhhhhhhhlhhh                    ====                  T       g      2                                                  T 3  g               BB",
	"BB                               L               L                   4                    hhlhhhhhhhhhhhhhhhlhhhh                                           hhlhhhhhhhhhlhh           BB",
	"BB                               L               L                x ====       BBB          L               L                                                 L         L             BB",
	"BB                               L               L            BBBB             BBB          L               L                     ===  ===  ===               L         L             BB",
	"BB  P t T Y  T  S  T  S  T  t    L    T   S      L     T 5    BBBB    g        BBB g  K t   L   S   T   w   L     S Y         g                    x     T    L S       L   T w T Y E BB",
	"###########################################################   BBBBBBBBBBBBBBBBBBBBBBBB#################################   BBBBBBB               BBBBBBB#################################",
	"###########################################################^^^BBBBBBBBBBBBBBBBBBBBBBBB#################################^^^BBBBBBB^^^^^^^^^^^^^^^BBBBBBB#################################",
	"##############################################################BBBBBBBBBBBBBBBBBBBBBBBB####################################BBBBBBB###############BBBBBBB#################################",
]
