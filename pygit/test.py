import os

from binascii import \
        a2b_hex

from object import \
        from_filename, Blob, Tree, RawEntry, parse_object, CommitHeader, \
        Commit

SHA1_TO_FILE = {
        '1b8ae996b7685aa07180a050332df81e0a6be40e': 'commit1',
        '815fa52ea791bf9a0d152ca3386d61d3ad023a5a': 'tree1',
        '00909da106de7af4a10f609de58136c47ca3221e': 'tree2',
        '379bf459121513d43d0758e2b57629c064a5f727': 'tree3',
        '6ff9ac7448e894a8df4bbb6dc248f8fac255c86b': 'subdir1',
        'a94e2db7b97aab44f1ec897c10e0bdf2e5dbd80f': 'README',
        'dc1b915cba9cd6efd61c353fefb96823aaf2dd8f': 'TODO'}
FILE_TO_SHA1 = dict([(v, k) for k, v in SHA1_TO_FILE.items()])

# Raw content of each git object (as they are on-disk, excluding header)
SHA1_TO_CONTENT = {
        '1b8ae996b7685aa07180a050332df81e0a6be40e':
            """\
tree 815fa52ea791bf9a0d152ca3386d61d3ad023a5a
author David Cournapeau <cournape@gmail.com> 1254378435 +0900
committer David Cournapeau <cournape@gmail.com> 1254378435 +0900

Initial commit.\n""",
        '815fa52ea791bf9a0d152ca3386d61d3ad023a5a':
            '%d %s\0%s' % (100644, 'TODO', a2b_hex(FILE_TO_SHA1['TODO'])),
        '00909da106de7af4a10f609de58136c47ca3221e':
            '%d %s\0%s' % (100644, 'README', a2b_hex(FILE_TO_SHA1['README'])) + \
            '%d %s\0%s' % (100644, 'TODO', a2b_hex(FILE_TO_SHA1['TODO'])),
        '379bf459121513d43d0758e2b57629c064a5f727':
            '%d %s\0%s' % (100644, 'README', a2b_hex(FILE_TO_SHA1['README'])) + \
            '%d %s\0%s' % (100644, 'TODO', a2b_hex(FILE_TO_SHA1['TODO'])) + \
            '%d %s\0%s' % (40000, 'subdir1', a2b_hex(FILE_TO_SHA1['subdir1'])),
        'dc1b915cba9cd6efd61c353fefb96823aaf2dd8f': 'TODO Content.\n'}

class TestRawObject:
    """Test that we parse raw objects correctly: we just test whether we parse
    the header correctly, and that content match with the one hardcoded in
    SHA1_TO_CONTENT."""
    def test(self):
        for sha1, ref_content in SHA1_TO_CONTENT.items():
            f = open(SHA1_TO_FILE[sha1])
            try:
                content = parse_object(f.read())[0]
                assert content == ref_content
            finally:
                f.close()

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

    def test_simple_parse(self):
        # file which contains the content of a tree object
        for filename in ['tree1', 'tree2']:
            o = from_filename(filename)

            assert o.sha1() == FILE_TO_SHA1[filename]

            # Testing for sha1 should be enough, but we double check here
            assert o.content == SHA1_TO_CONTENT[o.sha1()]

    def test_simple_parse2(self):
        # this tree contains a subtree
        filename = 'tree3'
        o = from_filename(filename)

        assert o.sha1() == FILE_TO_SHA1[filename]

        # Testing for sha1 should be enough, but we double check here
        assert o.content == SHA1_TO_CONTENT[o.sha1()]

class TestCommit:
    def test_from_content(self):
        author = 'David Cournapeau <cournape@gmail.com> 1254378435 +0900'
        committer = 'David Cournapeau <cournape@gmail.com> 1254378435 +0900'
        tree = '815fa52ea791bf9a0d152ca3386d61d3ad023a5a'
        message = "Initial commit.\n"
        header = CommitHeader(author, committer, tree)

        commit = Commit(header, message)

        assert commit.content[:30] == SHA1_TO_CONTENT[FILE_TO_SHA1['commit1']][:30]
        assert commit.sha1() == FILE_TO_SHA1['commit1']
