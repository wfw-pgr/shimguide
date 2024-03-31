import numpy as np

# ========================================================= #
# ===  generate__sampleHole.py                          === #
# ========================================================= #

def generate__sampleHole():

    max_radius = 500.0
    Dcircle    = 8.0
    min_margin = 4.0
    radius     = 0.5*Dcircle

    interval    = min_margin + Dcircle
    n_put_radii = max_radius // interval
    put_radii   = np.arange( n_put_radii ) * interval
    circumf     = 2.0 * np.pi * put_radii
    nCircumf    = circumf // interval
    nCircumf[0] = 1
    nHole       = int( np.sum( nCircumf ) )
    dtheta      = 2.0*np.pi/nCircumf
    stack       = []
    for ik, put_radius in enumerate(put_radii):
        theta = dtheta[ik] * np.arange( nCircumf[ik] )
        xpos  = put_radius * np.cos( theta )
        ypos  = put_radius * np.sin( theta )
        radii = radius * np.ones( (theta.shape[0], ) )
        flag  = np.ones( (theta.shape[0], ) )
        hData = np.concatenate( [ xpos [:,np.newaxis], ypos[:,np.newaxis],\
                                  radii[:,np.newaxis], flag[:,np.newaxis] ], axis=1 )
        stack += [hData]
    holes      = np.concatenate( stack, axis=0 )

    import nkUtilities.save__pointFile as spf
    outFile   = "dat/circularTray001_hole.dat"
    spf.save__pointFile( outFile=outFile, Data=holes )
    print( holes.shape )
    

# ========================================================= #
# ===   Execution of Pragram                            === #
# ========================================================= #

if ( __name__=="__main__" ):
    generate__sampleHole()
