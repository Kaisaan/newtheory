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
            
            pkm = open(os.path.join(outFolder, filePath), "rb")
            pkm.seek(0)
            magic = pkm.read(2)    
            unknown1 = _intlit(pkm.read(2))
            pkmFileCount = _intlit(pkm.read(4))
            unknown2 = _intlit(pkm.read(4))
            unknown3 = _intlit(pkm.read(2))
            unknown4 = _intlit(pkm.read(2))

            pkmFiles = []

            log.write(f"{filePath} {pkmFileCount} {offset} {size} {unknown1} {unknown2} {unknown3} {unknown4}\n")        

            for i in range(pkmFileCount):
            
                pkmFilePath = pkm.read(256).decode(encoding="utf-8", errors="backslashreplace")
                pkmFilePath = pkmFilePath[:pkmFilePath.find("\x00")]
                pkmFilePath = _native_path(pkmFilePath)

                offset = _intlit(pkm.read(4))
                size = _intlit(pkm.read(4))

                pkmFiles.append([pkmFilePath, 0, offset, size])
            
            pos = pkm.tell()
            

            if((pos % 64 ) == 0):
                start = pos + 64

            else:
                start = (64 - (pos % 64)) + pos

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

    pki.write(PKM_MAGIC)   
    pki.write(_writeint(int(pkiInfo[1]), 2))
    pki.write(_writeint(int(pkiInfo[0]), 4))
    pki.write(_writeint(int(pkiInfo[2]), 4))
    pki.write(_writeint(int(pkiInfo[3]), 2))
    pki.write(_writeint(int(pkiInfo[4]), 2))
    
    for i in range(int(pkiInfo[0])):
        fileinfo = log.readline().rstrip("\n").split()
        name = fileinfo[0]

        if name.endswith(".PKM") == True:

            fileCount = int(fileinfo[1])
            new = open(os.path.join(outFolder, _native_path(f"{name}")), "w+b")
            new.write(PKM_MAGIC)
            new.write(_writeint(int(fileinfo[4]), 2))
            new.write(_writeint(fileCount, 4))
            new.write(_writeint(int(fileinfo[5]), 4))
            new.write(_writeint(int(fileinfo[6]), 2))
            new.write(_writeint(int(fileinfo[7]), 2))



            pkmCurrent = 0
            pkmData = []
            for j in range(fileCount):
                pkmInfo = log.readline().rstrip("\n").split()
                pkmName = pkmInfo[0]
                pkmSize = os.path.getsize(f"{outFolder}\\{pkmName}")

                new.write(pkmName.encode(encoding="utf-8"))
                padding = (256 - (len(pkmName) % 256))
                new.write(bytes(padding))

                new.write(_writeint(pkmCurrent, 4))

                new.write(_writeint(pkmSize, 4))
                

                pkmCurrent = pkmCurrent + pkmSize

                if ((pkmCurrent % 16) == 0):
                    padding = 0
                else:
                    padding = (16 - (pkmCurrent % 16))
                    
                pkmCurrent = pkmCurrent + padding

                pkmData.append([pkmName, padding])

            end = new.tell()
            if ((end % 64) == 0):
                padding = 64
            else:
                padding = (64 - (end % 64))
            
            new.write(bytes(padding))
            
            for k in range(fileCount):
                with open(os.path.join(outFolder, _native_path(pkmData[k][0])), "rb") as file:
                    data = file.read()
                new.write(data)
                new.write(bytes(pkmData[k][1]))
            
            
            new.close()
            


        file = open(os.path.join(outFolder, _native_path(name)), "rb")
        data = file.read()
        size = len(data)

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
