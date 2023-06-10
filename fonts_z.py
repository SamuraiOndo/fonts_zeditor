from zouna_utf8 import *
from binary_reader import BinaryReader
import json
import sys
import os
import math
def readObjectHeader(reader):
    reader.seek(20)
    namecrc32 = reader.read_uint32()
    linkcrc32 = reader.read_uint32()
    links = []
    for i in range(reader.read_uint32()):
        links.append(reader.read_uint32())
    header = {
        "Name CRC32": namecrc32,
        "Link CRC32": linkcrc32,
        "Links": links
    }
    
    return header
def readFonts_Z():
    f = open(sys.argv[1],"rb")
    reader = BinaryReader(f.read())
    header = readObjectHeader(reader)
    charCount = reader.read_uint32()
    stay = reader.pos()
    for i in range(charCount):
        reader.seek(28,1)
    materialCrc32Count = reader.read_uint32()
    materials = []
    for i in range(materialCrc32Count):
            materials.append(reader.read_uint32())
    reader.seek(stay)
    p = 0
    header.update({"Materials":materials})
    chars = []
    for i in range(charCount):
        x = {
            "ID": font_character_id_to_zouna_utf8_bytes(reader.read_uint32()).decode("utf-8"),
            "Material Index": reader.read_uint32(),
            "Descent": reader.read_float(),
            "Top Left Coordinate":[reader.read_float(),reader.read_float()],
            "Bottom Right Coordinate":[reader.read_float(),reader.read_float()]
        }
        p+=1
        chars.append(x)
    header.update({"Chars":chars})
    return header
def saveNewFontsZ(fontszjson):
    w = BinaryReader()
    for _ in range(4):
        w.write_uint32(0)
    w.write_uint32(1536002910)
    w.write_uint32(fontszjson["Name CRC32"])
    w.write_uint32(fontszjson["Link CRC32"])
    w.write_uint32(len(fontszjson["Links"]))
    for link in fontszjson["Links"]:
        w.write_uint32(link)
    headersize = w.pos()
    w.write_uint32(len(fontszjson["Chars"]))
    for char in fontszjson["Chars"]:
        w.write_bytes(utf8_bytes_to_zouna_font_character_id(char["ID"].encode()).to_bytes(4,byteorder = 'little'))
        w.write_uint32(char["Material Index"])
        w.write_float(char["Descent"])
        for coord in char["Top Left Coordinate"]:
            w.write_float(coord)
        for coord in char["Bottom Right Coordinate"]:
            w.write_float(coord)
    w.write_uint32(len(fontszjson["Materials"]))
    for material in fontszjson["Materials"]:
        w.write_uint32(material)
    datasize = w.pos() - headersize
    w.seek(0)
    linksize = len(fontszjson["Links"])*4 + 4 + 4
    w.write_uint32(datasize + (linksize))
    w.write_uint32(linksize)
    w.write_uint32(datasize)
    return (w.buffer())
def updateFontszJson(fontszjson,newfontjson):
    oldCharArray = fontszjson["Chars"]
    newCharArray = []
    for char in newfontjson["symbols"]:
        if (char["id"] != 32):
            print(char["id"].to_bytes(4,byteorder = 'little').decode())
            x = {
                "ID": char["id"].to_bytes(4,byteorder = 'little').decode(),
                "Material Index": 2,
                "Descent": math.ceil(char["yoffset"]/2.0),
                "Top Left Coordinate":[char["x"],char["y"]-1],
                "Bottom Right Coordinate":[char["x"] + char["width"],char["y"] + char["height"]+1]
            }
            newCharArray.append(x)
    for x in oldCharArray:
        newCharArray.append(x)
    fontszjson["Chars"] = newCharArray
if __name__ == "__main__":
    if (sys.argv[1].endswith(".Fonts_Z")):
        header = readFonts_Z()
        filejson = open(os.path.basename(sys.argv[1]) + ".json", "w",encoding="utf-8")
        filejson.write(json.dumps(header, ensure_ascii=False, indent=2))
        filejson.close()
    elif(sys.argv[1].endswith(".json") and len(sys.argv) == 2):
        fontszjson = json.loads(open(sys.argv[1],"r",encoding="utf-8").read())
        fe = open("fuck","wb")
        fe.write(saveNewFontsZ(fontszjson))
        fe.close()
    elif(sys.argv[1].endswith(".json") and sys.argv[2].endswith(".json")):
        fontszjson = json.loads(open(sys.argv[1],"r",encoding="utf-8").read())
        newfontjson = json.loads(open(sys.argv[2],"r",encoding="utf-8").read())
        fe = open("fuck","wb")
        updateFontszJson(fontszjson,newfontjson)
        fe.write(saveNewFontsZ(fontszjson))
        fe.close()