import ezdxf
import os, sys
import numpy as np
from   ezdxf import bbox
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen        import canvas

# -- coding index -- #
w_, h_     = 0, 1

# DXFファイルを読み込む
inpFile = "dxf/dxf_test_02.dxf"
doc     = ezdxf.readfile( inpFile )

# Paperspaceを取得
msp     = doc.modelspace()

# modelspaceのbboxを取得
bb         = ezdxf.bbox.extents( msp, cache=ezdxf.bbox.Cache() )
msp_width  = bb.extmax[w_] - bb.extmin[w_]
msp_height = bb.extmax[h_] - bb.extmin[h_]
msp_center = np.array( [ float( val ) for val in bb.center ] )
extmin     = np.array( [ float( val ) for val in bb.extmin ] )
extmax     = np.array( [ float( val ) for val in bb.extmax ] )
print()
print( "  modelspace_extmin :: ( {0[0]:.3f}, {0[1]:.3f} )"  .format( extmin     ) )
print( "  modelspace_extmax :: ( {0[0]:.3f}, {0[1]:.3f} )"  .format( extmax     ) )
print( "  modelspace_width  :: {:.3f}"                      .format( msp_width  ) )
print( "  modelspace_height :: {:.3f}"                      .format( msp_height ) )
print( "  modelspace_center :: ( {0[0]:.3f}, {0[1]:.3f} ) " .format( msp_center ) )
print()

# paperspaceのbboxを取得

# modelspaceのbboxを取得
lo         = doc.layout()
vp_list    = lo.viewports()
vp         = vp_list[0]

print( "vp     :: ", vp            )
print( "width  :: ", vp.name  )
print( "center :: ", vp.dxf.center )
print( "view_center :: ", vp.dxf.view_center_point )
print( "view_limit  :: ", vp.get_modelspace_limits() )

print( "width  :: ", vp.dxf.width  )
print( "height :: ", vp.dxf.height )
print( "extmin :: ", vp.dxf.lower_left )
print( "extmax :: ", vp.dxf.upper_right )

# sys.exit()

# msp_width  = bb.extmax[w_] - bb.extmin[w_]
# msp_height = bb.extmax[h_] - bb.extmin[h_]
# msp_center = np.array( [ float( val ) for val in bb.center ] )
# extmin     = np.array( [ float( val ) for val in bb.extmin ] )
# extmax     = np.array( [ float( val ) for val in bb.extmax ] )
# print()
# print( "  modelspace_extmin :: ( {0[0]:.3f}, {0[1]:.3f} )"  .format( extmin     ) )
# print( "  modelspace_extmax :: ( {0[0]:.3f}, {0[1]:.3f} )"  .format( extmax     ) )
# print( "  modelspace_width  :: {:.3f}"                      .format( msp_width  ) )
# print( "  modelspace_height :: {:.3f}"                      .format( msp_height ) )
# print( "  modelspace_center :: ( {0[0]:.3f}, {0[1]:.3f} ) " .format( msp_center ) )
# print()

# PDFドキュメントを作成
outFile = "pdf/dxf_test.pdf"
c       = canvas.Canvas( outFile, pagesize=A4 )

# sys.exit()


# print( msp.query("Layout1") )

# for entity in msp.query("Layout1"):  # Paperspace内のすべてのエンティティを取得
#     print( entity )
#     if entity.dxftype() == "LINE":
#         # 線分を描画
#         start_point = (entity.dxf.start.x, entity.dxf.start.y)
#         end_point = (entity.dxf.end.x, entity.dxf.end.y)
#         c.line(*start_point, *end_point)
#     elif entity.dxftype() == "CIRCLE":
#         # 円を描画
#         center = (entity.dxf.center.x, entity.dxf.center.y)
#         radius = entity.dxf.radius
#         c.circle(center[0], center[1], radius)

# ページを保存
c.save()
