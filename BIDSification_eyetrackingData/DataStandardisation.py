#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from .File import open_file, save_file
from .StandardisationProcess import *
from .StandardisationProcessDataEyelink import *

class DataStandardisation:

    '''
    Standardization of data

    Parameters
    ----------
    path_oldData: str
        Path of the data directory to BIDSified
    path_newData: str
        Path of the new BIDS data directory

    infofilesname: str
        Name of the file containing the information on the files to be
        BIDSified
    settingsfilename: str
        Name of the file containing the settings of the data to be
        BIDSified

    eyetacktype: str
        Name of the type of eyetackeur used
    dataformat: str
        Data format
    saved_events: list
        List of events to be extracted from the trials

    StartMessage: str
        Message marking the start of the trial
    EndMessage: str
        Message marking the end of the trial
    '''

    def __init__(self, path_oldData, path_newData, infofilesname,
                 settingsfilename, eyetacktype, dataformat, saved_events,
                 StartMessage, EndMessage):

        # checks if the directory of the data to be BISDified exists
        if not os.path.isdir(path_oldData):
            raise ValueError("Directory '%s' does not exist"%path_oldData)


        # global variable
        self.eyetacktype = eyetacktype
        self.saved_events = saved_events
        self.settings = None


        # Standard process
        #----------------------------------------------------------------------
        self.process = StandardisationProcess(path_oldData)
        # Check the information file on all the data files present in the
        #  directory
        self.process.check_infoFiles(infofilesname, dataformat)
        infofilesname = self.process.infofilesname
        # Sort infoFiles to give a dictionnary of list of settings per file and
        #  per participant
        infos = self.process.sort_infoFiles(infofilesname)

        # Eyetracking process
        #----------------------------------------------------------------------
        self.process_ET = None
        if self.eyetacktype=='Eyelink':
            self.process_ET = StandardisationProcessDataEyelink(path_oldData,
                                                                StartMessage,
                                                                EndMessage)

        #######################################################################
        #  BIDSification of all files in infoFiles
        #######################################################################

        # Open the information file
        infoFiles = open_file(infofilesname, path_oldData)

        for f in infoFiles:

            print(f['participant_id'])

            # creation of the path to the old data
            #------------------------------------------------------------------
            filepath = os.path.join(path_oldData, f['filepath'])

            # creation of the directory that will contain the data to be
            #  BIDSified if it does not already exist
            #------------------------------------------------------------------
            new_filepath = self.create_filepath(infoFile=f, path=path_newData)


            # creation of the file names of the BIDSified data
            #------------------------------------------------------------------
            new_filename = self.create_filename(infoFile=f)

            ###################################################################
            #  CREATION OF THE FILES
            ###################################################################
            arg = dict(filename=f['filename'], filepath=filepath,
                       new_filename=new_filename, new_filepath=new_filepath)

            # FILES *_eyetrack
            #------------------------------------------------------------------
            self.create_SettingsFile(settingsfilename=settingsfilename,
                                     infofilesname=infofilesname,
                                     list_settings=infos['file'], **arg)
            self.create_DataFile(**arg)

            # FILE *_events
            #------------------------------------------------------------------
            self.create_EventsFile(eventsfilename=f['eventsfilename'], **arg)

        # FILE *_participant.tsv
        #----------------------------------------------------------------------
        self.create_InfoParticipantsFile(infofilesname=infofilesname,
                                         list_settings=infos['participant'],
                                         path=path_newData)
        #######################################################################

    def create_filepath(self, infoFile, path):

        '''
        Creation of the directory that will contain the data to be BIDSified if
        it does not already exist

        Parameters
        ----------
        infoFile: dict
            Dictionary containing the information on the data to be BIDSified
        path: str
            Path of the new BIDS data directory

        Returns
        -------
        filepath: str
            Path of the file
        '''

        # Creation of file path
        filepath = os.path.join(path, 'sub-'+str(infoFile['participant_id']))
        if infoFile['ses']:
            filepath = os.path.join(filepath, 'ses-'+str(infoFile['ses']))
        filepath = os.path.join(filepath, 'eyetrack')

        # Creation of the directory if not exist
        if not os.path.isdir(filepath):
            os.makedirs(filepath)

        return filepath

    def create_filename(self, infoFile):

        '''
        Creation of the file names of the BIDSified data

        Parameters
        ----------
        infoFile: dict
            Dictionary containing the information on the data to be BIDSified

        Returns
        -------
        filename: str
            Name of the file
        '''

        # Creation of the file names
        filename  = 'sub-'+str(infoFile['participant_id'])
        filename += '_ses-'+str(infoFile['ses']) if infoFile['ses']  else ''
        filename += '_task-'+str(infoFile['task']) if infoFile['task'] else ''
        filename += '_acq-'+str(infoFile['acq']) if infoFile['acq']  else ''
        filename += '_run-'+str(infoFile['run']) if infoFile['run']  else ''

        return filename



    def create_SettingsFile(self, filename, filepath, new_filename,
                            new_filepath, settingsfilename, infofilesname,
                            list_settings):

        '''
        Creation of a settings file

        Parameters
        ----------
        filename: str
            Name of the data file to be BIDSified
        filepath: str
            Path of the data file to be BIDSified
        new_filename: str
            New name of the settings file to be BIDSified
        new_filepath: str
            New path of the settings file to be BIDSified
        settingsfile: str
            Name of the file containing the settings of the data to be
            BIDSified
        infofilesname: str
            Name of the file containing the information on the files to be
            BIDSified
        list_settings: list
            List of settings to be extracted
        '''

        settings = self.process.settings_init()

        # Extract settings in asc files
        if self.process_ET:
            settings = self.process_ET.Extract_settings_ascFile(filename,
                                                                filepath,
                                                                settings)

        # Extract settings in json files
        if settingsfilename:
            settings = self.process.Extract_settings_jsonFile(settingsfilename,
                                                              settings)

        # Extract settings in tsv files
        settings = self.process.Extract_settings_infoFiles(filename,
                                                           infofilesname,
                                                           list_settings,
                                                           settings)

        # Check that all the required settings are filled
        self.process.Check_required_settings(settings)

        self.settings = settings

        # save settings
        save_file(self.settings, new_filename+'_eyetrack.json', new_filepath)


    def create_DataFile(self, filename, filepath, new_filename, new_filepath):

        '''
        Creation of a data file

        Parameters
        ----------
        filename: str
            Name of the data file to be BIDSified
        filepath: str
            Path of the data file to be BIDSified
        new_filename: str
            New name of the data file to be BIDSified
        new_filepath: str
            New path of the data file to be BIDSified
        '''

        new_filename = new_filename+'_eyetrack'

        # save file .asc
        if self.eyetacktype=='Eyelink':
            import shutil
            shutil.copy2(os.path.join(filepath, filename),
                         os.path.join(new_filepath, new_filename+'.asc'))

        # Extract data in asc file pour convertir les données en tsv
        if self.process_ET:
            data = self.process_ET.Extract_data_ascFile(filename, filepath)
            # save data
            save_file(data, new_filename+'.tsv', new_filepath)


    def create_EventsFile(self, filename, eventsfilename, filepath,
                          new_filename, new_filepath):

        '''
        Creation of a events file

        Parameters
        ----------
        filename: str
            Name of the data file to be BIDSified
        eventsfilename: str
            Name of the events file to be BIDSified
        filepath: str
            Path of the data file to be BIDSified
        new_filename: str
            New name of the events file to be BIDSified
        new_filepath: str
            New path of the events file to be BIDSified
        '''

        events = self.process.events_init()

        # Extract Events in asc files
        if self.process_ET:
            events = self.process_ET.Extract_events_ascFile(filename, filepath,
                                                            self.saved_events,
                                                            self.settings,
                                                            events)
        # Extract Events in tsv files
        if eventsfilename:
            events = self.process.Extract_events_tsvFile(eventsfilename,
                                                         filepath, events)

        # save events
        save_file(events, new_filename+'_events.tsv', new_filepath)


    def create_InfoParticipantsFile(self, infofilesname, list_settings, path):

        '''
        Creation of an information file on participants

        Parameters
        ----------
        infofilesname: str
            Name of the file containing the information on the files to be
            BIDSified
        list_settings: list
            List of settings to be extracted
        path: str
            Path of the new BIDS dara directory
        '''

        # extract info participants in infoFiles
        participant = self.process.Extract_infoParticipants(infofilesname,
                                                            list_settings)

        # creation of file name
        if self.process.taskname:
            filename = 'task-'+self.process.taskname+'_participants.tsv'
        else:
            filename = 'participants.tsv'

        # save participant
        save_file(participant, filename, path)

