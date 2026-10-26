## Livello 1: "La collina dei goblin". Mappa ASCII, una cella = 16x16 pixel.
## Legenda:  # terra  B pietra  = asse (attraversabile dal basso)  ^ punte
##           t decorazione piccola (teschi, funghi...)  x decorazione grande  P partenza  K checkpoint  g goblin
##           S buca da cui spuntano goblin  C armatura  H cuore (+1 vita)  w lupo  E uscita
const MAP := [
	"BB                                                                                                                                                                        BB",
	"BB                                                                                                                                                                        BB",
	"BB                                                                                                                                                                        BB",
	"BB                                                                                                                                                                        BB",
	"BB                                                                                                                                                                        BB",
	"BB                                                            C                                                                                                           BB",
	"BB                                                          ====                                                                                                          BB",
	"BB                                                                                                                                                    H                   BB",
	"BB                          ====                       ====       BBB                  g                                                             ====                 BB",
	"BB                                        t g    BBBB             BBB                 ###                       ===  ===  ===                    g                        BB",
	"BB  Pt x t x t   gt       t   x  S    ########   BBBBx   g        BBB g  K  t   S   ####### xw S  t         g                 t    x   t S  #######     x  g  x w   E     BB",
	"#####################   ######################   BBBBBBBBBBBBBBBBBBBBBBBB############################   BBBBBBB               BBBBBBB#######################################",
	"#####################^^^######################   BBBBBBBBBBBBBBBBBBBBBBBB############################^^^BBBBBBB^^^^^^^^^^^^^^^BBBBBBB#######################################",
	"##############################################   BBBBBBBBBBBBBBBBBBBBBBBB###############################BBBBBBB###############BBBBBBB#######################################",
]
