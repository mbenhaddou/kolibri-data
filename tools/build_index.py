from build_packages import find_packages, _get_sub_datasets
import os, json
from kdmt.checksum import md5_hexdigest




def build_index(root, recreate_packages=False):
    """
    Create a new data.xml index file, by combining the xml description
    files for various packages and collections.  ``root`` should be the
    path to a directory containing the package xml and zip files; and
    the collection json files.

    All identifiers (for both packages and collections) must be unique.
    """
    # Find all packages.
    packages = []
    for pkg_json, zf, subdir in find_packages(os.path.join(root), recreate_packages):
        zipstat = os.stat(zf.filename)
        url = f"https://github.com/mbenhaddou/kolibri-data/raw/main/packages/{subdir}/{os.path.split(zf.filename)[1]}"
        unzipped_size = sum(zf_info.file_size for zf_info in zf.infolist())

        # Fill in several fields of the package xml with calculated values.
        pkg_json["unzipped_size"]= "%s" % unzipped_size
        pkg_json["size"]= "%s" % zipstat.st_size
        pkg_json["checksum"]= "%s" % md5_hexdigest(zf.filename)
        pkg_json["path"]= os.path.join('packages',subdir)
        pkg_json["unzip"]= True
        # pkg_xml['svn_revision', _svn_revision(zf.filename))
        if not pkg_json.get("url"):
            pkg_json["url"]= url

        # Record the package.
        packages.append(pkg_json)


    # Check that all UIDs are unique
    uids = set()
    for item in packages:
        if item.get("id") in uids:
            raise ValueError("Duplicate UID: %s" % item.get("id"))
        uids.add(item.get("id"))

    # Put it all together
    json_data = {"kolibri_data":{"packages":[]}}
    json_data["kolibri_data"]["packages"].extend(sorted(packages, key=lambda package: package.get("id")))

    data_sets_path="/Users/mohamedmentis/Dropbox/Mac (2)/Documents/Mentis/Development/Python/kolibri-data/datasets"
    json_data["kolibri_data"]["datasets"]=_get_sub_datasets(data_sets_path, data_sets_path)["datasets"]

    return json_data


json_string=build_index("/Users/mohamedmentis/Dropbox/Mac (2)/Documents/Mentis/Development/Python/kolibri-data/packages", True)

with open("../index.json", 'w') as outfile:
    json.dump(json_string, outfile)



#print(md5_hexdigest("/Users/mohamedmentis/Dropbox/kolibri/packages/language_detection/lid.176.bin"))