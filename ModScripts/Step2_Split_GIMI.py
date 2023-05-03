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
            # Here you must notice!
            # GIMI use R32 will need 1H,but we use R16 will nead H
            ib += struct.pack('H', struct.unpack('H', data[i:i+2])[0]+offset)
            i += 2
    return ib


def collect_vb(vb_file_name, stride, ignore_tangent=True):
    # GIMI use POSITION -> BLEND -> TEXCOORD in vb file
    # but my script use POSITION -> TEXCOORD -> BLEND in vb file.
    # TODO，现在这里是写死的，测试成功后改成动态读取计算
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

            texcoord += data[i + 40:i + 40 + 20]
            blend += data[i+60:i+stride]
            i += stride
    return position, blend, texcoord


if __name__ == "__main__":
    """
    This split script is copied from GIMI project with some little change to fit our script.
    """
    SplitFolder = "C:/Program Files/Star Rail/Game/Mods/output/"

    vertex_config = configparser.ConfigParser()
    vertex_config.read('configs/vertex_attr_body.ini')
    preset_config = configparser.ConfigParser()
    preset_config.read('configs/preset.ini', "utf-8")
    tmp_config = configparser.ConfigParser()
    tmp_config.read('configs/tmp.ini')

    part_names = tmp_config["Ini"]["part_names"].split(",")
    repair_tangent = preset_config["Split"]["repair_tangent"]

    # calculate the stride
    element_list = preset_config["Merge"]["element_list"].split(",")
    # first,calculat the byte_width
    byte_width_list = []
    stride = 0
    for element in element_list:
        byte_width = int(vertex_config[element].getint("byte_width"))
        byte_width_list.append(byte_width)
        stride = stride + byte_width

    # collect vb
    offset = 0
    position_buf, blend_buf, texcoord_buf = bytearray(), bytearray(), bytearray()
    # vb filename
    for part_name in part_names:

        vb_filename = SplitFolder + part_name + ".vb"
        position_bytearray, blend_bytearray, texcoord_bytearray = collect_vb(vb_filename, stride, ignore_tangent=True)
        position_buf += position_bytearray
        blend_buf += blend_bytearray
        texcoord_buf += texcoord_bytearray

        # collect ib
        ib_filename = SplitFolder + part_name + ".ib"
        ib_buf = collect_ib(ib_filename, offset)
        with open(SplitFolder + part_name + "_new.ib", "wb") as ib_buf_file:
            ib_buf_file.write(ib_buf)

        # After collect ib, set offset for the next time's collect
        offset = len(position_buf) // 40
        print(offset)

    # write vb buf to file.
    mod_name = preset_config["General"]["mod_name"]
    with open(SplitFolder + mod_name + "_POSITION.buf","wb") as position_buf_file:
        position_buf_file.write(position_buf)
    with open(SplitFolder + mod_name + "_BLEND.buf","wb") as blend_buf_file:
        blend_buf_file.write(blend_buf)
    with open(SplitFolder + mod_name + "_TEXCOORD.buf","wb") as texcoord_buf_file:
        texcoord_buf_file.write(texcoord_buf)

    # TODO set the draw number,because the draw tech broke in HSR,so i don't think we need this.
    draw_numbers = ""
    draw_numbers = draw_numbers[0:len(draw_numbers) - 1]
    tmp_config.set("Ini", "draw_numbers", draw_numbers)
    tmp_config.write(open("configs/tmp.ini", "w"))

    print("----------------------------------------------------------\r\nAll process done！")

