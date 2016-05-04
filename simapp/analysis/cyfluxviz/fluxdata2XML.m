function [] = fluxdata2XML(fluxdata, xmlFilename)
% fluxdata2XML : Writes the fluxdata for CyFluxViz to XML. 
% The resulting XML can be imported in CyFluxViz.
%
%   fluxdata : simulation data struct (either flux or kinetic)
%   xmlFilename : output XML file for CyFluxViz
%
% Check which type of flux data (flux simulation or kinetic simulation.
% For a flux simulation the following fields are necessary
%   modelId : SBML model id
%   simIds : unique simulation ids for reference
%   fluxes : matrix of flux values [Nreaction x Nsim]
%
% @author: Matthias Koenig
% @date: 2013-08-07

dType = '';
if all(isfield(fluxdata, {'modelId', 'simIds', 'reactionIds', 'fluxes'}))
   dType = 'Flux';
end

% A kinetic simulations needs in addition the speciesIds and the respective
% concentration matrix for the simulations
%   speciesIds : ids corresponding to the SBML ids
%   concentrations : matrix of concentration values [Nspecies x Nsim]
if strcmp(dType, 'Flux') && all(isfield(fluxdata, {'time', 'speciesIds', 'concentrations'}))
   dType = 'Kinetic';
end

if strcmp(dType, '')
    error('Fields in fluxdata missing. Neither "Flux" or "Kinetic" data.\n Check the fields of "fluxdata"'); 
end

modelId = fluxdata.modelId;
simIds = fluxdata.simIds;
reactionIds = fluxdata.reactionIds;
fluxes = fluxdata.fluxes;           % [Nv x Ns]
Nsim = length(simIds);
Nv = length(reactionIds);

% For kinetic simulations additional concentration values are provided
if strcmp(dType,'Kinetic')
    speciesIds = fluxdata.speciesIds;
    concentrations = fluxdata.concentrations;
    time = fluxdata.time;
    Nx = length(speciesIds);
end

% used XML tags
FD_COLLECTION = 'fluxDistributionCollection';
FD_LIST = 'listOfFluxDistributions';
FD = 'fluxDistribution';
FD_ID = 'id';
FD_NAME = 'name';
FD_NETWORKID = 'networkId';
FD_TIME = 'time';

FLUX_LIST = 'listOfFluxes';
FLUX = 'flux';
FLUX_ID = 'id';
FLUX_VALUE = 'fluxValue';
FLUX_TYPE = 'type';
FLUX_TYPE_NODE = 'nodeFlux';

CONCENTRATION_LIST = 'listOfConcentrations';
CONCENTRATION = 'concentration';
CONCENTRATION_ID = 'id';
CONCENTRATION_VALUE = 'concentrationValue';
CONCENTRATION_TYPE = 'type';
CONCENTRATION_TYPE_NODE = 'nodeConcentration';

% write the XML file for the given data
docNode = com.mathworks.xml.XMLUtils.createDocument(FD_COLLECTION);
docRootNode = docNode.getDocumentElement;
fdListElement = docNode.createElement(FD_LIST);
docRootNode.appendChild(fdListElement);
for ks=1:Nsim
    % Create the FD Element and set the attributes
    fdElement = docNode.createElement(FD);
    fdElement.setAttribute(FD_ID, simIds{ks});
    fdElement.setAttribute(FD_NAME, simIds{ks});
    fdElement.setAttribute(FD_NETWORKID, modelId);
    if strcmp(dType,'Kinetic')
       fdElement.setAttribute(FD_TIME, num2str(time(ks)));
    end
    fdListElement.appendChild(fdElement);
    
    % Create the list of fluxes
    fluxListElement = docNode.createElement(FLUX_LIST);
    fdElement.appendChild(fluxListElement);
    
    % Create the fluxes
    for kv = 1:Nv
        flux = fluxes(kv, ks);
        if (flux ~= 0.0)        
            fluxElement = docNode.createElement(FLUX);
            fluxElement.setAttribute(FLUX_ID, reactionIds{kv});
            fluxElement.setAttribute(FLUX_VALUE, num2str(flux));
            fluxElement.setAttribute(FLUX_TYPE, FLUX_TYPE_NODE);
            fluxListElement.appendChild(fluxElement);
        end
    end
    
    if strcmp(dType,'Kinetic')
        % Create the list of concentrations
        concentrationListElement = docNode.createElement(CONCENTRATION_LIST);
        fdElement.appendChild(concentrationListElement);
    
        % Create the concentrations
        for kx = 1:Nx
            concentration = concentrations(kx, ks);
                    
            concentrationElement = docNode.createElement(CONCENTRATION);
            concentrationElement.setAttribute(CONCENTRATION_ID, speciesIds{kx});
            concentrationElement.setAttribute(CONCENTRATION_VALUE, num2str(concentration));
            concentrationElement.setAttribute(CONCENTRATION_TYPE, CONCENTRATION_TYPE_NODE);
            concentrationListElement.appendChild(concentrationElement);
        end
    end
    
end

% write the xml file
xmlwrite(xmlFilename, docNode);
fprintf('fluxdata2XML : XML file written -> %s\n', xmlFilename);

