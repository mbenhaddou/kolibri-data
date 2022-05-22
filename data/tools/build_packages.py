#!/usr/bin/env python

"""
Build the corpus package index.  Usage:
  build_pkg_index.py <path-to-packages> <base-url> <output-file>
"""


import sys
from xml.etree import ElementTree
import os, glob
import zipfile
from kdmt.checksum import md5_hexdigest
from kdmt.file import read_json_file

def _path_from(parent, child):
    if os.path.split(parent)[1] == "":
        parent = os.path.split(parent)[0]
    path = []
    while parent != child:
        child, dirname = os.path.split(child)
        path.insert(0, dirname)
        assert os.path.split(child)[0] != child
    return path


def _get_sub_package_data(dirname, root, pkg_file):

    for f_root, d_names, f_names in os.walk(dirname):
        content = {"path": "/".join(_path_from(root, f_root)), "files": []}
        for f in f_names:
            if f != "_package_.json" and f != pkg_file["zip_name"]:
                content["files"].append(
                    {"name": f, "path": "/".join(_path_from(root, os.path.join(f_root,f))), "checksum": md5_hexdigest(os.path.join(f_root,f))})
        if len(content["files"]) > 0:
            pkg_file["sub_packages"].append(content)
    return pkg_file

def find_packages(root):

    for dirname, subdirs, files in os.walk(root):
        relpath = "/".join(_path_from(root, dirname))
        for filename in files:
            if filename=="_package_.json":
                pkg_file = read_json_file(os.path.join(dirname, filename))

                zipfilename = pkg_file["package_id"] + ".zip"
                pkg_file["sub_packages"]=[]
                zipfilename_full_path=os.path.join(dirname, zipfilename)
                pkg_file["zip_name"]=zipfilename
                if not os.path.exists(zipfilename_full_path):
                    with zipfile.ZipFile(zipfilename_full_path, 'w') as zipMe:
                        for file in os.listdir(dirname):
                            if file!="_package_.json" and file!=zipfilename:
                                zipMe.write(os.path.join(dirname,file), compress_type=zipfile.ZIP_DEFLATED)
                _get_sub_package_data(dirname, root, pkg_file)


                try:
                    zf = zipfile.ZipFile(zipfilename_full_path)
                except Exception as e:
                    raise ValueError(f"Error reading file {zipfilename_full_path!r}!\n{e}") from e
                yield pkg_file, zf, relpath





