from lxml import etree

# Charger le schéma XSD
with open('voye_app/docs/voye_project.xsd', 'rb') as f:
    schema_root = etree.XML(f.read())

schema = etree.XMLSchema(schema_root)

# Charger le document XML
with open('voye_app/templates/index_document_view_form.xml', 'rb') as f:
    xml_doc = etree.XML(f.read())

# Valider le document XML
try:
    schema.assertValid(xml_doc)
    print("Le document XML est valide.")
except etree.DocumentInvalid as e:
    print("Le document XML n'est pas valide.")
    print(e)
