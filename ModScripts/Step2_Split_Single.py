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
import configparser


def split_file(source_name, repair_tangent=None):
    """
    About source_name:
    This is the .vb and .ib filename you want to split, need to specify by yourself.

    :return: None
    """

    vb_name = source_name + ".vb"
    vb_file = open(SplitFolder + vb_name, "rb")
    vb_file_buffer = vb_file.read()
    vb_file.close()

    element_name_list = preset_config["Merge"]["element_list"].split(",")

    fmt_stride = 0
    # strides
    width_list = []
    # aligned_byte_offsets
    aligned_byte_offsets = []
    for element in element_name_list:
        aligned_byte_offsets.append(fmt_stride)
        byte_width = vertex_config[element].getint("byte_width")
        fmt_stride = fmt_stride + byte_width
        width_list.append(byte_width)

    print("width_list:")
    print(width_list)

    # vertex_data的数量
    vertex_count = int(len(vb_file_buffer) / fmt_stride)
    print("vb file vertex_count:" + str(vertex_count))



    # use to store parsed vertex_data.
    vertex_data_list = [[] for i in range(vertex_count)]

    # parse vertex_data,load into vertex_data_list.
    for index in range(len(width_list)):
        for i in range(vertex_count):
            start_index = i * fmt_stride + aligned_byte_offsets[index]
            vertex_data = vb_file_buffer[start_index:start_index + width_list[index]]
            vertex_data_list[i].append(vertex_data)
    print(vertex_data_list)

    if repair_tangent == "simple":
        # TODO need to repair the TANGENT
        pass

    if repair_tangent == "nearest":
        # TODO need to repair the TANGENT
        pass

    position_vertex_data = [[] for i in range(vertex_count)]
    blend_vertex_data = [[] for i in range(vertex_count)]
    texcoord_vertex_data = [[] for i in range(vertex_count)]

    for index in range(len(width_list)):
        for i in range(vertex_count):
            if element_name_list[index] in ["POSITION", "NORMAL", "TANGENT"]:
                position_vertex_data[i].append(vertex_data_list[i][index])

            if element_name_list[index] in ["BLENDWEIGHTS", "BLENDINDICES"]:
                blend_vertex_data[i].append(vertex_data_list[i][index])

            if element_name_list[index] in ["TEXCOORD", "TEXCOORD1", "COLOR"]:
                texcoord_vertex_data[i].append(vertex_data_list[i][index])

    position_bytes = b""
    for vertex_data in position_vertex_data:
        for data in vertex_data:
            position_bytes = position_bytes + data

    position_stride = 40
    pisition_valid = len(position_bytes) % position_stride
    if pisition_valid != 0:
        print("position bytes length not valid !")

    position_length = len(position_bytes) / position_stride
    print("position_bytes length / "+str(position_stride) +": ")
    print(int(position_length))

    blend_bytes = b""
    for vertex_data in blend_vertex_data:
        for data in vertex_data:
            blend_bytes = blend_bytes + data

    texcoord_bytes = b""
    for vertex_data in texcoord_vertex_data:
        for data in vertex_data:
            texcoord_bytes = texcoord_bytes + data

    output_position_filename = source_name + "_POSITION.buf"
    output_blend_filename = source_name + "_BLEND.buf"
    output_texcoord_filename = source_name + "_TEXCOORD.buf"

    with open(SplitFolder + output_position_filename, "wb+") as output_position_file:
        output_position_file.write(position_bytes)
    with open(SplitFolder + output_blend_filename, "wb+") as output_blend_file:
        output_blend_file.write(blend_bytes)
    with open(SplitFolder + output_texcoord_filename, "wb+") as output_texcoord_file:
        output_texcoord_file.write(texcoord_bytes)

    # return position_length as draw_number
    return position_length


if __name__ == "__main__":
    # set work dir.
    SplitFolder = "C:/Program Files/Star Rail/Game/output/"

    # TODO 暂时测试身体的，后续再测试武器的
    vertex_config = configparser.ConfigParser()
    vertex_config.read('configs/vertex_attr_body.ini')

    # get the element list need to split.
    preset_config = configparser.ConfigParser()
    preset_config.read('configs/preset.ini',"utf-8")

    # get the part's name which need to be split.
    tmp_config = configparser.ConfigParser()
    tmp_config.read('configs/tmp.ini')
    part_names = tmp_config["Ini"]["part_names"].split(",")

    repair_tangent = preset_config["Split"]["repair_tangent"]

    draw_numbers = ""
    for part_name in part_names:
        print("Processing " + part_name + ".vb")
        draw_number = split_file(part_name, repair_tangent=repair_tangent)
        draw_numbers = draw_numbers + str(int(draw_number)) + ","
    draw_numbers = draw_numbers[0:len(draw_numbers)-1]
    tmp_config.set("Ini","draw_numbers", draw_numbers)
    tmp_config.write(open("configs/tmp.ini", "w"))

    print("----------------------------------------------------------\r\nAll process done！")

