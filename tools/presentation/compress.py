#!/usr/bin/env python3
"""Make the printed presentation small enough to download: Chromium stores every picture with
transparency (the product cut-outs and their drop shadows) losslessly, which makes the PDF ~11 MB.
This re-encodes those pictures and their transparency masks as JPEG (4:4:4, so the white lettering on
the red body stays crisp). Needs pikepdf and Pillow.
  python3 -I tools/presentation/compress.py <in.pdf> <out.pdf> [quality=82]
"""
import io, sys
import pikepdf
from PIL import Image

src, dst = sys.argv[1:3]
quality = int(sys.argv[3]) if len(sys.argv) > 3 else 82
pdf = pikepdf.open(src)
masks = {o.get('/SMask').objgen for o in pdf.objects
         if isinstance(o, pikepdf.Stream) and o.get('/Subtype') == '/Image' and o.get('/SMask') is not None}
before = after = 0
for obj in pdf.objects:
    if not isinstance(obj, pikepdf.Stream) or obj.get('/Subtype') != '/Image':
        continue
    if obj.get('/Filter') != '/FlateDecode' or int(obj.get('/BitsPerComponent', 8)) != 8:
        continue
    raw = obj.read_raw_bytes()
    if len(raw) < 20_000:
        continue
    img = pikepdf.PdfImage(obj).as_pil_image()
    if img.mode == 'RGBA':      # newer pikepdf merges the /SMask into the picture; the mask stays its own object
        img = img.convert('RGB')
    if img.mode not in ('RGB', 'L'):
        continue
    buf = io.BytesIO()
    # the transparency masks (soft shadows, smooth edges) take JPEG well too, a little finer
    img.save(buf, 'JPEG', quality=(quality + 6 if obj.objgen in masks else quality), subsampling=0, optimize=True)
    data = buf.getvalue()
    if len(data) >= len(raw):
        continue
    obj.write(data, filter=pikepdf.Name.DCTDecode)
    if '/DecodeParms' in obj:
        del obj['/DecodeParms']
    before += len(raw); after += len(data)
pdf.save(dst, compress_streams=True, object_stream_mode=pikepdf.ObjectStreamMode.generate)
print(f'pictures {before // 1024} KB -> {after // 1024} KB')
