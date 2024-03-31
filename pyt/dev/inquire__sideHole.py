import extract__holeinfo as ext


databaseFile = "../input_format/shimbolt_small.db"
flagFile1    = "../input_format/test3_1.01"
flagFile2    = "../input_format/test3_2.01"
trayName     = "all"
action       = "all"
z_polarity   = "+"
database_ex  = ext.load__database   ( databaseFile=databaseFile, flagFile1=flagFile1, flagFile2=flagFile2 )
ret          = ext.extract__holeinfo( database=database_ex, trayName=trayName, \
                                      action=action, z_polarity=z_polarity )
print( ret )
