from io import BytesIO
import hashlib
import binascii
from fastapi import UploadFile
from typing import Dict, Tuple, Optional

MAX_FILE_SIZE = 100 * 1024 * 1024

ALLOWED_MIME_TYPES = {
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    'text/plain'
}

# 文件签名数据库（十六进制格式）
FILE_SIGNATURES: Dict[str, Dict[str, Tuple[bytes, Optional[int]]]] = {
    # 文本类
    ".txt": {"patterns": (b"",), "offset": 0},  # 无固定签名
    ".md": {"patterns": (b"",), "offset": 0},
    
    # 文档类
    ".pdf": {
        "patterns": (b"%PDF-",),
        "offset": 0,
        "additional": lambda h: b"%%EOF" in h[-1024:]  # 验证尾部特征
    },
    ".docx": {
        "patterns": (b"504B0304", b"504B0506", b"504B0708"),  # ZIP头
        "offset": 0,
        "structure": ["[Content_Types].xml", "word/"]
    },
    ".pptx": {
        "patterns": (b"504B0304",),
        "offset": 0,
        "structure": ["[Content_Types].xml", "ppt/"]
    },
    ".xlsx": {
        "patterns": (b"504B0304",),
        "offset": 0,
        "structure": ["[Content_Types].xml", "xl/"]
    },
    
    # 数据类
    ".json": {
        "validate": lambda c: is_valid_json(c)
    },
    ".csv": {
        "validate": lambda c: is_valid_csv(c)
    },
    
    # 音频类
    ".mp3": {
        "patterns": (b"494433", b"FFFB", b"FFF3"),  # ID3v2或MPEG帧
        "offset": 0
    },
    ".wav": {
        "patterns": (b"52494646",),  # "RIFF"
        "offset": 0,
        "subheader": (b"57415645", 8)  # "WAVE" at 8字节
    },
    
    # 图片类
    ".png": {
        "patterns": (b"89504E470D0A1A0A",),  # PNG头
        "offset": 0,
        "trailer": (b"49454E44AE426082", -12)  # IEND trailer
    },
    ".jpg": {
        "patterns": (b"FFD8FFE0", b"FFD8FFE1", b"FFD8FFE8"),
        "offset": 0,
        "trailer": (b"FFD9", -2)  # EOI标记
    },
    
    # 编程类
    ".py": {
        "patterns": (b"2321",),  # shebang可能
        "offset": 0,
        "validate": lambda c: b"import " in c or b"def " in c
    }
}

def get_file_hash(file_path: str) -> str:
    """计算文件哈希值(SHA-256)"""
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
    return sha256.hexdigest()

def check_file_size(file: UploadFile):
    content = b''
    if file.size > MAX_FILE_SIZE:
        raise BaseException("文件大小超过限制")

async def validate_upload_file(file: UploadFile) -> bool:
    """验证上传文件的签名"""
    ext = file.filename.split('.')[-1].lower()
    if f".{ext}" not in FILE_SIGNATURES:
        raise ValueError(f"不支持的文件类型: .{ext}")
    
    spec = FILE_SIGNATURES[f".{ext}"]
    
    # 读取文件头（异步优化）
    header = await read_upload_file_header(file, max_bytes=64)
    
    # 基础签名验证
    if "patterns" in spec:
        if not check_header_pattern(header, spec["patterns"], spec.get("offset", 0)):
            return False
    
    # ZIP结构验证
    if "zip_files" in spec:
        content = await file.read()
        await file.seek(0)  # 重置指针
        if not validate_zip_structure(content, spec["zip_files"]):
            return False
    
    # 尾部验证（PDF/图片）
    if "trailer" in spec:
        trailer_data = await read_upload_file_trailer(file, spec["trailer"][1])
        if not trailer_data.endswith(spec["trailer"][0]):
            return False
    
    # 内容格式验证
    if "validate" in spec:
        content = await file.read()
        await file.seek(0)
        if not spec["validate"](content):
            return False
    
    return True

async def read_upload_file_header(file: UploadFile, max_bytes: int = 64) -> bytes:
    """读取文件头部数据（优化大文件处理）"""
    await file.seek(0)
    header = await file.read(max_bytes)
    await file.seek(0)
    return header

async def read_upload_file_trailer(file: UploadFile, offset: int) -> bytes:
    """读取文件尾部数据"""
    file_size = file.size
    if offset < 0:
        read_pos = max(0, file_size + offset)
    else:
        read_pos = max(0, file_size - offset)
    
    await file.seek(read_pos)
    return await file.read()

def check_header_pattern(header: bytes, patterns: Tuple[str], offset: int) -> bool:
    """验证二进制模式"""
    hex_header = binascii.hexlify(header).upper()
    for pattern in patterns:
        pattern_bytes = binascii.unhexlify(pattern)
        start = offset * 2  # 转换为hex偏移量
        end = start + len(pattern)
        if hex_header[start:end] == pattern:
            return True
    return False

def validate_zip_structure(content: bytes, required_files: Tuple[str]) -> bool:
    """验证ZIP包结构"""
    from zipfile import ZipFile
    try:
        with ZipFile(BytesIO(content)) as zf:
            return all(name in zf.namelist() for name in required_files)
    except:
        return False

# 辅助验证函数
def is_valid_json(content: bytes) -> bool:
    import json
    try:
        json.loads(content.decode('utf-8'))
        return True
    except:
        return False

def is_valid_csv(content: bytes) -> bool:
    import csv
    from io import StringIO
    try:
        # 验证首行字段数一致性
        reader = csv.reader(StringIO(content.decode('utf-8-sig')))
        header = next(reader)
        for row in reader:
            if len(row) != len(header):
                return False
        return True
    except:
        return False