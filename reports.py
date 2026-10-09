from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image


def make_report(folder: Path, result: dict):
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(str(folder/'report.pdf'), pagesize=A4,
                            topMargin=34, bottomMargin=34, leftMargin=38, rightMargin=38)
    story = [Paragraph('AUTOINSPECT / Inspection report', styles['Title']),
             Paragraph('Visual quality intelligence | PatchCore baseline', styles['Normal']), Spacer(1,18)]
    rows = [['Inspection', result['id']], ['Timestamp (UTC)', result['created_at']],
            ['Source image', Paragraph(escape(result['image_name']), styles['Normal'])],
            ['Model', result['model']], ['Decision', result['decision']],
            ['Anomaly score', f"{result['normalized_anomaly_score']:.6f} (threshold 0.500000)"],
            ['Processing time', f"{result['duration_ms'] / 1000:.2f} seconds"]]
    table = Table(rows, colWidths=[135, 380])
    table.setStyle(TableStyle([('BACKGROUND',(0,0),(0,-1),colors.HexColor('#edf3f7')),
                              ('TEXTCOLOR',(0,0),(-1,-1),colors.HexColor('#142b3b')),
                              ('VALIGN',(0,0),(-1,-1),'TOP'),('BOTTOMPADDING',(0,0),(-1,-1),8),
                              ('TOPPADDING',(0,0),(-1,-1),8)]))
    story.extend([table,Spacer(1,16)])
    pictures=[]
    from PIL import Image as PILImage
    for name in ('input.png','heatmap.png'):
        with PILImage.open(folder/name) as im:
            w,h=im.size
        scale=min(245/w,235/h)
        pictures.append(Image(str(folder/name),width=w*scale,height=h*scale))
    story.extend([Table([['Uploaded component','Anomaly overlay'],pictures],colWidths=[257,258]),
                  Spacer(1,18),Paragraph('Interpretation',styles['Heading2']),
                  Paragraph(escape(result['status'])+'. Red regions show higher anomaly response. The score is not a probability or a measurement of defect severity.',styles['Normal']),
                  Spacer(1,10),Paragraph('Model scope',styles['Heading2']),
                  Paragraph('Trained on MVTec AD metal_nut images. No defect classification or automotive acceptance validation. A known scratch sample is missed by this baseline. Human review and representative validation are required for production decisions.',styles['Normal']),
                  Spacer(1,10),Paragraph('Attribution: MVTec AD (Bergmann et al.), CC BY-NC-SA 4.0. Educational, noncommercial prototype.',styles['Normal'])])
    doc.build(story)
