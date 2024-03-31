import os, sys, math, json
import reportlab
import draw__shapes          as dsh
from reportlab.lib           import units
from reportlab.lib.pagesizes import A3, A0
from reportlab.pdfgen        import canvas


# ========================================================= #
# ===   Execution of Pragram                            === #
# ========================================================= #

if ( __name__=="__main__" ):
    
    # ------------------------------------------------- #
    # --- [1] ページ設定                            --- #
    # ------------------------------------------------- #
    pt_width, pt_height = A0
    orig_size           = ( pt_width, pt_height )
    linewidth           = 1.0e-3
    pt2inch, inch2mm    = 1.0 / 72.0, 25.4
    pt2mm               = pt2inch   * inch2mm
    mm_width            = pt_width  * pt2mm
    mm_height           = pt_height * pt2mm

    # ------------------------------------------------- #
    # --- [2] pdf ( 描画エリア: canvas ) の生成     --- #
    # ------------------------------------------------- #
    outFile             = "pdf/circularTray001.pdf"
    page_size           = ( mm_width, mm_height )
    pdfcanvas           = canvas.Canvas( outFile, pagesize=page_size )
    pdfcanvas.setLineWidth( linewidth )

    print( "\n" + " --- reportlab --- " + "\n" )
    print( "  page_size (pt) :: ( {0[0]:.3f}, {0[1]:.3f} )".format( orig_size ) )
    print( "  page_size (mm) :: ( {0[0]:.3f}, {0[1]:.3f} )".format( page_size ) )
    print()

    # ------------------------------------------------- #
    # --- [3] draw shapes                           --- #
    # ------------------------------------------------- #
    shpFile = "dat/circularTray001.json"
    with open( shpFile, "r" ) as f:
        info = json.load( f  )
    
    cards    = info["shape"]
    settings = info["settings"]
    print( cards )
    print( settings )
    # dsh.draw__shapes( pdfcanvas=pdfcanvas, cards=cards )

    # ------------------------------------------------- #
    # --- [4] showpage and save in a file           --- #
    # ------------------------------------------------- #
    pdfcanvas.showPage()
    pdfcanvas.save()
    print( "[basic_sample.py] outFile :: {} ".format( outFile ) )
