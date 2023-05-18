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
    # for convenience,the format we generate will as same as GIMI output format.

    mod_name = preset_config["General"]["mod_name"]
    mod_folder = preset_config["General"]["OutputFolder"]
    mod_ini_name = mod_folder + mod_name +".ini"
    # -----------------------------------------------------------------------------------------------------------

    output_str = ""
    output_str = output_str + "; " + mod_name + "\n" + "\n"

    split_str = "-------------------------"
    output_str = output_str + "; Constants " + split_str + "\n" + "\n"
    output_str = output_str + "; Overrides " + split_str + "\n" + "\n"

    # Resource_name
    resource_position_name = "Resource_" + mod_name + "_POSITION"
    resource_blend_name = "Resource_" + mod_name + "_BLEND"
    resource_texcoord_name = "Resource_" + mod_name + "_TEXCOORD"

    # slot
    position_slot = preset_config["Slot"]["position_slot"]
    texcoord_slot = preset_config["Slot"]["texcoord_slot"]
    blend_slot = preset_config["Slot"]["blend_slot"]

    max_vertex_number = preset_config["Merge"].getint("max_vertex_number")
    control_draw_number = preset_config["Merge"].getboolean("control_draw_number")

    if preset_config["Generate"].getboolean("compatible_with_srmi"):
        position_vb = tmp_config["Ini"]["position_vb"]
        output_str = output_str + "[TextureOverride_" + mod_name + "_POSITION]" + "\n"
        output_str = output_str + "hash = " + position_vb + "\n"
        output_str = output_str + position_slot + " = " + resource_position_name + "\n"
        output_str = output_str + blend_slot + " = " + resource_blend_name + "\n"

        output_str = output_str + "handling = skip\n"
        if control_draw_number:
            output_str = output_str + "draw = " + str(max_vertex_number) + ",0\n" + "\n"
        else:
            draw_numbers = tmp_config["Ini"]["draw_numbers"]
            output_str = output_str + "draw = " + draw_numbers + ",0\n" + "\n"

        blend_vb = tmp_config["Ini"]["blend_vb"]
        output_str = output_str + ";[TextureOverride_" + mod_name + "_BLEND]" + "\n"
        output_str = output_str + ";hash = " + blend_vb + "\n" + "\n"
        # output_str = output_str + "handling = skip\n"
        # output_str = output_str + "vb2 = " + resource_blend_name + "\n"
    else:
        position_vb = tmp_config["Ini"]["position_vb"]
        output_str = output_str + "[TextureOverride_" + mod_name + "_POSITION]" + "\n"
        output_str = output_str + "hash = " + position_vb + "\n"
        # output_str = output_str + "handling = skip\n"
        # TODO 生成时自动获取position的槽位

        output_str = output_str + position_slot + " = " + resource_position_name + "\n" + "\n"
        # output_str = output_str + "vb2 = " + resource_blend_name + "\n"

        blend_vb = tmp_config["Ini"]["blend_vb"]
        output_str = output_str + "[TextureOverride_" + mod_name + "_BLEND]" + "\n"
        output_str = output_str + "hash = " + blend_vb + "\n"
        output_str = output_str + blend_slot + " = " + resource_blend_name + "\n"

        output_str = output_str + "handling = skip\n"
        if control_draw_number:
            output_str = output_str + "draw = " + str(max_vertex_number) + ",0\n" + "\n"
        else:
            draw_numbers = tmp_config["Ini"]["draw_numbers"]
            output_str = output_str + "draw = " + draw_numbers + ",0\n" + "\n"

    texcoord_vb = tmp_config["Ini"]["texcoord_vb"]
    output_str = output_str + ";[TextureOverride_" + mod_name + "_TEXCOORD]" + "\n"
    output_str = output_str + ";hash = " + texcoord_vb + "\n" + "\n"
    # output_str = output_str + "handling = skip\n"
    # output_str = output_str + "vb1 = " + resource_texcoord_name + "\n"
    # output_str = output_str + "drawindexed = auto\n\n"

    # GIMI have a VertexLimitRaise,but original 3dmigoto don't have.
    # And seems it can not work properly,so we don't need this now.
    vertex_limit_vb = tmp_config["Ini"]["vertex_limit_vb"]
    output_str = output_str + "[TextureOverride_" + mod_name +"_VertexLimitRaise]" + "\n"
    output_str = output_str + "hash = " + vertex_limit_vb + "\n" + "\n"

    # -----------------------------------------------------------------------------------------------------------
    # Different generate method for single part and multipart cloth.
    part_names = tmp_config["Ini"]["part_names"].split(",")
    draw_ib = preset_config["Merge"]["draw_ib"]

    if len(part_names) == 1:
        output_str = output_str + "[TextureOverride_" + mod_name + "_IB]" + "\n"
        output_str = output_str + "hash = " + draw_ib + "\n"
        output_str = output_str + "handling = skip\n\n"

        match_first_index = tmp_config["Ini"]["match_first_index"].split(",")
        resource_ib_partnames = []
        for part_name in part_names:
            name = "Resource_" + mod_name + "_" + part_name
            resource_ib_partnames.append(name)

        for i in range(len(part_names)):
            part_name = part_names[i]
            first_index = match_first_index[i]
            output_str = output_str + "[TextureOverride_" + mod_name + "_" + part_name + "]\n"
            output_str = output_str + "hash = " + draw_ib + "\n"
            output_str = output_str + "match_first_index = " + first_index + "\n"
            output_str = output_str + "ib = " + resource_ib_partnames[i] + "\n"
            output_str = output_str + texcoord_slot + " = " + resource_texcoord_name + "\n"
            output_str = output_str + "drawindexed = auto\n\n"
    else:
        output_str = output_str + "[TextureOverride_" + mod_name + "_IB]" + "\n"
        output_str = output_str + "hash = " + draw_ib + "\n"
        output_str = output_str + "handling = skip\n" + "\n"
        # output_str = output_str + "drawindexed = auto\n\n"

        match_first_index = tmp_config["Ini"]["match_first_index"].split(",")
        resource_ib_partnames = []
        for part_name in part_names:
            name = "Resource_" + mod_name + "_" + part_name
            resource_ib_partnames.append(name)

        for i in range(len(part_names)):
            part_name = part_names[i]
            first_index = match_first_index[i]
            output_str = output_str + "[TextureOverride_" + mod_name + "_" + part_name + "]\n"
            output_str = output_str + "hash = " + draw_ib + "\n"
            output_str = output_str + "match_first_index = " + first_index + "\n"
            output_str = output_str + "ib = " + resource_ib_partnames[i] + "\n"
            output_str = output_str + texcoord_slot + " = " + resource_texcoord_name + "\n"
            output_str = output_str + "drawindexed = auto\n\n"

    # Resource section
    # -----------------------------------------------------------------------------------------------------------
    output_str = output_str + "; CommandList " + split_str + "\n" + "\n"
    output_str = output_str + "; Resources " + split_str + "\n" + "\n"

    # Auto generate the ps slot we possibly will use.
    output_str = output_str + ";[Resource_diffuse1]\n"
    output_str = output_str + ";filename = diffuse1.dds\n" + "\n"

    output_str = output_str + ";[Resource_light1]\n"
    output_str = output_str + ";filename = light1.dds\n" + "\n"

    output_str = output_str + "[" + resource_position_name + "]\n"
    output_str = output_str + "type = Buffer\n"
    output_str = output_str + "stride = " + tmp_config["Ini"]["position_stride"] + "\n"

    part_name = tmp_config["Ini"]["part_names"]
    # if len(part_names) == 1:
    #     output_str = output_str + "filename = " + part_name + "_POSITION.buf\n\n"
    # else:
    output_str = output_str + "filename = " + mod_name +"_POSITION.buf\n\n"

    output_str = output_str + "[" + resource_blend_name + "]\n"
    output_str = output_str + "type = Buffer\n"
    output_str = output_str + "stride = " + tmp_config["Ini"]["blend_stride"] + "\n"
    # if len(part_names) == 1:
    #     output_str = output_str + "filename = " + part_name +"_BLEND.buf\n\n"
    # else:
    output_str = output_str + "filename = " + mod_name +"_BLEND.buf\n\n"

    output_str = output_str + "[" + resource_texcoord_name + "]\n"
    output_str = output_str + "type = Buffer\n"
    output_str = output_str + "stride = " + tmp_config["Ini"]["texcoord_stride"] + "\n"
    # if len(part_names) == 1:
    #     output_str = output_str + "filename = " + part_name +"_TEXCOORD.buf\n\n"
    # else:
    output_str = output_str + "filename = " + mod_name +"_TEXCOORD.buf\n\n"

    if len(part_names) == 1:
        for i in range(len(part_names)):
            part_name = part_names[i]
            resource_name = resource_ib_partnames[i]
            output_str = output_str + "[" + resource_name + "]\n"
            output_str = output_str + "type = Buffer\n"
            output_str = output_str + "format = " + preset_config["Merge"]["ib_format"] + "\n"
            output_str = output_str + "filename = " + part_name + ".ib\n\n"
    else:
        for i in range(len(part_names)):
            part_name = part_names[i]
            resource_name = resource_ib_partnames[i]
            output_str = output_str + "[" + resource_name + "]\n"
            output_str = output_str + "type = Buffer\n"
            output_str = output_str + "format = " + preset_config["Merge"]["ib_format"] + "\n"
            # compatible with GIMI script.
            if i == 0:
                output_str = output_str + "filename = " + part_name + ".ib\n\n"
            else:
                output_str = output_str + "filename = " + part_name + "_new.ib\n\n"

    # -----------------------------------------------------------------------------------------------------------
    output_str = output_str + "; .ini generated by HSR-Fix script.\n"
    output_str = output_str + "; Github: https://github.com/airdest/HSR-Fix\n"
    output_str = output_str + "; Discord: https://discord.gg/U8cRdUYZrR\n"
    output_str = output_str + "; Author of this mod: " + preset_config["General"]["Author"] +"\n"

    output_file = open(mod_ini_name, "w")
    output_file.write(output_str)
    output_file.close()

    # Move to the final folder
    # -----------------------------------------------------------------------------------------------------------
    move_modfiles_flag = preset_config["General"].getboolean("move_modfiles_flag")
    if move_modfiles_flag:
        final_output_folder = mod_folder + mod_name + "/"
        # Make sure the final mod folder exists.
        if not os.path.exists(final_output_folder):
            os.mkdir(final_output_folder)
        print("move mod files to final output mod folder.")
        mod_file_list = []
        part_names = tmp_config["Ini"]["part_names"].split(",")
        for num in range(len(part_names)):
            if num == 0:
                mod_file_list.append(part_names[num] + ".ib")
            else:
                mod_file_list.append(part_names[num] + "_new.ib")
        mod_file_list.append(mod_name + ".ini")
        mod_file_list.append(mod_name + "_BLEND.buf")
        mod_file_list.append(mod_name + "_POSITION.buf")
        mod_file_list.append(mod_name + "_TEXCOORD.buf")

        for file_path in mod_file_list:
            original_file_path = mod_folder + file_path
            dest_file_path = final_output_folder + file_path
            if os.path.exists(original_file_path):
                shutil.move(original_file_path, dest_file_path)


    print("All process done!")
