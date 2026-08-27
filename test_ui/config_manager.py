import xml.etree.ElementTree as ET
import os
import shutil
import uuid

PROPERTIES_FILE = os.path.join("resources", "properties.xml")
PROPERTIES_BACKUP = os.path.join("resources", "properties.xml.bak")

MANIFEST_FILE = "manifest.xml"
MANIFEST_BACKUP = "manifest.xml.bak"

def backup_properties():
    if not os.path.exists(PROPERTIES_BACKUP):
        shutil.copyfile(PROPERTIES_FILE, PROPERTIES_BACKUP)
    if not os.path.exists(MANIFEST_BACKUP):
        shutil.copyfile(MANIFEST_FILE, MANIFEST_BACKUP)

def restore_properties():
    if os.path.exists(PROPERTIES_BACKUP):
        shutil.copyfile(PROPERTIES_BACKUP, PROPERTIES_FILE)
        os.remove(PROPERTIES_BACKUP)
    if os.path.exists(MANIFEST_BACKUP):
        shutil.copyfile(MANIFEST_BACKUP, MANIFEST_FILE)
        os.remove(MANIFEST_BACKUP)

def set_properties(props_dict):
    """
    Updates properties.xml with new keys, and injects a random UUID into manifest.xml
    to bypass the aggressive Garmin Connect IQ .SET property caching.
    """
    backup_properties()
    
    # 1. Update properties
    tree = ET.parse(PROPERTIES_FILE)
    root = tree.getroot()
    for prop in root.findall('property'):
        prop_id = prop.get('id')
        if prop_id in props_dict:
            prop.text = str(props_dict[prop_id])
    tree.write(PROPERTIES_FILE, encoding="utf-8", xml_declaration=False)

    # 2. Mutate manifest UUID to trick simulator into a fresh install
    ET.register_namespace('iq', 'http://www.garmin.com/xml/connectiq')
    manifest_tree = ET.parse(MANIFEST_FILE)
    manifest_root = manifest_tree.getroot()
    app_node = manifest_root.find('{http://www.garmin.com/xml/connectiq}application')
    if app_node is not None:
        new_uuid = uuid.uuid4().hex
        app_node.set('id', new_uuid)
    manifest_tree.write(MANIFEST_FILE, encoding="utf-8", xml_declaration=True)

