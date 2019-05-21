# this script is python2.7 because bqapi is python2.7 only

import os
import csv
from datetime import datetime
try:
    from lxml import etree
except ImportError:
    import xml.etree.ElementTree as etree

from bqapi import BQSession, BQCommError
from bqapi.util import save_blob, localpath2url

img_home = '/home/austin/datasets/MARE/frames/all'
annos_path = '/home/austin/datasets/MARE/scripts/MARE.csv'
dataset_name = 'MARE_frames'

# parse csv
files = []
with open(annos_path, 'rb') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        f = {}
        for k,v in row.iteritems():
            # csv has some empty fields, check for them
            if k is None or v is None or k is '' or v is '':
                continue
            f[k] = v
        print(f)
        files.append(f)

# prepare xml
ignore = ['url', 'resource']
for f in files:
    resource = etree.Element ('image', name=f['filename'])
    for k,v in f.iteritems():
        if k not in ignore:
            t = etree.SubElement (resource, 'tag', name=k, value=v)
            if 'url' in k:
                t.set('type', 'link')
    print etree.tostring(resource)
    f['resource'] = resource

# begin bisque session
root = 'http://bisque.ece.ucsb.edu'
user = 'mcever'
pswd = 'Bisque1'
session = BQSession().init_local(user, pswd, bisque_root=root, create_mex=False)

# upload files
for f in files:
    print '\nuploading %s'%f['filename']
    filepath = os.path.join(img_home, f['filename'])
    resource = f['resource']

    # use import service to /import/transfer activating import service
    r = etree.XML(session.postblob(filepath, xml=resource)).find('./') 

    if r is None or r.get('uri') is None:
        print 'Upload failed'
    else:
        print 'Uploaded ID: %s, URL: %s'%(r.get('resource_uniq'), r.get('uri'))
        f['url'] = r.get('uri')

# upload dataset
dataset = etree.Element ('dataset', name=dataset_name)
for f in files:
    if 'url' not in f:
        continue
    v = etree.SubElement (dataset, 'value', type="object")
    v.text = f['url']
print etree.tostring(dataset)

url = session.service_url('data_service')
r = session.postxml(url, dataset)

if r is None or r.get('uri') is None:
    print 'Dataset failed'
else:
    print 'Dataset ID: %s, URL: %s'%(r.get('resource_uniq'), r.get('uri'))
    f['url'] = r.get('uri')

session.close()
