import os, sys
import numpy  as np
import pandas as pd

# ========================================================= #
# ===  return__holePosition.py                          === #
# ========================================================= #

def return__holePosition( database=None, databaseFile=None, flagFile1=None, flagFile2=None, \
                          returnType="ID" ):

    names = [ "ID", "x", "y", "z", "vol", "d", "trayID", "x0", "y0" ]
    
    # ------------------------------------------------- #
    # --- [1] Arguments                             --- #
    # ------------------------------------------------- #
    if ( database is None ):
        if ( databaseFile is None ):
            sys.exit( "[return__holePosition.py] database / databaseFile == ???" )
        else:
            database = pd.read_csv( databaseFile, delimiter="\s+", names=names )
    else:
        sys.exit( "[return__holePosition.py] database / databaseFile == ???" )

    if ( flagFile1 is None ): sys.exit( "[return__holePosition.py] flagFile1 == ???" )
    if ( flagFile2 is None ): sys.exit( "[return__holePosition.py] flagFile2 == ???" )
        
    # ------------------------------------------------- #
    # --- [2]  read file                            --- #
    # ------------------------------------------------- #
    Data1  = pd.read_csv( flagFile1, delimiter="\s+", names=["ID","flag","x","y","z"] )
    Data2  = pd.read_csv( flagFile2, delimiter="\s+", names=["ID","flag","x","y","z"] )
    ids    = np.array( Data1["ID"] )
    flags1 = Data1["flag"]
    flags2 = Data2["flag"]
    
    # ------------------------------------------------- #
    # --- [3] return data                           --- #
    # ------------------------------------------------- #
    diff  = np.array( flags2 - flags1 )
    if ( returnType == "ID" ):
        adds    = ids[ np.where( diff == +1 ) ]
        rmvs    = ids[ np.where( diff == -1 ) ]
        noch    = ids[ np.where( diff ==  0 ) ]
        return( { "adds":adds, "rmvs":rmvs, "noch":noch, "ids":ids } )
    if ( returnType == "diff" ):
        return( diff )
    if ( returnType == "loaded" ):
        return( database, flags )


# ========================================================= #
# ===   Execution of Pragram                            === #
# ========================================================= #

if ( __name__=="__main__" ):
    
    databaseFile = "input_format/shimbolt_small.db"
    flagFile1    = "input_format/test3_1.01"
    flagFile2    = "input_format/test3_2.01"
    ret          = return__holePosition( databaseFile=databaseFile, flagFile1=flagFile1, flagFile2=flagFile2, \
                                         returnType="ID" )
    print( ret["adds"].shape )
    print( ret["rmvs"].shape )
    print( ret["noch"].shape )
