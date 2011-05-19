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

    def query(self, type, pair, bbox) :

        # for example
        # [bbox=-123.51855362314379,37.33815370551646,-121.3212879982315,38.31438176170056]

        wnes = ",".join(map(str, [bbox[1], bbox[0], bbox[3], bbox[2]]))
        q = "%s[%s][bbox=%s]" % (type, pair, wnes)

        url = self.endpoint + q
        # print >> sys.stderr, url

        rsp = urllib2.urlopen(url)
        doc = ET.parse(rsp)

        if type == 'node':
            features = self.nodes(doc)
        elif type == 'way':
            features = self.ways(doc)
        else:
            features = []

        return {
            'type' : 'FeatureCollection',
            'features' : features
            }

    def ways (self, doc):

        features = []

        # because elementtree can't do @attrib=foo
        # selectors pre version 1.3...

        _nodes = {}

        for node in doc.findall(".//node"):
            node_id = node.attrib['id']
            _nodes[node_id] = node

        xpath = ".//way"

        for what in doc.findall(xpath):

            _what = what.attrib

            for t in what.findall(".//tag"):
                k = t.attrib['k']
                v = t.attrib['v']
                _what[k] = v

            nodes = []
            coords = []

            for n in what.findall(".//nd"):

                node_id = n.attrib['ref']
                nodes.append(node_id)

                node = _nodes[node_id]
                lat = node.attrib['lat']
                lon = node.attrib['lon']

                coords.append((lon, lat))

            _what['nodes'] = nodes

            features.append({
                    'type' : 'Feature',
                    'geometry' : {
                        'type' : 'Polygon',
                        'coordinates' : [ coords ]
                        },
                    'properties' : _what
                    })

        return features

    def nodes (self, doc):

        features = []

        xpath = ".//node"

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

        return features

if __name__ == '__main__' :

    # python ./xapi.py "amenity=hospital" 37.695141 -123.013657 37.832371 -122.356979 > hospitals-sfcounty.json

    import sys
    import json

    # sudo, use opt-parser...

    what = sys.argv[1]
    query = sys.argv[2]
    bbox = sys.argv[3:]

    x = xapi()
    rsp = x.query(what, query, bbox)

    print json.dumps(rsp, indent=2)
