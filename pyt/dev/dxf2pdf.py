import ezdxf
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen        import canvas

# DXFファイルを読み込む
inpFile = "dxf/dxf_test.dxf"
doc     = ezdxf.readfile( inpFile )

# Paperspaceを取得
msp = doc.modelspace()

# PDFドキュメントを作成
outFile = "pdf/dxf_test.pdf"
c = canvas.Canvas( outFile, pagesize=A4 )

# Paperspace内の図形を描画
for entity in msp.query("Layout1"):  # Paperspace内のすべてのエンティティを取得
    if entity.dxftype() == "LINE":
        # 線分を描画
        start_point = (entity.dxf.start.x, entity.dxf.start.y)
        end_point = (entity.dxf.end.x, entity.dxf.end.y)
        c.line(*start_point, *end_point)
    elif entity.dxftype() == "CIRCLE":
        # 円を描画
        center = (entity.dxf.center.x, entity.dxf.center.y)
        radius = entity.dxf.radius
        c.circle(center[0], center[1], radius)

# ページを保存
c.save()
