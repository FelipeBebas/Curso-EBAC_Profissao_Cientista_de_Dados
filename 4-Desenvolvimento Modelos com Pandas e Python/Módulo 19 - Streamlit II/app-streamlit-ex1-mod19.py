import os
if os.path.exists("../img/Bank-Branding.jpg"):
    image = Image.open("../img/Bank-Branding.jpg")
else:
    print("Arquivo não encontrado!")