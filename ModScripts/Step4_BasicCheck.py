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
from MergeUtil import *


if __name__ == "__main__":
    # We do not use configparser here anymore because we need to add comments
    # and multiple checktextureoverride need to add,but configparser do not support it.

    FrameAnalyseFolder = preset_config["General"]["FrameAnalyseFolder"]
    LoaderFolder = preset_config["General"]["LoaderFolder"]
    draw_ib = preset_config["Merge"]["draw_ib"]

    # weather to generate a basic_config.ini to [OutputFolder]/[mod_name] folder.
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

    # all VertexShader will show in IndexBuffer related files.
    ib_files = get_filter_filenames(LoaderFolder + FrameAnalyseFolder, draw_ib, ".txt")


    # Get all VertexShader need to check
    vertex_shader_list = []
    for filename in ib_files:
        vs = filename.split("-vs=")[1][0:16]
        if vs not in vertex_shader_list:
            vertex_shader_list.append(vs)

    print(vertex_shader_list)

    # Add texcoord VertexShader check
    position_slot = preset_config["Slot"]["position_slot"]
    texcoord_slot = preset_config["Slot"]["texcoord_slot"]
    blend_slot = preset_config["Slot"]["blend_slot"]

    texcoord_check_slots = [texcoord_slot, "ib"]
    action_check_slots = [position_slot]

    # output str
    output_str = ""
    output_str = output_str + ";Texcoord Check List:" + "\n" + "\n"
    for vs in sorted(vertex_shader_list):
        section_name = "[ShaderOverride_VS_" + vs + "_Test_]"
        print("add section :" + section_name)

        output_str = output_str + section_name + "\n"
        output_str = output_str + "hash = " + vs + "\n"
        output_str = output_str + "if $costume_mods" + "\n"
        for slot in texcoord_check_slots:
            output_str = output_str + "  checktextureoverride = " + slot + "\n"
        output_str = output_str + "endif" + "\n"
        output_str = output_str + "\n"

    # Add action VertexShader check
    add_action_check = False
    if add_action_check:
        output_str = output_str + ";Action Check:" + "\n" + "\n"
        output_str = output_str + "[ShaderOverride_ROOT_VS]" + "\n"
        root_vs = preset_config["Merge"]["root_vs"]
        output_str = output_str + "hash = " + root_vs + "\n"
        output_str = output_str + "if $costume_mods" + "\n"
        for slot in action_check_slots:
            output_str = output_str + " checktextureoverride = " + slot + "\n"
        output_str = output_str + "endif" + "\n"
        output_str = output_str + "\n"


    # We normally will not check PS,but keep this for some special usage.
    GeneratePSCheck = False
    if GeneratePSCheck:
        pixel_shader_list = []
        for filename in ib_files:
            ps = filename.split("-ps=")[1][0:16]
            if ps not in pixel_shader_list:
                pixel_shader_list.append(ps)

        for ps in sorted(pixel_shader_list):
            pass
            # basic_check_config.set("ShaderOverride_PS_" + ps + "_Test_", "hash", ps)
            # basic_check_config.set("ShaderOverride_PS_" + ps + "_Test_", "run", "CommandListCheckTexcoordIB")

    # Finally save the config file.
    if generate_basic_check:
        output_file = open(basic_check_filename, "w")
        output_file.write(output_str)
        output_file.close()
        # basic_check_config.write(open(basic_check_filename, "w"))

    else:
        pass
    print("All process done!")


