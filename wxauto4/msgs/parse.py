import os, json
from pathlib import Path
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import SHA512, SHA1  # 兼容v3时会用到

SALT_SIZE = 16

def derive_rawkey_v4(master_hex: str, db_path: str) -> str:
    # 生成 SQLCipher raw key（96 hex= key64 + salt32），适用于 v4 默认参数
    with open(db_path, 'rb') as f:
        salt = f.read(SALT_SIZE)
    passphrase = bytes.fromhex(master_hex)
    key = PBKDF2(passphrase, salt, dkLen=32, count=256000, hmac_hash_module=SHA512)  # v4
    return "0x" + key.hex() + salt.hex()

def derive_rawkey_v3_candidates(master_hex: str, db_path: str):
    # 可选：生成 v3 常见两种候选（不同KDF/迭代），用于老库排障
    with open(db_path, 'rb') as f:
        salt = f.read(SALT_SIZE)
    p = bytes.fromhex(master_hex)
    k1 = PBKDF2(p, salt, dkLen=32, count=64000, hmac_hash_module=SHA1)   # v3 典型
    k2 = PBKDF2(p, salt, dkLen=32, count=64000, hmac_hash_module=SHA512) # 有些构建改成SHA512
    return ["0x" + k1.hex() + salt.hex(), "0x" + k2.hex() + salt.hex()]

def derive_for_dir(master_hex: str, src_dir: str, out_json="db_keys.json"):
    mapping = {}
    for root, _, files in os.walk(src_dir):
        for name in files:
            if name.endswith(".db"):
                p = os.path.join(root, name)
                try:
                    mapping[p] = derive_rawkey_v4(master_hex, p)  # 先按v4生成
                except Exception as e:
                    mapping[p] = f"ERROR: {e}"
    if out_json:
        Path(out_json).write_text(json.dumps(mapping, ensure_ascii=False, indent=2), encoding="utf-8")
    return mapping