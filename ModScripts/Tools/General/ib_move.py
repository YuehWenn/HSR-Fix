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


if __name__ == "__main__":
    """
    Move all the index buffer related files to output folder
    """

if __name__ == "__main__":
    # Set work dir, here is your FrameAnalysis dump dir.
    FrameAnalyseFolder = "FrameAnalysis-2023-04-16-120908"
    NOSLoaderFolder = "C:/Users/Administrator/Desktop/NOSLoader/"
    os.chdir(NOSLoaderFolder + FrameAnalyseFolder + "/")
    move_ib = "8c31344a"
    output_folder_name = "output_ib_files_" +"5"

    if not os.path.exists(output_folder_name):
        os.mkdir(output_folder_name)

    indices = []
    filenames = glob.glob("*"+move_ib+"*")
    for filename in filenames:
        index = filename.split("-")[0]
        if index not in indices:
            indices.append(index)

    for index in indices:
        filenames = glob.glob("*" + index + "*")
        for filename in filenames:
            if os.path.exists(filename):
                print("Moving ： " + filename + " ....")
                shutil.copy2(filename, output_folder_name + '/' + filename)

    print("All move done.")


