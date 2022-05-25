#!/usr/bin/env python

"""
Build the corpus package index.  Usage:
  build_pkg_index.py <path-to-packages> <base-url> <output-file>
"""


import sys
import shutil
import os, glob
from kdmt.zip import zipdir
import zipfile
from kdmt.checksum import md5_hexdigest
from kdmt.file import read_json_file

def _path_from(parent, child, base_dir=None):
    if os.path.split(parent)[1] == "":
        parent = os.path.split(parent)[0]

    path = []
    while parent != child:
        child, dirname = os.path.split(child)
        path.insert(0, dirname)
        assert os.path.split(child)[0] != child
    if base_dir is not None:
        path.insert(0,base_dir)

    if len(path)>1:
        return os.path.join(*path)
    elif len(path)==1:
        return path[0]
    return path


def _get_sub_package_data(dirname, root, pkg_file):

    for f_root, d_names, f_names in os.walk(dirname):
        content = {"path": _path_from(root, f_root,base_dir="packages"), "files": []}
        for f in f_names:
            if f not in ["_package_.json",  pkg_file["name"], "_other_packages_.json", ".DS_Store"]:
                content["files"].append(
                    {"name": f, "path": _path_from(root, os.path.join(f_root,f), base_dir="packages"), "checksum": md5_hexdigest(os.path.join(f_root,f)), "url": f"https://github.com/mbenhaddou/kolibri-data/raw/main/packages/{os.path.relpath(f_root, root)}/{f}", "unzip": False})
        if len(content["files"]) > 0:
            pkg_file["sub_packages"].append(content)

    return pkg_file

def find_packages(root, recreate_packages=False):

    for dirname, subdirs, files in os.walk(root):
        relpath = _path_from(root, dirname)

        pkg_filename="_package_.json"
        other_pkg_filename = "_other_packages_.json"
        try:
            pkg_file = read_json_file(os.path.join(dirname, pkg_filename))
        except:
            continue
        zipfilename = pkg_file["package_id"] + ".zip"
        pkg_file["sub_packages"]=[]
        zipfilename_full_path=os.path.join(dirname, zipfilename)
        pkg_file["name"]=zipfilename

        if not os.path.exists(zipfilename_full_path) or recreate_packages:
            zipdir(dirname, zipfilename_full_path, ["_package_.json", zipfilename, "_other_packages_.json"])


        _get_sub_package_data(dirname, root, pkg_file)

        try:
            other_pkg_file = read_json_file(os.path.join(dirname, other_pkg_filename))
            pkg_file["other_packages"]=[]
            for pkg in other_pkg_file:
                pkg_file["other_packages"].append(pkg)
        except:
            pass

        try:
            zf = zipfile.ZipFile(zipfilename_full_path)
        except Exception as e:
            raise ValueError(f"Error reading file {zipfilename_full_path!r}!\n{e}") from e
        yield pkg_file, zf, relpath





