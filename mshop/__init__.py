import subprocess
import os
import sys
import StringIO

import shapeways

# Get keys from the environment
try:
    consumer_key = (os.environ['MSHOP_CONSUMER_KEY'], os.environ['MSHOP_CONSUMER_KEY_SECRET'])
    access_token = (os.environ['MSHOP_ACCESS_TOKEN'], os.environ['MSHOP_ACCESS_TOKEN_SECRET'])
except KeyError, e:
    sys.stderr.write("Please set MSHOP_CONSUMER_KEY, MSHOP_CONSUMER_KEY_SECRET, MSHOP_ACCESS_TOKEN and MSHOP_ACCESS_TOKEN_SECRET environment variables.\n")

def get_wrl(molecule_name):
    # TODO: use operating system's temporary file facilities so you can run concurrently
    script = "load \":%s\"\nspacefill on\nwrite temp.wrl" % (molecule_name,)
    open("temp.script", "w").write(script)
    command = "java -mx512m -jar JmolData.jar -s temp.script"
    subprocess.call(command, stdout=open(os.devnull, 'w'))
    wrl = StringIO.StringIO(open("temp.wrl", "rb").read())
    os.remove("temp.script")
    os.remove("temp.wrl")
    return wrl

def add_molecule(molecule_name, size='medium'):
    '''
    molecule_name is the PubChem resolvable molecule name.  Capitalization is preserved for use in the title and description, so type "Aspirin" and not "aspirin".
    size is 'mini', 'small', 'medium' or 'large'.  They correspond to the following:
   
    'mini':   x10,000,000 (1A = 1mm)
    'small':  x20,000,000 (1A = 2mm)
    'medium': x40,000,000 (1A = 4mm)
    'large':  x80,000,000 (1A = 8mm)
    '''
        
    api = shapeways.API(consumer_key, access_token)
    
    scale = {
        'mini': 0.001,
        'small': 0.002,
        'medium': 0.004,
        'large': 0.008
    }[size.lower()]
    
    factor = int(scale * 1000 * 10 * 1000000)
    size_equivalence = scale * 1000
    
    title = "%s molecule (x%s, 1A = %dmm)" % (molecule_name.capitalize(), "{:,}".format(factor), size_equivalence)
    pubchem_url = "http://www.ncbi.nlm.nih.gov/pccompound?term=%s" % molecule_name
    description = "See PubChem's <a href=\"%s\">%s</a> listings for more info.  Created using <a href=\"http://jmol.sourceforge.net/\">Jmol</a>.<BR>By <a href=\"https://twitter.com/justanotherpaul\">@justanotherpaul</a>.  Fork this on Github: <a href=\"https://github.com/pauldw/mostlymolecules\">https://github.com/pauldw/mostlymolecules</a>." % (pubchem_url, molecule_name)

    api.add_model(
        get_wrl(molecule_name), 
        '%s.wrl' % molecule_name,
        title = title,
        description = description,
        is_public = True,
        is_for_sale = True,
        is_downloadable = True,
        default_material_id = 26, # 26 - Full Color Sandstone
        scale = scale
    )