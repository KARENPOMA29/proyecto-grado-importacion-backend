# src/utils/security.py
import hashlib

def md5_hash(texto: str) -> str:
    if not texto:
        return ""
    return hashlib.md5(texto.encode("utf-8")).hexdigest()
