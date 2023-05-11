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
import time

from MergeUtil import *
import logging
import time
import configparser

preset_config = configparser.ConfigParser()
preset_config.read('configs/preset.ini', 'utf-8')

tmp_config = configparser.ConfigParser()
tmp_config.read('configs/tmp.ini', 'utf-8')

vertex_config = configparser.ConfigParser()
if preset_config["Merge"]["type"] == "weapon":
    vertex_config.read('configs/vertex_attr_weapon.ini', 'utf-8')
else:
    vertex_attr_body_filename = preset_config["General"]["vertex_attr_filename"]
    vertex_config.read('configs/' + vertex_attr_body_filename, 'utf-8')

def get_pointlit_and_trianglelist_indices_V2():
    draw_ib = preset_config["Merge"]["draw_ib"]
    root_vs = preset_config["Merge"]["root_vs"]
    use_pointlist = preset_config["Merge"]["use_pointlist"]

    logging.info("执行函数：get_pointlit_and_trianglelist_indices_V2(HSR)")
    logging.info("开始读取所有vb0文件的index列表：")

    indices = get_filter_vb_indices(WorkFolder,"-vb0")

    pointlist_indices_dict = {}
    trianglelist_indices_dict = {}
    """
    format:
    {index:vertex count,index2,vertex count2,...}
    """

    trianglelist_vertex_count = b"0"

    # 1.First, grab all vb0 file's indices.
    for index in range(len(indices)):

        vb0_filename = get_filter_filenames(WorkFolder,indices[index] + "-vb0",".txt")[0]

        logging.info("当前处理的vb0文件：" + vb0_filename)
        topology, vertex_count = get_topology_vertexcount(WorkFolder + vb0_filename)
        logging.info("当前vb0文件的topology：" + str(topology))
        logging.info("当前vb0文件的vertex_count：" + str(vertex_count))

        if topology == b"pointlist":
            # print("index: " + str(indices[index]) + " VertexCount = " + str(vertex_count))

            # Filter, vb0 filename must have ROOT VS.
            if use_pointlist:
                if root_vs in vb0_filename:
                    pointlist_indices_dict[indices[index]] = vertex_count
            else:
                pointlist_indices_dict[indices[index]] = vertex_count

        ib_filename = get_filter_filenames(WorkFolder,indices[index] + "-ib", ".txt")[0]
        logging.info("当前处理的ib文件：" + ib_filename)

        topology, vertex_count = get_topology_vertexcount(WorkFolder + ib_filename)
        logging.info("当前ib文件的topology： "+str(topology))
        logging.info("当前ib文件的vertex_count： "+str(vertex_count))
        logging.info(split_str)

        if topology == b"trianglelist":
            # Filter,ib filename must include input_ib_hash.
            # print(draw_ib)
            # print(ib_filename)
            if draw_ib in ib_filename:
                topology, vertex_count = get_topology_vertexcount(WorkFolder + vb0_filename)
                print(indices[index])
                trianglelist_indices_dict[(indices[index])] = vertex_count

                """
                在所有的游戏中，即使一个index buffer中出现了多个index的多个vertex count,
                只有最大的那个vertex count是整个index buffer的
                """
                vertex_count_int = int.from_bytes(vertex_count, "big")
                trianglelist_vertex_count_int = int.from_bytes(trianglelist_vertex_count, "big")

                logging.info("vertex_count_int:")
                logging.info(vertex_count_int)
                logging.info("trianglelist_vertex_count_int:")
                logging.info(trianglelist_vertex_count_int)

                if vertex_count_int >= trianglelist_vertex_count_int:
                    trianglelist_vertex_count = vertex_count
                    logging.info(trianglelist_vertex_count)

    logging.info("Based on vertex count, remove the duplicated pointlist indices.")
    logging.info("output pointlist and trianglelist before remove:")
    logging.info(pointlist_indices_dict)
    logging.info(trianglelist_indices_dict)

    # 输出一下vertex_count，看看是否正常
    logging.info(trianglelist_vertex_count)

    # 注意，星穹铁道中相同的pointlist会出现两次，且数值完全一样
    pointlist_indices = []
    trianglelist_indices = []
    for pointlist_index in pointlist_indices_dict:
        if pointlist_indices_dict.get(pointlist_index) == trianglelist_vertex_count:
            pointlist_indices.append(pointlist_index)

    for trianglelist_index in trianglelist_indices_dict:
        trianglelist_indices.append(trianglelist_index)

    logging.info("indices全部处理完毕")
    logging.info("----------------------------------------------------------")
    logging.info("Pointlist vb indices: " + str(pointlist_indices))
    logging.info("Trianglelist vb indices: " + str(trianglelist_indices))
    logging.info("函数：get_pointlit_and_trianglelist_indices_v2执行完成")

    return pointlist_indices, trianglelist_indices


def save_output_ini_body_BH3(pointlist_indices, trianglelist_indices, merge_info=MergeInfo()):
    # don't care if pointlist_indices has many candidates,because we only use one of them
    # because they are totally same,just show twice in pointlist files.

    # TODO 这里要从配置文件中决定，position_vb在哪个槽，其他的在哪个槽等等，要自动生成
    #  现在需要测试trianglelist的生成
    position_slot = preset_config["Slot"]["position_slot"]
    texcoord_slot = preset_config["Slot"]["texcoord_slot"]
    blend_slot = preset_config["Slot"]["blend_slot"]

    pointlist_filenames = sorted(get_filter_filenames(WorkFolder,pointlist_indices[0] + "-vb", ".txt"))
    position_vb = pointlist_filenames[int(position_slot[2:3])]
    position_vb = position_vb[position_vb.find("-" + position_slot + "=") + 5:position_vb.find("-vs=")]
    blend_vb = pointlist_filenames[int(blend_slot[2:3])]
    blend_vb = blend_vb[blend_vb.find("-" + blend_slot + "=") + 5:blend_vb.find("-vs=")]

    trianglelist_filenames = sorted(get_filter_filenames(WorkFolder, trianglelist_indices[0] + "-vb", ".txt"))
    texcoord_vb = trianglelist_filenames[int(texcoord_slot[2:3])]
    print(texcoord_vb)
    texcoord_vb = texcoord_vb[texcoord_vb.find("-" + texcoord_slot + "=") + 5:texcoord_vb.find("-vs=")]

    tmp_config.set("Ini", "position_vb", position_vb)
    tmp_config.set("Ini", "blend_vb", blend_vb)
    tmp_config.set("Ini", "texcoord_vb", texcoord_vb)


    element_list = merge_info.info_location.keys()

    position_stride = 0
    texcoord_stride = 0
    blend_stride = 0


    for element in element_list:
        byte_width = vertex_config[element.decode()].getint("byte_width")
        print(byte_width)
        print("---------")

        # TODO 现在是获取元素名称，默认从对应槽位读取，应该改为
        #  应该从vertex_attr_body中就能直接读取对应的槽位，根据槽位放到对应的步长里面
        if vertex_config[element.decode()]["replace_slot"] == "position":
            position_stride = position_stride + byte_width

        if vertex_config[element.decode()]["replace_slot"] == "texcoord":
            texcoord_stride = texcoord_stride + byte_width

        if vertex_config[element.decode()]["replace_slot"] == "blend":
            blend_stride = blend_stride + byte_width

    tmp_config.set("Ini", "position_stride", str(position_stride))
    tmp_config.set("Ini", "texcoord_stride", str(texcoord_stride))
    tmp_config.set("Ini", "blend_stride", str(blend_stride))


    # 保存
    tmp_config.write(open("configs/tmp.ini","w"))


def save_output_ini_body(pointlist_indices, merge_info=MergeInfo()):
    # don't care if pointlist_indices has many candidates,because we only use one of them
    # because they are totally same,just show twice in pointlist files.
    filenames = sorted(get_filter_filenames(WorkFolder,pointlist_indices[0] + "-vb",".txt"))



    position_vb = filenames[0]
    position_vb = position_vb[position_vb.find("-vb0=") + 5:position_vb.find("-vs=")]

    texcoord_vb = filenames[1]
    texcoord_vb = texcoord_vb[texcoord_vb.find("-vb1=") + 5:texcoord_vb.find("-vs=")]

    blend_vb = filenames[2]
    blend_vb = blend_vb[blend_vb.find("-vb2=") + 5:blend_vb.find("-vs=")]

    tmp_config.set("Ini", "position_vb", position_vb)
    tmp_config.set("Ini", "texcoord_vb", texcoord_vb)
    tmp_config.set("Ini", "blend_vb", blend_vb)



    element_list = merge_info.info_location.keys()

    position_stride = 0
    texcoord_stride = 0
    blend_stride = 0

    for element in element_list:
        byte_width = vertex_config[element.decode()].getint("byte_width")
        print(byte_width)
        print("---------")
        if merge_info.info_location.get(element) == "vb0":
            position_stride = position_stride + byte_width
        if merge_info.info_location.get(element) == "vb1":
            texcoord_stride = texcoord_stride + byte_width
        if merge_info.info_location.get(element) == "vb2":
            blend_stride = blend_stride + byte_width

    tmp_config.set("Ini", "position_stride", str(position_stride))
    tmp_config.set("Ini", "texcoord_stride", str(texcoord_stride))
    tmp_config.set("Ini", "blend_stride", str(blend_stride))


    # 保存
    tmp_config.write(open("configs/tmp.ini","w"))


def merge_pointlist_trianglelist_files(pointlist_indices, trianglelist_indices, merge_info, texcoord_trianglelist=True):
    # TODO 崩坏三读取方法
    part_name = preset_config["Merge"]["part_name"]
    read_pointlist_element_list = merge_info.info_location.keys()

    logging.info("Start to move ps-t0 files to output folder.")
    # now we move all ps-t*
    move_related_files(trianglelist_indices, preset_config["General"]["OutputFolder"], move_dds=True, only_pst7=False)
    logging.info(split_str)

    logging.info("Start to read info from pointlist vb files.")
    logging.info("The elements need to read is: " + str(read_pointlist_element_list))

    # split the info_location
    pointlist_info_location = {}
    trianglelist_info_location = {}

    element_names = preset_config["Merge"]["element_list"].split(",")
    for element_name in element_names:
        if vertex_config[element_name]["extract_tech"] == "pointlist":
            pointlist_info_location[element_name.encode()] = vertex_config[element_name]["extract_vb_file"]

        if vertex_config[element_name]["extract_tech"] == "trianglelist":
            trianglelist_info_location[element_name.encode()] = vertex_config[element_name]["extract_vb_file"]

    # print(pointlist_info_location)
    # print(trianglelist_info_location)
    pointlist_vertex_data_chunk_list = read_vertex_data_chunk_list_gracefully(pointlist_indices[0],
                                                                              pointlist_info_location)

    # print(pointlist_vertex_data_chunk_list[1])
    # TODO we need to decide which trianglelist index to use,for default we use the vs 82b7eb5d0e45e0f5
    #  首先要获取准确的步长，根据步长才能正确的推断出
    #  遍历所有trianglelistindices对应的vb1(槽位) 的stride信息
    #  好像不用，目前可以确定，cc018b922a74a180是角色最后一次渲染的VS，所以从那个文件拿到的数据应该就能用
    #  只要在读取的时候做控制就好了


    final_trianglelist_indices = []
    for index in trianglelist_indices:
        filenames = get_filter_filenames(WorkFolder, index, ".txt")
        for filename in filenames:
            if "-vb1" in filename and filename.endswith(".txt"):
                # TODO read from config file.
                if preset_config["Merge"]["outline_vs"] in filename:
                    final_trianglelist_indices.append(index)
    print(final_trianglelist_indices)
    triangle_vertex_data_chunk_list = read_vertex_data_chunk_list_gracefully(final_trianglelist_indices[0],
                                                                              trianglelist_info_location)
    print(triangle_vertex_data_chunk_list[0])
    print("xxxxxx")

    logging.info("Based on output_element_list，generate a final header_info.")
    header_info = get_header_info_by_elementnames(read_pointlist_element_list, merge_info.type)

    # Set vertex count
    header_info.vertex_count = str(len(pointlist_vertex_data_chunk_list)).encode()

    final_vertex_data_chunk_list = [[] for i in range(int(str(header_info.vertex_count.decode())))]
    for index in range(len(pointlist_vertex_data_chunk_list)):
        final_vertex_data_chunk_list[index] = final_vertex_data_chunk_list[index] + pointlist_vertex_data_chunk_list[
            index]
        final_vertex_data_chunk_list[index] = final_vertex_data_chunk_list[index] + triangle_vertex_data_chunk_list[
            index]

    logging.info("Solve TEXCOORD1 can't match the element's semantic name TEXCOORD problem.")

    # Get element_aligned_byte_offsets to a new format.
    # Before set the output header info ,we need to fix the semantic name equals TEXCOORD1 problem
    # This will cause vb0 file can not import into blender.
    element_aligned_byte_offsets = {}
    new_element_list = []
    for element in header_info.elementlist:
        logging.info("-----------------")
        logging.info(element.semantic_name)
        logging.info(element.semantic_index)
        element_aligned_byte_offsets[element.semantic_name] = element.aligned_byte_offset

        # Fix texcoord1 problem
        if element.semantic_name.startswith(b"TEXCOORD") and element.semantic_index != b"0":
            element.semantic_name = b"TEXCOORD"
        new_element_list.append(element)
    header_info.elementlist = new_element_list

    logging.info("Change aligned byte offset in vertex data")
    new_final_vertex_data_chunk_list = []
    for vertex_data_chunk in final_vertex_data_chunk_list:
        new_vertex_data_chunk = []
        for vertex_data in vertex_data_chunk:
            vertex_data.aligned_byte_offset = element_aligned_byte_offsets[vertex_data.element_name]
            new_vertex_data_chunk.append(vertex_data)
        new_final_vertex_data_chunk_list.append(new_vertex_data_chunk)
    final_vertex_data_chunk_list = new_final_vertex_data_chunk_list

    output_vb_fileinfo = VbFileInfo()
    output_vb_fileinfo.header_info = header_info
    output_vb_fileinfo.vertex_data_chunk_list = final_vertex_data_chunk_list


    ib_file_bytes, ib_file_first_index_list = get_unique_ib_bytes_by_indices(trianglelist_indices)

    logging.info("Save ini information to tmp.ini")
    # TODO 这里的trianglelist_indices是由前面计算得到的，所以需要修改
    save_output_ini_body_BH3(pointlist_indices, final_trianglelist_indices, merge_info)

    # Save the part_names and match_first_index to tmp.ini
    part_names = ""
    match_first_index = ""
    for num in range(len(ib_file_bytes)):
        output_partname = part_name + "_part" + str(num)
        part_names = part_names + output_partname

        first_index = ib_file_first_index_list[num]
        match_first_index = match_first_index + first_index.decode()

        if num != len(ib_file_bytes) -1:
            part_names = part_names + ","
            match_first_index = match_first_index + ","

    print("original order:")
    print(part_names)
    print(match_first_index)

    # we need to rearrange the order to compatible with split script.
    part_name_list = part_names.split(",")
    match_first_index_list = match_first_index.split(",")
    order_dict = {}
    for num in range(len(part_name_list)):
        part_name = part_name_list[num]
        first_index = int(match_first_index_list[num])
        order_dict[first_index] = part_name
    print("order_dict")
    print(order_dict)

    ordered_dict = {}

    for first_index in sorted(order_dict.keys()):
        print(first_index)
        ordered_dict[str(first_index)] = order_dict.get(first_index)
    print(ordered_dict)

    part_names = ""
    match_first_index = ""
    for first_index in ordered_dict:
        part_name = ordered_dict.get(first_index)
        part_names = part_names + part_name + ","
        match_first_index = match_first_index + first_index + ","

    part_names = part_names[0:len(part_names) -1]
    match_first_index = match_first_index[0:len(match_first_index) -1]
    print(part_names)
    print(match_first_index)

    tmp_config = configparser.ConfigParser()
    tmp_config.read('configs/tmp.ini')
    tmp_config.set("Ini", "part_names", part_names)
    tmp_config.set("Ini", "match_first_index", match_first_index)
    tmp_config.write(open("configs/tmp.ini", "w"))

    # Reset to use the correct order part name
    part_name_list = list(ordered_dict.values())
    print(part_name_list)
    logging.info("Output to file.")
    for index in range(len(ib_file_bytes)):

        ib_file_byte = ib_file_bytes[index]
        output_vbname = preset_config["General"]["OutputFolder"] + merge_info.draw_ib + "-" + part_name_list[index] + "-vb0.txt"
        output_ibname = preset_config["General"]["OutputFolder"] + merge_info.draw_ib + "-" + part_name_list[index] + "-ib.txt"
        output_vb_fileinfo.output_filename = output_vbname

        logging.info("Output Step 1: Write to ib file.")
        output_ibfile = open(output_ibname, "wb+")
        output_ibfile.write(ib_file_byte)
        output_ibfile.close()

        logging.info("Output Step 2: Write to vb file.")
        output_vb_file(output_vb_fileinfo)

        logging.info(split_str)



def merge_pointlist_files(pointlist_indices, trianglelist_indices, merge_info):
    part_name = preset_config["Merge"]["part_name"]
    read_pointlist_element_list = merge_info.info_location.keys()
    print(read_pointlist_element_list)

    logging.info("Start to move ps-t0 files to output folder.")
    # now we move all ps-t*
    move_related_files(trianglelist_indices, preset_config["General"]["OutputFolder"], move_dds=True, only_pst7=False)
    logging.info(split_str)

    logging.info("Start to read info from pointlist vb files(Only from pointlist files).")
    logging.info("The elements need to read is: " + str(read_pointlist_element_list))
    pointlist_vertex_data_chunk_list = read_vertex_data_chunk_list_gracefully(pointlist_indices[0],
                                                                              merge_info.info_location)
    logging.info("Based on output_element_list，generate a final header_info.")

    header_info = get_header_info_by_elementnames(read_pointlist_element_list, merge_info.type)
    # Set vertex count
    header_info.vertex_count = str(len(pointlist_vertex_data_chunk_list)).encode()

    final_vertex_data_chunk_list = [[] for i in range(int(str(header_info.vertex_count.decode())))]
    for index in range(len(pointlist_vertex_data_chunk_list)):
        final_vertex_data_chunk_list[index] = final_vertex_data_chunk_list[index] + pointlist_vertex_data_chunk_list[
            index]

    logging.info("Solve TEXCOORD1 can't match the element's semantic name TEXCOORD problem.")

    # Get element_aligned_byte_offsets to a new format.
    # Before set the output header info ,we need to fix the semantic name equals TEXCOORD1 problem
    # This will cause vb0 file can not import into blender.
    element_aligned_byte_offsets = {}
    new_element_list = []
    for element in header_info.elementlist:
        logging.info("-----------------")
        logging.info(element.semantic_name)
        logging.info(element.semantic_index)
        element_aligned_byte_offsets[element.semantic_name] = element.aligned_byte_offset

        # Fix texcoord1 problem
        if element.semantic_name.startswith(b"TEXCOORD") and element.semantic_index != b"0":
            element.semantic_name = b"TEXCOORD"
        new_element_list.append(element)
    header_info.elementlist = new_element_list

    logging.info("Change aligned byte offset in vertex data")
    new_final_vertex_data_chunk_list = []
    for vertex_data_chunk in final_vertex_data_chunk_list:
        new_vertex_data_chunk = []
        for vertex_data in vertex_data_chunk:
            vertex_data.aligned_byte_offset = element_aligned_byte_offsets[vertex_data.element_name]
            new_vertex_data_chunk.append(vertex_data)
        new_final_vertex_data_chunk_list.append(new_vertex_data_chunk)
    final_vertex_data_chunk_list = new_final_vertex_data_chunk_list

    output_vb_fileinfo = VbFileInfo()
    output_vb_fileinfo.header_info = header_info
    output_vb_fileinfo.vertex_data_chunk_list = final_vertex_data_chunk_list


    ib_file_bytes, ib_file_first_index_list = get_unique_ib_bytes_by_indices(trianglelist_indices)

    logging.info("Save ini information to tmp.ini")
    save_output_ini_body(pointlist_indices, merge_info)

    # Save the part_names and match_first_index to tmp.ini
    part_names = ""
    match_first_index = ""
    for num in range(len(ib_file_bytes)):
        output_partname = part_name + "_part" + str(num)
        part_names = part_names + output_partname

        first_index = ib_file_first_index_list[num]
        match_first_index = match_first_index + first_index.decode()

        if num != len(ib_file_bytes) -1:
            part_names = part_names + ","
            match_first_index = match_first_index + ","

    print("original order:")
    print(part_names)
    print(match_first_index)

    # we need to rearrange the order to compatible with split script.
    part_name_list = part_names.split(",")
    match_first_index_list = match_first_index.split(",")
    order_dict = {}
    for num in range(len(part_name_list)):
        part_name = part_name_list[num]
        first_index = int(match_first_index_list[num])
        order_dict[first_index] = part_name
    print("order_dict")
    print(order_dict)

    ordered_dict = {}

    for first_index in sorted(order_dict.keys()):
        print(first_index)
        ordered_dict[str(first_index)] = order_dict.get(first_index)
    print(ordered_dict)

    part_names = ""
    match_first_index = ""
    for first_index in ordered_dict:
        part_name = ordered_dict.get(first_index)
        part_names = part_names + part_name + ","
        match_first_index = match_first_index + first_index + ","

    part_names = part_names[0:len(part_names) -1]
    match_first_index = match_first_index[0:len(match_first_index) -1]
    print(part_names)
    print(match_first_index)

    tmp_config = configparser.ConfigParser()
    tmp_config.read('configs/tmp.ini')
    tmp_config.set("Ini", "part_names", part_names)
    tmp_config.set("Ini", "match_first_index", match_first_index)
    tmp_config.write(open("configs/tmp.ini", "w"))

    # Reset to use the correct order part name
    part_name_list = list(ordered_dict.values())
    print(part_name_list)
    logging.info("Output to file.")
    for index in range(len(ib_file_bytes)):

        ib_file_byte = ib_file_bytes[index]
        output_vbname = preset_config["General"]["OutputFolder"] + merge_info.draw_ib + "-" + part_name_list[index] + "-vb0.txt"
        output_ibname = preset_config["General"]["OutputFolder"] + merge_info.draw_ib + "-" + part_name_list[index] + "-ib.txt"
        output_vb_fileinfo.output_filename = output_vbname

        logging.info("Output Step 1: Write to ib file.")
        output_ibfile = open(output_ibname, "wb+")
        output_ibfile.write(ib_file_byte)
        output_ibfile.close()

        logging.info("Output Step 2: Write to vb file.")
        output_vb_file(output_vb_fileinfo)

        logging.info(split_str)



def get_element_list_from_pointlist():
    # TODO 自动从pointlist中读取要使用的element_list


    pass


if __name__ == "__main__":
    split_str = "----------------------------------------------------------------------------------------------"

    # General Info
    GameName = preset_config["General"]["GameName"]
    OutputFolder = preset_config["General"]["OutputFolder"]
    LoaderFolder = preset_config["General"]["LoaderFolder"]
    FrameAnalyseFolder = preset_config["General"]["FrameAnalyseFolder"]
    WorkFolder = LoaderFolder + FrameAnalyseFolder + "/"

    # Merge Info
    merge_info = MergeInfo()
    merge_info.part_name = preset_config["Merge"]["part_name"]
    merge_info.type = preset_config["Merge"]["type"]
    merge_info.root_vs = preset_config["Merge"]["root_vs"]
    merge_info.draw_ib = preset_config["Merge"]["draw_ib"]
    merge_info.use_pointlist = preset_config["Merge"].getboolean("use_pointlist")
    merge_info.only_pointlist = preset_config["Merge"].getboolean("only_pointlist")

    # Automatically get element list and which vb file it's extracted from by read config file.
    element_list = preset_config["Merge"]["element_list"].split(",")

    info_location = {}
    for element in element_list:
        extract_vb_file = vertex_config[element]["extract_vb_file"]
        info_location[element.encode()] = extract_vb_file
    merge_info.info_location = info_location
    merge_info.element_list = info_location.keys()
    print(merge_info.element_list)

    # Decide weather to create a new one.
    DeleteOutputFolder = preset_config["General"].getboolean("DeleteOutputFolder")
    if DeleteOutputFolder:
        if os.path.exists(OutputFolder):
            shutil.rmtree(OutputFolder)
    # Make sure the OutputFolder exists.
    if not os.path.exists(OutputFolder):
        os.mkdir(OutputFolder)

    # set the output log file.
    logging.basicConfig(filename=OutputFolder + str(time.strftime('%Y-%m-%d_%H_%M_%S_')) + str(time.time_ns()) + '.log', level=logging.DEBUG)

    logging.info("MergeScript Current Version V0.1")
    logging.info("Switch to work dir: " + WorkFolder)
    logging.info(split_str)

    logging.info("Current Game: " + GameName)
    logging.info("Set RootVS To: " + merge_info.root_vs)
    logging.info("Set LoaderFolder To:" + LoaderFolder)
    logging.info("Set FrameAnalyseFolder To: " + FrameAnalyseFolder)
    logging.info("Set work dir to: " + WorkFolder)
    logging.info(split_str)

    logging.info("Start to process hash: " + merge_info.draw_ib)
    logging.info("Current hash's part name: " + merge_info.part_name)
    logging.info("Whether current object use Pointlist Topology: " + str(merge_info.use_pointlist))

    logging.info("Start to read pointlist and trianglelist indices.")
    pointlist_indices, trianglelist_indices = get_pointlit_and_trianglelist_indices_V2()
    # INFO:root:Pointlist vb indices: ['000010', '000012']
    # INFO:root:Trianglelist vb indices: ['000047', '000051', '000059', '000064', '000069', '000097']

    # TODO 获取vertex_limit_vb
    logging.info("Now grab the vertex limit vertex buffer hash value:")
    vertex_limit_raise_index = trianglelist_indices[0]
    # 获取vb0文件名称
    first_draw_vb_filename = get_filter_filenames(WorkFolder, vertex_limit_raise_index+"-vb0=", ".txt")[0]
    # print(first_draw_vb_filename)
    index_vb_prefix = vertex_limit_raise_index + "-vb0="
    # print(index_vb_prefix)
    vertex_limit_vb = first_draw_vb_filename[len(index_vb_prefix):len(index_vb_prefix) + 8]

    tmp_config.set("Ini", "vertex_limit_vb", vertex_limit_vb)
    tmp_config.write(open("configs/tmp.ini", "w"))

    # print(split_str)
    # print(first_draw_vb_filename)

    # TODO auto calculate vb list

    if merge_info.use_pointlist:
        if len(pointlist_indices) == 0:
            logging.error("Can't find any pointlist file,please turn pointlist tech flag to False for:")
            logging.error("['" + preset_config["Merge"]["part_name"] + "']")
            exit(1)

        if merge_info.only_pointlist:
            merge_pointlist_files(pointlist_indices, trianglelist_indices, merge_info)
        else:
            # TODO BH3 collect TEXCOORD from trianglelist.
            merge_pointlist_trianglelist_files(pointlist_indices, trianglelist_indices, merge_info)

    else:
        # TODO need to fix this method,it can not work now.
        logging.info("Only fetch from trianglelist files.")


    logging.info(split_str)
    logging.info("----------------------------------------------------------\r\nAll process done！")
