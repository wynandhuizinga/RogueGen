
from classes.CharGen import *
from classes.Settings import *
from classes.PlayGen import *
from classes.Arena import *
from classes.FloortextureGen import *

Abort = False

# Validate settings
if(number_of_generations < lengthOfGame):
    print("Abort, number of characters to be generated (",number_of_generations,") < lengthOfGame (",lengthOfGame,")")
    Abort = True

if not Abort:

    seed = random.randint(10000000, 99999999)
    if SeedOverride != "" and isinstance(SeedOverride, int):
        seed = SeedOverride 

    if playDirectory == "":
        chargen = CharGen(seed)
        path = chargen.setup()
        chargen.generate(seed)
        arena = Arena(seed,path)
        
    else:
        arena = Arena(seed,playDirectory)
    
    arena.play()

    