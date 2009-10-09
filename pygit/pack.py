import struct
import binascii
from hashlib import \
    sha1

_V2_MAGIC = "\377tOc"
_V2_VERINT = "\0\0\0\2"

class Pack:
    pass

# Size in bytes
FANOUT_SIZE = 4
FANOUT_NUMBER = 256
def _parse_header_v2(f):
    _fanout = f.read(FANOUT_SIZE * FANOUT_NUMBER)
    fanouts = [struct.unpack('!i', _fanout[4*i:4*i+4])[0] for i in range(FANOUT_NUMBER)]

    nobjects = fanouts[-1]

    crc32_table = [binascii.b2a_hex(f.read(4)) for i in range(nobjects)]

    offset_table = [struct.unpack('!i', f.read(4)) for i in range(nobjects)]

    pack_checksum = binascii.b2a_hex(f.read(20))
    index_checksum = binascii.b2a_hex(f.read(20))

    if f.read():
        raise NotImplementedError("64 bits offset not supported yet")
    return fanouts, object_table, crc32_table, offset_table, pack_checksum, index_checksum

# Support only V2 for now
# Structure of a pack index V2 (from git doc sources + jgit PackIndexV2.java)
#
# +-----------------------------------------------------------+ 
# | Magic number (4 bytes)                  \377t0c           |
# +-----------------------------------------------------------+ 
# | Version number (4 bytes)                \0\0\0\2          |
# +-----------------------------------------------------------+ 
# | Fanout table: 256 entries               fanout[0]         |
# | of 4 bytes (1024 bytes)                 fanout[1]
# |                                         ...
# | fanout[i]-fanout[i-1] is the number of  fanout[255]
# | objects whose name starts
# | with hex(i), e.g. fanout[224]
# | is the number of objects whose 
# | name follow the pattern 00xxxxx
# | up to e0xxxx.... ('0xe0' == 224)
# |
# | fanout[255] is thus the total number 
# | of objects: nobjects == fanout[255]
# +-----------------------------------------------------------+ 
# | Name table: nobjects entries of sha1    name[0]
# | names (nobjects * 20 bytes)             ....
# |                                         name[nobjects-1]
# +-----------------------------------------------------------+ 
# | CRC32 table: nobjects entries of crc32  crc32[0]
# | (nobjects * 4 bytes)                    ....
# |                                         crc32[nobjects-1]
# +-----------------------------------------------------------+ 
# | 32 bits offset table: nobjects          offset[0]
# | (nobject * 4 bytes)                     ....
# |                                         offset[nobjects-1]
class PackIndexV2:
    def __init__(self, fobject):
        """fobject is a file object advanced after the header (8 bytes)."""
        _fanout = fobject.read(FANOUT_SIZE * FANOUT_NUMBER)
        self.fanout_table = [
            struct.unpack('!i', _fanout[4*i:4*i+4])[0] for i in range(FANOUT_NUMBER)]

        self.nobjects = self.fanout_table[-1]

        self.names = []
        for i in range(FANOUT_NUMBER):
            self.names[binascii.b2a_hex(f.read(20)) for i in range(self.nobjects)]
 
    def has_object(self):
        pass

    def offset(self, name):
        # Index in the fanout table
        idx1 = int(name[:2], 16)
        idx2 = int(name[:2], 16)

    def __str__(self):
        return "Pack Index v2: %d objects" % self.nobjects

    def __repr__(self):
        return self.__str__()

def pack_index_factory(packfile):
    f = open(packfile)
    magic = f.read(4)
    ver = f.read(4)
    if magic == _V2_MAGIC and ver == _V2_VERINT:
        ver = 2
    else:
        ver = 1

    if ver == 2:
        return PackIndexV2(f)
    else:
        raise NotImplementedError("version 1 of pack-*.idx not implemented")

if __name__ == "__main__":
    pack = "pack-b2277b2587127f0f1b4162cba58a3dc18bf0df48.idx"
    index = pack_index_factory(pack)

    #f = open(pack).read()[:-20]

    #print sha1(f).hexdigest()
    #print ichecksum
