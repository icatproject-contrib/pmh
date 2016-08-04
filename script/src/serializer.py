from lxml import etree

class XMLSerializer:

    def __init__(self, 
                 root_name='qdc',
                 root_namespace_id='oai_qdc',
                 root_namespace="http://pandata.org/pmh/oai_qdc/",

                 first_namespace_id='dc',
                 first_namespace="http://purl.org/dc/elements/1.1/",

                 second_namespace_id='dcterms',
                 second_namespace="http://purl.org/dc/terms/",

                 schema_location="http://pandata.org/pmh/oai_qdc/ http://pandata.org/pmh/oai_qdc.xsd",     
                 xsi="http://www.w3.org/2001/XMLSchema-instance"                 
                ):
        
        self.root_name = root_name
        self.root_namespace_id = root_namespace_id
        self.root_namespace = root_namespace
        self.first_namespace_id = first_namespace_id
        self.first_namespace = first_namespace
        self.second_namespace_id = second_namespace_id
        self.second_namespace = second_namespace
        self.schema_location = schema_location
        self.xsi = xsi

        self.nsmap = {
                        self.root_namespace_id: self.root_namespace,
                        self.first_namespace_id: self.first_namespace,
                        self.second_namespace_id: self.second_namespace,
                        'xsi': self.xsi
                     }

        self.root = etree.Element("{"+self.root_namespace+"}"+self.root_name, 
                                  attrib={"{"+self.xsi+"}schemaLocation" : self.schema_location},
                                  nsmap=self.nsmap)

    def getRoot(self):
        return self.root


    def addEntry(self, name, value, parent=None, attributes={}, namespacemap={}, use_second_namespace=False, xsi_type=None):
        
        if parent == None:
            parent = self.root
        
        if use_second_namespace:
            namespace = self.second_namespace
        else:
            namespace = self.first_namespace

        if xsi_type:
            attributes["{"+self.xsi+"}type"] = xsi_type
        elif "{"+self.xsi+"}type" in attributes:
            del attributes["{"+self.xsi+"}type"]

        element = etree.SubElement(parent, "{"+namespace+"}"+str(name), attrib=attributes, nsmap=namespacemap)
        element.text = value
        return element


    def write(self, filename, pretty_print=True):
        self.tree = etree.ElementTree(self.root)
        self.tree.write(filename, pretty_print=pretty_print, encoding="UTF-8", xml_declaration="True")