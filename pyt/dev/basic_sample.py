import math
import reportlab
from reportlab.lib           import units
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen        import canvas

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
c                   = canvas.Canvas( outFile, pagesize=page_size )
c.setLineWidth( linewidth )

print( "\n" + " --- reportlab --- " + "\n" )
print( "  page_size (pt) :: ( {0[0]:.3f}, {0[1]:.3f} )".format( orig_size ) )
print( "  page_size (mm) :: ( {0[0]:.3f}, {0[1]:.3f} )".format( page_size ) )
print()

# ------------------------------------------------- #
# --- [3] 中心位置の取得                        --- #
# ------------------------------------------------- #
center_x = mm_width  / 2
center_y = mm_height / 2

# ------------------------------------------------- #
# --- [4] 矩形の描画  (枠)                      --- #
# ------------------------------------------------- #
margin   = 10.0
wRect    = mm_width  - 2.0*margin
hRect    = mm_height - 2.0*margin
xRect    = center_x  - 0.5*wRect
yRect    = center_y  - 0.5*hRect
c.rect( xRect, yRect, wRect, hRect )

# ------------------------------------------------- #
# --- [5] 円弧 - 形状の描画                     --- #
# ------------------------------------------------- #
radius1 = 50.0
radius2 = 150.0
angle1  = 0.0
angle2  = 45.0
c.arc( center_x-radius1, center_y-radius1, center_x+radius1, center_y+radius1, angle1, angle2 )
c.arc( center_x-radius2, center_y-radius2, center_x+radius2, center_y+radius2, angle1, angle2 )

# ------------------------------------------------- #
# --- [6] 円 - 形状の描画                       --- #
# ------------------------------------------------- #
radius3 = 8.0 * 0.5
c.circle( center_x, center_y, radius3 )

# ページを保存
c.showPage()
c.save()
print( "[basic_sample.py] outFile :: {} ".format( outFile ) )
