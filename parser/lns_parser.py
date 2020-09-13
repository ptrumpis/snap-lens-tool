import zstd
from .binary_reader import BinaryReader
from .exceptions import ParserException

class LnsParser:
    def __init__(self, filename, data=None):
        self.filename = filename
        self.reader = data and BinaryReader(data)

    def parse(self):
        if self.reader is None:
            with open(self.filename, "rb") as f:
                data = f.read()
            self.reader = BinaryReader(data)

        magic = self.reader.readBytes(4)
        if magic != b"LZC\0":
            raise ParserException("Unexpected magic number")
        self.reader.skip(4)
        file_count = self.reader.readUInt32()
        header_size = self.reader.readUInt32()

        self.reader.seek(header_size + 4)
        compressed_size = self.reader.readUInt32()
        zstd_data = self.reader.readBytes(compressed_size)
        dctx = zstd.ZstdDecompressor()
        zstd_reader = BinaryReader(dctx.decompress(zstd_data))

        files = {}
        self.reader.seek(0x48)
        for _ in range(file_count):
            path_len = self.reader.readUInt32()
            file_path = self.reader.readString(path_len)
            self.reader.skip(4)
            file_size = self.reader.readUInt32()
            file_offset = self.reader.readUInt32()
            zstd_reader.seek(file_offset)
            files[file_path] = zstd_reader.readBytes(file_size)

        return files
