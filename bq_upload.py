import os
import csv
from datetime import datetime
try:
    from lxml import etree
except ImportError:
    import xml.etree.ElementTree as etree

from bqapi import BQSession, BQCommError
from bqapi.util import save_blob, localpath2url

img_path = 'kang0.jpg'
annos_home = 'Fish_Invert_Habitat_Data.xlsx'

annos = ['anno']

root = 'http://bisque.ece.ucsb.edu'
user = 'mcever'
pswd = 'Bisque1'

session = BQSession().init_local(user, pswd, bisque_root=root, create_mex=False)

path_on_bisque = 'demo/nuclei_%s/img_name'%(datetime.now().strftime('%Y%m%dT%H%M%S'))
resource = etree.Element ('image', name=path_on_bisque)
print etree.tostring(resource)

# use import service to /import/transfer activating import service
r = etree.XML(session.postblob(img_path, xml=resource)).find('./') 

if r is None or r.get('uri') is None:
    print 'Upload failed'
else:
    print 'Uploaded ID: %s, URL: %s\n'%(r.get('resource_uniq'), r.get('uri'))
    print etree.tostring(r)

g = etree.SubElement (r, 'gobject', type='My nuclei')
for a in annos:
    p = etree.SubElement (g, 'point')
    etree.SubElement (p, 'tag', name='fish', value=a)

print etree.tostring(r)

url = session.service_url('data_service')
r = session.postxml(url, r)

if r is None or r.get('uri') is None:
    print 'Adding annotations failed'
else:
    print 'Image ID: %s, URL: %s'%(r.get('resource_uniq'), r.get('uri'))
    
