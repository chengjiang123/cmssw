#!/usr/bin/env python
"""
_pp_

Scenario supporting proton collisions

"""

import os
import sys

from Configuration.DataProcessing.Scenario import Scenario
import FWCore.ParameterSet.Config as cms
from Configuration.PyReleaseValidation.ConfigBuilder import ConfigBuilder
from Configuration.PyReleaseValidation.ConfigBuilder import Options
from Configuration.PyReleaseValidation.ConfigBuilder import defaultOptions
from Configuration.PyReleaseValidation.ConfigBuilder import installFilteredStream
from Configuration.PyReleaseValidation.ConfigBuilder import addOutputModule
from Configuration.GlobalRuns.reco_TLR import reco_TLR

class pp(Scenario):
    """
    _pp_

    Implement configuration building for data processing for proton
    collision data taking

    """


    def promptReco(self, globalTag, skims = [], writeTiers = ['RECO','ALCA']):
        """
        _promptReco_

        Proton collision data taking prompt reco

        """
        if len(skims) >0:
          step = ',ALCAPRODUCER:'
          for skim in skims:
            step += (skim+"+")
          step = step.rstrip('+')
        else:
          step = ''
        options = Options()
        options.__dict__.update(defaultOptions.__dict__)
        options.scenario = "pp"
        options.step = 'RAW2DIGI,L1Reco,RECO:reconstruction_withPixellessTk'+step+',DQM,ENDJOB'
        options.isMC = False
        options.isData = True
        options.beamspot = None
        options.eventcontent = None
        options.magField = 'AutoFromDBCurrent'
        options.conditions = "FrontierConditions_GlobalTag,%s" % globalTag
        options.relval = False
        
        
        process = cms.Process('RECO')
        cb = ConfigBuilder(options, process = process)

        # Input source
        process.source = cms.Source("PoolSource",
            fileNames = cms.untracked.vstring()
        )
        cb.prepare()


        for tier in writeTiers: 
          addOutputModule(process, tier, "RECO")        

        #add the former top level patches here
        reco_TLR(process)
        
        return process

    def expressProcessing(self, globalTag,  writeTiers = [],
                          datasets = [], alcaDataset = None):
        """
        _expressProcessing_

        Implement proton collision Express processing

        """

        options = Options()
        options.__dict__.update(defaultOptions.__dict__)
        options.scenario = "pp"
        options.step = \
          """RAW2DIGI,L1Reco,RECO,ALCA:SiStripCalZeroBias+TkAlMinBias+MuAlCalIsolatedMu+RpcCalHLT,ENDJOB"""
        options.isMC = False
        options.isData = True
        options.eventcontent = None
        options.relval = None
        options.beamspot = None
        options.conditions = "FrontierConditions_GlobalTag,%s" % globalTag
        
        process = cms.Process('EXPRESS')
        cb = ConfigBuilder(options, process = process)

        process.source = cms.Source(
           "NewEventStreamFileReader",
           fileNames = cms.untracked.vstring()
        )
        
        cb.prepare()

        #  //
        # // Install the OutputModules for everything but ALCA
        #//
        self.addExpressOutputModules(process, writeTiers, datasets)
        
        #  //
        # // TODO: Install Alca output
        #//
        
        #add the former top level patches here
        reco_TLR(process)

        return process
    

    def alcaSkim(self, skims):
        """
        _alcaSkim_

        AlcaReco processing & skims for proton collisions

        """
        step = "ALCAOUTPUT:"
        for skim in skims:
          step += (skim+"+")
        options = Options()
        options.__dict__.update(defaultOptions.__dict__)
        options.scenario = "pp"
        options.step = step+'DQM,ENDJOB'
        options.isMC = False
        options.isData = True
        options.beamspot = None
        options.eventcontent = None
        options.relval = None
        options.triggerResultsProcess = 'RECO'
        
        process = cms.Process('ALCA')
        cb = ConfigBuilder(options, process = process)

        # Input source
        process.source = cms.Source(
           "PoolSource",
           fileNames = cms.untracked.vstring()
        )

        cb.prepare() 

        return process
                

        

        


    def dqmHarvesting(self, datasetName, runNumber,  globalTag, **options):
        """
        _dqmHarvesting_

        Proton collisions data taking DQM Harvesting

        """
        options = defaultOptions
        options.scenario = "pp"
        options.step = "HARVESTING:dqmHarvesting"
        options.isMC = False
        options.isData = True
        options.beamspot = None
        options.eventcontent = None
        options.name = "EDMtoMEConvert"
        options.conditions = "FrontierConditions_GlobalTag,%s" % globalTag
        options.arguments = ""
        options.evt_type = ""
        options.filein = []
 
        process = cms.Process("HARVESTING")
        process.source = cms.Source("PoolSource")
        configBuilder = ConfigBuilder(options, process = process)
        configBuilder.prepare()

        #
        # customise process for particular job
        #
        process.source.processingMode = cms.untracked.string('RunsAndLumis')
        process.source.fileNames = cms.untracked(cms.vstring())
        process.maxEvents.input = -1
        process.dqmSaver.workflow = datasetName
        
        return process
