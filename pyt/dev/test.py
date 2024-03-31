import os, sys, math, json, glob
import reportlab
import pypdf
import numpy                 as np
from reportlab.lib           import pagesizes
from reportlab.lib.units     import mm
from reportlab.pdfgen        import canvas


# ========================================================= #
# ===  draw trayFrame                                   === #
# ========================================================= #

def draw__trayFrame( pdfcanvas=None, page_bbox=None, cards=None ):

    x_, y_   = 0, 1
    r_, th_  = 0, 1    
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
        if ( val["shapeType"].lower() == "line"   ):
            startpt = ( val["start"] - page_bbox_lb )*mm
            endpt   = ( val["end"]   - page_bbox_lb )*mm
            pdfcanvas.line  ( startpt[x_], startpt[y_], endpt[x_], endpt[y_] )
        # -- [2-2] circle case                       -- #
        if ( val["shapeType"].lower() == "circle" ):
            centerpt = ( val["center"] - page_bbox_lb )*mm
            radius   = ( val["radius"] )*mm
            pdfcanvas.circle( centerpt[x_], centerpt[y_], radius )
            
        # -- [2-3] arc case                          -- #
        if ( val["shapeType"].lower() == "arc"    ):
            centerpt = val["center"] - page_bbox_lb
            x1, y1   = ( centerpt[x_]-val["radius"] )*mm, ( centerpt[y_]-val["radius"] )*mm
            x2, y2   = ( centerpt[x_]+val["radius"] )*mm, ( centerpt[y_]+val["radius"] )*mm
            a1, a2   = val["angle1"], val["angle2"] - val["angle1"]
            pdfcanvas.arc( x1, y1, x2, y2, a1, a2 )

        # -- [2-4] radial line case                  -- #
        if ( val["shapeType"].lower() == "radialline"   ):
            ang2rad  = np.pi / 180.0
            cos, sin = np.cos( val["angle"]*ang2rad ), np.sin( val["angle"]*ang2rad )
            startpt  = ( np.array( [ val["r1"]*cos, val["r1"]*sin ] )  - page_bbox_lb )*mm
            endpt    = ( np.array( [ val["r2"]*cos, val["r2"]*sin ] )  - page_bbox_lb )*mm
            pdfcanvas.line  ( startpt[x_], startpt[y_], endpt[x_], endpt[y_] )

        # -- [2-4] radial line case                  -- #
        if ( val["shapeType"].lower() == "polyline_inrt" ):
            s_,e_    = 0, 1              # start & end
            ang2rad  = np.pi / 180.0
            center   = np.array( val["center"]    )
            points   = np.array( val["points_rt"] )
            cos,sin  = np.cos( points[:,th_]*ang2rad ), np.sin( points[:,th_]*ang2rad )
            xp, yp   = points[:,r_]*cos+center[x_], points[:,r_]*sin+center[y_]
            xn, yn   = ( xp[:] - page_bbox_lb[x_] )*mm, ( yp[:] - page_bbox_lb[y_] )*mm
            xynorm   = np.concatenate( [xn[:,np.newaxis], yn[:,np.newaxis]], axis=1 )
            lines    = np.concatenate( [xynorm[:-1,:,np.newaxis],xynorm[1:,:,np.newaxis]], axis=2 )
            for ik,pt in enumerate( lines ):
                pdfcanvas.line  ( pt[x_,s_], pt[y_,s_], pt[x_,e_], pt[y_,e_] )

    # ------------------------------------------------- #
    # --- [3] return pdf's canvas                   --- #
    # ------------------------------------------------- #
    return( pdfcanvas )


# ========================================================= #
# ===  draw shim hole                                   === #
# ========================================================= #

def draw__shimHole( pdfcanvas=None, page_bbox=None, holes=None ):

    x_, y_, r_ = 0, 1, 2
    
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
        pdfcanvas.circle( xyr[x_], xyr[y_], xyr[r_] )
            
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
    x1, y1 = 1.0*mm, 1.0*mm
    Lx ,Ly = ( pagesize[x_]-2.0 )*mm, ( pagesize[y_]-2.0 )*mm
    pdfcanvas.rect( x1, y1, Lx, Ly )
            
    # ------------------------------------------------- #
    # --- [3] return pdf's canvas                   --- #
    # ------------------------------------------------- #
    return( pdfcanvas )

    
# ========================================================= #
# ===  merge__pdfFile                                   === #
# ========================================================= #

def merge__pdfFile( nParallel=1, inpFile=None, outFile="merged.pdf" ):

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
        

# ========================================================= #
# === make__shimGuideMask.py                            === #
# ========================================================= #

def make__shimGuideMask( jsonFile=None ):

    x_ , y_ , r_ , f_  = 0, 1, 2, 3
    x1_, y1_, x2_, y2_ = 0, 1, 2, 3

    # ------------------------------------------------- #
    # --- [1] arguments                             --- #
    # ------------------------------------------------- #
    if ( jsonFile is None ): sys.exit( "[make__shimGuideMask.py] jsonFile == ???" )

    # ------------------------------------------------- #
    # --- [2] load settings                         --- #
    # ------------------------------------------------- #
    with open( jsonFile, "r" ) as f:
        info = json.load( f  )
    cards    = info["shape"]
    settings = info["settings"]
    pagesize = np.array( settings["pagesize"] )

    # ------------------------------------------------- #
    # --- [3] load hole file                        --- #
    # ------------------------------------------------- #
    if ( len( settings["holeFile"] ) > 0 ):
        with open( settings["holeFile"], "r" ) as f:
            holes_ = np.loadtxt( f )
        flags = np.array( holes_[:,f_], dtype=bool )
        holes = ( holes_[ flags ] )[:,0:3]
    else:
        holes = None
        
    # ------------------------------------------------- #
    # --- [4] divide bbox into several pages        --- #
    # ------------------------------------------------- #
    overall_width    = ( settings["bbox"][x2_] - settings["bbox"][x1_] )
    overall_height   = ( settings["bbox"][y2_] - settings["bbox"][y1_] )
    nPage_w          = math.ceil( overall_width  / pagesize[x_] )
    nPage_h          = math.ceil( overall_height / pagesize[y_] )
    # if ( not( nPage_w.is_integer() ) ): nPage_w = math.ceil( nPage_w )
    # if ( not( nPage_h.is_integer() ) ): nPage_h = math.ceil( nPage_h )

    # ------------------------------------------------- #
    # --- [5] centering                             --- #
    # ------------------------------------------------- #
    if ( settings["centering"] ):
        overall_width_   = nPage_w * pagesize[x_]
        overall_height_  = nPage_h * pagesize[y_]
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
    page_bbox = np.zeros( (nPage_w,nPage_h,4) )
    pagesize_ = np.concatenate( [pagesize,pagesize] )
    tray_base = np.concatenate( [tray_bbox[:2],tray_bbox[:2]] )
    for ik in range( nPage_w ):
        for jk in range( nPage_h ):
            page_bbox[ik,jk,:] = tray_base[:] + np.array( [ik,jk,ik+1,jk+1] ) * pagesize_[:]
            
    # ------------------------------------------------- #
    # --- [7] page settings for pdf canvas          --- #
    # ------------------------------------------------- #
    outFileBase  = (settings["outFile"]).replace( ".pdf", "_{0:02}_{1:02}.pdf" )
    canvas_list  = []
    for ik in range( nPage_w ):
        for jk in range( nPage_h ):
            outFile            = outFileBase.format( ik+1,jk+1 )
            pdfcanvas = canvas.Canvas( outFile, pagesize=pagesizes.A3 )
            pdfcanvas.setLineWidth( settings["linewidth"] )
            pdfcanvas = draw__trayFrame( pdfcanvas=pdfcanvas, \
                                         page_bbox=page_bbox[ik,jk,:], \
                                         cards=cards )
            if ( holes is not None ):
                pdfcanvas = draw__shimHole ( pdfcanvas=pdfcanvas, \
                                             page_bbox=page_bbox[ik,jk,:], \
                                             holes=holes )
            if ( settings["outframe"] ):
                pdfcanvas = draw__outFrame ( pdfcanvas=pdfcanvas, \
                                             pagesize=pagesize )
            pdfcanvas.showPage()
            pdfcanvas.save()
            print( "[make__shimGuideMask.py] outFile :: {} ".format( outFile ) )

    # ------------------------------------------------- #
    # --- [8] merge pdf file                        --- #
    # ------------------------------------------------- #
    inpFile   = settings["outFile"].replace( ".pdf", "_*.pdf" )
    merge__pdfFile( nParallel=settings["nParallel"], inpFile=inpFile, outFile=settings["mergeFile"] )



# ========================================================= #
# ===   Execution of Pragram                            === #
# ========================================================= #

if ( __name__=="__main__" ):
    
    # jsonFile            = "dat/circularTray001.json"
    # jsonFile            = "dat/fanTray001.json"
    jsonFile            = "dat/test001.json"
    make__shimGuideMask( jsonFile=jsonFile )
