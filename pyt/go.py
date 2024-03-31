import os, re, sys, pypdf, glob, argparse, shutil, json
import make__shimGuideMask as msm

# # --   files   -- #
# flagFile1    = "dat/before.01"
# flagFile2    = "dat/after.01"
# # -- parameter -- #
# actions        = [ "add", "remove" ]
# z_polarities   = [ "+", "-" ]

z_pol_dir      = { "+":"zUpper", "-":"zLower" }

group1,group2  = [], []
group1        += [ "disc", "adjacent" ]
group1        += [ "sector{}"    .format(ik+1) for ik in range( 8) ]
group2        += [ "lamp_shade{}".format(ik+1) for ik in range(30) ]
all_trayName   = group1 + group2

configFile     = "cnf/system_config.json"
with open( configFile, "r" ) as f:
    conf = json.load( f )

if   ( conf["01.DefaultFileMode"].lower() == "search_latest" ):
    searched   = glob.glob( conf["01.DefaultFileBase"] )
    fnames     = sorted( searched )
    default_flagFile1 = fnames[-2]
    default_flagFile2 = fnames[-1]
    # expression = conf["01.DefaultFileBase"].replace( "*", "([0-9]+)" )
    # values     = [ int( ( re.match( expression, fname ) ).group(1) ) for fname in searched ]
    
elif ( conf["01.DefaultFileMode"].lower() in [ "from_config", "direct" ] ):
    default_flagFile1 = conf["01.direct.inpFile1"]
    default_flagFile2 = conf["01.direct.inpFile2"]
else:
    print( "[go.py] unknown 01.DefaultFileMode :: {} ".format( conf["01.DefaultFileMode"] ) )
    sys.exit()

# ========================================================= #
# ===  [1] arguments settings                           === #
# ========================================================= #

# -- arg parser -- #
parser = argparse.ArgumentParser()
# -- arguments  -- #
parser.add_argument( "--previous"  , help="previous 01 data file :: (e.g.) dat/before.01 "    )
parser.add_argument( "--latest"    , help="latest   01 data file :: (e.g.) dat/after.01 "     )
parser.add_argument( "--db"        , help="shim database file :: (e.g.) dat/shimbolt_mod.db " )
parser.add_argument( "--action"    , help="choose from [ add / remove / all ]"    )
parser.add_argument( "--z"         , help="choose from [ upper / lower / all ]"   )
parser.add_argument( "--trayName"  , help="trayName list or str   :: (e.g.) 'sector1' or '[sector1,lamp_shade1]' etc... " )
parser.add_argument( "--clean", action="store_true", help="clean up pdf directories. Be Carefull." )

# ========================================================= #
# ===  [2] set arguments                                === #
# ========================================================= #

args  = parser.parse_args()

# -- clean -- #
if ( args.clean ):
    print( "[go.py] clean up pdf/ directory... ", end="" )
    shutil.rmtree( "pdf/" )
    os.mkdir( "pdf/" )
    print( "    [Done]" )

# -- previous -- #
if ( args.previous ):
    if ( os.path.exists ):
        flagFile1 = args.previous
    else:
        sys.exit( "[ERROR] Cannot find  previous file :: {}".format( args.previous ) )
else:
    flagFile1 = default_flagFile1

# -- latest -- #
if ( args.latest ):
    if ( os.path.exists ):
        flagFile2 = args.latest
    else:
        sys.exit( "[ERROR] Cannot find  --latest file :: {}".format( args.latest   ) )
else:
    flagFile2 = default_flagFile2

# -- databaseFile -- #
if ( args.db ):
    if ( os.path.exists ):
        databaseFile = args.db
    else:
        sys.exit( "[ERROR] Cannot find  --db file :: {}".format( args.db   ) )
else:
    databaseFile = conf["db.DefaultFile"]

# -- action -- #
if ( args.action ):
    if   ( args.action.lower() in [ "add", "remove" ] ):
        actions = [ args.action.lower() ]
    elif ( args.action.lower() in [ "all" ] ):
        actions = [ "add", "remove" ]
    else:
        sys.exit( "[ERROR] Undefined --action :: {}".format( args.action   ) )
else:
    actions = [ "add", "remove" ]
    
# -- z_polarities -- #
if ( args.z ):
    if   ( args.z.lower() in [ "upper" ] ):
        z_polarities = [ "+" ]
    elif ( args.z.lower() in [ "lower" ] ):
        z_polarities = [ "-" ]
    elif ( args.z.lower() in [ "all"   ] ):
        z_polarities = [ "+", "-" ]
    else:
        sys.exit( "[ERROR] Undefined --z :: {}".format( args.z   ) )
else:
    z_polarities = [ "+", "-" ]

# -- trayName -- #
if ( args.trayName ):
    expression = "\[(.+)\]"
    list_match = re.match( expression, args.trayName  )
    if ( args.trayName.lower() in ["all"] ):
        group1,group2  = [], []
        group1        += [ "disc", "adjacent" ]
        group1        += [ "sector{}"    .format(ik+1) for ik in range( 8) ]
        group2        += [ "lamp_shade{}".format(ik+1) for ik in range(30) ]
    elif ( list_match ):  # list match
        htrayNames = ( list_match.group(1) ).split(",")
        group1_ = [ tN for tN in htrayNames if ( tN in group1 ) ]
        group2_ = [ tN for tN in htrayNames if ( tN in group2 ) ]
        group1  = group1_
        group2  = group2_
    elif ( args.trayName in group1 ):    # single match 
        group1, group2 = [ args.trayName ], []
    elif ( args.trayName in group2 ):    # single match
        group1, group2 = [ args.trayName ], []
    else:
        print( "[go.py] invalid input: --trayName {}".format( args.trayName ) )
        print( "[go.py]    --trayName sector1   or   --trayName [disc,lamp_shade1] etc. " )
        print( "[go.py]   trayName in [ disc, adjacent, sectorN (N=1,2,3,...), lamp_shadeN ( N=1, 2, 3, ... )]" )
        sys.exit()
else:
    group1,group2  = [], []
    group1        += [ "disc", "adjacent" ]
    group1        += [ "sector{}"    .format(ik+1) for ik in range( 8) ]
    group2        += [ "lamp_shade{}".format(ik+1) for ik in range(30) ]

if ( ( len(group2)%2 ) == 1 ):
    group1 += [ group2.pop() ]
    
fileGroup1     = [ "cnf/{}.json".format( name ) for name in group1 ]
fileGroup2     = [ "cnf/{}.json".format( name ) for name in group2 ]
fileGroup2     = [ fileGroup2[ik:ik+2] for ik in range( 0, len(fileGroup2), 2 ) ]

# ========================================================= #
# ===  [3] display inputs                               === #
# ========================================================= #
print()
print( "[go.py] previous file  :: ", flagFile1    )
print( "[go.py] latest file    :: ", flagFile2    )
print( "[go.py] database file  :: ", databaseFile )
print()
print( "[go.py] actions        :: ", actions      )
print( "[go.py] z_polarities   :: ", z_polarities )
print( "[go.py] Trays (group1) :: ", group1       )
print( "[go.py] Trays (group2) :: ", group2       )
print()

# ========================================================= #
# ===  [4] loop execution                               === #
# ========================================================= #

# --    run    -- #
print()
print( "[go.py] begin making of shimGuideMask...." )
print()
for action in actions:
    for z_polarity in z_polarities:
        outDir = "pdf/{0}_{1}/".format( action, z_pol_dir[z_polarity] )
        os.makedirs( outDir, exist_ok=True )
        for jsonFile in fileGroup1:
            msm.make__shimGuideMask( databaseFile=databaseFile, flagFile1=flagFile1, flagFile2=flagFile2, \
                                     jsonFile=jsonFile, action=action, z_polarity=z_polarity, outDir=outDir )
        
        for jsonFile1,jsonFile2 in fileGroup2:
            msm.make__shimGuideMask_multiple_lampshade( flagFile1=flagFile1, flagFile2=flagFile2, \
                                                        jsonFile1=jsonFile1, jsonFile2=jsonFile2, \
                                                        databaseFile=databaseFile, \
                                                        action=action, z_polarity=z_polarity, outDir=outDir )

print()
print( "[go.py] making of shimGuideMask has ended  [END]" )
print()

# ========================================================= #
# ===  [5] merge pdf                                    === #
# ========================================================= #
outDirs       = [ "pdf/{0}_{1}/".format( act, z_pol_dir[zpd] ) for act in actions for zpd in z_polarities ]
outFile_stack = []
for outDir in outDirs:
    print( "[go.py] merging files in {} ".format( outDir ) )
    inpFiles = [ "disc*merged.pdf"  , "adjacent*merged.pdf", \
                 "sector*merged.pdf", "lamp_shade*merged.pdf" ]
    stack = []
    for inpFile in inpFiles:
        stack += glob.glob( outDir + inpFile )

    readers  = [ pypdf.PdfReader( ifile ) for ifile in stack ]
    pages    = [ apage for reader in readers for apage in reader.pages[:] ]
    writer   = pypdf.PdfWriter()
    for ik,apage in enumerate( pages ):
        writer.add_page( apage )
    outFile = outDir.strip( "/" ) + "_merged.pdf"
    writer.write( outFile )
    outFile_stack += [ outFile ]

print( "\n" + "[go.py] merging of pdf File has ended [END]" + "\n" )
print( "[go.py] output Files :: " )
for outFile in outFile_stack:
    print( "[go.py] save in a file :: {} ".format( outFile ) )
print()


# ========================================================= #
# ===  [6] divide pdf                                   === #
# ========================================================= #
if ( conf["nParallel"] > 1 ):
    for outFile in outFile_stack:
        msm.merge__pdfFile( nParallel=conf["nParallel"], inpFile=outFile, outFile=outFile, erase=False )
