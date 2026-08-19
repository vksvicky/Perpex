from PIL import Image
img = Image.open('/Users/vivek/.gemini/antigravity-ide/brain/9cac8e9a-aad7-442d-a56b-48032557f0b0/option_a_base.jpg')
img = img.resize((390, 390), Image.LANCZOS)
img.save('resources/drawables/dial_bg.png', 'PNG')
