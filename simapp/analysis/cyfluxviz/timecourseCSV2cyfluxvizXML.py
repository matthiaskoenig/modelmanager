"""
Module for creating the cyfluxviz data from given CSV structure of data, i.e.
one header line of SBML identifiers. First column is 'time' column.

Different from the export format necessary to handle FBA data which has no primary
time column, but a primary odesim column, which specifies all the simulations
which were performed on the SBML network.

@date: 2014-05-11
@author: Matthias Koenig
"""
# TODO: get some minimal examples
# TODO: implement as basic script which can be called on a list of files.

import xml.etree.ElementTree as ETree
import xml.dom.minidom as minidom
from libsbml import readSBML

def getSpeciesDictFromModel(model):
    species = dict()
    slist = model.getListOfSpecies()
    for s in slist:
        species[s.getId()] = s
    return species

def getReactionsDictFromModel(model):
    reactions = dict()
    rlist = model.getListOfReactions()
    for r in rlist:
        reactions[r.getId()] = r
    return reactions

###################################################
# used XML tags
###################################################
FD_COLLECTION = 'fluxDistributionCollection'
FD_LIST = 'listOfFluxDistributions'
FD = 'fluxDistribution'
FD_ID = 'id'
FD_NAME = 'name'
FD_NETWORKID = 'networkId'
FD_TIME = 'time'

FLUX_LIST = 'listOfFluxes'
FLUX = 'flux'
FLUX_ID = 'id'
FLUX_VALUE = 'fluxValue'
FLUX_TYPE = 'type'
FLUX_TYPE_NODE = 'nodeFlux'

CONCENTRATION_LIST = 'listOfConcentrations'
CONCENTRATION = 'concentration'
CONCENTRATION_ID = 'id'
CONCENTRATION_VALUE = 'concentrationValue'
CONCENTRATION_TYPE = 'type'
CONCENTRATION_TYPE_NODE = 'nodeConcentration'
###################################################

def csv2xml(csvfile, xmlfile, model, sep=",", comment="#"):
    """ Converts csv with given SBML model to the xml.
        TODO: very crude way to read the csv, no handling
              empty lines and comments.
    """
    # get species and reactions dictionaries
    species = getSpeciesDictFromModel(model)
    reactions = getReactionsDictFromModel(model)

    # Create core xml
    root = ETree.Element(FD_COLLECTION)
    fdListElement = ETree.SubElement(root, FD_LIST)

    # get the maximum count
    count_max = 0
    f_csv = open(csvfile, 'r')
    for line in f_csv:
        count_max += 1
    f_csv.close()

    # create the xml file
    xmlstring = prettyXML(root)
    print xmlfile
    f = open(xmlfile, 'w')
    f.write(xmlstring)
    f.close()

    # get header and items
    count = 0
    for line in open(csvfile, 'r'):
        if count == 0:
            header = line.split(sep)
            header = [item.strip() for item in header]
            print header
        else:
            items = line.split(sep)
            items = [item.strip() for item in items]
            items_dict = dict()
            for k in xrange(len(header)):
                items_dict[header[k]] = items[k]
            createFluxDistribution(1.0*count/count_max, fdListElement, items_dict, model, reactions, species)
        count += 1

    xmlstring = prettyXML(root)
    print xmlfile
    f = open(xmlfile, 'w')
    f.write(xmlstring)
    f.close()

def createFluxDistribution(count_rel, fdListElement, items_dict, model, reactions, species):
    """ Writes single flux distribution in the xml. """
    modelId = model.getId()
    time = str(items_dict['time'])
    simId = str(count_rel) + 'time_' + time
    
    #Create the FD Element and set the attributes
    fdElement = ETree.SubElement(fdListElement, FD)
    fdElement.set(FD_ID, simId)
    fdElement.set(FD_NAME, simId)
    fdElement.set(FD_NETWORKID, modelId)
    fdElement.set(FD_TIME, time)

    # Create the list of fluxes
    fluxListElement = ETree.SubElement(fdElement, FLUX_LIST)
    concentrationListElement = ETree.SubElement(fdElement, CONCENTRATION_LIST)

    for key in items_dict.keys():
        # Create the fluxes
        if reactions.has_key(key):
            flux = items_dict[key]
            if flux != 0.0:
                fluxElement = ETree.SubElement(fluxListElement, FLUX)
                fluxElement.set(FLUX_ID, key)
                fluxElement.set(FLUX_VALUE, str(flux))
                fluxElement.set(FLUX_TYPE, FLUX_TYPE_NODE)
        # Create the concentrations
        if species.has_key(key):
            concentration = items_dict[key]
            
            concentrationElement = ETree.SubElement(concentrationListElement, CONCENTRATION)
            concentrationElement.set(CONCENTRATION_ID, key)
            concentrationElement.set(CONCENTRATION_VALUE, str(concentration))
            concentrationElement.set(CONCENTRATION_TYPE, CONCENTRATION_TYPE_NODE)


def prettyXML(element):
    """Return a pretty-printed XML string for the Element. """
    rough_string = ETree.tostring(element, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="\t")

if __name__ == "__main__":
    import django
    django.setup()
    
    
    print 'Test: timecourse2cyfluxviz'
    from simapp.models import Simulation
    
    sim = Simulation.objects.get(pk=780)
    
    csvfile = str(sim.timecourse.file.path)
    print csvfile
    xmlfile = csvfile[0:-4] + '_flux.xml'
    print xmlfile
    
    sbmlfile = str(sim.task.model.file.path)
    print sbmlfile
    
    document = readSBML(sbmlfile)
    model = document.getModel()

    csv2xml(csvfile, xmlfile, model=model)