"""
Create detailed HTML report from given SBML.

The model report is implemented based on the django template language, which
 is used to render the SBML information.
"""

import libsbml
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from django.template import loader, RequestContext
from django.shortcuts import Http404

from simapp.models import CompModel

# TODO: rate rules are not displayed correctly (they need dy/dt on the left side, compared to AssignmentRules)
# TODO: hasOnlySubstanceUnits missing in species table


def report(request, model_pk):
    """
    Creates the report view for the given SBML model.
    SBML has to be in the database.
    """
    sbml_model = get_object_or_404(CompModel, pk=model_pk)
    sbml_path = sbml_model.file.path     # this is the absolute path in filesystem
    
    doc = libsbml.readSBMLFromFile(str(sbml_path))
    model = doc.getModel()
    if not model:
        print 'Model could not be read.'
        raise Http404
    
    # Create the value_dictionary
    values = create_value_dictionary(model)

    # Render the template with the data
    template = loader.get_template('report/report.html')
    context = RequestContext(request, {
        'doc': doc,
        'sbml_model': sbml_model,
        'model': model,
        'values': values, 
        'units': model.getListOfUnitDefinitions(),
        'units_size': model.getListOfUnitDefinitions().size(),
        'compartments': model.getListOfCompartments(),
        'compartments_size': model.getListOfCompartments().size(),
        'functions': model.getListOfFunctionDefinitions(),
        'functions_size': model.getListOfFunctionDefinitions().size(),
        'parameters': model.getListOfParameters(),
        'parameters_size': model.getListOfParameters().size(),
        'rules': model.getListOfRules(),
        'rules_size': model.getListOfRules().size(),
        'assignments': model.getListOfInitialAssignments(),
        'assignments_size': model.getListOfInitialAssignments().size(),
        'species': model.getListOfSpecies(),
        'species_size': model.getListOfSpecies().size,
        'reactions': model.getListOfReactions(),
        'reactions_size': model.getListOfReactions().size(),
        'constraints': model.getListOfConstraints(),
        'constraints_size': model.getListOfConstraints().size(),
        'events': model.getListOfEvents(),
        'events_size': model.getListOfEvents().size(),
    })
    return HttpResponse(template.render(context))


def create_value_dictionary(model):
    values = dict()
    
    # parse all the initial assignments
    for assignment in model.getListOfInitialAssignments():
        sid = assignment.getId()
        math = ' = {}'.format(libsbml.formulaToString(assignment.getMath()))
        values[sid] = math
    # rules
    for rule in model.getListOfRules():
        sid = rule.getVariable()
        math = ' = {}'.format(libsbml.formulaToString(rule.getMath()))
        values[sid] = math
    return values
