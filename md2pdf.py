from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import re


# Registrieren Sie eine Unicode-fähige Schriftart (optional, falls die Standardschriftart nicht ausreicht)
# pdfmetrics.registerFont(TTFont('DejaVu', 'DejaVuSans.ttf'))

def normalize_content(text):
    normalized_text = re.sub(r'[–—]', '-', text)
    normalized_text = normalized_text.replace('"', '"').replace('"', '"')
    normalized_text = normalized_text.replace("'", "'")
    return normalized_text


def create_pdf_with_symbols(content, output_path):
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    styles = getSampleStyleSheet()

    # Erstellen Sie benutzerdefinierte Stile für ChatGPT und Claude
    styles.add(ParagraphStyle(name='ChatGPT', parent=styles['Normal'], textColor=colors.blue))
    styles.add(ParagraphStyle(name='Claude', parent=styles['Normal'], textColor=colors.green))

    story = [Paragraph("AI-to-AI Discussion Summary", styles['Title'])]

    lines = content.split("\n")
    for line in lines:
        if "ChatGPT" in line:
            p = Paragraph(f"🤖 ChatGPT: {line.replace('[DEBUG]: == Working Agent: ChatGPT', '').strip()}",
                          styles['ChatGPT'])
            story.append(p)
            story.append(Spacer(1, 12))
        elif "Claude" in line:
            p = Paragraph(f"🟢 Claude: {line.replace('[DEBUG]: == Working Agent: Claude', '').strip()}",
                          styles['Claude'])
            story.append(p)
            story.append(Spacer(1, 12))
        else:
            p = Paragraph(line.strip(), styles['Normal'])
            story.append(p)

    doc.build(story)


file_path = 'FirstRun_OpenChampion.md'

with open(file_path, 'r', encoding='utf-8') as file:
    content = file.read()

normalized_content = normalize_content(content)

output_pdf_path = "AI_to_AI_Discussion_Summary_with_Symbols.pdf"
create_pdf_with_symbols(normalized_content, output_pdf_path)

print(f"PDF wurde erfolgreich erstellt: {output_pdf_path}")