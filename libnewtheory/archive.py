import os

def _intlit(b: bytes) -> int:
    return int.from_bytes(b, byteorder="little")

def _writeint(num, size):
    return num.to_bytes(size, byteorder="little")

PKM_MAGIC = b"xf"

def _native_path(path: str) -> str:
    return path.replace("\\", os.sep)

def extractDat():
    pak = open("extracted/DAT.PAK", "rb")
    pki = open("extracted/DAT.PKI", "rb")
    log = open("DAT.txt", "w", encoding="utf-8")

    outFolder = "DAT"

    # This could be turned into a separate function to get PKM info

    magic = pki.read(2)

    if magic != PKM_MAGIC:
        exit("DAT.PKI has Invalid Magic Number!")
    
    unknown1 = _intlit(pki.read(2))     # Should be 0x00 (0) (Endianess, if it's 1 then it's big-endian)
    fileCount = _intlit(pki.read(4))
    unknown2 = _intlit(pki.read(4))     # Should be 0x67 (103) (Applies to all PKM)
    unknown3 = _intlit(pki.read(2))     # Should be 0x02 (2) (If it's not 2 then the PKM has no files names, but I assume they all have file names)
    unknown4 = _intlit(pki.read(2))     # Should be 0x0800 (2048) ()

    log.write(f"{fileCount} {unknown1} {unknown2} {unknown3} {unknown4}\n")

    for _ in range(fileCount):
        filePath = pki.read(256).decode(encoding="utf-8", errors="backslashreplace")
        filePath = filePath[:filePath.find("\x00")]
        filePath = _native_path(filePath)

        fileName = os.path.split(filePath)[1]
        fileDir = os.path.split(filePath)[0]

        offset = _intlit(pki.read(4))
        size = _intlit(pki.read(4))

        pak.seek(offset)
        fileData = pak.read(size)

        os.makedirs(os.path.join(outFolder, fileDir), exist_ok=True)

        file = open(os.path.join(outFolder, filePath), "w+b")
        file.write(fileData)

        file.seek(0)
        header = file.read(2)
        
        if header == PKM_MAGIC:
            print(fileName)
            
            pkm = open(os.path.join(outFolder, filePath), "rb")
            pkm.seek(0)
            magic = pkm.read(2)    
            unknown1 = _intlit(pkm.read(2))
            pkmFileCount = _intlit(pkm.read(4))
            unknown2 = _intlit(pkm.read(4))
            unknown3 = _intlit(pkm.read(2))
            unknown4 = _intlit(pkm.read(2))
            print(pkmFileCount)
            print(f"{pkm.tell():X}")

            pkmFiles = []

            log.write(f"{filePath} {pkmFileCount} {offset} {size} {unknown1} {unknown2} {unknown3} {unknown4}\n")        

            for i in range(pkmFileCount):
            
                pkmFilePath = pkm.read(256).decode(encoding="utf-8", errors="backslashreplace")
                pkmFilePath = pkmFilePath[:pkmFilePath.find("\x00")]
                pkmFilePath = _native_path(pkmFilePath)

                offset = _intlit(pkm.read(4))
                size = _intlit(pkm.read(4))

                pkmFiles.append([pkmFilePath, 0, offset, size])
                

            while((pkm.tell() % 64) != 0):
                pkm.read(1)
            start = pkm.tell()

            for i in range(pkmFileCount):

                pkmFiles[i][1] = pkmFiles[i][2] + start
                log.write(f"{pkmFiles[i][0]} {pkmFiles[i][1]} {pkmFiles[i][2]} {pkmFiles[i][3]}\n")
                
                pkm.seek(pkmFiles[i][1])

                newFileName = os.path.split(pkmFiles[i][0])[1]
                newFileDir = os.path.split(pkmFiles[i][0])[0]

                os.makedirs(os.path.join(outFolder, newFileDir), exist_ok=True)

                newFileData = pkm.read(pkmFiles[i][3])

                newFile = open(os.path.join(outFolder, newFileDir, newFileName), "wb")
                newFile.write(newFileData)

        else:
            log.write(f"{filePath} {offset} {size}\n")

def buildDat():
    log = open("DAT.txt", "r", encoding="utf-8")
    pak = open("DAT.PAK", "w+b")
    pki = open("DAT.PKI", "w+b")
    outFolder = "DAT"
    current = 0

    pkiInfo = log.readline().split()
    print(pkiInfo)
    pki.write(PKM_MAGIC)   
    pki.write(_writeint(int(pkiInfo[1]), 2))
    pki.write(_writeint(int(pkiInfo[0]), 4))
    pki.write(_writeint(int(pkiInfo[2]), 4))
    pki.write(_writeint(int(pkiInfo[3]), 2))
    pki.write(_writeint(int(pkiInfo[4]), 2))
    
    for i in range(int(pkiInfo[0])):
        fileinfo = log.readline().rstrip("\n").split()
        name = fileinfo[0]
        file = open(os.path.join(outFolder, _native_path(name)), "rb")
        data = file.read()
        size = len(data)

        if name.endswith(".PKM") == False:
            print(name)


        else:
            fileCount = int(fileinfo[1])
            print(name)
            for j in range(fileCount):
                print(log.readline().rstrip("\n"))
        
        pki.write(name.encode(encoding="utf-8"))
        padding = (256 - (len(name) % 256))
        pki.write(bytes(padding))



        pki.write(_writeint(current, 4))

        pki.write(_writeint(size, 4))
        

        current = current + size

        if ((current % 0x800) == 0):
            padding = 0
        else:
            padding = (0x800 - (current % 0x800))
        current = current + padding

        pak.write(data)
        pak.write(bytes(padding))

def unpack():
    extractDat()

def pack():
    buildDat()
