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
import configparser


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


if __name__ == "__main__":
    """
    This split script is copied from GIMI project with some little change.
    """
    SplitFolder = "C:/Program Files/Star Rail/Game/output/"

    vertex_config = configparser.ConfigParser()
    vertex_config.read('configs/vertex_attr_body.ini')
    preset_config = configparser.ConfigParser()
    preset_config.read('configs/preset.ini', "utf-8")
    tmp_config = configparser.ConfigParser()
    tmp_config.read('configs/tmp.ini')

    part_names = tmp_config["Ini"]["part_names"].split(",")
    repair_tangent = preset_config["Split"]["repair_tangent"]

    # TODO 计算步长
    element_list = preset_config["Merge"]["element_list"].split(",")
    # TODO 计算总stride需要每个的byte_width
    byte_width_list = []
    stride = 0
    for element in element_list:
        byte_width = int(vertex_config[element].getint("byte_width"))
        byte_width_list.append(byte_width)
        stride = stride + byte_width
    # TODO 收集vb
    offset = 0
    position_buf, blend_buf, texcoord_buf = bytearray(), bytearray(), bytearray()
    # vb filename
    for part_name in part_names:
        vb_filename = SplitFolder + part_name + ".vb"
        position_bytearray, blend_bytearray, texcoord_bytearray = collect_vb(vb_filename, stride, ignore_tangent=True)
        position_buf += position_bytearray
        blend_buf += blend_bytearray
        texcoord_buf += texcoord_bytearray

    mod_name = preset_config["General"]["mod_name"]
    with open(SplitFolder + mod_name + "_POSITION.buf","wb") as position_buf_file:
        position_buf_file.write(position_buf)
    with open(SplitFolder + mod_name + "_BLEND.buf","wb") as blend_buf_file:
        blend_buf_file.write(blend_buf)
    with open(SplitFolder + mod_name + "_TEXCOORD.buf","wb") as texcoord_buf_file:
        texcoord_buf_file.write(texcoord_buf)

    # TODO 收集ib，在测试收集ib之前，先测试这样做出的mod能不能用



    draw_numbers = ""
    draw_numbers = draw_numbers[0:len(draw_numbers) - 1]
    tmp_config.set("Ini", "draw_numbers", draw_numbers)
    tmp_config.write(open("configs/tmp.ini", "w"))

    print("----------------------------------------------------------\r\nAll process done！")

