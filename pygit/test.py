SHA1_TO_FILE = {
        '815fa52ea791bf9a0d152ca3386d61d3ad023a5a': 'tree',
        'dc1b915cba9cd6efd61c353fefb96823aaf2dd8f': 'TODO'}

SHA1_TO_CONTENT = {
        '815fa52ea791bf9a0d152ca3386d61d3ad023a5a': 'tree',
        'dc1b915cba9cd6efd61c353fefb96823aaf2dd8f': 'TODO Content.\n'}

from object import \
        from_filename, Blob

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
