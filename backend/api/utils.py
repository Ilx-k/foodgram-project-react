from collections import namedtuple
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle


def generate_shopping_list_pdf(shopping_list, user):

    def header_footer(canvas, doc):
        canvas.saveState()
        canvas.setFont('Timesnewromanpsmt', 24)
        header_text = 'Список продуктов'
        footer_text = 'Foodgram'
        w, h = doc.pagesize
        canvas.drawString(250, h - 0.5 * inch, header_text)
        canvas.setFont('Wolgadeutsche', 24)
        canvas.drawString(inch, 0.5 * inch, footer_text)

        canvas.restoreState()

    pdfmetrics.registerFont(
        TTFont('Wolgadeutsche', 'data/Wolgadeutsche.ttf'))
    pdfmetrics.registerFont(
        TTFont('Timesnewromanpsmt', 'data/timesnewromanpsmt.ttf'))

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, title='Shopping List')

    data = [
        ['Ингредиенты', 'Количество']
    ]
    for ingredient in shopping_list:
        data.append([ingredient[0], f'{ingredient[1]} {ingredient[2]}'])

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Timesnewromanpsmt'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    doc.build([table], onFirstPage=header_footer, onLaterPages=header_footer)
    buffer.seek(0)

    return buffer


ShoppingListItem = namedtuple('ShoppingListItem',
                              ['name', 'amount', 'measurement_unit'])


def process_shopping_list(recipe_list):
    ingredients = {}
    for recipe in recipe_list:
        for ingredient in (recipe.ingredientes.select_related
                           ('ingredient').all()):
            piece = (ingredient.ingredient.name,
                     ingredient.ingredient.measurement_unit)
            if piece not in ingredients:
                ingredients[piece] = 0
            ingredients[piece] += ingredient.amount

    return [ShoppingListItem(name, amount, measurement_unit)
            for ((name, measurement_unit), amount) in ingredients.items()]
