"""
Definition of database objects to describe simulations & simulation series.
"""
from __future__ import print_function, division

import os
import logging
import warnings
import datetime

from django.db import models
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.files import File
from django_enumfield import enum

from simapp.storage import OverwriteStorage

# ===============================================================================
# Core
# ===============================================================================
from multiscale.multiscale_settings import COMPUTERS
from multiscale.util.util_classes import hash_for_file


class Core(models.Model):
    """ Single computer core for simulation, defined by ip and cpu.
    Time corresponds to the last time the core object was accessed/used.
    This can be creation time or simulation time.
    """
    ip = models.CharField(max_length=200)
    cpu = models.IntegerField()
    time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return '{}-cpu-{}'.format(self.ip, self.cpu)
    
    def _is_active(self, cutoff_minutes=10):
        """ Test if simulation is still active. """
        if not self.time:
            return False
        return timezone.now() <= self.time + datetime.timedelta(minutes=cutoff_minutes)
    
    active = property(_is_active)
    
    class Meta:
        verbose_name = "Core"
        verbose_name_plural = "Cores"
        unique_together = ("ip", "cpu")
        
    def _get_computer_name(self):
        return COMPUTERS.get(self.ip, self.ip)
    computer = property(_get_computer_name)


# ===============================================================================
# CompModel
# ===============================================================================
class CompModelException(Exception):
        pass


class CompModelFormat(enum.Enum):
    SBML = 1
    CELLML = 2
    labels = {
        SBML: "SBML",
        CELLML: "CELLML"
    }


class CompModel(models.Model):
    """ Storage class for models. """
    model_id = models.CharField(max_length=200, unique=True)
    model_format = enum.EnumField(CompModelFormat)
    file = models.FileField(upload_to='model', max_length=200, storage=OverwriteStorage())
    md5 = models.CharField(max_length=36)
    
    def __str__(self):
        return '<{}: {}>'.format(self.model_format_str, self.model_id)
    
    class Meta:
        verbose_name = 'CompModel'
        verbose_name_plural = 'CompModels'
    
    def _filepath(self):
        return str(self.file.path)
    filepath = property(_filepath)

    def _model_format_str(self):
        return CompModelFormat.labels[self.model_format]
    model_format_str = property(_model_format_str)

    def _md5_short(self, length=10):
        return '{}...'.format(self.md5[0:length])
    md5_short = property(_md5_short)
    
    def _sbml_id(self):
        if self.is_sbml():
            return self.model_id
        return None
    sbml_id = property(_sbml_id)
    
    def is_sbml(self):
        return self.model_format == CompModelFormat.SBML

    def is_cellml(self):
        return self.model_format == CompModelFormat.CELLML
    
    @classmethod
    def create(cls, file_path, model_format):
        if model_format not in CompModelFormat.values:
            raise CompModelException('model_format is not a supported format: {}'.format(model_format))
        try:
            with open(file_path) as f:
                pass
        except IOError as exc:
            raise IOError("%s: %s" % (file_path, exc.strerror))
        
        # check if model id and filename are identical
        if model_format == CompModelFormat.SBML:
            model_id = cls._get_sbml_id_from_file(file_path)
            # if '{}.xml'.format(model_id) != os.path.basename(file_path):
            #     raise CompModelException('model id different from basename of file:, {}, {}'.format(model_id, file_path))
        else:
            model_id = os.path.basename(file_path)
        
        # check via hash
        md5 = hash_for_file(file_path, hash_type='MD5')
        try:
            model = cls.objects.get(model_id=model_id)
            if model.md5 == md5:
                logging.info('CompModel already in database: {}'.format(model_id))
                return model
            else:
                # the files are not identical
                warn_string = 'CompModel exists with model_id, model is not created: {}'.format(model_id)
                # TODO: how to handle logging and warnings correctly
                logging.warn(warn_string)
                warnings.warn(warn_string)
                return None
            
        except ObjectDoesNotExist: 
            f = open(file_path, 'r')
            myfile = File(f)
            logging.info('CompModel created : {}'.format(model_id))
            model = cls(model_id=model_id, model_format=model_format, file=myfile, md5=md5)
            model.save() 
            return model
    
    @staticmethod
    def _get_sbml_id_from_file(filepath):
        """ Reads the SBML id from the given file. """
        import libsbml
        doc = libsbml.SBMLReader().readSBML(filepath)
        sbml_id = doc.getModel().getId()
        return sbml_id
   

# ===============================================================================
# Settings
# ===============================================================================
class DataType(enum.Enum):
    STR = 1
    BOOL = 2
    FLOAT = 3
    INT = 4
    labels = {
        STR: "str", BOOL: "bool", FLOAT: "float", INT: "int"
    }
    
    @staticmethod
    def cast_value(value, datatype):
        """ Cast setting to corresponding datatype. """
        if datatype == DataType.STR:
            return str(value)
        elif datatype == DataType.FLOAT:
            return float(value)
        elif datatype == DataType.INT:
            return int(value)
        elif datatype == DataType.BOOL:
            return bool(value)
        else:
            raise KeyError(datatype)


class SettingKey(enum.Enum):
    INTEGRATOR = 1
    VAR_STEPS = 2
    ABS_TOL = 3
    REL_TOL = 4
    T_START = 5
    T_END = 6
    STEPS = 7
    STIFF = 8
    MIN_TIME_STEP = 9
    MAX_TIME_STEP = 10
    MAX_NUM_STEP = 11
    labels = {
        INTEGRATOR: "INTEGRATOR", VAR_STEPS: "VAR_STEPS",
        ABS_TOL: "ABS_TOL", REL_TOL: "REL_TOL",
        T_START: "T_START", T_END: "T_END", STEPS: "STEPS", STIFF: "STIFF",
        MIN_TIME_STEP: "MIN_TIME_STEP", MAX_TIME_STEP: "MAX_TIME_STEP",
        MAX_NUM_STEP: "MAX_NUM_STEP"
    }
    
SETTINGS_DATATYPE = {
    SettingKey.INTEGRATOR: DataType.STR,  # due to enum.Enum
    SettingKey.VAR_STEPS: DataType.BOOL,
    SettingKey.ABS_TOL: DataType.FLOAT,
    SettingKey.REL_TOL: DataType.FLOAT,
    SettingKey.T_START: DataType.FLOAT,
    SettingKey.T_END: DataType.FLOAT,
    SettingKey.STEPS: DataType.INT,
    SettingKey.STIFF: DataType.BOOL,
    SettingKey.MIN_TIME_STEP: DataType.FLOAT,
    SettingKey.MAX_TIME_STEP: DataType.FLOAT,
    SettingKey.MAX_NUM_STEP: DataType.INT,
}


class SimulatorType(enum.Enum):
    COPASI = "COPASI"
    ROADRUNNER = "ROADRUNNER"


class Setting(models.Model):
    DEFAULTS = {
        SettingKey.INTEGRATOR: SimulatorType.ROADRUNNER,
        SettingKey.VAR_STEPS: True,
        SettingKey.ABS_TOL: 1E-6,
        SettingKey.REL_TOL: 1E-6,
        SettingKey.STIFF: True
    }  
    
    key = enum.EnumField(SettingKey)
    value = models.CharField(max_length=40)
    datatype = enum.EnumField(DataType)

    def __str__(self):
        return "{} = {}".format(self.key_str, self.value)
    
    def save(self, *args, **kwargs):
        # get the datatype from the dictionary
        self.datatype = SETTINGS_DATATYPE[self.key]
        super(Setting, self).save(*args, **kwargs)  # Call the "real" save() method.
    
    def _cast_value(self):
        return DataType.cast_value(value=self.value, datatype=self.datatype)
    cast_value = property(_cast_value)

    def _key_str(self):
        return SettingKey.labels[self.key]
    key_str = property(_key_str)

    def _datatype_str(self):
        return DataType.labels[self.datatype]
    datatype_str = property(_datatype_str)

    @staticmethod 
    def _combine_dicts(*args):
        """ Combine the dictionaries given in args.
        The last dict wins, i.e. earlier identical key, value pairs
        are overwritten. """
        d_all = dict()
        for d in args:
            d_all.update(d)
        return d_all
    
    @classmethod
    def get_or_create(cls, key, value):
        """ In database represented as string. """
        return cls.objects.get_or_create(key=key, value=str(value))
    
    @classmethod
    def get_or_create_from_dict(cls, d_settings, add_defaults=True):
        """ Get settings based on settings dictionary.
        The settings dictionary is extended with the provided settings.
        """
        if add_defaults:
            d_settings = cls._combine_dicts(cls.DEFAULTS, d_settings)
        
        # create settings from dictionary
        settings = []
        for key, value in d_settings.iteritems():
            s, _ = cls.get_or_create(key=key, value=value)
            settings.append(s)
        return settings
    
    @classmethod
    def get_or_create_defaults(cls):
        """ Gets the default settings defined via DEFAULTS. """
        return cls.get_or_create_from_dict({}, add_defaults=True)

# ===============================================================================
# Method
# ===============================================================================


class MethodType(enum.Enum):
    ODE = 1
    FBA = 2
    labels = { 
        ODE: "ODE", FBA: "FBA"
    }
    

class Method(models.Model):
    """ Method settings are managed via a collection of settings. """
    method_type = enum.EnumField(MethodType)
    settings = models.ManyToManyField(Setting)

    def __str__(self):
        return 'M{}'.format(self.pk) 
    
    class Meta:
        verbose_name = 'Method'
        verbose_name_plural = "Methods"
        
    def get_settings_dict(self):
        return {s.key: s.cast_value for s in self.settings.all()}
    
    def get_setting(self, key):
        s = self.settings.get(key=key)
        return s.cast_value

    def _method_type_str(self):
        return MethodType.labels[self.method_type]
    method_type_str = property(_method_type_str)

    def _get_integrator(self):
        return self.get_setting(SettingKey.INTEGRATOR)
    integrator = property(_get_integrator)
        
    @staticmethod
    def _create_method(method_type, settings):
        method = Method(method_type=method_type)
        method.save()
        method.settings.add(*settings)
        return method

    @staticmethod
    def get_or_create(method_type, settings):
        """ Find or create the method belonging to the set of settings. """
        settings_set = frozenset(settings)
        for method in Method.objects.filter(method_type=method_type):
            # uniqueness tested via the set equality 
            if settings_set == frozenset(method.settings.all()):
                return method
        else:
            return Method._create_method(method_type, settings)
    

# ===============================================================================
# Parameter
# ===============================================================================
class ParameterType(enum.Enum):
    GLOBAL_PARAMETER = 1
    BOUNDARY_INIT = 2
    FLOATING_INIT = 3
    NONE_SBML_PARAMETER = 4
    labels = {
        GLOBAL_PARAMETER: 'GLOBAL_PARAMETER',
        BOUNDARY_INIT: 'BOUNDARY_INIT',
        FLOATING_INIT: 'FLOATING_INIT',
        NONE_SBML_PARAMETER: 'NONE_SBML_PARAMETER'
    }    


class Parameter(models.Model):
    key = models.CharField(max_length=50)
    value = models.FloatField()
    unit = models.CharField(max_length=50)
    parameter_type = enum.EnumField(ParameterType)
    
    def __str__(self):
        return '{} = {} [{}]'.format(self.key, self.value, self.unit)
    
    class Meta:
        unique_together = ("key", "value")

    def _parameter_type_str(self):
        return ParameterType.labels[self.parameter_type]
    parameter_type_str = property(_parameter_type_str)

# ===============================================================================
# Task
# ===============================================================================

class TaskStatus(enum.Enum):
    """ Finalization of tasks, so simulations can not be changed/added."""
    OPEN = 1       # simulations can be added
    FINALIZED = 2  # no simulations can be added or removed

    labels = {
        OPEN: 'OPEN',
        FINALIZED: 'FINALIZED'
    }


class Task(models.Model):
    """ Tasks are defined sets of simulations under consistent conditions.
        Tasks are compatible on their method setting and the
        underlying model.
        Task are uniquely identified via the combination of model, method
        and the information string. Replicates of the same task can be run via
        modifying the info.
    """
    model = models.ForeignKey(CompModel, related_name="tasks")
    method = models.ForeignKey(Method, related_name="tasks")
    priority = models.IntegerField(default=0)
    info = models.TextField(null=True, blank=True)
    status = enum.EnumField(TaskStatus, default=TaskStatus.OPEN)
    
    class Meta:
        unique_together = ("model", "method", "info")
    
    def __str__(self):
        return 'T{}'.format(self.pk)

    def _get_setting(self, key):
        return self.method.settings.get(key=key).cast_value
    
    def _get_integrator(self):
        return self._get_setting(SettingKey.INTEGRATOR)
    integrator = property(_get_integrator)
    
    def _get_var_steps(self):
        return self._get_setting(SettingKey.VAR_STEPS)
    varSteps = property(_get_var_steps)
    
    def _get_rel_tol(self):
        return self._get_setting(SettingKey.REL_TOL)
    relTol = property(_get_rel_tol)
    
    def _get_abs_tol(self):
        return self._get_setting(SettingKey.ABS_TOL)
    absTol = property(_get_abs_tol)
      
    def _get_steps(self):
        return self._get_setting(SettingKey.STEPS)
    steps = property(_get_steps)
    
    def _get_tstart(self):
        return self._get_setting(SettingKey.T_START)
    tstart = property(_get_tstart)
    
    def _get_tend(self):
        return self._get_setting(SettingKey.T_END)
    tend = property(_get_tend)

    def sim_count(self):
        return self.simulations.count()
    
    def _status_count(self, status):
        return self.simulations.filter(status=status).count()
    
    def done_count(self):
        return self._status_count(SimulationStatus.DONE)
    
    def assigned_count(self):
        return self._status_count(SimulationStatus.ASSIGNED)
    
    def unassigned_count(self):
        return self._status_count(SimulationStatus.UNASSIGNED)
    
    def error_count(self):
        return self._status_count(SimulationStatus.ERROR)

    def is_done(self):
        return self.done_count() == self.sim_count()

    # status functions
    def finalize_status(self):
        self.status = TaskStatus.FINALIZED
        self.save()

    def open_status(self):
        self.status = TaskStatus.OPEN
        self.save()

    def has_status_finalized(self):
        return self.status == TaskStatus.FINALIZED

    def has_status_open(self):
        return self.status == TaskStatus.OPEN

    def _status_str(self):
        """ Task status. """
        return TaskStatus.labels[self.status]
    status_str = property(_status_str)


# ===============================================================================
# Simulation
# ===============================================================================

class SimulationStatus(enum.Enum):
    UNASSIGNED = 1
    ASSIGNED = 2
    DONE = 3
    ERROR = 4
    labels = {
        UNASSIGNED: "UNASSIGNED",
        ASSIGNED: "ASSIGNED",
        DONE: "DONE",
        ERROR: "ERROR"
    }
    rev_labels = dict(zip(labels.values(), labels.keys()))

class Simulation(models.Model):     
    task = models.ForeignKey(Task, related_name='simulations')
    parameters = models.ManyToManyField(Parameter)
    status = enum.EnumField(SimulationStatus, default=SimulationStatus.UNASSIGNED)
    time_create = models.DateTimeField(default=timezone.now)
    time_assign = models.DateTimeField(null=True, blank=True)
    core = models.ForeignKey(Core, null=True, blank=True)
    time_sim = models.DateTimeField(null=True, blank=True)

    def clean(self):
        # Don't allow the creation of simulations for finalized tasks
        # New simulations do not have a primary key yet
        if self.pk is None and self.task.status == TaskStatus.FINALIZED:
            raise ValidationError('No simulation can be added to a FINALIZED task. \
                                   OPEN task for adding simulations first.')

    def save(self, *args, **kwargs):
        self.clean()
        super(Simulation, self).save(*args, **kwargs)  # Call the "real" save() method.

    @classmethod
    def unassigned_objects(cls):
        return cls.objects.filter(status=SimulationStatus.UNASSIGNED)

    @classmethod
    def assigned_objects(cls):
        return cls.objects.filter(status=SimulationStatus.ASSIGNED)

    @classmethod
    def done_objects(cls):
        return cls.objects.filter(status=SimulationStatus.DONE)

    @classmethod
    def error_objects(cls):
        return cls.objects.filter(status=SimulationStatus.ERROR)

    def __str__(self):
        return 'S{}'.format(self.pk)
    
    def is_error(self):
        return self.status == SimulationStatus.ERROR

    def is_unassigned(self):
        return self.status == SimulationStatus.UNASSIGNED

    def is_assigned(self):
        return self.status == SimulationStatus.ASSIGNED

    def is_done(self):
        return self.status == SimulationStatus.DONE
    
    def _get_duration(self):
        if not self.time_assign or not self.time_sim:
            return None
        return (self.time_sim - self.time_assign).total_seconds()  # difference converted to seconds
    duration = property(_get_duration)
    
    def _is_hanging(self, cutoff_minutes=10):
        """ Simulation did not finish """
        if not self.time_assign:
            return False
        elif self.status != SimulationStatus.ASSIGNED.value:
            return False
        else:
            return timezone.now() >= self.time_assign+datetime.timedelta(minutes=cutoff_minutes)
    hanging = property(_is_hanging)

    def _status_str(self):
        return SimulationStatus.labels[self.status]
    status_str = property(_status_str)

# ===============================================================================
# Result
# ===============================================================================
def result_filename(self, filename):
    name = filename.split("/")[-1]
    return os.path.join('result', str(self.simulation.task), name)


class ResultType(enum.Enum):
    CSV = 1
    HDF5 = 2
    JSON = 3
    PNG = 4
    
    labels = {
        CSV: "csv",
        HDF5: "hdf5",
        JSON: "json",
        PNG: "png"
    }


class Result(models.Model):
    """ Result of simulation. 
        The type is defined via the simulation type.
        and not already existing. Write api function to store result.
    """
    # TODO: manage multiple result types
    # TODO: check that result is unique for simulation
    simulation = models.ForeignKey(Simulation, related_name="results")
    result_type = enum.EnumField(ResultType)
    file = models.FileField(upload_to=result_filename, max_length=200, storage=OverwriteStorage())
    
    def __str__(self):
        return 'R{} ({})'.format(self.pk, self.result_type_str)

    def _filepath(self):
        return str(self.file.path)
    filepath = property(_filepath)

    def _result_type_str(self):
        return ResultType.labels[self.result_type]
    result_type_str = property(_result_type_str)


# ===============================================================================
# Plots and Analysis
# ===============================================================================
