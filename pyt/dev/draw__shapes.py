import math
import reportlab
from reportlab.lib           import units
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen        import canvas


# ========================================================= #
# ===  draw__shapes.py                                  === #
# ========================================================= #

def draw__shapes( pdfcanvas=None, cards=None, linewidth=1.e-3 ):

    # ------------------------------------------------- #
    # --- [0] preparation & description             --- #
    # ------------------------------------------------- #
    #  *
    #  * cards     :: dict of dict == { "line01": { "start": [0,0], "end":[1,1] } } etc.
    #  * pdfcanvas :: canvas.canvas class of reportlab.
    #  *
    # ------------------------------------------------- #
    #  * parameters
    #  *
    x_, y_, z_ = 0, 1, 2
    # ------------------------------------------------- #
    
    
    # ------------------------------------------------- #
    # --- [1] arguments                             --- #
    # ------------------------------------------------- #
    if ( cards     is None ): sys.exit( "[draw__shapes.py] cards  == ???" )
    if ( pdfcanvas is None ): sys.exit( "[draw__shapes.py] pdfcanvas == ???" )
    pdfcanvas.setLineWidth( linewidth )
    
    # ------------------------------------------------- #
    # --- [2] draw shapes                           --- #
    # ------------------------------------------------- #
    for key, val in cards.items():
        print( key )
        # -- [2-1] line case                         -- #
        if ( val["shapeType"].lower() == "line"   ):
            pdfcanvas.line  ( val["start"][x_], val["start"][y_], 
                              val["end"]  [x_], val["end"]  [y_] )
        # -- [2-2] circle case                       -- #
        if ( val["shapeType"].lower() == "circle" ):
            pdfcanvas.circle( val["center"][x_], val["center"][y_], val["radius"] )
            
        # -- [2-3] arc case                          -- #
        if ( val["shapeType"].lower() == "arc"    ):
            x1, y1 = val["center"][x_]-val["radius"], val["center"][y_]-val["radius"]
            x2, y2 = val["center"][x_]+val["radius"], val["center"][y_]+val["radius"]
            a1, a2 = val["angle1"], val["angle2"] - val["angle1"]
            pdfcanvas.arc( x1, y1, x2, y2, a1, a2 )
    return()



# ========================================================= #
# ===   Execution of Pragram                            === #
# ========================================================= #

if ( __name__=="__main__" ):
    

    # ------------------------------------------------- #
    # --- [1] ページ設定                            --- #
    # ------------------------------------------------- #
    pt_width, pt_height = A4
    orig_size           = ( pt_width, pt_height )
    linewidth           = 1.0e-3
    pt2inch, inch2mm    = 1.0 / 72.0, 25.4
    pt2mm               = pt2inch   * inch2mm
    mm_width            = pt_width  * pt2mm
    mm_height           = pt_height * pt2mm

    # ------------------------------------------------- #
    # --- [2] pdf ( 描画エリア: canvas ) の生成     --- #
    # ------------------------------------------------- #
    outFile             = "pdf/example.pdf"
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
    cards = { "line01"  : { "shapeType":"line", "start":[0.0,0.0], "end":[100,100] }, \
              "circle01": { "shapeType":"circle", "center":[50.0,50.0], "radius":20, }, \
              "arc01"   : { "shapeType":"arc" , "center":[100.,100.] , "radius":50, \
                            "angle1":0.0, "angle2":135.0 }, \
    }
    draw__shapes( pdfcanvas=pdfcanvas, cards=cards )

    # ------------------------------------------------- #
    # --- [4] showpage and save in a file           --- #
    # ------------------------------------------------- #
    pdfcanvas.showPage()
    pdfcanvas.save()
    print( "[basic_sample.py] outFile :: {} ".format( outFile ) )
