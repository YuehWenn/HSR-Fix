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

import re
import glob
import os
import shutil
import logging
import configparser
import warnings

global_config = configparser.ConfigParser()
global_config.read("global_config.ini", "utf-8")
config_folder = global_config["Global"]["config_folder"]

preset_config = configparser.ConfigParser()
preset_config.read(config_folder + '/preset.ini', 'utf-8')

tmp_config = configparser.ConfigParser()
tmp_config.read(config_folder + '/tmp.ini', 'utf-8')

vertex_config = configparser.ConfigParser()
vertex_attr_ini = preset_config["Merge"]["vertex_attr_ini"]
vertex_config.read(config_folder + '/' + vertex_attr_ini, 'utf-8')



class MergeInfo:
    # vertex buffer hash.
    draw_vb = None
    # index buffer hash,the index buffer hash you want to extract.
    draw_ib = None
    # if you use pointlist,it's root vs,if a game use pointlist tech,it's animation will load in root_vs.
    root_vs = None
    # the output ini file name,and need to be blender vb and ib file name,set a name for this ib part.
    part_name = None
    # if this object use pointlist tech,True or False, if true,use pointlist tech,if not,use trianglelist tech only.
    use_pointlist = None
    # if this object can only extract from pointlist.
    only_pointlist = None
    # define every element info from which vb slot,eg: POSITION from vb0 : info_location.position = "vb0"
    # if it is None,will ignore this element info.
    info_location = {}
    # based on the type to determine some setting eg:the format and length of BLENDINDICES
    # type must be one of these value: "cloth","weapon","item","body","hair"
    type = None
    # if multiple pointlist file appears,you can force to use a special pointlist file index.
    force_pointlist_index = None
    # the element list you want to extract,The vertex data you want to read from vb file.
    element_list = None


class HeaderInfo:
    file_index = None
    stride = None
    first_vertex = None
    vertex_count = None
    topology = None

    # Header have many semantic element,like POSITION,NORMAL,COLOR etc.
    elementlist = None


class Element:
    semantic_name = None
    semantic_index = None
    format = None
    input_slot = None
    aligned_byte_offset = None
    input_slot_class = None
    instance_data_step_rate = None

    # the order of the element,start from 0.
    element_number = None

    # the byte length of this Element's data.
    byte_width = None


class VertexData:
    vb_file_number = b"vb0"  # vb0
    index = None
    aligned_byte_offset = None
    element_name = None
    data = None

    def __init__(self, line_bytes=b""):
        if line_bytes != b"":
            line_str = str(line_bytes.decode())
            # vb_file_number = line_str.split("[")[0]
            # because we vb_merge into one file, so it always be vb0
            vb_file_number = "vb0"
            self.vb_file_number = vb_file_number.encode()

            tmp_left_index = line_str.find("[")
            tmp_right_index = line_str.find("]")
            index = line_str[tmp_left_index + 1:tmp_right_index]
            self.index = index.encode()

            tmp_left_index = line_str.find("]+")
            aligned_byte_offset = line_str[tmp_left_index + 2:tmp_left_index + 2 + 3]
            self.aligned_byte_offset = aligned_byte_offset.encode()

            tmp_right_index = line_str.find(": ")
            element_name = line_str[tmp_left_index + 2 + 3 + 1:tmp_right_index]
            self.element_name = element_name.encode()

            tmp_left_index = line_str.find(": ")
            tmp_right_index = line_str.find("\r\n")
            data = line_str[tmp_left_index + 2:tmp_right_index]
            self.data = data.encode()

    def __str__(self):
        return self.vb_file_number + b"[" + self.index + b"]+" + self.aligned_byte_offset.decode().zfill(3).encode() + b" " + self.element_name + b": " + self.data + b"\r\n"


class VbFileInfo:
    header_info = HeaderInfo()
    vertex_data_chunk_list = [[VertexData()]]
    output_filename = None


def get_work_folder():
    LoaderFolder = preset_config["General"]["LoaderFolder"]
    FrameAnalyseFolder = preset_config["General"]["FrameAnalyseFolder"]
    WorkFolder = LoaderFolder + FrameAnalyseFolder + "/"
    return WorkFolder


def read_vertex_data_chunk_list_gracefully(file_index, input_info_location, only_vb1=False, sanity_check=False):
    # TODO 还得拆开，这一个步骤强依赖的变量太多了

    print("read_vertex_data_chunk_list_gracefully")
    print(input_info_location)
    # TODO only_vb1 is deprecated.
    input_element_list = list(input_info_location.keys())

    """
    :param file_index:  the file index numbers you want to process.
    :param read_element_list:  the element name list you need to read.
    :param only_vb1:  weather read only from vb slot 1 file.
    :param sanity_check: weather check the first line to remove duplicated content.
    :return:
    """
    WorkFolder = get_work_folder()


    # Get vb filenames by the file_index.
    if only_vb1:
        vb_filenames = sorted(get_filter_filenames(WorkFolder, file_index+ "-vb1", ".txt"))
    else:
        vb_filenames = sorted(get_filter_filenames(WorkFolder, file_index + "-vb", ".txt"))

    print("开始读取vertex-data部分：")
    print("file_index: " + str(file_index))
    print("vb_filenames: " + str(vb_filenames))

    topology, vertex_count = get_topology_vertexcount(WorkFolder + vb_filenames[0])

    vertex_data_chunk_list = [[] for i in range(int(str(vertex_count.decode())))]

    # temp vertex_data_chunk
    vertex_data_chunk = []

    chunk_index = 0

    logging.info("Note:the order of read must same as element list order.")
    logging.info("Rearange vb_filenames.")

    vb_filenames_rearrange = []
    for element in input_info_location:
        vb = input_info_location.get(element)
        for filename in vb_filenames:
            if vb in filename:
                if filename not in vb_filenames_rearrange:
                    vb_filenames_rearrange.append(filename)

    logging.info("重新排序后的顺序:")
    logging.info(vb_filenames_rearrange)

    for filename in vb_filenames_rearrange:
        # Get the vb file's slot number.
        vb_number = filename[filename.find("-vb"):filename.find("=")][1:].encode()

        # Open the vb file.
        vb_file = open(WorkFolder + filename, 'rb')
        # For temporarily record the last line.
        line_before_tmp = b"\r\n"

        vb_file_size = os.path.getsize(vb_file.name)
        while vb_file.tell() <= vb_file_size:
            # Read a line
            line = vb_file.readline()

            # Process vertexdata
            if line.startswith(vb_number):

                line_before_tmp = line

                vertex_data = VertexData(line)
                vertex_data_chunk.append(vertex_data)
                chunk_index = int(vertex_data.index.decode())

            # Process when meet the \r\n.
            if (line.startswith(b"\r\n") or vb_file.tell() == vb_file_size) and line_before_tmp.startswith(vb_number):

                line_before_tmp = b"\r\n"

                # If we got \r\n,it means this vertex_data_chunk as ended,so put it into the final vertex_data_chunk_list.
                vertex_data_chunk_list[chunk_index].append(vertex_data_chunk)

                # Reset temp VertexData
                vertex_data_chunk = []

            if vb_file.tell() == vb_file_size:
                break
        vb_file.close()

    # 看起来这里是把所有的vb0文件的所有的Vertexdata全部拿来了


    # Combine every chunk split part by corresponding index.
    new_vertex_data_chunk_list = []
    for vertex_data_chunk in vertex_data_chunk_list:
        new_vertex_data_chunk = []
        for vertex_data_chunk_split in vertex_data_chunk:
            for vertex_data in vertex_data_chunk_split:
                new_vertex_data_chunk.append(vertex_data)
        new_vertex_data_chunk_list.append(new_vertex_data_chunk)
    vertex_data_chunk_list = new_vertex_data_chunk_list

    # Check TEXCOORD and remove duplicated content.
    # TODO 这里要添加一种情况，那就是存在多个TEXCOORD的同时，所有TEXCOORD还都是0，0
    #  判断如果是TEXCOORD，则允许内容重复
    if sanity_check:
        vertex_data_chunk_check = vertex_data_chunk_list[0]
        # Count every time the different kind of data appears.
        repeat_value_time = {}
        for vertex_data in vertex_data_chunk_check:
            if repeat_value_time.get(vertex_data.data) is None:
                repeat_value_time[vertex_data.data] = 1
            else:
                repeat_value_time[vertex_data.data] = repeat_value_time[vertex_data.data] + 1

        # Decide the unique element_name by the data appears time.
        unique_element_names = []
        for vertex_data in vertex_data_chunk_check:
            # 这里新增了，认为所有的TEXCOORD都是独一无二的，经过测试，这样是行不通的
            # if repeat_value_time.get(vertex_data.data) == 1 or vertex_data.element_name.startswith(b"TEXCOORD"):
            if repeat_value_time.get(vertex_data.data) == 1:
                unique_element_names.append(vertex_data.element_name)

        # Retain vertex_data based on the unique element name.
        new_vertex_data_chunk_list = []
        for vertex_data_chunk in vertex_data_chunk_list:
            new_vertex_data_chunk = []
            for vertex_data in vertex_data_chunk:
                if vertex_data.element_name in unique_element_names:
                    new_vertex_data_chunk.append(vertex_data)
            new_vertex_data_chunk_list.append(new_vertex_data_chunk)
        vertex_data_chunk_list = new_vertex_data_chunk_list


    # Retain some content based on the input element_list.
    revised_vertex_data_chunk_list = []
    for index in range(len(vertex_data_chunk_list)):
        vertex_data_chunk = vertex_data_chunk_list[index]
        new_vertex_data_chunk = []
        for vertex_data in vertex_data_chunk:
            if vertex_data.element_name in input_element_list:
                new_vertex_data_chunk.append(vertex_data)
        revised_vertex_data_chunk_list.append(new_vertex_data_chunk)

    return revised_vertex_data_chunk_list


def output_vb_file(vb_file_info):
    header_info = vb_file_info.header_info
    vertex_data_chunk_list = vb_file_info.vertex_data_chunk_list

    output_filename = vb_file_info.output_filename
    logging.info("Starting output to file: " + output_filename)

    logging.info("Grab the first vertex_data, and judge which element exists.")
    vertex_data_chunk_test = vertex_data_chunk_list[0]
    print(vertex_data_chunk_test)
    vertex_data_chunk_has_element_list = []

    logging.info("Default we think all element does not exist,unless we detected it.")
    for vertex_data in vertex_data_chunk_test:
        vertex_data_chunk_has_element_list.append(vertex_data.element_name)

    logging.info("Get the element list which can be output.")
    header_info_has_element_list = []
    for element in header_info.elementlist:
        name = element.semantic_name
        if element.semantic_name == b"TEXCOORD" and element.semantic_index != b"0":
                name = element.semantic_name + element.semantic_index
        header_info_has_element_list.append(name)

    logging.info("Output to the final file.")
    output_file = open(output_filename, "wb+")

    logging.info("(1) First output header.")
    output_file.write(b"stride: " + header_info.stride + b"\r\n")
    output_file.write(b"first vertex: " + header_info.first_vertex + b"\r\n")
    output_file.write(b"vertex count: " + header_info.vertex_count + b"\r\n")
    output_file.write(b"topology: " + header_info.topology + b"\r\n")

    logging.info("(2) Traversal elementlist,if element exists then output it.")
    element_list = header_info.elementlist
    for element in element_list:
        element_name = element.semantic_name
        semantic_index = element.semantic_index
        if element_name == b"TEXCOORD":
            if semantic_index != b'0':
                element_name = element_name + semantic_index

        if vertex_data_chunk_has_element_list.__contains__(element_name):
            # print("Detected："+str(element_name))
            # Output the corroesponding element.
            output_file.write(b"element[" + element.element_number + b"]:" + b"\r\n")
            output_file.write(b"  SemanticName: " + element.semantic_name + b"\r\n")
            output_file.write(b"  SemanticIndex: " + element.semantic_index + b"\r\n")
            output_file.write(b"  Format: " + element.format + b"\r\n")
            output_file.write(b"  InputSlot: " + element.input_slot + b"\r\n")
            output_file.write(b"  AlignedByteOffset: " + element.aligned_byte_offset + b"\r\n")
            output_file.write(b"  InputSlotClass: " + element.input_slot_class + b"\r\n")
            output_file.write(b"  InstanceDataStepRate: " + element.instance_data_step_rate + b"\r\n")

    logging.info("(3) Write the vertex-data part.")
    output_file.write(b"\r\n")
    output_file.write(b"vertex-data:\r\n")
    output_file.write(b"\r\n")

    logging.info("Before we output the vertex data part,we need to make sure the order of element is right, "
                 "so we can split it correctly later,This process should be done in read process.")
    logging.info("Show header_info_has_element_list: ")
    logging.info(header_info_has_element_list)

    logging.info("It's element_name must appear in header_info_has_element_list,otherwise it can't be output.")
    for index in range(len(vertex_data_chunk_list)):
        vertex_data_chunk = vertex_data_chunk_list[index]

        for vertex_data in vertex_data_chunk:
            if vertex_data.element_name in header_info_has_element_list:
                output_file.write(vertex_data.__str__())

        if index != len(vertex_data_chunk_list) - 1:
            # logging.info("it is the final line ,we need to append a line break.")
            output_file.write(b"\r\n")

    output_file.close()


def move_related_files(indices, output_folder, move_dds=False, only_pst7=False, move_vscb=False, move_pscb=False):

    """
    :param indices:  the file indix you want to move
    :param move_dds: weather move dds file.
    :param only_pst7: weather only move ps-t7 dds file.
    :param move_vscb:
    :param move_pscb:
    :return:
    """

    if move_dds:
        logging.info("----------------------------------------------------------------")
        logging.info("Start to move .dds files.")
        # Start to move .dds files.
        if only_pst7:
            filenames = get_filter_filenames(get_work_folder(),"ps-t0",".dds")
        else:
            filenames = get_filter_filenames(get_work_folder(),"ps-t",".dds")

        print(filenames)

        for filename in filenames:
            if os.path.exists(get_work_folder()+ filename):
                for index in indices:
                    if filename.__contains__(index):
                        logging.info("Moving ： " + filename + " ....")

                        shutil.copy2(get_work_folder()+ filename, output_folder + filename)

    if move_vscb:
        logging.info("----------------------------------------------------------------")
        logging.info("Start to move VS-CB files.")
        # Start to move VS-CB files.
        filenames = get_filter_filenames(get_work_folder(), "vs-cb", "")

        for filename in filenames:
            if os.path.exists(filename):
                # Must have the vb index you sepcified.
                for index in indices:
                    if filename.__contains__(index):
                        logging.info("Moving ： " + filename + " ....")
                        shutil.copy2(get_work_folder()+filename, output_folder + filename)

    if move_pscb:
        logging.info("----------------------------------------------------------------")
        logging.info("Start to move PS-CB files.")
        # Start to move PS-CB files.
        filenames = glob.glob('*ps-cb*')
        filenames = get_filter_filenames(get_work_folder(), "ps-cb", "")

        for filename in filenames:
            if os.path.exists(filename):
                # Must have the vb index you sepcified.
                for index in indices:
                    if filename.__contains__(index):
                        logging.info("Moving ： " + filename + " ....")

                        shutil.copy2(get_work_folder()+filename, output_folder + filename)


def get_topology_vertexcount(filename):
    ib_file = open(filename, "rb")
    ib_file_size = os.path.getsize(filename)
    get_topology = None
    get_vertex_count = None
    count = 0
    while ib_file.tell() <= ib_file_size:
        line = ib_file.readline()
        # Because topology only appear in the first 5 line,so if count > 5 ,we can stop looking for it.
        count = count + 1
        if count > 5:
            break
        if line.startswith(b"vertex count: "):
            get_vertex_count = line[line.find(b"vertex count: ") + b"vertex count: ".__len__():line.find(b"\r\n")]

        if line.startswith(b"topology: "):
            topology = line[line.find(b"topology: ") + b"topology: ".__len__():line.find(b"\r\n")]
            if topology == b"pointlist":
                get_topology = b"pointlist"
                break
            if topology == b"trianglelist":
                get_topology = b"trianglelist"
                break

    # Safely close the file.
    ib_file.close()
    logging.info("Get Topology:" + str(get_topology))
    logging.info("Get VertexCount:" + str(get_vertex_count))

    return get_topology, get_vertex_count


def get_attribute_from_txtfile(filename,attribute):
    file = open(get_work_folder()+ filename, "rb")
    filesize = os.path.getsize(get_work_folder()+filename)

    attribute_name = str(attribute + ": ").encode()
    attribute_value = None
    count = 0
    while file.tell() <= filesize:
        line = file.readline()
        # Because topology only appear in the first 5 line,so if count > 5 ,we can stop looking for it.
        count = count + 1
        if count > 5:
            break
        if line.startswith(attribute.encode()):
            attribute_value = line[line.find(attribute_name) + attribute_name.__len__():line.find(b"\r\n")]

    # Safely close the file.
    file.close()

    # return value we get.
    return attribute_value


def get_first_index_in_ibfile(filename):
    ib_file = open(get_work_folder()+ filename, "rb")
    ib_file_size = os.path.getsize(get_work_folder()+filename)
    get_topology = None
    get_first_index = None
    count = 0
    while ib_file.tell() <= ib_file_size:
        line = ib_file.readline()
        # Because topology only appear in the first 5 line,so if count > 5 ,we can stop looking for it.
        count = count + 1
        if count > 5:
            break
        if line.startswith(b"first index: "):
            get_first_index = line[line.find(b"first index: ") + b"first index: ".__len__():line.find(b"\r\n")]

    # Safely close the file.
    ib_file.close()
    logging.info("Get first index:" + str(get_topology))

    return get_first_index


def get_unique_ib_bytes_by_indices(indices):
    ib_filenames = []
    for index in range(len(indices)):
        indexnumber = indices[index]
        ib_filename = sorted(get_filter_filenames(get_work_folder(),str(indexnumber) + "-ib",".txt"))[0]
        ib_filenames.append(ib_filename)

    ib_file_bytes = []
    ib_file_first_index_list = []
    for ib_filename in ib_filenames:
        first_index = get_first_index_in_ibfile(ib_filename)

        with open(get_work_folder()+ ib_filename, "rb") as ib_file:
            bytes = ib_file.read()
            if bytes not in ib_file_bytes:
                ib_file_bytes.append(bytes)

                # also need [first index] info to generate the .ini file.
                if first_index not in ib_file_first_index_list:
                    ib_file_first_index_list.append(first_index)

    # 这里必须得重新排序
    original_dict = {}
    for num in range(len(ib_file_first_index_list)):
        first_index = ib_file_first_index_list[num]
        ib_bytes = ib_file_bytes[num]
        original_dict[first_index] = ib_bytes

    order_first_index_list = sorted(original_dict.keys())
    ordered_dict = {}
    for first_index in order_first_index_list:
        ib_bytes = original_dict.get(first_index)
        ordered_dict[first_index] = ib_bytes

    ib_file_first_index_list = list(ordered_dict.keys())
    ib_file_bytes = list(ordered_dict.values())

    print("重新排序后的list")
    print(ib_file_first_index_list)
    return ib_file_bytes, ib_file_first_index_list


def get_header_info_by_elementnames(output_element_list):

    header_info = HeaderInfo()
    # 1.Generate element_list.
    element_list = []
    for element_name in output_element_list:
        element = Element()
        element.semantic_name = element_name

        print(vertex_config)
        element.input_slot = vertex_config[element_name.decode()]["input_slot"].encode()
        element.input_slot_class = vertex_config[element_name.decode()]["input_slot_class"].encode()
        element.instance_data_step_rate = vertex_config[element_name.decode()]["instance_data_step_rate"].encode()

        element.semantic_index = vertex_config[element_name.decode()]["semantic_index"].encode()
        element.format = vertex_config[element_name.decode()]["format"].encode()
        element.byte_width = vertex_config[element_name.decode()].getint("byte_width")

        element_list.append(element)

    # 2.Calculate aligned_byte_offset and element_number.
    new_element_list = []
    aligned_byte_offset = 0
    for index in range(len(element_list)):
        element = element_list[index]
        element.element_number = str(index).encode()
        element.aligned_byte_offset = str(aligned_byte_offset).encode()
        aligned_byte_offset = aligned_byte_offset + element.byte_width
        new_element_list.append(element)

    # 3.Set element_list and stride.
    header_info.first_vertex = b"0"
    header_info.topology = b"trianglelist"
    header_info.stride = str(aligned_byte_offset).encode()
    header_info.elementlist = new_element_list

    return header_info


def get_filter_vb_indices(target_folder, vb_number ):
    dump_files = os.listdir(target_folder)

    indices = []
    for filename in dump_files:
        if vb_number in filename and filename.endswith(".txt"):
            index = filename.split(vb_number)[0]
            indices.append(index)
    return indices


def get_filter_filenames(target_folder,key, endstr):
    dump_files = os.listdir(target_folder)
    filenames = []
    for filename in dump_files:
        if key in filename and filename.endswith(endstr):
            filenames.append(filename)
    return filenames
