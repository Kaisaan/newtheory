import os

def _intlit(b: bytes) -> int:
    return int.from_bytes(b, "little")

def _writeint(num, size):
    return num.to_bytes(size, byteorder="little")

PKM_MAGIC = b"xf"

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

        fileName = os.path.split(filePath)[1]
        fileDir = os.path.split(filePath)[0]

        offset = _intlit(pki.read(4))
        size = _intlit(pki.read(4))

        pak.seek(offset)
        fileData = pak.read(size)

        os.makedirs(f"{outFolder}\\{fileDir}", exist_ok="true")

        file = open(f"{outFolder}\\{filePath}", "wb")
        file.write(fileData)
        
        if fileName.endswith(".PKM"):
            
            pkm = open(f"{outFolder}\\{filePath}", "r+b")
            pkm.seek(0)
            
            magic = pkm.read(2)
            print(magic)
            continue

            if magic != PKM_MAGIC:
                print(f"{filePath} has Invalid Magic Number! {magic}")
                continue
                
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

                offset = int.from_bytes(pkm.read(4), byteorder="little")
                size = int.from_bytes(pkm.read(4), byteorder="little")

                pkmFiles.append([pkmFilePath, 0, offset, size])
                

            while(pkm.tell()%64 !=0):
                pkm.read(1)
            start = pkm.tell()

            for i in range(pkmFileCount):

                pkmFiles[i][1] = pkmFiles[i][2] + start
                log.write(f"{pkmFiles[i][0]} {pkmFiles[i][1]} {pkmFiles[i][2]} {pkmFiles[i][3]}\n")
                
                pkm.seek(pkmFiles[i][1])

                newFileName = os.path.split(pkmFiles[i][0])[1]
                newFileDir = os.path.split(pkmFiles[i][0])[0]

                os.makedirs(f"{outFolder}\\{newFileDir}", exist_ok="true")

                newFileData = pkm.read(pkmFiles[i][3])

                newFile = open(f"{outFolder}\\{newFileDir}\\{newFileName}", "wb")
                newFile.write(newFileData)

        else:
            log.write(f"{filePath} {offset} {size}\n")        

def unpack():
    extractDat()
    