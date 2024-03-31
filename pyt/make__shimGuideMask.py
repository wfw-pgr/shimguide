import os, sys, math, json, glob, re
import reportlab
import pypdf
import numpy             as     np
import numpy.random
from reportlab.lib       import pagesizes
from reportlab.lib.units import mm
from reportlab.pdfgen    import canvas
from reportlab.pdfbase   import pdfmetrics, ttfonts

# ========================================================= #
# ===  draw trayFrame                                   === #
# ========================================================= #

def draw__trayFrame( pdfcanvas=None, page_bbox=None, cards=None, trayLabel=None ):

    x_, y_   = 0, 1
    r_, th_  = 0, 1
    s_, e_   = 0, 1   # start & end
    
    # ------------------------------------------------- #
    # --- [1] arguments                             --- #
    # ------------------------------------------------- #
    if ( pdfcanvas is None ): sys.exit( "[make__shimGuideMask.py] pdfcanvas == ???" )
    if ( page_bbox is None ): sys.exit( "[make__shimGuideMask.py] page_bbox == ???" )
    if ( cards     is None ): sys.exit( "[make__shimGuideMask.py] cards     == ???" )
    if ( trayLabel is None ): trayLabel = "trayLabel is not specified"
    
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
            
        elif ( val["shapeType"].lower() == "rectangular" ):
            centerpt = ( val["center"] - page_bbox_lb )*mm
            wh       = ( np.array( val["wh_length"] ) )*mm
            pdfcanvas.rect( centerpt[x_]-0.5*wh[x_], centerpt[y_]-0.5*wh[y_], wh[x_], wh[y_] )
            
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
            if ( "label.edges" in val ):
                stack = []
                for ik,edgeNum in enumerate( val["label.edges"] ):
                    fraction = val["label.fraction"][ik]
                    ie1,ie2  = edgeNum-1, edgeNum
                    xyM      = ( xynorm[ie1,:]*(1.0-fraction) + xynorm[ie2,:]*fraction )
                    xyD      =       xynorm[ie2,:] - xynorm[ie1,:]
                    l_angle  = np.arctan2( xyD[y_], xyD[x_] )
                    cos,sin  = np.cos( l_angle ), np.sin( l_angle )
                    W, L     = val["label.WL"]
                    labelbox = np.array( [ [ xyM[x_]-0.5*L*cos      , xyM[y_]-0.5*L*sin       ],
                                           [ xyM[x_]-0.5*L*cos-W*sin, xyM[y_]-0.5*L*sin+W*cos ],
                                           [ xyM[x_]+0.5*L*cos-W*sin, xyM[y_]+0.5*L*sin+W*cos ],
                                           [ xyM[x_]+0.5*L*cos      , xyM[y_]+0.5*L*sin       ] ] )
                    boxM     = np.average( labelbox, axis=0 )
                    stack += [ ( np.copy( labelbox ) )  ]
                    #### -- put character here -- ###
                    pdfcanvas.saveState()
                    pdfcanvas.translate( *boxM )
                    pdfcanvas.rotate( l_angle * 180.0/np.pi )
                    pdfcanvas.translate( *( -boxM ) )
                    pdfcanvas.drawCentredString( *boxM, trayLabel )
                    pdfcanvas.restoreState()
 
                stack = np.array( stack )
                for ik,edgeNum_ in enumerate( val["label.edges"] ):
                    edgeNum = 4*ik + edgeNum_
                    xynorm  = np.insert( xynorm, edgeNum, np.reshape( stack[ik,:,:], (4,2) ), axis=0 )
                    
            lines    = np.concatenate( [xynorm[:-1,:,np.newaxis],xynorm[1:,:,np.newaxis]], axis=2 )
            if   ( not( "linetype" in val ) ):
                val["linetype"] = "solid"
            if   ( val["linetype"] == "solid" ):
                for ik,pt in enumerate( lines ):
                    pdfcanvas.line  ( pt[x_,s_], pt[y_,s_], pt[x_,e_], pt[y_,e_] )
            elif ( val["linetype"] == "dashed" ):
                if ( not( "dashed.nDiv" in val ) ): val["dashed.nDiv"] = 20  # division of dashed line ( def.=20 )
                if ( not( "dashed.duty" in val ) ): val["dashed.duty"] = 0.5 # duty of dashed line     ( def.=0.5 )
                for ik,pt in enumerate( lines ):
                    dxy      = 0.5 * ( ( pt[:,e_] - pt[:,s_] ) / ( val["dashed.nDiv"] ) ) * val["dashed.duty"]
                    xc       = np.linspace( pt[x_,s_], pt[x_,e_], val["dashed.nDiv"]+1 )
                    yc       = np.linspace( pt[y_,s_], pt[y_,e_], val["dashed.nDiv"]+1 )
                    xc       = ( 0.5*( np.roll( xc, -1 ) + xc ) ) [:-1]  # middle point of the dashed lines
                    yc       = ( 0.5*( np.roll( yc, -1 ) + yc ) ) [:-1]
                    for il in range( val["dashed.nDiv"] ):
                        pdfcanvas.line( xc[il]-dxy[x_], yc[il]-dxy[y_], xc[il]+dxy[x_], yc[il]+dxy[y_] )
            else:
                print( "[make__shimGuideMask.py] unknown linetype ... {} ".format( val["linetype"] ) )
                sys.exit()

        
        # -- [2-6] xy-coordinate line case           -- #
        elif ( val["shapeType"].lower() == "polyline_inxy" ):
            ang2rad  = np.pi / 180.0
            points   = np.array( val["points_xy"] )
            xn, yn   = ( points[:,x_] - page_bbox_lb[x_] )*mm, ( points[:,y_] - page_bbox_lb[y_] )*mm
            xynorm   = np.concatenate( [xn[:,np.newaxis], yn[:,np.newaxis]], axis=1 )
            if ( "label.edges" in val ):
                stack = []
                for ik,edgeNum in enumerate( val["label.edges"] ):
                    fraction = val["label.fraction"][ik]
                    ie1,ie2  = edgeNum-1, edgeNum
                    xyM      = ( xynorm[ie1,:]*(1.0-fraction) + xynorm[ie2,:]*fraction )
                    xyD      =       xynorm[ie2,:] - xynorm[ie1,:]
                    l_angle  = np.arctan2( xyD[y_], xyD[x_] )
                    cos,sin  = np.cos( l_angle ), np.sin( l_angle )
                    W, L     = val["label.WL"]
                    labelbox = np.array( [ [ xyM[x_]-0.5*L*cos      , xyM[y_]-0.5*L*sin       ],
                                           [ xyM[x_]-0.5*L*cos-W*sin, xyM[y_]-0.5*L*sin+W*cos ],
                                           [ xyM[x_]+0.5*L*cos-W*sin, xyM[y_]+0.5*L*sin+W*cos ],
                                           [ xyM[x_]+0.5*L*cos      , xyM[y_]+0.5*L*sin       ] ] )
                    boxM     = np.average( labelbox, axis=0 )
                    stack   += [ ( np.copy( labelbox ) )  ]
                    #### -- put character here -- ###
                    pdfcanvas.saveState()
                    pdfcanvas.translate( *boxM )
                    pdfcanvas.rotate( l_angle * 180.0/np.pi )
                    pdfcanvas.translate( *( -boxM ) )
                    pdfcanvas.drawCentredString( *boxM, trayLabel )
                    pdfcanvas.restoreState()

                stack = np.array( stack )
                for ik,edgeNum_ in enumerate( val["label.edges"] ):
                    edgeNum = 4*ik + edgeNum_
                    xynorm  = np.insert( xynorm, edgeNum, np.reshape( stack[ik,:,:], (4,2) ), axis=0 )

            lines    = np.concatenate( [xynorm[:-1,:,np.newaxis],xynorm[1:,:,np.newaxis]], axis=2 )
            if   ( not( "linetype" in val ) ):
                val["linetype"] = "solid"
            if   ( val["linetype"] == "solid" ):
                for ik,pt in enumerate( lines ):
                    pdfcanvas.line  ( pt[x_,s_], pt[y_,s_], pt[x_,e_], pt[y_,e_] )
            elif ( val["linetype"] == "dashed" ):
                if ( not( "dashed.nDiv" in val ) ): val["dashed.nDiv"] = 20  # division of dashed line ( def.=20 )
                if ( not( "dashed.duty" in val ) ): val["dashed.duty"] = 0.5 # duty of dashed line     ( def.=0.5 )
                # for each line
                for ik,pt in enumerate( lines ):
                    dxy      = 0.5 * ( ( pt[:,e_] - pt[:,s_] ) / ( val["dashed.nDiv"] ) ) * val["dashed.duty"]
                    xc       = np.linspace( pt[x_,s_], pt[x_,e_], val["dashed.nDiv"]+1 )
                    yc       = np.linspace( pt[y_,s_], pt[y_,e_], val["dashed.nDiv"]+1 )
                    xc       = ( 0.5*( np.roll( xc, -1 ) + xc ) ) [:-1]  # middle point of the dashed lines
                    yc       = ( 0.5*( np.roll( yc, -1 ) + yc ) ) [:-1]
                    for il in range( val["dashed.nDiv"] ):
                        pdfcanvas.line( xc[il]-dxy[x_], yc[il]-dxy[y_], xc[il]+dxy[x_], yc[il]+dxy[y_] )
            else:
                print( "[make__shimGuideMask.py] unknown linetype ... {} ".format( val["linetype"] ) )
                sys.exit()

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
# ===  draw__divisionLine.py                            === #
# ========================================================= #

def draw__divisionLine( pdfcanvas=None, page_bbox=None, division_h_line=[], division_w_line=[], \
                        nDiv=20, duty=0.15 ):

    x_, y_   = 0, 1
    r_, th_  = 0, 1
    s_, e_   = 0, 1   # start & end

    # ------------------------------------------------- #
    # --- [1] arguments                             --- #
    # ------------------------------------------------- #
    if ( pdfcanvas is None ): sys.exit( "[make__shimGuideMask.py] pdfcanvas == ???" )
    if ( page_bbox is None ): sys.exit( "[make__shimGuideMask.py] page_bbox == ???" )

    # ------------------------------------------------- #
    # --- [2] draw lines   (w)                      --- #
    # ------------------------------------------------- #
    for wpos in division_w_line:
        pt       = np.array( [ [ wpos         - page_bbox[0], wpos         - page_bbox[0] ],\
                               [ page_bbox[1] - page_bbox[1], page_bbox[3] - page_bbox[1] ] ] ) * mm
        yl       = pt[y_,e_] - pt[y_,s_]
        pt[y_,:] = pt[y_,:] + np.array( [ -0.1*yl, +0.1*yl ] )
        dxy      = 0.5 * ( ( pt[:,e_] - pt[:,s_] ) / ( nDiv ) ) * duty
        xc       = np.linspace( pt[x_,s_], pt[x_,e_], nDiv+1 )
        yc       = np.linspace( pt[y_,s_], pt[y_,e_], nDiv+1 )
        xc       = ( 0.5*( np.roll( xc, -1 ) + xc ) ) [:-1]  # middle point of the dashed lines
        yc       = ( 0.5*( np.roll( yc, -1 ) + yc ) ) [:-1]
        dev      = ( yl / nDiv ) * np.random.uniform()
        yc       = yc + dev
        for il in range( nDiv ):
            pdfcanvas.line( xc[il]-dxy[x_], yc[il]-dxy[y_], xc[il]+dxy[x_], yc[il]+dxy[y_] )

    # ------------------------------------------------- #
    # --- [3] draw lines   (h)                      --- #
    # ------------------------------------------------- #
    for hpos in division_h_line:
        pt       = np.array( [ [ page_bbox[0] - page_bbox[0], page_bbox[2] - page_bbox[0] ],\
                               [ hpos         - page_bbox[1], hpos         - page_bbox[1] ] ] ) * mm
        xl       = pt[x_,e_] - pt[x_,s_]
        pt[x_,:] = pt[x_,:] + np.array( [ -0.1*xl, +0.1*xl ] )
        dxy      = 0.5 * ( ( pt[:,e_] - pt[:,s_] ) / ( nDiv ) ) * duty
        xc       = np.linspace( pt[x_,s_], pt[x_,e_], nDiv+1 )
        yc       = np.linspace( pt[y_,s_], pt[y_,e_], nDiv+1 )
        xc       = ( 0.5*( np.roll( xc, -1 ) + xc ) ) [:-1]  # middle point of the dashed lines
        yc       = ( 0.5*( np.roll( yc, -1 ) + yc ) ) [:-1]
        dev      = ( xl / nDiv ) * np.random.uniform()
        xc       = xc + dev
        for il in range( nDiv ):
            pdfcanvas.line( xc[il]-dxy[x_], yc[il]-dxy[y_], xc[il]+dxy[x_], yc[il]+dxy[y_] )

    # ------------------------------------------------- #
    # --- [4] return pdf's canvas                   --- #
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
        print( "[make__shimGuideMask.py] outFile :: {} ".format( ofile ) )

    # ------------------------------------------------- #
    # --- [3] erase input files                     --- #
    # ------------------------------------------------- #
    if ( erase ):
        for inpFile in inpFiles:
            os.remove( inpFile )
        

# ========================================================= #
# === make__shimGuideMask.py                            === #
# ========================================================= #

def make__shimGuideMask( jsonFile=None, databaseFile=None, flagFile1=None, flagFile2=None, \
                         action=None, z_polarity=None, eraseEachFile=True, silent=True, outDir="pdf/", \
                         confFile="cnf/system_config.json" ):

    x_ , y_ , d_ , f_  = 0, 1, 2, 3
    x1_, y1_, x2_, y2_ = 0, 1, 2, 3
    m2mm               = 1.e+3

    # ------------------------------------------------- #
    # --- [1] arguments                             --- #
    # ------------------------------------------------- #
    if ( jsonFile is None ): sys.exit( "[make__shimGuideMask.py] jsonFile == ???" )

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

    division_w_line = np.array( [ tray_bbox[x_] + (ik)*pagesize_actual[x_] for ik in range( 1,nPage_w ) ] )
    division_h_line = np.array( [ tray_bbox[y_] + (ik)*pagesize_actual[y_] for ik in range( 1,nPage_h ) ] )
    
    # ------------------------------------------------- #
    # --- [7] page settings for pdf canvas          --- #
    # ------------------------------------------------- #
    z_character  = { "+":"U", "-":"L" }[z_polarity]
    a_character  = { "add":"A", "remove":"R" }[action]
    outFileBase  = "{0}{1}_{2}_".format( outDir, settings["trayName"], z_character )
    outFileEach  = outFileBase + "each_{0:02}_{1:02}.pdf"
    for ik in range( nPage_w ):
        for jk in range( nPage_h ):
            if ( ( nPage_w == 1 ) and ( nPage_h == 1 ) ):
                trayLabel = "{0}-{1}-{2}".format( settings["trayName"].replace( "_", "-" ), action, z_character )
            else:
                trayLabel = "{0}-{1}-{2}-X{3}/{4}-Y{5}/{6}".format( settings["trayName"].replace( "_", "-" ), \
                                                                    action, z_character, \
                                                                    ik+1, nPage_w, jk+1, nPage_h )
            outFile   = outFileEach.format( ik+1,jk+1 )
            pdfcanvas = canvas.Canvas( outFile, pagesize=pagesize*mm )
            pdfcanvas.setLineWidth( conf["linewidth"] )
            if ( conf["label.font.useTTF"] ):
                pdfmetrics.registerFont( ttfonts.TTFont( conf["label.font.name"], conf["label.font.path"] ) )
            pdfcanvas.setFont( conf["label.font.name"], conf["label.font.size"] )
            pdfcanvas = draw__trayFrame( pdfcanvas=pdfcanvas, \
                                         page_bbox=page_bbox[ik,jk,:], \
                                         cards=cards, trayLabel=trayLabel )
            if ( holes is not None ):
                pdfcanvas = draw__shimHole ( pdfcanvas=pdfcanvas, \
                                             page_bbox=page_bbox[ik,jk,:], \
                                             holes=holes )
            if ( conf["division.line.sw"] ):
                pdfcanvas = draw__divisionLine( pdfcanvas=pdfcanvas, page_bbox=page_bbox[ik,jk,:],
                                                division_w_line=division_w_line, division_h_line=division_h_line, \
                                                nDiv=conf["division.line.nDiv"], duty=conf["division.line.duty"] )
                
            if ( conf["outframe"] ):
                pdfcanvas = draw__outFrame ( pdfcanvas=pdfcanvas, \
                                             pagesize=pagesize )
            pdfcanvas.showPage()
            pdfcanvas.save()
            if ( not(silent) ):
                print( "[make__shimGuideMask.py] outFile :: {} ".format( outFile ) )

    # ------------------------------------------------- #
    # --- [8] merge pdf file                        --- #
    # ------------------------------------------------- #
    inpFile   = outFileBase + "each_*.pdf"
    outFile   = outFileBase + "merged.pdf"
    # nParallel = conf["nParallel"]
    nParallel = 1
    merge__pdfFile( nParallel=nParallel, inpFile=inpFile, outFile=outFile, erase=eraseEachFile )


    
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
            z_character  = { "+":"zUpper", "-":"zLower" }[z_polarity]
            trayLabel    = "{0}-{1}-{2}".format( settings["trayName"].replace("_","-"), action, z_character )
            pdfcanvas    = draw__trayFrame( pdfcanvas=pdfcanvas, \
                                            page_bbox=page_bbox[ik,jk,:], \
                                            cards=cards, trayLabel=trayLabel )
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
def make__shimGuideMask_multiple_lampshade( jsonFile1=None, jsonFile2=None, databaseFile=None, \
                                            flagFile1=None, flagFile2=None, confFile="cnf/system_config.json", \
                                            action=None, z_polarity=None, eraseEachFile=True, silent=True, \
                                            outDir="pdf/" ):
    
    # ------------------------------------------------- #
    # --- [1] input settings                        --- #
    # ------------------------------------------------- #
    iTray1       = ( re.match( "cnf/lamp_shade([0-9]+)\.json", jsonFile1 ) ).group(1)
    iTray2       = ( re.match( "cnf/lamp_shade([0-9]+)\.json", jsonFile2 ) ).group(1)
    z_character  = { "+":"zUpper", "-":"zLower" }[z_polarity]
    outFileBase  = "{0}lamp_shade_{1}and{2}_{3}_{4}_".format( outDir, iTray1, iTray2, action, z_character )
    outFile      = outFileBase + "merged.pdf"
    piecesize    = pagesizes.landscape( pagesizes.A3 )
    pdfcanvas    = canvas.Canvas( outFile, pagesize=piecesize )
    with open( confFile, "r" ) as f:
        conf     = json.load( f )
    pdfcanvas.setLineWidth( conf["linewidth"] )
    if ( conf["label.font.useTTF"] ):
        pdfmetrics.registerFont( ttfonts.TTFont( conf["label.font.name"], conf["label.font.path"] ) )
    pdfcanvas.setFont( conf["label.font.name"], conf["label.font.size"] )

    # ------------------------------------------------- #
    # --- [2] call make__shimGuideMask              --- #
    # ------------------------------------------------- #
    make__shimGuideMask_single_lampshade( pdfcanvas=pdfcanvas, jsonFile=jsonFile1, databaseFile=databaseFile, \
                                          flagFile1=flagFile1, flagFile2=flagFile2, \
                                          action=action, z_polarity=z_polarity, page_parity="odd"  )
    make__shimGuideMask_single_lampshade( pdfcanvas=pdfcanvas, jsonFile=jsonFile2, databaseFile=databaseFile, \
                                          flagFile1=flagFile1, flagFile2=flagFile2, \
                                          action=action, z_polarity=z_polarity, page_parity="even" )

    # ------------------------------------------------- #
    # --- [3] save in a file                        --- #
    # ------------------------------------------------- #
    pdfcanvas.showPage()
    pdfcanvas.save()
    print( "[make__shimGuideMask.py] outFile :: {} ".format( outFile ) )

    
# ========================================================= #
# ===   Execution of Pragram                            === #
# ========================================================= #

if ( __name__=="__main__" ):
    # -- prefix -- #
    flagFile1    = "dat/before.01"
    flagFile2    = "dat/after.01"
    databaseFile = "cnf/shimbolt_mod.db"
    # -- parameter -- #
    jsonFile     = "cnf/disc.json"
    # jsonFile     = "cnf/sector1.json"
    # jsonFile     = "cnf/lamp_shade1.json"
    # jsonFile     = "cnf/adjacent.json"
    action       = "add"
    z_polarity   = "+"
    # -- run -- #
    multi_lampshade_mode = False
    if ( multi_lampshade_mode ):
        print( "multi_lampshade_mode is on...." )
        jsonFile1 = "cnf/lamp_shade1.json"
        jsonFile2 = "cnf/lamp_shade2.json"
        print( " jsonFile1 :: {}".format( jsonFile1 ) )
        print( " jsonFile2 :: {}".format( jsonFile2 ) )
        make__shimGuideMask_multiple_lampshade( jsonFile1=jsonFile1, jsonFile2=jsonFile2, \
                                                flagFile1=flagFile1, flagFile2=flagFile2, \
                                                databaseFile=databaseFile, \
                                                action=action, z_polarity=z_polarity )
    else:
        make__shimGuideMask( jsonFile=jsonFile, databaseFile=databaseFile, \
                             flagFile1=flagFile1, flagFile2=flagFile2, \
                             action=action, z_polarity=z_polarity )
        
