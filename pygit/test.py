import os

from binascii import \
        a2b_hex

from object import \
        from_filename, Blob, Tree, RawEntry

SHA1_TO_FILE = {
        '815fa52ea791bf9a0d152ca3386d61d3ad023a5a': 'tree',
        'dc1b915cba9cd6efd61c353fefb96823aaf2dd8f': 'TODO'}
FILE_TO_SHA1 = dict([(v, k) for k, v in SHA1_TO_FILE.items()])

# Raw content of each git object (as they are on-disk, excluding header)
SHA1_TO_CONTENT = {
        '815fa52ea791bf9a0d152ca3386d61d3ad023a5a':
            '%d %s\0%s' % (100644, 'TODO', a2b_hex(FILE_TO_SHA1['TODO'])),
        'dc1b915cba9cd6efd61c353fefb96823aaf2dd8f': 'TODO Content.\n'}

class TestBlob:
    def test_from_content(self):
        sha1name = 'dc1b915cba9cd6efd61c353fefb96823aaf2dd8f'
        content = SHA1_TO_CONTENT[sha1name]

        blob = Blob(content)
        assert blob.sha1() == sha1name

    def test_parse(self):
        # file which contains the content of a blob object
        filename = 'TODO'
        o = from_filename(filename)
        try:
            real_filename = SHA1_TO_FILE[o.sha1()]
            assert real_filename == filename
        except KeyError:
            assert False, "Wrong sha1"

        assert o.content == SHA1_TO_CONTENT[o.sha1()]

class TestTree:
    def test_from_entries(self):
        sha1name = '815fa52ea791bf9a0d152ca3386d61d3ad023a5a'
        raw_entries = [RawEntry(os.stat('TODO').st_mode, 'TODO',
                                FILE_TO_SHA1['TODO'])]

        tree = Tree(raw_entries)
        assert tree.sha1() == sha1name
