import sys
import pandas                     as pd
import numpy                      as np
import nkUtilities.load__config   as lcf
import nkUtilities.plot1D         as pl1
import nkUtilities.configSettings as cfs
import extract__holeinfo          as ext
import matplotlib.cm              as cm

# ========================================================= #
# ===  display                                          === #
# ========================================================= #
def display():

    x_,y_ = 0, 1

    flagFile1    = "dat/before.01"
    flagFile2    = "dat/after.01"
    databaseFile = "cnf/shimbolt_renewed2.db"
    action       = "all"
    trayName     = "all"
    z_polarity   = "+"
    zp           = ({"+":"upr","-":"lwr"})[z_polarity]
    pngFile      = "png/shimPosition_tray_{}_action_{}_z_{}.png".format( trayName, action, zp )
    
    # ------------------------------------------------- #
    # --- [1] Arguments                             --- #
    # ------------------------------------------------- #
    config  = lcf.load__config()

    database_ex  = ext.load__database   ( databaseFile=databaseFile, flagFile1=flagFile1, flagFile2=flagFile2 )
    holeinfo     = ext.extract__holeinfo( database=database_ex, trayName=trayName, \
                                          action=action, z_polarity=z_polarity )
    holeinfo     = holeinfo[ holeinfo["side"] == False ]
    trayTypeList = set( holeinfo["trayName"] )
    
    # ------------------------------------------------- #
    # --- [3] config Settings                       --- #
    # ------------------------------------------------- #
    cfs.configSettings( configType="plot1D_def", config=config )
    config["xTitle"]         = "X (m)"
    config["yTitle"]         = "Y (m)"
    config["plt_xAutoRange"] = True
    config["plt_yAutoRange"] = True
    config["plt_xRange"]     = [-5.0,+5.0]
    config["plt_yRange"]     = [-5.0,+5.0]
    config["plt_linewidth"]  = 1.0
    config["xMajor_Nticks"]  = 5
    config["yMajor_Nticks"]  = 5
    config["plt_marker"]     = "o"
    config["plt_linestyle"]  = "none"
    config["plt_markersize"] = 0.4

    # ------------------------------------------------- #
    # --- [4] plot Figure                           --- #
    # ------------------------------------------------- #
    fig    = pl1.plot1D( config=config, pngFile=pngFile )
    nColor = len( trayTypeList ) + 2
    for ik,tray in enumerate( trayTypeList ):
        cv           = (ik+1) / nColor
        xAxis        = ( holeinfo[ holeinfo["trayName"] == tray ] )["x"].to_numpy()
        yAxis        = ( holeinfo[ holeinfo["trayName"] == tray ] )["y"].to_numpy()
        fig.add__plot( xAxis=xAxis, yAxis=yAxis, color=cm.jet(cv) )
    fig.set__axis()
    fig.save__figure()


# ======================================== #
# ===  実行部                          === #
# ======================================== #
if ( __name__=="__main__" ):
    display()

