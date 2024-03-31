import numpy  as np
import pandas as pd

# ========================================================= #
# ===  read__inputFile.py                               === #
# ========================================================= #

def read__inputFile( database=None, databaseFile=None, flagFile=None ):

    names = [ "ID", "x", "y", "z", "vol", "d", "trayID", "x0", "y0" ]
    
    # ------------------------------------------------- #
    # --- [1] Arguments                             --- #
    # ------------------------------------------------- #
    if ( database is None ):
        if ( databaseFile is None ):
            sys.exit( "[read__inputFile.py] database / databaseFile == ???" )
        else:
            database = pd.read_csv( databaseFile, delimiter="\s+", names=names )
    else:
        sys.exit( "[read__inputFile.py] database / databaseFile == ???" )
    if ( flagFile is None ):
        if ( flagFile is None ): sys.exit( "[read__inputFile.py] flagFile == ???" )
        
    # ------------------------------------------------- #
    # --- [2]  read file                            --- #
    # ------------------------------------------------- #
    Data_r  = pd.read_csv( flagFile, delimiter="\s+", names=["ID","flag","x","y","z"] )
    Data_f  = Data_r.set_index( "ID" )
    flags   = Data_f["flag"]
    
    # ------------------------------------------------- #
    # --- [3] return data                           --- #
    # ------------------------------------------------- #
    return( database, flags )


# ========================================================= #
# ===   Execution of Pragram                            === #
# ========================================================= #

if ( __name__=="__main__" ):
    
    databaseFile = "input_format/shimbolt_small.db"
    flagFile     = "input_format/error_Y3Y6_2%_2043x2_small.01"
    db, fl = read__inputFile( databaseFile=databaseFile, flagFile=flagFile )
    print( db )
    print( fl )
