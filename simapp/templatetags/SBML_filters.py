"""
Django template filters related to the rendering of SBML.
"""

import libsbml
from django import template

from sbmlutils import annotation

register = template.Library()


class AnnotationHTML():

    @classmethod
    def annotation_to_html(cls, item):
        """ Renders HTML representation of given annotation. """
        items = []
        for kcv in xrange(item.getNumCVTerms()):
            cv = item.getCVTerm(kcv)
            q_type = cv.getQualifierType()
            if q_type == 0:
                qualifier = annotation.ModelQualifierType[cv.getModelQualifierType()]
            elif q_type == 1:
                qualifier = annotation.BiologicalQualifierType[cv.getBiologicalQualifierType()]
            items.append(''.join(['<b>', qualifier, '</b>']))

            for k in xrange(cv.getNumResources()):
                uri = cv.getResourceURI(k)
                tokens = uri.split('/')
                resource_id = tokens[-1]
                link = ''.join(['<a href="', uri, '" target="_blank">', resource_id, '</a>'])
                items.append(link)
        res = "<br />".join(items)
        return res

@register.filter
def SBML_astnodeToString(astnode):
    return libsbml.formulaToString(astnode)


@register.filter
def SBML_annotationToString(annotation):
    return AnnotationHTML.annotation_to_html(annotation)


@register.filter
def SBML_unitDefinitionToString1(ud):
    return libsbml.UnitDefinition_printUnits(ud)

unit_dict = dict()
unit_dict['kilogram'] = 'kg'
unit_dict['meter'] = 'm'
unit_dict['metre'] = 'm'
unit_dict['second'] = 's'


@register.filter
def SBML_unitDefinitionToString(udef):
    """ Proper formating of the units.
        TODO: fix bug with scale and multiplier
    """
    libsbml.UnitDefinition_reorder(udef)
    items = []
    for u in udef.getListOfUnits():
        # multiplier
        m = u.getMultiplier()
        if abs(m-1.0) < 1E-10:
            m = ''
        else:
            m = str(m) + '*'
        s = u.getScale()
        e = u.getExponent()
        k = libsbml.UnitKind_toString(u.getKind())
        k = unit_dict.get(k, k)
        
        # (multiplier * 10^scale *ukind)^exponent
        if s == 0 and e == 1:
            string = '{}{}'.format(m, k)
        elif (s == 0) and (m == ''):
            string = '{}^{}'.format(k,e)
        else:
            string = '({}10^{}*{})^{}'.format(m, s, k, e)
        items.append(string)
    return ' * '.join(items)


@register.filter
def SBML_modelHistoryToString(mhistory):
    return modelHistoryToString(mhistory)


@register.filter
def SBML_reactionToString(reaction):
    return _equationStringFromReaction(reaction)


def _equationStringFromReaction(reaction):
    left = halfEquation(reaction.getListOfReactants())
    right = halfEquation(reaction.getListOfProducts())
    if reaction.getReversible():
        sep = '<=>'
    else:
        sep = '=>'
    # mods = modifierEquation(reaction.getListOfModifiers())
    # if mods == None:
    #     return " ".join([left, sep, right])
    # else:
    #     return " ".join([left, sep, right, mods])
    return " ".join([left, sep, right])


def modifierEquation(modifierList):
    if len(modifierList) == 0:
        return None
    mids = [m.getSpecies() for m in modifierList]
    return '[' + ', '.join(mids) + ']' 


def halfEquation(speciesList):
    items = []
    for sr in speciesList:
        stoichiometry = sr.getStoichiometry()
        species = sr.getSpecies()
        if abs(stoichiometry-1.0)<1E-8:
            sd = '{}'.format(species)
        elif abs(stoichiometry+1.0)<1E-8:
            sd = '-{}'.format(species)
        elif stoichiometry > 0:
            sd = '{} {}'.format(stoichiometry, species)
        elif stoichiometry < 0:
            sd = '-{} {}'.format(stoichiometry, species)
        items.append(sd)
    return ' + '.join(items)


def modelHistoryToString(mhistory):
    """ Renders HTML representation of the model history. """
    if not mhistory:
        return ""
    items = []
    items.append('<b>Creator</b>')
    for kc in xrange(mhistory.getNumCreators()):
        cdata = []
        c = mhistory.getCreator(kc)
        if c.isSetGivenName():
            cdata.append(c.getGivenName())
        if c.isSetFamilyName():
            cdata.append(c.getFamilyName())
        if c.isSetOrganisation():
            cdata.append(c.getOrganisation())
        if c.isSetEmail():
            cdata.append('<a href="mailto:{}" target="_blank">{}</a>'.format(c.getEmail(), c.getEmail()))
        items.append(", ".join(cdata))
    if mhistory.isSetCreatedDate():
        items.append('<b>Created:</b> ' + dateToString(mhistory.getCreatedDate()))
    for km in xrange(mhistory.getNumModifiedDates()):
        items.append('<b>Modified:</b> ' + dateToString(mhistory.getModifiedDate(km)))
    items.append('<br />')
    return "<br />".join(items)


def dateToString(d):
    """ Creates string representation of date. """
    return "{}-{:0>2d}-{:0>2d} {:0>2d}:{:0>2d}".format(d.getYear(), d.getMonth(), d.getDay(),
        d.getHour(), d.getMinute())
