"""
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
import struct


def collect_ib(filename, offset):
    ib = bytearray()
    with open(filename, "rb") as f:
        data = f.read()
        data = bytearray(data)
        i = 0
        while i < len(data):
            ib += struct.pack('1H', struct.unpack('1H', data[i:i+2])[0]+offset)
            i += 2
    return ib


def collect_vb(vb_file_name, stride, ignore_tangent=True):
    position = bytearray()
    blend = bytearray()
    texcoord = bytearray()
    with open(vb_file_name, "rb") as f:
        data = f.read()
        data = bytearray(data)
        i = 0
        while i < len(data):
            # This gave me a lot of trouble - the "tangent" the game uses doesn't seem to be any sort of tangent I'm
            #   familiar with. In fact, it has a lot more in common with the normal
            # Setting this equal to the normal gives significantly better results in most cases than using the tangent
            #   calculated by blender
            if ignore_tangent:
                # POSITION NORMAL
                position += data[i:i + 24]
                # TANGENT recalculate
                position += data[i+12:i+24] + bytearray(struct.pack("f", 1))
            else:
                position += data[i:i+40]
            blend += data[i+40:i+72]
            texcoord += data[i+72:i+stride]
            i += stride
    return position, blend, texcoord


def split_GIMI(source_name, repair_tangent=None):

    pass


if __name__ == "__main__":
    """
    This split script is copied from GIMI project with some little change.
    """
    pass