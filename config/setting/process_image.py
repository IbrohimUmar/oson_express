
def process_image(image_file, size, suffix):
    from PIL import Image
    import uuid
    from io import BytesIO
    from django.core.files.base import ContentFile

    image = Image.open(image_file)
    image = image.convert("RGB")  # Renk modunu normalize et

    # Yeni Pillow sürümüne uygun resampling kullan
    image = image.resize(size, Image.Resampling.LANCZOS)

    # UUID üret ve dosya adı oluştur
    unique_id = uuid.uuid4().hex[:10]
    filename = f"{unique_id}_{suffix}.jpg"

    # Görseli sıkıştırarak hafızaya yaz
    buffer = BytesIO()
    image.save(buffer, format="JPEG", quality=75)

    return filename, ContentFile(buffer.getvalue())

