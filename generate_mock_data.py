import os
from PIL import Image, ImageDraw, ImageFont

def create_dummy_image(path: str, text_lines: list):
    # Create white image
    img = Image.new('RGB', (800, 1000), color='white')
    d = ImageDraw.Draw(img)

    # Try to load a font, fallback to default
    try:
        # This path is common on linux, but might fail if fonts aren't installed.
        # Using default if fails.
        font = ImageFont.truetype("DejaVuSans.ttf", 20)
    except:
        font = ImageFont.load_default()

    y = 50
    for line in text_lines:
        d.text((50, y), line, fill='black', font=font)
        y += 30

    # Create dir if not exists
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path)

def generate_mock_data():
    root = "workdrive_mock"

    # Case 1: Cedolino with Cessione inside a Fiscal Code Folder
    cf1 = "RSSMRA80A01H501U"
    lines1 = [
        "AZIENDA SPA - CEDOLINO PAGA",
        f"Dipendente: Mario Rossi - CF: {cf1}",
        "Mese: Gennaio 2024",
        "--------------------------------",
        "Stipendio Base: 2000.00",
        "Trattenute:",
        "Cod. 501 - Cessione del Quinto - BANCA INTESA",
        "Rata: 250.00 - Scadenza: 31/12/2026 - Residuo: 24 mesi",
        "Cod. 502 - Delega - FINDOMESTIC",
        "Rata: 150.00 - Scadenza: 15/06/2025"
    ]
    create_dummy_image(f"{root}/{cf1}/cedolino_gennaio.jpg", lines1)

    # Case 2: Documento identità (Generic)
    cf2 = "VRDLGI90B02F205Z"
    lines2 = [
        "REPUBBLICA ITALIANA",
        "CARTA D'IDENTITA",
        f"Cognome: Verdi  Nome: Luigi",
        f"CF: {cf2}",
        "Nato il: 02/02/1990"
    ]
    create_dummy_image(f"{root}/{cf2}/documenti/ci.png", lines2)

    # Case 3: Estratto Conto (No loans)
    lines3 = [
        "BANCA NAZIONALE",
        "ESTRATTO CONTO AL 31/12/2023",
        "Intestatario: Bianchi Giovanni",
        "Saldo: +15,000.00"
    ]
    create_dummy_image(f"{root}/BNCGNN70C03L219K/estratto.jpg", lines3)

    print(f"Mock data generated in '{root}'")

if __name__ == "__main__":
    generate_mock_data()
