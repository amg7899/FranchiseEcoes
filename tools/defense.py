#!/usr/bin/env python3
"""The restricted Defense area (client, 2026-11-09): /defense/ and /bg/defense/ show the client's gate text, and
the content opens only with the access code the client gives out (one shared code).

The site is static and the repository is public, so the content is ENCRYPTED here and only the ciphertext is
published: AES-256-GCM, the key derived from the code with PBKDF2-SHA256 (600 000 rounds, a fresh random salt
and IV each time). The page carries it as JSON in <script type="application/json" id="vault">; assets/js/vault.js
asks for the code and decrypts it in the browser (Web Crypto). Without the code the content cannot be read, not
even in the page source. The photos of the content (data: URIs in the content file) are taken out and stored
beside the page as encrypted files, vault-1.bin, vault-2.bin, ... (the same key, a fresh IV each, the file name
as associated data): the gate page stays small and loads at once, and vault.js fetches and decrypts the photos
only after the code has opened the content (2026-11-09; before, the page carried them and weighed 600 KB).
`open` puts them back as data: URIs, so the content file is complete again for editing. The plain content is never committed: to change it, open it with the code, edit the
HTML file, seal it again. If the code is lost, rebuild the content from the client's document and seal it
with a new code. To change the code, open with the old one and seal with the new one (both pages).

  python3 tools/defense.py newcode                         a new random code (16 characters, 80 bits)
  python3 tools/defense.py seal <page.html> <content.html> encrypt the content into the page
  python3 tools/defense.py open <page.html> <out.html>     decrypt the page's content into a file
The code comes from the environment variable DEFENSE_CODE or is asked for. Spaces, dashes and letter case do
not matter (normalised the same way as in vault.js). Needs the `cryptography` package.
"""
import base64, getpass, glob, json, os, re, secrets, sys

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

ITER = 600_000
ALPHABET = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'      # no 0/O, 1/I: easy to read out and type
BLOCK = re.compile(r'(<script type="application/json" id="vault">)(.*?)(</script>)', re.S)
IMG = re.compile(r'src="data:(image/[a-z+]+);base64,([A-Za-z0-9+/=]+)"')
HOLD = 'data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7'   # 1 x 1, transparent
PLACED = re.compile(r'src="' + re.escape(HOLD) + r'" data-vault-src="([^"]+)" data-vault-type="([^"]+)"')


def norm(code):
    return re.sub(r'[^0-9A-Za-z]', '', code).upper()


def derive(code, salt, iterations=ITER):
    return PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=iterations).derive(norm(code).encode())


def b64(b):
    return base64.b64encode(b).decode()


def get_code():
    code = os.environ.get('DEFENSE_CODE') or getpass.getpass('Access code: ')
    if len(norm(code)) < 12:
        sys.exit('the code is too short (at least 12 letters or digits)')
    return code


def seal(page, content):
    code = get_code()
    salt, iv = secrets.token_bytes(16), secrets.token_bytes(12)
    aes = AESGCM(derive(code, salt))
    folder = os.path.dirname(page) or '.'
    for old in glob.glob(os.path.join(folder, 'vault-*.bin')):
        os.remove(old)
    files = []
    def stash(m):
        name = f'vault-{len(files) + 1}.bin'
        fiv = secrets.token_bytes(12)
        with open(os.path.join(folder, name), 'wb') as fh:
            fh.write(fiv + aes.encrypt(fiv, base64.b64decode(m.group(2)), name.encode()))
        files.append(name)
        return f'src="{HOLD}" data-vault-src="{name}" data-vault-type="{m.group(1)}"'
    plain = IMG.sub(stash, open(content, encoding='utf-8').read()).encode()
    ct = aes.encrypt(iv, plain, None)
    data = json.dumps({'v': 2, 'kdf': 'PBKDF2-SHA256', 'iter': ITER, 'salt': b64(salt), 'iv': b64(iv), 'ct': b64(ct)})
    s = open(page, encoding='utf-8').read()
    s, n = BLOCK.subn(lambda m: m.group(1) + data + m.group(3), s)
    if n != 1:
        sys.exit(f'{page}: no <script type="application/json" id="vault"> block')
    open(page, 'w', encoding='utf-8').write(s)
    print(f'sealed {content} into {page} ({len(plain)} bytes) and {len(files)} photo file(s) beside it')


def unseal(page, out):
    code = get_code()
    m = BLOCK.search(open(page, encoding='utf-8').read())
    d = json.loads(m.group(2))
    aes = AESGCM(derive(code, base64.b64decode(d['salt']), d['iter']))
    try:
        plain = aes.decrypt(base64.b64decode(d['iv']), base64.b64decode(d['ct']), None).decode()
    except Exception:
        sys.exit('wrong code')
    folder = os.path.dirname(page) or '.'
    def restore(m):
        raw = open(os.path.join(folder, m.group(1)), 'rb').read()
        img = aes.decrypt(raw[:12], raw[12:], m.group(1).encode())
        return f'src="data:{m.group(2)};base64,{b64(img)}"'
    plain = PLACED.sub(restore, plain)
    open(out, 'w', encoding='utf-8').write(plain)
    print(f'opened {page} into {out}')


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else ''
    if cmd == 'newcode':
        c = ''.join(secrets.choice(ALPHABET) for _ in range(16))
        print('-'.join(c[i:i + 4] for i in range(0, 16, 4)))
    elif cmd == 'seal' and len(sys.argv) == 4:
        seal(sys.argv[2], sys.argv[3])
    elif cmd == 'open' and len(sys.argv) == 4:
        unseal(sys.argv[2], sys.argv[3])
    else:
        sys.exit(__doc__)
