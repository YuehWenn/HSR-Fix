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

import os
import glob
import shutil
import configparser
from MergeUtil import *




if __name__ == "__main__":
    FrameAnalyseFolder = preset_config["General"]["FrameAnalyseFolder"]
    LoaderFolder = preset_config["General"]["LoaderFolder"]
    draw_ib = preset_config["Merge"]["draw_ib"]

    basic_check_config = configparser.ConfigParser()

    # TODO 要不要直接生成一个目标目录的basic_check.ini?
    generate_basic_check = preset_config["Generate"].getboolean("generate_basic_check")
    if generate_basic_check:
        OutputFolder = preset_config["General"]["OutputFolder"]
        mod_name = preset_config["General"]["mod_name"]
        mod_folder = OutputFolder + mod_name + "/"
        basic_check_filename = mod_folder + "basic_check.ini"

        if not os.path.exists(mod_folder):
            os.mkdir(mod_folder)

        # 创建一个新的basic_check.ini
        file = open(basic_check_filename, "w+")
        file.write("")
        file.close()

        basic_check_config.read(basic_check_filename, 'utf-8')
    else:
        basic_check_config.read('configs/basic_check.ini', 'utf-8')

    # set draw_ib to "-vb0" to let it collect all VS check.
    # draw_ib = "-vb0"

    ib_files = get_filter_filenames(LoaderFolder + FrameAnalyseFolder, draw_ib, ".txt")

    vertex_shader_list = []
    for filename in ib_files:
        vs = filename.split("-vs=")[1][0:16]
        if vs not in vertex_shader_list:
            vertex_shader_list.append(vs)

    check_list = ""
    for vs in sorted(vertex_shader_list):
        try:
            section_name = "ShaderOverride_VS_"+vs+"_Test_"
            basic_check_config.add_section(section_name)
            print("add section :" + section_name)
        except configparser.DuplicateSectionError:
            print("Section [" + section_name + "] already exists, will overwrite it.")

        basic_check_config.set("ShaderOverride_VS_"+vs+"_Test_", "hash", vs)
        basic_check_config.set("ShaderOverride_VS_"+vs+"_Test_", "run", "CommandListCheckTexcoordIB")

    # We normally will not check PS,but keep this for some special usage.
    GeneratePSCheck = False
    if GeneratePSCheck:
        pixel_shader_list = []
        for filename in ib_files:
            ps = filename.split("-ps=")[1][0:16]
            if ps not in pixel_shader_list:
                pixel_shader_list.append(ps)

        check_list = ""
        for ps in sorted(pixel_shader_list):
            basic_check_config.set("ShaderOverride_PS_" + ps + "_Test_", "hash", ps)
            basic_check_config.set("ShaderOverride_PS_" + ps + "_Test_", "run", "CommandListCheckTexcoordIB")

    # Finally save the config file.
    if generate_basic_check:
        basic_check_config.write(open(basic_check_filename, "w"))

    else:
        basic_check_config.write(open("configs/basic_check.ini", "w"))
    print("All process done!")


