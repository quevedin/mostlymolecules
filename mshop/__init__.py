import subprocess
import os
import sys
import StringIO
import json

import shapeways

def get_keys(filename='oauth_keys.json'):
    '''Returns keys stored in filename as ((consumer_key, consumer_key_secret), (access_token, access_token_secret))'''
    keys = json.load(open(filename))
    
    r = ((keys['consumer_key'], keys['consumer_key_secret']), (keys['access_token'], keys['access_token_secret']))
    
    return r
    
def get_wrl(molecule_name, spacefill=True):
    # TODO: use operating system's temporary file facilities so you can run concurrently
    
    script = "load \":%s\"\n" % (molecule_name,)
    if spacefill:
        script += "spacefill on\n"
    script += "write temp.wrl" 
    
    open("temp.script", "w").write(script)
    command = "java -mx512m -jar JmolData.jar -s temp.script"
    subprocess.call(command, stdout=open(os.devnull, 'w'))
    wrl = StringIO.StringIO(open("temp.wrl", "rb").read())
    os.remove("temp.script")
    os.remove("temp.wrl")
    return wrl

def add_assortment(molecule_name):
    '''Adds a molecule in an assortment of sizes, materials and model types.'''
    
    # Metal
    add_molecule(molecule_name, size='mini', material='metal', spacefill=False)
    add_molecule(molecule_name, size='small', material='metal', spacefill=False)
    
    # Gypsum
    add_molecule(molecule_name, size='small', material='gypsum', spacefill=True)
    add_molecule(molecule_name, size='medium', material='gypsum', spacefill=True)
    add_molecule(molecule_name, size='medium', material='gypsum', spacefill=False)
    
    # Ceramic
    add_molecule(molecule_name, size='large', material='ceramic', spacefill=False)
    
def add_molecule(molecule_name, size='medium', material='gypsum', spacefill=True):
    '''
    molecule_name is the PubChem resolvable molecule name.  Capitalization is preserved for use in the title and description, so type "Aspirin" and not "aspirin".
    size is 'mini', 'small', 'medium' or 'large'.  They correspond to the following:
   
    'mini':   x10,000,000 (1A = 1mm)
    'small':  x20,000,000 (1A = 2mm)
    'medium': x40,000,000 (1A = 4mm)
    'large':  x80,000,000 (1A = 8mm)
    
    Material is 'metal', 'gypsum' or 'ceramic'.
    
    Spacefill is True or False, and determine whether ball and stick (False) or Van der Waals radii (True) are used.
    
    Some combinations, such as a mini ball and stick in porcelain, are unlikely to be printable.  Currently this check is not front loaded.
    '''
    
    (consumer_key, access_token) = get_keys()
        
    api = shapeways.API(consumer_key, access_token)
    
    scale = {
        'mini': 0.001,
        'small': 0.002,
        'medium': 0.004,
        'large': 0.008
    }[size.lower()]
    
    materials = {
        'metal': [(id, 0.0) for id in [89, 66, 83, 81, 86, 87, 84, 85, 23, 28, 90, 39, 38, 54, 31, 37, 88, 53]],
        'gypsum': [(26, 0.0)],
        'ceramic': [(id, 0.0) for id in [63, 64, 74, 73, 72, 70]]
    }[material.lower()]
    
    factor = int(scale * 1000 * 10 * 1000000)
    size_equivalence = scale * 1000
    
    title = "%s molecule (x%s, 1A = %dmm)" % (molecule_name.capitalize(), "{:,}".format(factor), size_equivalence)
    pubchem_url = "http://www.ncbi.nlm.nih.gov/pccompound?term=%s" % molecule_name
    description = "See PubChem's <a href=\"%s\">%s</a> listings for more info.  Created using <a href=\"http://jmol.sourceforge.net/\">Jmol</a>.<BR>By <a href=\"https://twitter.com/justanotherpaul\">@justanotherpaul</a>.  Fork this on Github: <a href=\"https://github.com/pauldw/mostlymolecules\">https://github.com/pauldw/mostlymolecules</a>." % (pubchem_url, molecule_name)

    api.add_model(
        get_wrl(molecule_name, spacefill), 
        '%s.wrl' % molecule_name,
        title = title,
        description = description,
        is_public = True,
        is_for_sale = True,
        is_downloadable = True,
        default_material_id = materials[0][0],
        scale = scale,
        materials = materials
    )