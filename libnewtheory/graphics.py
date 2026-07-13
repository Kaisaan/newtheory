"""
Ys IV graphics (TIM2) extractor & inserter.
"""
import shutil

from pathlib import Path
from struct import pack

from PIL import Image

from reversebox.image.swizzling.swizzle_ps2 import unswizzle_ps2, swizzle_ps2

TIM2_MAGIC = b'TIM2'

def _intlit(b: bytes) -> int:
    return int.from_bytes(b, "little")

def _writeint(num, size):
    return num.to_bytes(size, byteorder="little")

def fingerprint(filepath: str | Path) -> str | None:
    """
    Return 'naxa', 'gbxa', or None based on the file's 8-byte identifier.
    """
    with open(filepath, "rb") as f:
        ident = f.read(4)
    if ident == TIM2_MAGIC:
        return "tim2"
    return None


def _read_clut(graphic, output_dir: Path, filename: str, logFile, clutSize: int, clutOffset: int):
    """
    Reads the CLUT and writes to .pal. Returns (clut_bytes, bpp).
    8BPP CLUTs are swizzled in 0x80-byte rows; 4BPP CLUTs are used as-is.
    """
    palSize = 4

    if clutSize == 256:
        bpp = 8
        logFile.write(f"{filename} is 8BPP its CLUT is at {clutOffset:X}\n")
    elif clutSize == 16:
        bpp = 4
        logFile.write(f"{filename} is 4BPP its CLUT is at {clutOffset:X}\n")
    else:
        raise ValueError(f"unsupported CLUT size {clutSize}")

    sectionSize = 0x20

    graphic.seek(clutOffset)

    if bpp == 8:
        origclut = graphic.read(clutSize * palSize)
        with open(output_dir / f"{filename}_orig.pal", "wb") as palette:
            palette.write(origclut)
        print(f"{filename}/{filename}_orig.pal saved!")

        clut = b''
        for i in range(8):          # Swizzle the palette (there's probably a better way to do this, but it works!)
            palOffset = i * 0x80
            for sub in (0x00, 0x40, 0x20, 0x60):
                graphic.seek(clutOffset + palOffset + sub)
                clut += graphic.read(sectionSize)
        with open(output_dir / f"{filename}_swzl.pal", "wb") as palette:
            palette.write(clut)
        print(f"{filename}/{filename}_swzl.pal saved!")
        return clut, bpp

    clut = graphic.read(clutSize * palSize)
    with open(output_dir / f"{filename}_orig.pal", "wb") as palette:
        palette.write(clut)
    print(f"{filename}/{filename}_orig.pal saved!")
    return clut, bpp

def extract_tim2(filepath):
    filepath = Path(filepath).resolve()
    filedir = filepath.parent
    filename = filepath.name

    graphic = open(filepath, "rb")

    header = graphic.read(0x40)

    if header[0x0:0x4] != TIM2_MAGIC:
        raise ValueError(f"{filepath} is not a TIM2 file")

    filename = filename[:filename.rfind(".TM2")]
    output_dir = filedir / filename
    output_dir.mkdir(exist_ok=True)

    logFile = open(output_dir / f"{filename}.txt", "w", encoding="utf-8")
    logFile.write("tim2\n")

    pxlOffset = _intlit(header[0x14:0x18])      # Just get the needed info from the TIM2 headers
    clutOffset = _intlit(header[0x18:0x1C])
    clutOffset = clutOffset + 0x40              # clutOffset doesn't account for header
    clutSize = _intlit(header[0x1E:0x20])
    width = _intlit(header[0x24:0x26])
    height = _intlit(header[0x26:0x28])
    mode = _intlit(header[0x2A:0x2B])

    clut, bpp = _read_clut(graphic, output_dir, filename, logFile, clutSize, clutOffset)

    dataSize = width * height

    graphic.seek(pxlOffset)

    if bpp == 4:
        dataSize = dataSize // 2
        data = graphic.read(dataSize)
        with open(output_dir / f"{filename}_packed.bin", "wb") as bin: # Save the original indexing data separate from the image to help with re-insertion
            bin.write(data)
        print(f"{filename}/{filename}_packed.bin saved!")

        if mode == 0x40:        # Very crude check for pixel storage mode (it should be checking a specific bit)
            data = unswizzle_ps2(data, width, height, bpp, swizzle_type=1)
            logFile.write(f"Pixel data is swizzled\n")

        unpackData = b""
        for byte in data:
            unpackData += pack("bb", byte & 0xF, byte >> 4)
        with open(output_dir / f"{filename}_unpacked.bin", "wb") as bin:
            bin.write(unpackData)
        print(f"{filename}/{filename}_unpacked.bin saved!")
        data = unpackData

    else:
        data = graphic.read(dataSize)
        with open(output_dir / f"{filename}_8bpp.bin", "wb") as bin:
            bin.write(data)

    sprite = Image.frombytes("P", (height, width), bytes(data))
    sprite.putpalette(clut, rawmode="RGBA")
    sprite.save(fp=output_dir / f"{filename}.png")
    print(f"{filename}/{filename}.png saved!")

    logFile.write(f"{filename}.png is at {pxlOffset:X} its size is {height:X}H by {width:X}W its data size is {dataSize:X} bytes\n")

    graphic.close()
    logFile.close()


def extract_graphics(filepath: str | Path):
    """
    Fingerprint the file by its 8-byte identifier and dispatch to the
    matching format-specific extractor. extract_frames is ignored for
    GBXA files (no animation table).
    """
    fmt = fingerprint(filepath)
    if fmt == "tim2":
        extract_tim2(filepath)
    else:
        raise ValueError(f"{filepath}: unknown graphics identifier (not NAXA5010 or GBXA2000)")
    

def update_tim2(filepath):
    """
    Insert edited graphic back into a .TM2 file.
    
    Args:
        filepath: Path to the .TM2 file
    """

    filepath = Path(filepath).resolve()
    filedir = filepath.parent
    filename = filepath.name

    origFile = open(filepath, "rb")

    filename = filename[:filename.rfind(".TM2")]

    input_dir = filedir / filename

    shutil.copy(filepath, filedir / f"{filename}_new.TM2")

    newFile = open(filedir / f"{filename}_new.TM2", "r+b")

    header = origFile.read(0x40)

    newFile.seek(0)
    newFile.write(header)

    pxlOffset = _intlit(header[0x14:0x18])      # Just get the needed info from the TIM2 headers
    clutOffset = _intlit(header[0x18:0x1C])
    clutOffset = clutOffset + 0x40              # clutOffset doesn't account for header
    clutSize = _intlit(header[0x1E:0x20])
    width = _intlit(header[0x24:0x26])
    height = _intlit(header[0x26:0x28])
    mode = _intlit(header[0x2A:0x2B])

    if (clutSize == 256):
        bpp = 8
    elif (clutSize == 16):
        bpp = 4
    else:
        exit("other BPP formats not supported yet")

    with Image.open(input_dir / f"{filename}.png", "r") as graphic:
        
        if graphic.mode != "P":
            exit(f"{filename}.png has wrong Image mode as {graphic.mode}")

        data = list(graphic.getdata())

    binData = b""
    if (bpp == 8):
        for i in range(len(data)):
            byte = data[i].to_bytes(1)
            binData = binData + byte
    elif (bpp == 4):
        for i in range(0, len(data), 2):
            byte1 = data[i]
            byte2 = data[i+1]
            if byte1 == 16:
                byte1 = 1
            if byte2 == 16:
                byte2 = 1
            byte2 = byte2 << 4
            byte = byte2 + byte1
            byte = byte.to_bytes(1)
            binData = binData + byte

        if mode == 0x40:
            binData = swizzle_ps2(binData, width, height, bpp, swizzle_type=1)
            
    newFile.seek(pxlOffset)
    newFile.write(binData)

    with open(input_dir / f"{filename}_orig.pal", "rb") as palFile:
        clut = palFile.read(clutSize * 4)

    newFile.seek(clutOffset)
    newFile.write(clut)

    print(f"{filename}_new.TM2 saved!")

    newFile.close()
    origFile.close()


def insert_graphics(filepath: str | Path):

    fmt = fingerprint(filepath)
    if fmt == "tim2":
        update_tim2(filepath)
    else:
        raise ValueError(f"{filepath}: unknown graphics identifier (not TIM2)")
