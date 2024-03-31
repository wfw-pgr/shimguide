import ezdxf
import os, sys
import numpy as np
from   ezdxf import bbox
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen        import canvas

# DXFファイルを読み込む
inpFile1 = "dxf/dxf_test_01.dxf"
inpFile2 = "dxf/dxf_test_02.dxf"
doc1     = ezdxf.readfile( inpFile1 )
doc2     = ezdxf.readfile( inpFile2 )

# Paperspaceを取得
msp1     = doc1.modelspace()
msp2     = doc2.modelspace()

# layout
lo1      = doc1.layout()
lo2      = doc2.layout()

# viewport
vp1      = lo1.viewports()[0]
vp2      = lo2.viewports()[0]

print( vp1.clipping_rect() )
print( vp2.clipping_rect() )

for ent in vp1:
    print( ent )
