import numpy  as np
import pandas as pd

side_xval1 = np.cos(6.0/180.0*np.pi) *  990.0e-3 + 5.0e-3
side_xval2 = np.cos(6.0/180.0*np.pi) * 1000.0e-3 + 5.0e-3

databaseFile               = "cnf/shimbolt_use.db"
names                      = [ "ID", "x", "y", "z", "vol", "d", "trayID", "x0", "y0" ]
database                   = pd.read_csv( databaseFile, delimiter="\s+", names=names )
x0                         = database[ database["trayID"].str.contains( "lamp_shade" ) ]["x0"]
y0                         = database[ database["trayID"].str.contains( "lamp_shade" ) ]["y0"]

angle1                     = np.angle( database["x" ]+1j*database["y" ], deg=True )
# angle2                     = np.angle(             x0+1j*y0            , deg=True )
angle2                     = np.angle( database["x" ]+1j*database["y" ], deg=True )
angle1[ angle1 < -22.5 ]  += 360.0
angle2[ angle2 <  -6.0 ]  += 360.0
label1                     = ( np.ceil( (angle1+22.5)/45.0 ) ).astype( int )
label2                     = ( np.ceil( (angle2+ 6.0)/12.0 ) ).astype( int )

database.loc[ ( database["trayID"].str.contains( "_side" ) ), "x0" ] = side_xval1
database.loc[ ( database["trayID"].str.contains( "_side" ) )&( label2 >=18 )&( label2 <= 29 ), "x0" ] = side_xval2

label2                     = label2[ database["trayID"].str.contains( "lamp_shade" ) ]
database["newID"]          = "sector" + pd.DataFrame( label1.astype( str ) )

database.loc[ database["trayID"].str.contains( "sector" ), "trayID" ] = database.loc[ database["trayID"].str.contains( "sector" ), "newID" ]


rot_ang  = np.pi/180.0 * ( label2 - 1 )*12.0
print( label2  )
print( rot_ang )
cos, sin = np.cos( rot_ang ), np.sin( rot_ang )
RotMat   = np.array( [ [ cos, -sin ], \
                       [ sin,  cos ] ] )
RotMat   = np.transpose( RotMat, (2,0,1) )
x0y0     = ( database.loc[ database["trayID"].str.contains( "lamp_shade" ), ["x0","y0"] ] ).to_numpy()
x0y0     = np.reshape( x0y0, (-1,2,1) )
print( RotMat.shape, x0y0.shape )
xy0_new  = np.reshape( np.matmul( RotMat, x0y0 ), (-1,2) )
database.loc[ database["trayID"].str.contains( "lamp_shade" ), ["x0","y0"] ] = xy0_new
database = database.drop( ["newID"], axis=1 )

outFile  = "cnf/shimbolt_mod.db"
print( database )
database.to_csv( outFile, sep=" ", index=False, header=False )


# rot_ang  = np.pi/180.0 * ( ( database.loc[ database["trayID"].str.contains( "lamp_shade" ), "label" ] - 1 )*45.0 )
# rot_ang  = rot_ang.to_numpy()

