# -*- coding: utf-8 -*-
'''
Created on 2013-11-15

@author: juliochen
'''
import os
import util
import zipfile
import xml.etree.ElementTree as ET


class PackageError(Exception):

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return Exception.__str__(self) + self.msg


class Apk(object):

    def __init__(self, store_path, version=''):

        self.path = util.get_path(store_path)
        self.package = '' 
        self.activities = []
        if version:
            self.version = version
        else:
            self.version = os.path.basename(self.path)
        self.parse_manifest()

    def get_package_name(self, file_path):
        pass

    def uninstall(self, device):
        cmd = "adb -s %s uninstall %s " % (device, self.pkg_name)
        ret = os.popen(cmd).readlines()
        for r in ret:
            if "Failure" in r:
                return False
        return True

    def install(self, device, override=False):
        op = '-r' if override else ''
        cmd = "adb -s %s install %s %s" % (device, op, self.path)
        ret = os.popen(cmd).readlines()

        for line in ret:
            if "Failure" in line:
                print("Failed install package on %s: %s" % (device, line))
                return False
                #raise PackageError("Failed install package on %s" % d)

        return True

    def _load_manifest(self):
        output = util.get_path("./temp")
        print output

        manifest = ''
        if os.path.isfile(self.path):
            zip = zipfile.ZipFile(self.path)
            zip.extract('AndroidManifest.xml', output)
            manifest = os.path.join(output, 'AndroidManifest.xml')
        if os.path.isfile(manifest):
            cmd = "java -jar %s %s > %s" % \
                  (util.get_path('./res/AXMLPrinter2.jar'),
                   manifest, util.get_path('./temp/AndroidManifest_decoded.xml'))
            os.popen(cmd)
            return util.get_path('./temp/AndroidManifest_decoded.xml')

    def parse_manifest(self):
        xml = self._load_manifest()
        if not os.path.isfile(xml):
            return
        tree = ET.parse(xml)
        root = tree.getroot()
        if root.attrib.has_key("package"):
            self.package = root.attrib['package']
        
        app = root.find('application')
        for activity in app.findall('activity'):
            name = activity.attrib['{http://schemas.android.com/apk/res/android}name']
            self.activities.append(name.split('.')[-1])



if __name__ == "__main__":
    ap = Apk('./packages/weishi_guanwang_2_2_0.apk',
             'weishi_2_2_0_test_20140225')
    print ap.package
    print ap.activities
