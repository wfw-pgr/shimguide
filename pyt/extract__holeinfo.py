import os, sys, re
import numpy  as np
import pandas as pd

# ========================================================= #
# ===  load__database()                                 === #
# ========================================================= #

def load__database( database=None, databaseFile=None, flagFile1=None, flagFile2=None, \
                    overwrite__lampshade_xy=True ):

    names        = [ "ID", "x", "y", "z", "vol", "d", "trayID", "x0", "y0" ]
    trayNameList = [ "adjacent", "disc", "all" ] + [ "sector{}".format(ik+1) for ik in range(8) ] \
                   + [ "lamp_shade{}".format(ik+1) for ik in range(30) ]
    
    # ------------------------------------------------- #
    # --- [1] Arguments                             --- #
    # ------------------------------------------------- #
    if ( database is None ):
        if ( databaseFile is None ):
            sys.exit( "[extract__holeinfo.py] database / databaseFile == ???" )
        else:
            database = pd.read_csv( databaseFile, delimiter="\s+", names=names )
            database.set_index( "ID" )
    else:
        sys.exit( "[extract__holeinfo.py] database / databaseFile == ???" )

    if ( flagFile1 is None ): sys.exit( "[extract__holeinfo.py] flagFile1 == ???" )
    if ( flagFile2 is None ): sys.exit( "[extract__holeinfo.py] flagFile2 == ???" )
    
    # ------------------------------------------------- #
    # --- [2]  read file                            --- #
    # ------------------------------------------------- #
    Data1                          = pd.read_csv( flagFile1, delimiter="\s+", names=["ID","flag","x","y","z"] )
    Data2                          = pd.read_csv( flagFile2, delimiter="\s+", names=["ID","flag","x","y","z"] )
    Data1                          = Data1.drop( ["x","y","z"], axis=1 )
    Data2                          = Data2.drop( ["x","y","z"], axis=1 )
    Data                           = Data2.copy()
    Data["diff"]                   = Data2["flag"] - Data1["flag"]
    Data["adds"]                   = ( Data["diff"] == +1 )
    Data["rmvs"]                   = ( Data["diff"] == -1 )
    Data["noch"]                   = ( Data["diff"] ==  0 )
    Data["accu"]                   = ( Data["flag"] == +1 )
    merged                         = pd.merge( database, Data, on="ID", how="left" )
    merged["side"]                 = merged["trayID"].str.contains( "_side" )
    merged["trayName"]             = merged["trayID"].str.replace ( "_side", "" )
    merged[["trayType","trayNum"]] = merged["trayName"].str.extract( r"(\D+)([0-9]*)" )
    merged["trayNum"]              = np.where( merged["trayNum"] == "", 0, merged["trayNum"] )
    if ( overwrite__lampshade_xy ):
        merged.loc[ merged["trayType"]=="lamp_shade", "x" ] = merged.loc[ merged["trayType"]=="lamp_shade", "x0" ]
        merged.loc[ merged["trayType"]=="lamp_shade", "y" ] = merged.loc[ merged["trayType"]=="lamp_shade", "y0" ]
    return( merged )

    
# ========================================================= #
# ===  extract__holeinfo.py                             === #
# ========================================================= #

def extract__holeinfo( database=None, trayName=None, action=None, z_polarity=None ):

    key_dict     = { "add":"adds", "remove":"rmvs", "accumulate":"accu", "all":"all" }
    trayNameList = [ "adjacent", "disc", "all" ] + [ "sector{}".format(ik+1) for ik in range(8) ] \
                   + [ "lamp_shade{}".format(ik+1) for ik in range(30) ]
    
    # ------------------------------------------------- #
    # --- [1] arguments                             --- #
    # ------------------------------------------------- #
    if ( database is None                   ): sys.exit( "[extract__holeinfo.py] database == ???" )
    if ( not( trayName in trayNameList )    ): sys.exit( "[extract__holeinfo.py] trayName   == ???" )
    if ( not( action   in key_dict.keys() ) ): sys.exit( "[extract__holeinfo.py] action  == ???" )
    if ( not( z_polarity in [ "+", "-", "+-" ] ) ):sys.exit( "[extract__holeinfo.py] z_polarity  == ???" )

    # ------------------------------------------------- #
    # --- [2] make dataframe                        --- #
    # ------------------------------------------------- #
    action_key = key_dict[ action.lower() ]
    # database.loc[ database["side"] == True, action_key ] = True   ## this line is used to confirm side circles.
    if ( action.lower() == "all"   ):
        selected = database.copy()
    else:
        selected = database[ ( database[action_key] == True ) ]


    if ( trayName.lower() == "all" ):
        pass
    else:
        selected   = selected[ ( selected["trayName"] == trayName ) ]

    if   ( z_polarity == "+" ):
        selected = selected[ selected["z"] > 0.0 ]
    elif ( z_polarity == "-" ):
        selected = selected[ selected["z"] < 0.0 ]
    elif ( z_polarity == "+-" ):
        pass

    
    # ------------------------------------------------- #
    # --- [3] return                                --- #
    # ------------------------------------------------- #
    return( selected )
    


# ========================================================= #
# ===   Execution of Pragram                            === #
# ========================================================= #

if ( __name__=="__main__" ):
    
    databaseFile = "input_format/shimbolt_small.db"
    flagFile1    = "input_format/test3_1.01"
    flagFile2    = "input_format/test3_2.01"
    trayName     = "disc"
    action       = "all"
    z_polarity   = "+"
    database_ex  = load__database   ( databaseFile=databaseFile, flagFile1=flagFile1, flagFile2=flagFile2 )
    ret          = extract__holeinfo( database=database_ex, trayName=trayName, \
                                      action=action, z_polarity=z_polarity )
    print( ret )
