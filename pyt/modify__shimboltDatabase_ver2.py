import numpy  as np
import pandas as pd

xval1      = 994.5e-3
xval2      = 995.0e-3
xval3      = 994.0e-3

databaseFile               = "cnf/shimbolt_use.db"
names                      = [ "ID", "x", "y", "z", "vol", "d", "trayID", "x0", "y0" ]
database                   = pd.read_csv( databaseFile, delimiter="\s+", names=names )

for ik in np.arange(1,17):
    database.loc[ ( database["trayID"].str.contains( "lamp_shade{}_side".format(ik) ) ), "x0" ] = xval1
for ik in [17,30]:
    database.loc[ ( database["trayID"].str.contains( "lamp_shade{}_side".format(ik) ) ), "x0" ] = xval2
for ik in np.arange(18,30):
    database.loc[ ( database["trayID"].str.contains( "lamp_shade{}_side".format(ik) ) ), "x0" ] = xval3

outFile  = "cnf/shimbolt_mod.db"
print( database )
database.to_csv( outFile, sep=" ", index=False, header=False )

