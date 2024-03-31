import os, sys, math, json, glob
import reportlab
import pypdf
import numpy             as     np
from reportlab.lib       import pagesizes
from reportlab.lib.units import mm
from reportlab.pdfgen    import canvas


# ========================================================= #
# ===  draw trayFrame                                   === #
# ========================================================= #

def draw__trayFrame( pdfcanvas=None, page_bbox=None, cards=None ):

    x_, y_   = 0, 1
    r_, th_  = 0, 1
    s_, e_   = 0, 1   # start & end

    # ------------------------------------------------- #
    # --- [1] arguments                             --- #
    # ------------------------------------------------- #
    if ( pdfcanvas is None ): sys.exit( "[make__shimGuideMask.py] pdfcanvas == ???" )
    if ( page_bbox is None ): sys.exit( "[make__shimGuideMask.py] page_bbox == ???" )
    if ( cards     is None ): sys.exit( "[make__shimGuideMask.py] cards     == ???" )

    # ------------------------------------------------- #
    # --- [2] draw shapes according to cards        --- #
    # ------------------------------------------------- #
    page_bbox_lb = np.copy( page_bbox[0:2] )
    for key, val in cards.items():
        # -- [2-1] line case                         -- #
        if   ( val["shapeType"].lower() == "line"   ):
            startpt = ( val["start"] - page_bbox_lb )*mm
            endpt   = ( val["end"]   - page_bbox_lb )*mm
            pdfcanvas.line  ( startpt[x_], startpt[y_], endpt[x_], endpt[y_] )
        # -- [2-2] circle case                       -- #
        elif ( val["shapeType"].lower() == "circle" ):
            centerpt = ( val["center"] - page_bbox_lb )*mm
            radius   = ( val["radius"] )*mm
            pdfcanvas.circle( centerpt[x_], centerpt[y_], radius )
            
        # -- [2-3] arc case                          -- #
        elif ( val["shapeType"].lower() == "arc"    ):
            centerpt = val["center"] - page_bbox_lb
            x1, y1   = ( centerpt[x_]-val["radius"] )*mm, ( centerpt[y_]-val["radius"] )*mm
            x2, y2   = ( centerpt[x_]+val["radius"] )*mm, ( centerpt[y_]+val["radius"] )*mm
            a1, a2   = val["angle1"], val["angle2"] - val["angle1"]
            pdfcanvas.arc( x1, y1, x2, y2, a1, a2 )

        # -- [2-4] radial line case                  -- #
        elif ( val["shapeType"].lower() == "radialline"   ):
            ang2rad  = np.pi / 180.0
            cos, sin = np.cos( val["angle"]*ang2rad ), np.sin( val["angle"]*ang2rad )
            startpt  = ( np.array( [ val["r1"]*cos, val["r1"]*sin ] )  - page_bbox_lb )*mm
            endpt    = ( np.array( [ val["r2"]*cos, val["r2"]*sin ] )  - page_bbox_lb )*mm
            pdfcanvas.line  ( startpt[x_], startpt[y_], endpt[x_], endpt[y_] )

        # -- [2-5] radial line case                  -- #
        elif ( val["shapeType"].lower() == "polyline_inrt" ):
            ang2rad  = np.pi / 180.0
            center   = np.array( val["center"]    )
            points   = np.array( val["points_rt"] )
            cos,sin  = np.cos( points[:,th_]*ang2rad ), np.sin( points[:,th_]*ang2rad )
            xp, yp   = points[:,r_]*cos+center[x_], points[:,r_]*sin+center[y_]
            xn, yn   = ( xp[:] - page_bbox_lb[x_] )*mm, ( yp[:] - page_bbox_lb[y_] )*mm
            xynorm   = np.concatenate( [xn[:,np.newaxis], yn[:,np.newaxis]], axis=1 )
            lines    = np.concatenate( [xynorm[:-1,:,np.newaxis],xynorm[1:,:,np.newaxis]], axis=2 )
            if   ( val["linetype"] == "solid" ):
                for ik,pt in enumerate( lines ):
                    pdfcanvas.line  ( pt[x_,s_], pt[y_,s_], pt[x_,e_], pt[y_,e_] )
            elif ( val["linetype"] == "dashed" ):
                for ik,pt in enumerate( lines ):
                    dxy      = ( pt[:,e_] - pt[:,s_] ) / ( 2*val["dashed.nDiv"]+1 )
                    for il in range( 1, 2*val["dashed.nDiv"]+1, 2 ):
                        pdfcanvas.line( pt[x_,s_]+(il  )*dxy[x_], pt[y_,s_]+(il  )*dxy[y_], \
                                        pt[x_,s_]+(il+1)*dxy[x_], pt[y_,s_]+(il+1)*dxy[y_]  )
            
        
        # -- [2-6] xy-coordinate line case           -- #
        elif ( val["shapeType"].lower() == "polyline_inxy" ):
            ang2rad  = np.pi / 180.0
            points   = np.array( val["points_xy"] )
            xn, yn   = ( points[:,x_] - page_bbox_lb[x_] )*mm, ( points[:,y_] - page_bbox_lb[y_] )*mm
            xynorm   = np.concatenate( [xn[:,np.newaxis], yn[:,np.newaxis]], axis=1 )
            lines    = np.concatenate( [xynorm[:-1,:,np.newaxis],xynorm[1:,:,np.newaxis]], axis=2 )
            for ik,pt in enumerate( lines ):
                pdfcanvas.line  ( pt[x_,s_], pt[y_,s_], pt[x_,e_], pt[y_,e_] )

        # -- [2-7] side-parts case                  -- #
        elif ( val["shapeType"].lower() == "polyline_side" ):
            ang2rad  = np.pi / 180.0
            center   = np.array( val["center"]     )
            p_rt     = np.array( val["points_rt"]  )
            cos,sin  = np.cos( p_rt[:,th_]*ang2rad ), np.sin( p_rt[:,th_]*ang2rad )
            xp, yp   = p_rt[:,r_]*cos+center[x_], p_rt[:,r_]*sin+center[y_]
            xs, ys   = np.copy(xp)+val["width"], np.copy(yp)
            xp, yp   = ( np.concatenate( [xp,xs] ) )[ [0,2,3,1] ], ( np.concatenate( [yp,ys] ) )[ [0,2,3,1] ]
            xn, yn   = ( xp[:] - page_bbox_lb[x_] )*mm, ( yp[:] - page_bbox_lb[y_] )*mm
            xynorm   = np.concatenate( [xn[:,np.newaxis], yn[:,np.newaxis]], axis=1 )
            lines    = np.concatenate( [xynorm[:-1,:,np.newaxis],xynorm[1:,:,np.newaxis]], axis=2 )
            for ik,pt in enumerate( lines ):
                pdfcanvas.line  ( pt[x_,s_], pt[y_,s_], pt[x_,e_], pt[y_,e_] )

        else:
            print( "[make__shimGuideMask.py] unknown shapeType == {} ".format( val["shapeType"] ) )
            sys.exit()
                
    # ------------------------------------------------- #
    # --- [3] return pdf's canvas                   --- #
    # ------------------------------------------------- #
    return( pdfcanvas )


# ========================================================= #
# ===  draw shim hole                                   === #
# ========================================================= #

def draw__shimHole( pdfcanvas=None, page_bbox=None, holes=None ):

    x_, y_, d_ = 0, 1, 2
    
    # ------------------------------------------------- #
    # --- [1] arguments                             --- #
    # ------------------------------------------------- #
    if ( pdfcanvas is None ): sys.exit( "[make__shimGuideMask.py] pdfcanvas == ???" )
    if ( page_bbox is None ): sys.exit( "[make__shimGuideMask.py] page_bbox == ???" )
    if ( holes     is None ): sys.exit( "[make__shimGuideMask.py] holes     == ???" )

    # ------------------------------------------------- #
    # --- [2] draw shapes according to cards        --- #
    # ------------------------------------------------- #
    page_bbox_lb = np.insert( np.array( page_bbox[0:2] ), 2, 0.0 )
    page_ref     = np.repeat( page_bbox_lb[np.newaxis,:], holes.shape[0], axis=0 )
    holes_page   = ( holes - page_ref ) * mm
    for xyr in holes_page:
        pdfcanvas.circle( xyr[x_], xyr[y_], 0.5*xyr[d_] )
            
    # ------------------------------------------------- #
    # --- [3] return pdf's canvas                   --- #
    # ------------------------------------------------- #
    return( pdfcanvas )

    
# ========================================================= #
# ===  draw out frame                                   === #
# ========================================================= #

def draw__outFrame( pdfcanvas=None, pagesize=(297.0,420.0) ):

    x_, y_ = 0, 1

    # ------------------------------------------------- #
    # --- [1] arguments                             --- #
    # ------------------------------------------------- #
    if ( pdfcanvas is None ): sys.exit( "[make__shimGuideMask.py] pdfcanvas == ???" )

    # ------------------------------------------------- #
    # --- [2] draw shapes according to cards        --- #
    # ------------------------------------------------- #
    x1, y1 = 1.0, 1.0
    Lx ,Ly = ( pagesize[x_]-x1 )*mm, ( pagesize[y_]-y1 )*mm
    pdfcanvas.rect( x1, y1, Lx, Ly )
            
    # ------------------------------------------------- #
    # --- [3] return pdf's canvas                   --- #
    # ------------------------------------------------- #
    return( pdfcanvas )

    
# ========================================================= #
# ===  merge__pdfFile                                   === #
# ========================================================= #

def merge__pdfFile( nParallel=1, inpFile=None, outFile="merged.pdf", erase=False ):

    # ------------------------------------------------- #
    # --- [1] arguments                             --- #
    # ------------------------------------------------- #
    if ( inpFile is None ): sys.exit( "[make__shimGuideMask.py] inpFile == ???" )

    # ------------------------------------------------- #
    # --- [2] preparation                           --- #
    # ------------------------------------------------- #
    inpFiles = glob.glob( inpFile )
    if   ( nParallel == 1 ):
        outFiles = [ outFile ]
    elif ( nParallel >= 2 ):
        outFiles = [ outFile.replace( ".pdf", "_{}.pdf".format( ik+1 ) ) for ik in range( nParallel ) ]
    readers  = [ pypdf.PdfReader( ifile ) for ifile in inpFiles ]
    pages    = [ apage for reader in readers for apage in reader.pages[:] ]
    writers  = [ pypdf.PdfWriter() for ofile in outFiles ] 
    
    # ------------------------------------------------- #
    # --- [2] merge pdf file into one               --- #
    # ------------------------------------------------- #
    page_set = [ [] for ik in range( nParallel ) ]
    for ik,apage in enumerate(pages):
        idx  = ik % nParallel
        ( writers[ idx ] ).add_page( apage )
    for writer,ofile in zip( writers, outFiles ):
        writer.write( ofile )
        print( "[make__shimGuideMask.py] merged into :: {} ".format( ofile ) )

    # ------------------------------------------------- #
    # --- [3] erase input files                     --- #
    # ------------------------------------------------- #
    if ( erase ):
        for inpFile in inpFiles:
            os.remove( inpFile )
        

    
# ========================================================= #
# === make__shimGuideMask_single_lampshade.py           === #
# ========================================================= #

def make__shimGuideMask_single_lampshade( pdfcanvas=None, \
                                          jsonFile=None, databaseFile=None, flagFile1=None, flagFile2=None, \
                                          action=None, z_polarity=None, eraseEachFile=True, silent=True, \
                                          outDir="pdf/", confFile="cnf/system_config.json", page_parity="odd" ):
    
    x_ , y_ , d_ , f_  = 0, 1, 2, 3
    x1_, y1_, x2_, y2_ = 0, 1, 2, 3
    m2mm               = 1.e+3

    # ------------------------------------------------- #
    # --- [1] arguments                             --- #
    # ------------------------------------------------- #
    if ( jsonFile is None ): sys.exit( "[make__shimGuideMask_single_lampshade.py] jsonFile == ???" )

    # ------------------------------------------------- #
    # --- [2] load settings                         --- #
    # ------------------------------------------------- #
    with open( jsonFile, "r" ) as f:
        info     = json.load( f  )
        settings = info["settings"]
        cards    = info["shape"]
        pagesize = np.array( settings["pagesize"] )
    with open( confFile, "r" ) as f:
        conf     = json.load( f )
    
    # ------------------------------------------------- #
    # --- [3] load hole file                        --- #
    # ------------------------------------------------- #
    import extract__holeinfo as ext
    database_ex  = ext.load__database   ( databaseFile=databaseFile, flagFile1=flagFile1, flagFile2=flagFile2 )
    holeinfo     = ext.extract__holeinfo( database=database_ex, trayName=settings["trayName"], \
                                          action=action, z_polarity=z_polarity )
    holes        = ( holeinfo[ ["x","y","d"] ].to_numpy() ) * m2mm
    holes[:,d_]  = holes[:,d_] + conf["Dhole.margin"]
    
    if ( settings["holeRotation"] != 0.0 ):
        ang2rad  = np.pi / 180.0
        cos, sin = np.cos( settings["holeRotation"]*ang2rad ), np.sin( settings["holeRotation"]*ang2rad )
        rotMat   = np.transpose( np.array( [ [ cos, -sin ], \
                                             [ sin,  cos ] ] ) )    # ( Rx )^T = x^T R^T
        xy_b     = holes[:,x_:y_+1]
        xy_r     = np.dot( xy_b, rotMat )
        holes[:,x_:y_+1] = np.copy( xy_r )

    # ------------------------------------------------- #
    # --- [4] divide bbox into several pages        --- #
    # ------------------------------------------------- #
    overall_width    = ( settings["bbox"][x2_] - settings["bbox"][x1_] )
    overall_height   = ( settings["bbox"][y2_] - settings["bbox"][y1_] )
    pagesize_actual  = pagesize[:] - 2.0*settings["overlap"]
    nPage_w          = math.ceil( overall_width  / pagesize_actual[x_] )
    nPage_h          = math.ceil( overall_height / pagesize_actual[y_] )

    # ------------------------------------------------- #
    # --- [5] centering                             --- #
    # ------------------------------------------------- #
    if ( conf["centering"] ):
        overall_width_   = nPage_w * pagesize_actual[x_]
        overall_height_  = nPage_h * pagesize_actual[y_]
        margin_w         = 0.5 * ( overall_width_  - overall_width  )
        margin_h         = 0.5 * ( overall_height_ - overall_height )
        margins          = np.array( [ (-1.0)*margin_w, (-1.0)*margin_h, \
                                       (+1.0)*margin_w, (+1.0)*margin_h ] )
        tray_bbox        = np.array( settings["bbox"] ) + margins
    else:
        tray_bbox        = np.copy ( settings["bbox"] )

    # ------------------------------------------------- #
    # --- [6] prepare page's origin points          --- #
    # ------------------------------------------------- #
    page_bbox  = np.zeros( (nPage_w,nPage_h,4) )
    pagesize_  = np.concatenate( [pagesize_actual,pagesize_actual] )
    tray_base  = np.concatenate( [tray_bbox[:2],tray_bbox[:2]] )
    overlap_wh = np.array( [ -settings["overlap"], -settings["overlap"], +settings["overlap"], +settings["overlap"] ] )
    for ik in range( nPage_w ):
        for jk in range( nPage_h ):
            page_bbox[ik,jk,:] = tray_base[:] + np.array( [ik,jk,ik+1,jk+1] ) * pagesize_[:] + overlap_wh
            
    # ------------------------------------------------- #
    # --- [7] page settings for pdf canvas          --- #
    # ------------------------------------------------- #
    for ik in range( nPage_w ):
        for jk in range( nPage_h ):
            if   ( page_parity == "odd"  ):
                pass
            elif ( page_parity == "even" ):
                pdfcanvas.translate( pagesizes.A4[0], 0.0 )
            pdfcanvas.setLineWidth( conf["linewidth"] )
            pdfcanvas = draw__trayFrame( pdfcanvas=pdfcanvas, \
                                         page_bbox=page_bbox[ik,jk,:], \
                                         cards=cards )
            if ( holes is not None ):
                pdfcanvas = draw__shimHole ( pdfcanvas=pdfcanvas, \
                                             page_bbox=page_bbox[ik,jk,:], \
                                             holes=holes )
            if ( conf["outframe"] ):
                pdfcanvas = draw__outFrame ( pdfcanvas=pdfcanvas, \
                                             pagesize=pagesize )



# ========================================================= #
# ===  make__shimGuideMask_multiple_lampshade           === #
# ========================================================= #
def make__shimGuideMask_multiple_lampshade( jsonFileBase=None, databaseFile=None, flagFile1=None, flagFile2=None, \
                                            action=None, z_polarity=None, eraseEachFile=True, silent=True, \
                                            outDir="pdf/", confFile="cnf/system_config.json", iTrayNums=[1,2] ):
    
    # ------------------------------------------------- #
    # --- [1] input settings                        --- #
    # ------------------------------------------------- #
    z_character  = { "+":"zUpper", "-":"zLower" }[z_polarity]
    outFileBase  = "{0}lamp_shade_{1[0]}and{1[1]}_{2}_{3}_".format( outDir, iTrayNums, action, z_character )
    outFile      = outFileBase + "merge.pdf"
    piecesize    = pagesizes.landscape( pagesizes.A3 )
    pdfcanvas    = canvas.Canvas( outFile, pagesize=piecesize )

    # ------------------------------------------------- #
    # --- [2] call make__shimGuideMask              --- #
    # ------------------------------------------------- #
    for ik,iTrayNum in enumerate(iTrayNums):
        page_parity = ( [ "odd", "even" ] )[ ik%2 ]
        jsonFile    = jsonFileBase.format( iTrayNum )
        make__shimGuideMask_single_lampshade( pdfcanvas=pdfcanvas, jsonFile=jsonFile, databaseFile=databaseFile, \
                                              flagFile1=flagFile1, flagFile2=flagFile2, \
                                              action=action, z_polarity=z_polarity, page_parity=page_parity )

    # ------------------------------------------------- #
    # --- [3] save in a file                        --- #
    # ------------------------------------------------- #
    pdfcanvas.showPage()
    pdfcanvas.save()
    print( "[make__shimGuideMask_multiple_lampshade] outFile :: {} ".format( outFile ) )


    
# ========================================================= #
# ===   Execution of Pragram                            === #
# ========================================================= #

if ( __name__=="__main__" ):
    # jsonFile = "dat/circularTray001.json"
    # jsonFile = "dat/fanTray001.json"
    # jsonFile = "dat/umbrella_typeA_001.json"
    # jsonFile = "dat/umbrella_typeB_001.json"
    # jsonFile = "dat/umbrella_typeC_001.json"
    # jsonFile = "dat/umbrella_typeD_001.json"
    # -- prefix -- #
    flagFile1    = "dat/before.01"
    flagFile2    = "dat/after.01"
    databaseFile = "cnf/shimbolt_mod.db"
    # -- parameter -- #
    jsonFileBase = "cnf/lamp_shade{}.json"
    # jsonFile     = "cnf/lamp_shade1.json"
    # jsonFile     = "cnf/sector1.json"
    action       = "add"
    z_polarity   = "+"
    # -- run -- #
    multi__shimGuideMask_lampshade( jsonFileBase=jsonFileBase, databaseFile=databaseFile, \
                                    flagFile1=flagFile1, flagFile2=flagFile2, action=action, z_polarity=z_polarity )
    # make__shimGuideMask_lampshade( jsonFile=jsonFile, databaseFile=databaseFile, \
    #                                flagFile1=flagFile1, flagFile2=flagFile2, action=action, z_polarity=z_polarity )
    
