from PIL import Image, ImageFile


def _accept(prefix):
    return prefix[:4] == b"RW2"


class RW2ImageFile(ImageFile.ImageFile):

    format = "IIU"
    format_description = "Panasonic RW2 raw image"

    def _open(self):

        header = self.fp.read(128).split()

        # size in pixels (width, height)
        self._size = int(header[1]), int(header[2])

        # mode setting
        bits = int(header[3])
        if bits == 1:
            self.mode = "1"
        elif bits == 8:
            self.mode = "L"
        elif bits == 24:
            self.mode = "RGB"
        else:
            raise SyntaxError("unknown number of bits")

        # data descriptor
        self.tile = [("raw", (0, 0) + self.size, 128, (self.mode, 0, 1))]


Image.register_open(RW2ImageFile.format, RW2ImageFile, _accept)

Image.register_extensions(RW2ImageFile.format, [
    ".RW2",
    ".rwt",  # DOS version
])