import io
import warnings
from PIL import Image, ImageOps, UnidentifiedImageError
from fastapi import HTTPException, UploadFile

MAX_BYTES = 5 * 1024 * 1024
Image.MAX_IMAGE_PIXELS = 20_000_000

async def validate_image(file: UploadFile) -> bytes:
    raw = await file.read(MAX_BYTES + 1)
    if not raw:
        raise HTTPException(400, 'O arquivo está vazio.')
    if len(raw) > MAX_BYTES:
        raise HTTPException(413, 'A imagem deve ter no máximo 5 MB.')
    if file.content_type not in ('image/jpeg', 'image/png'):
        raise HTTPException(415, 'Envie uma imagem JPEG ou PNG.')
    try:
        with warnings.catch_warnings():
            warnings.simplefilter('error', Image.DecompressionBombWarning)
            with Image.open(io.BytesIO(raw)) as im:
                actual = {'JPEG': 'image/jpeg', 'PNG': 'image/png'}.get(im.format)
                if actual != file.content_type or getattr(im, 'n_frames', 1) != 1:
                    raise ValueError('Formato inválido')
                im.verify()
            with Image.open(io.BytesIO(raw)) as im:
                im.load()
                clean = ImageOps.exif_transpose(im).convert('RGB')
                clean.thumbnail((1600, 1600))
                out = io.BytesIO()
                clean.save(out, format='JPEG', quality=90)
                return out.getvalue()
    except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError, Image.DecompressionBombWarning):
        raise HTTPException(415, 'O conteúdo não é uma imagem JPEG ou PNG válida, ou tem dimensões excessivas.')
