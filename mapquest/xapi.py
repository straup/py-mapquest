import urllib2
import sys

try:
    import elementtree.ElementTree as ET
except Exception, e :
    import xml.etree.ElementTree as ET

class xapi:

    def __init__(self, host='open.mapquestapi.com', version='0.6'):
        self.host = host
        self.version = version
        self.endpoint = "http://%s/xapi/api/%s/" % (self.host, self.version)

    # this doesn't actually know how to deal with ways...

    def query(self, type, pair, bbox) :

        # for example
        # [bbox=-123.51855362314379,37.33815370551646,-121.3212879982315,38.31438176170056]

        wnes = ",".join(map(str, [bbox[1], bbox[0], bbox[3], bbox[2]]))
        q = "%s[%s][bbox=%s]" % (type, pair, wnes)

        url = self.endpoint + q
        # print >> sys.stderr, url

        rsp = urllib2.urlopen(url)
        doc = ET.parse(rsp)

        features = []

        xpath = ".//%s" % type

        for what in doc.findall(xpath):

            _what = what.attrib

            for t in what.findall(".//tag"):
                k = t.attrib['k']
                v = t.attrib['v']
                _what[k] = v

            lat = float(_what['lat'])
            lon = float(_what['lon'])

            del(_what['lat'])
            del(_what['lon'])

            features.append({
                    'type' : 'Feature',
                    'geometry' : {
                        'type' : 'Point',
                        'coordinates' : [ lon, lat ],
                        },
                    'properties' : _what
                    })

        return {
            'type' : 'FeatureCollection',
            'features' : features
            }

if __name__ == '__main__' :

    # python ./xapi.py "amenity=hospital" 37.695141 -123.013657 37.832371 -122.356979 > hospitals-sfcounty.json

    import sys
    import json

    query = sys.argv[1]
    bbox = sys.argv[2:6]

    x = xapi()
    rsp = x.query("node", query, bbox)

    print json.dumps(rsp, indent=2)
