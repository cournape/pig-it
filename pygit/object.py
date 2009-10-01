import zlib
import hashlib

def sort_by_values(d):
    """Sort a dict from its values."""
    return sorted(_TYPES_TO_ID.items(), key=lambda x: x[1])

# XXX: do we need to use integers ? The point of integer is to avoid string
# comparison when getting the type, but that may well be premature optimization
# -- most of the code here should be done in cython anyway when speed is in a
# issue.
_TYPES_TO_ID = {'blob': 0, 'tree': 1}
_ID_TO_TYPES = [i[0] for i in sort_by_values(_TYPES_TO_ID)]

def parse_object(string):
    """Parse the content of an object."""
    ustring = zlib.decompress(string)

    otp = None
    for tpstr in _TYPES_TO_ID:
        if ustring.startswith(tpstr):
            otp = _TYPES_TO_ID[tpstr]

    if otp is None:
        raise ValueError("Could not parse tp %s)" % ustring[:10])

    otpstr = _ID_TO_TYPES[otp]
    if not ustring[len(otpstr)] == ' ':
        raise ValueError("Expected a space character after object tp")

    ustring = ustring[len(otpstr)+1:]

    # Parse length of content
    ll = []
    i = 0
    while ustring[i] != '\0':
        ll.append(ustring[i])
        i += 1
    l = int(''.join(ll))

    # Skip the byte 0, hence starts at i+1
    content = ustring[i+1:]

    assert len(content) == l
    return content, otpstr

def header(content, tp):
    return '%s %d\0' % (tp, len(content))

def parse_tree(content):
    entries = []
    while content:
        mode, content = content.split(' ', 1)
        imode = int(mode, 8)

        # Parse name
        _name = []
        i = 0
        while content[i] != '\0':
            _name.append(content[i])
            i += 1
        name = ''.join(_name)

        # parse sha1
        sha1 = binascii.b2a_hex(content[i+1:i+21])
        entries.append(RawEntry(imode, name, sha1))

        content = content[i+21:]

    return entries

def from_filename(file):
    content, tp = parse_object(open(file).read())
    if tp == 'blob':
        return Blob(content)
    elif tp == 'tree':
        return Tree(parse_tree(content))
    else:
        raise NotImplementedError("type %s not implemented" % tp)

# # Raw git object
# class _GitRawObject(object):
#     def __init__(self, content, tp):
#         self.content = content
#         self.type = tp
#         try:
#             self._type_id = _TYPES_TO_ID[tp]
#         except KeyError:
#             raise ValueError("Unknown tp %s" % tp)

class GitObject(object):
    def header(self):
        return header(self.content, _ID_TO_TYPES[self._type_id])

    def sha1(self):
        return hashlib.sha1('%s%s' % (self.header(), self.content)).hexdigest()

class Blob(GitObject):
    type = 'blob'
    _type_id = _TYPES_TO_ID['blob']
    def __init__(self, content):
        self.content = content

# Format of an entry in a tree object
#   - st_mode (as defined in *stat functions)
#   - type of object
#   - sha1
#   - name (e.g. filename)
import binascii
import stat

class RawEntry(object):
    def __init__(self, mode, name, sha1):
        known = stat.S_ISREG(mode) or stat.S_ISLNK(mode) or stat.S_ISDIR(mode)
        if not known:
            raise ValueError("Unsupported file type (mode %o)" % mode)
        self.mode = mode
        self.sha1 = sha1
        self.name = name

    # def pretty_str(self):
    #     return '%o %s %s\t%s' % (self.mode, self.type, self.sha1, self.name)

    def raw_str(self):
        return '%o %s\0%s' % (self.mode, self.name, binascii.a2b_hex(self.sha1))

class Tree(GitObject):
    type = 'tree'
    _type_id = _TYPES_TO_ID['tree']
    def __init__(self, entries):
        self.entries = entries
        self.content = self._compute_content()

    def _compute_content(self):
        return "".join(e.raw_str() for e in self.entries)

    # def __str__(self):
    #     return "\n".join([e.pretty_str() for e in self.entries])

_TYPE_TO_CLS = {'blob': Blob, 'tree': Tree}

if __name__ == '__main__':
    import os
    import stat

    content = 'TODO Content.\n'
    o = Blob(content)
    print o.sha1()

    o = from_filename('TODO')
    print o.sha1(), o.content

    filename = 'TODO'
    o = from_filename(filename)

    entries = [RawEntry(os.stat(filename).st_mode, filename, o.sha1())]
    t = Tree(entries)
