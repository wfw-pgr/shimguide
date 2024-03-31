import os, sys

# ========================================================= #
# ===  make__scanParameterFile.py                       === #
# ========================================================= #

def make__scanParameterFile( inpFile=None, outFile=None, mark=None, values=[], replaceMode=False ):

    # ------------------------------------------------- #
    # --- [0] arguments                             --- #
    # ------------------------------------------------- #
    if ( inpFile is None ): sys.exit( "[make__scanParameterFile.py]  == ???" )
    if ( outFile is None ): sys.exit( "[make__scanParameterFile.py]  == ???" )
    
    # ------------------------------------------------- #
    # --- [1] read file                             --- #
    # ------------------------------------------------- #
    with open( inpFile, "r" ) as f:
        text = f.read()

    # ------------------------------------------------- #
    # --- [2] replace                               --- #
    # ------------------------------------------------- #
    if ( replaceMode ):
        for ik,val in enumerate(values):
            mark_ = mark + "{}".format(ik+1)
            text  = text.replace( mark_, val )
    else:
        text = text.format( *values )
    
    # ------------------------------------------------- #
    # --- [3] save file                             --- #
    # ------------------------------------------------- #
    with open( outFile, "w" ) as f:
        f.write( text )
        

# ========================================================= #
# ===   Execution of Pragram                            === #
# ========================================================= #

if ( __name__=="__main__" ):

    # ------------------------------------------------- #
    # --- [1] lamp shade shape                      --- #
    # ------------------------------------------------- #
    inpFile       = "ref/lamp_shade_1to16.json"
    outFile_base  = "cnf/lamp_shade{0}.json"
    for ik in range( 1, 16+1 ):
        outFile = outFile_base.format( ik )
        values  = [ "{}".format(ik), "{}".format(-12.0*(ik-1)) ]
        mark    = "$"
        make__scanParameterFile( inpFile=inpFile, outFile=outFile, values=values, mark=mark, replaceMode=True )

    inpFile       = "ref/lamp_shade_17and30.json"
    outFile_base  = "cnf/lamp_shade{0}.json"
    for ik in [17,30]:
        outFile = outFile_base.format( ik )
        values  = [ "{}".format(ik), "{}".format(-12.0*(ik-1)) ]
        mark    = "$"
        make__scanParameterFile( inpFile=inpFile, outFile=outFile, values=values, mark=mark, replaceMode=True )

    inpFile       = "ref/lamp_shade_18to29.json"
    outFile_base  = "cnf/lamp_shade{0}.json"
    for ik in range( 18, 29+1 ):
        outFile = outFile_base.format( ik )
        values  = [ "{}".format(ik), "{}".format(-12.0*(ik-1)) ]
        mark    = "$"
        make__scanParameterFile( inpFile=inpFile, outFile=outFile, values=values, mark=mark, replaceMode=True )


    # ------------------------------------------------- #
    # --- [2] sector shape                          --- #
    # ------------------------------------------------- #
    inpFile       = "ref/sector_1to8.json"
    outFile_base  = "cnf/sector{0}.json"
    for ik in range( 1, 8+1 ):
        outFile = outFile_base.format( ik )
        values  = [ "{}".format(ik), "{}".format(-45.0*(ik-1)) ]
        mark    = "$"
        make__scanParameterFile( inpFile=inpFile, outFile=outFile, values=values, mark=mark, replaceMode=True )

