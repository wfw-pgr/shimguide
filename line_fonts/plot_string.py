import json
import numpy             as np
import matplotlib.pyplot as plt


# ------------------------------------------------- #
# --- [1] load character.json                   --- #
# ------------------------------------------------- #

inpFile = "fonts.jsonc"
pngFile = "plot.png"

with open( inpFile, "r" ) as f:
    characters = json.load( f )

char        = "T"
x1,x2,y1,y2 = np.transpose( np.array( characters[char] ) )
nLine       = x1.shape[0]

# ------------------------------------------------- #
# --- [2] save in a png File                    --- #
# ------------------------------------------------- #
plt.figure()
for ik in range(nLine):
    xl,yl = np.array( [x1[ik],x2[ik]] ), np.array( [y1[ik],y2[ik]] )
    plt.plot( xl, yl, color="black" )
plt.savefig( pngFile )
