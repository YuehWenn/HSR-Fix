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
from MergeUtil import *


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


def calculate_tangent_nearest(position_input, head_file):
    print(head_file)
    position = position_input
    """
    copy from GIMI project:
    https://github.com/SilentNightSound/GI-Model-Importer
    
    :param position: bytearray()
    :param vb0_file: filename
    :return:
    """
    print("Replacing tangents with closest originals")
    # TODO 找到对应的vb0文件,暂时不能正常使用

    if not head_file:
        print("ERROR: unable to find original file for tangent data. Exiting")
        return
    with open(head_file, "r") as f:
        data = f.readlines()
        raw_points = [x.split(":")[1].strip().split(", ") for x in data if "+000 POSITION:" in x]
        tangents = [x.split(":")[1].strip().split(", ") for x in data if "+024 TANGENT:" in x]
        if len(raw_points[0]) == 3:
            points = [(float(x), float(y), float(z)) for x, y, z in raw_points]
        else:
            points = [(float(x), float(y), float(z)) for x, y, z, _ in raw_points]
        tangents = [(float(x), float(y), float(z), float(a)) for x, y, z, a in tangents]
        lookup = {}
        for x, y in zip(points, tangents):
            lookup[x] = y

        tree = KDTree(points, 3)

        i = 0
        while i < len(position):
            if len(raw_points[0]) == 3:
                x, y, z = struct.unpack("f", position[i:i + 4])[0], struct.unpack("f", position[i + 4:i + 8])[0], \
                    struct.unpack("f", position[i + 8:i + 12])[0]
                result = tree.get_nearest((x, y, z))[1]
                tx, ty, tz, ta = [struct.pack("f", a) for a in lookup[result]]
                position[i + 24:i + 28] = tx
                position[i + 28:i + 32] = ty
                position[i + 32:i + 36] = tz
                position[i + 36:i + 40] = ta
                i += 40
            else:
                x, y, z = struct.unpack("e", position[i:i + 2])[0], struct.unpack("e", position[i + 2:i + 4])[0], \
                    struct.unpack("e", position[i + 4:i + 6])[0]
                result = tree.get_nearest((x, y, z))[1]
                tx, ty, tz, ta = [(int(a * 255)).to_bytes(1, byteorder="big") for a in lookup[result]]

                position[i + 24:i + 25] = tx
                position[i + 25:i + 26] = ty
                position[i + 26:i + 27] = tz
                position[i + 27:i + 28] = ta
                i += 28
    return position


# https://github.com/Vectorized/Python-KD-Tree
# A brute force solution for finding the original tangents is O(n^2), and isn't good enough since n can get quite
#   high in many models (upwards of a minute calculation time in some cases)
# So we use a simple KD structure to perform quick nearest neighbor lookups
class KDTree(object):
    """
    Usage:
    1. Make the KD-Tree:
        `kd_tree = KDTree(points, dim)`
    2. You can then use `get_knn` for k nearest neighbors or
       `get_nearest` for the nearest neighbor
    points are be a list of points: [[0, 1, 2], [12.3, 4.5, 2.3], ...]
    """

    def __init__(self, points, dim, dist_sq_func=None):
        """Makes the KD-Tree for fast lookup.
        Parameters
        ----------
        points : list<point>
            A list of points.
        dim : int
            The dimension of the points.
        dist_sq_func : function(point, point), optional
            A function that returns the squared Euclidean distance
            between the two points.
            If omitted, it uses the default implementation.
        """

        if dist_sq_func is None:
            dist_sq_func = lambda a, b: sum((x - b[i]) ** 2
                                            for i, x in enumerate(a))

        def make(points, i=0):
            if len(points) > 1:
                points.sort(key=lambda x: x[i])
                i = (i + 1) % dim
                m = len(points) >> 1
                return [make(points[:m], i), make(points[m + 1:], i),
                        points[m]]
            if len(points) == 1:
                return [None, None, points[0]]

        def add_point(node, point, i=0):
            if node is not None:
                dx = node[2][i] - point[i]
                for j, c in ((0, dx >= 0), (1, dx < 0)):
                    if c and node[j] is None:
                        node[j] = [None, None, point]
                    elif c:
                        add_point(node[j], point, (i + 1) % dim)

        import heapq
        def get_knn(node, point, k, return_dist_sq, heap, i=0, tiebreaker=1):
            if node is not None:
                dist_sq = dist_sq_func(point, node[2])
                dx = node[2][i] - point[i]
                if len(heap) < k:
                    heapq.heappush(heap, (-dist_sq, tiebreaker, node[2]))
                elif dist_sq < -heap[0][0]:
                    heapq.heappushpop(heap, (-dist_sq, tiebreaker, node[2]))
                i = (i + 1) % dim
                # Goes into the left branch, then the right branch if needed
                for b in (dx < 0, dx >= 0)[:1 + (dx * dx < -heap[0][0])]:
                    get_knn(node[b], point, k, return_dist_sq,
                            heap, i, (tiebreaker << 1) | b)
            if tiebreaker == 1:
                return [(-h[0], h[2]) if return_dist_sq else h[2]
                        for h in sorted(heap)][::-1]

        def walk(node):
            if node is not None:
                for j in 0, 1:
                    for x in walk(node[j]):
                        yield x
                yield node[2]

        self._add_point = add_point
        self._get_knn = get_knn
        self._root = make(points)
        self._walk = walk

    def __iter__(self):
        return self._walk(self._root)

    def add_point(self, point):
        """Adds a point to the kd-tree.

        Parameters
        ----------
        point : array-like
            The point.
        """
        if self._root is None:
            self._root = [None, None, point]
        else:
            self._add_point(self._root, point)

    def get_knn(self, point, k, return_dist_sq=True):
        """Returns k nearest neighbors.
        Parameters
        ----------
        point : array-like
            The point.
        k: int
            The number of nearest neighbors.
        return_dist_sq : boolean
            Whether to return the squared Euclidean distances.
        Returns
        -------
        list<array-like>
            The nearest neighbors.
            If `return_dist_sq` is true, the return will be:
                [(dist_sq, point), ...]
            else:
                [point, ...]
        """
        return self._get_knn(self._root, point, k, return_dist_sq, [])

    def get_nearest(self, point, return_dist_sq=True):
        """Returns the nearest neighbor.
        Parameters
        ----------
        point : array-like
            The point.
        return_dist_sq : boolean
            Whether to return the squared Euclidean distance.
        Returns
        -------
        array-like
            The nearest neighbor.
            If the tree is empty, returns `None`.
            If `return_dist_sq` is true, the return will be:
                (dist_sq, point)
            else:
                point
        """
        l = self._get_knn(self._root, point, 1, return_dist_sq, [])
        return l[0] if len(l) else None


def collect_vb(vb_file_name, stride, ignore_tangent=True):
    # GIMI use POSITION -> BLEND -> TEXCOORD in vb file
    # but my script use POSITION -> TEXCOORD -> BLEND in vb file.

    position_width = vertex_config["POSITION"].getint("byte_width")
    normal_width = vertex_config["NORMAL"].getint("byte_width")
    tangent_width = vertex_config["TANGENT"].getint("byte_width")
    # print(position_width)
    # print(normal_width)
    # print(tangent_width)

    stride_position = position_width + normal_width + tangent_width

    color_width = vertex_config["COLOR"].getint("byte_width")
    texcoord_width = vertex_config["TEXCOORD"].getint("byte_width")
    texcoord1_width = vertex_config["TEXCOORD1"].getint("byte_width")
    # print(color_width)
    # print(texcoord_width)
    # print(texcoord1_width)

    element_list = preset_config["Merge"]["element_list"].split(",")
    print(element_list)

    # stride_texcoord = color_width + texcoord_width + texcoord1_width
    #
    # if "TEXCOORD1" not in element_list:
    #     stride_texcoord = color_width + texcoord_width

    stride_texcoord = 0
    for element in element_list:
        if element == "COLOR":
            stride_texcoord = stride_texcoord + color_width
        if element == "TEXCOORD":
            stride_texcoord = stride_texcoord + texcoord_width
        if element == "TEXCOORD1":
            stride_texcoord = stride_texcoord + texcoord1_width

    print(stride_texcoord)

    # blendweights_width = vertex_config["BLENDWEIGHTS"].getint("byte_width")
    # blendindices_width = vertex_config["BLENDINDICES"].getint("byte_width")
    # stride_blend = blendweights_width + blendindices_width

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
                position += data[i:i + position_width + normal_width]
                # TANGENT recalculate use normal value
                position += data[i+position_width:i + position_width + normal_width] + bytearray(struct.pack("f", 1))
            else:
                position += data[i:i+position_width + normal_width + tangent_width]

            texcoord += data[i + stride_position:i + stride_position + stride_texcoord]
            blend += data[i+stride_position + stride_texcoord:i+stride]
            i += stride
    return position, blend, texcoord


if __name__ == "__main__":

    SplitFolder = preset_config["General"]["OutputFolder"]
    # SplitFolder = "C:/Program Files/Star Rail/Game/Mods/output/"

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

        ignore_tangent = False

        if repair_tangent == "simple":
            ignore_tangent = True

        position_bytearray, blend_bytearray, texcoord_bytearray = collect_vb(vb_filename, stride, ignore_tangent=ignore_tangent)

        position_buf += position_bytearray
        blend_buf += blend_bytearray
        texcoord_buf += texcoord_bytearray

        # fix_vb_filename = get_filter_filenames(SplitFolder)
        # calculate nearest TANGENT
        if repair_tangent == "nearest":
            position_buf = calculate_tangent_nearest(position_buf, vb_filename)

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

    # set the draw number used in VertexLimitRaise
    draw_numbers = len(position_buf) // 40
    tmp_config.set("Ini", "draw_numbers", str(draw_numbers))
    tmp_config.write(open(config_folder + "/tmp.ini", "w"))

    print("----------------------------------------------------------\r\nAll process done！")

