import argparse
import pandas as pd

parser  = argparse.ArgumentParser()
parser.add_argument( "--inpFile", help="reference .01 file." )
parser.add_argument( "--outFile", help="output file name."   )

args = parser.parse_args()

if ( args.inpFile ):
    pass
else:
    args.inpFile = "dat/shim_01.01"
    print( "[generate__initialShimData.py] default reference file name will be used. ::{}".format( args.inpFile ) )

if ( args.outFile ):
    pass
else:
    args.outFile = "dat/shim_00.01"
    print( "[generate__initialShimData.py] default output file name will be used. ::{}".format( args.outFile ) )

refData         = pd.read_csv( args.inpFile, delimiter="\s+", names=["ID","flag","x","y","z"] )
refData["flag"] = 0.0
refData.to_csv( args.outFile, sep=" ", index=False, header=False )
print( "\n" + "[generate__initialShimData.py]  save in a file ::{} ".format( args.outFile ) + "\n" )


args.outFile = "dat/all_off.01"
refData["flag"] = 0.0
refData.to_csv( args.outFile, sep=" ", index=False, header=False )
print( "\n" + "[generate__initialShimData.py]  save in a file ::{} ".format( args.outFile ) + "\n" )

args.outFile = "dat/all_on.01"
refData["flag"] = 1.0
refData.to_csv( args.outFile, sep=" ", index=False, header=False )
print( "\n" + "[generate__initialShimData.py]  save in a file ::{} ".format( args.outFile ) + "\n" )
