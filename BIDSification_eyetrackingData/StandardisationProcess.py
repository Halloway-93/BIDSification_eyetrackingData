#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from .File import open_file, save_file



class InfoFilesError(Exception):

    '''
    Returns an error if the infoFiles file is not good
    '''

    def __init__(self, error, infofilesname, list_dataFilenames):

        self.infofilesname = infofilesname
        self.list_dataFilenames = list_dataFilenames
        self.message = ''

        if error=='noInfoFiles':
            self.create_infoFiles()

        elif error=='missingFilenames':
            self.missing_Files()

        elif error[0]=='incompletedInfoFiles':
            self.completed_infoFiles(error[1])

    def __str__(self):

        return self.message

    def create_infoFiles(self):

        '''
        Error message if the infoFiles file does not exist
        '''

        self.message = "The file containing the data information "
        self.message += "does not exist \n"
        self.message += "or is not in the right format \n"
        self.message += "this file must be in tsv format and the data "
        self.message += "must be separated by spaces \n"
        self.message += "and must contain information on the following files: "
        self.message += "\n%s\n \n"%self.list_dataFilenames
        self.message += "the minimum columns required are: \n"
        self.message += "\t\t- 'filename' which lists the data files "
        self.message += "in the folder \n"
        self.message += "\t\t- 'participant_id' corresponding to "
        self.message += "the participants' identifiers\n \n"
        self.message += "Before continuing, you can create it "

        self.message += "or do it automatically with the function:\n \n"

        fct = StandardisationProcess('').create_infoFiles
        arg = fct.__code__.co_varnames[1:fct.__code__.co_argcount]

        name_fct = fct.__name__
        doc_fct = fct.__doc__
        arg_fct = str(tuple([x for x in arg]))

        self.message += name_fct
        self.message += arg_fct + "\n"
        self.message += doc_fct

    def missing_Files(self):

        '''
        Error message if the infoFiles file does not contain all data files
        '''

        self.message = "Your %s file containing "%self.infofilesname
        self.message += "data information is incomplete \n"
        self.message += "the %s files "%self.list_dataFilenames
        self.message += "are not filled in. \n"
        self.message += "Before continuing, please complete your file and "
        self.message += "check that it contains the correct information "

    def completed_infoFiles(self, columnerror):

        '''
        Error message if the infoFiles file is not complete
        '''

        self.message = "Your %s file containing "%self.infofilesname
        self.message += "data information is incomplete \n"
        self.message += "the column '%s' does not exist. \n"%columnerror
        self.message += "Before continuing, please complete your file and "
        self.message += "check that it contains the correct information \n"

        if columnerror=='participant_id':

            self.message += "or do it automatically with the function:\n \n"

            fct = StandardisationProcess('').completed_infoFiles_participant_id
            arg = fct.__code__.co_varnames[1:fct.__code__.co_argcount]

            name_fct = fct.__name__
            doc_fct = fct.__doc__
            arg_fct = str(tuple([x for x in arg]))

            self.message += name_fct
            self.message += arg_fct + "\n"
            self.message += doc_fct


class StandardisationProcess:

    '''
    Processes to standardise data

    Parameters
    ----------
    dirpath: str
        Path of the data directory to BIDSified
    '''

    def __init__(self, dirpath):

        # global variables
        self.dirpath = dirpath
        self.participant = None
        self.taskname = None
        self.infofilesname = None

        self.required_setting = ['TaskName',
                                 'SamplingFrequency',
                                 'SampleCoordinateUnit',
                                 'SampleCoordinateSystem',
                                 'EnvironmentCoordinates',
                                 'ScreenSize',
                                 'ScreenResolution',
                                 'ScreenDistance']


    #--------------------------------------------------------------------------
    # infoFiles
    #--------------------------------------------------------------------------
    def check_infoFiles(self, filename, dataformat):

        '''
        Check an information file on all the data files present in the
        directory

        Parameters
        ----------
        filename: str
            Name of the file containing the information on the files to be
            BIDSified
        dataformat: str
            Data format
        '''

        #----------------------------------------------------------------------
        # Retrieves the list of data files in the directory
        #----------------------------------------------------------------------
        datafiles = []
        for root, dirs, files in os.walk(self.dirpath):

            path = root.replace(self.dirpath, '')
            if path!='':
                path = path[1:]

            # add file paths if they are in the right format
            datafiles.extend([path+'/'+f for f in files
                              if f[-(len(dataformat)):]==dataformat])
        datafiles.sort()

        #----------------------------------------------------------------------
        # Creating a list of potential infoFiles
        #----------------------------------------------------------------------
        infoFilesPotential = []

        if filename:
            # check if filename is file
            path_file = os.path.join(self.dirpath, filename)
            filename_is_file = os.path.isfile(path_file)

            # add filename to the potential infoFiles
            if filename_is_file:
                infoFilesPotential = [filename]
        else:
            # add all .tsv files to the potential infoFiles
            list_files = os.listdir(self.dirpath)
            #  f.split('.')[-1] is the file format
            infoFilesPotential = [f for f in list_files
                                  if f.split('.')[-1]=='tsv']
        #----------------------------------------------------------------------

        infoFiles = None
        error = None

        if len(infoFilesPotential)!=0:

            for filename in infoFilesPotential:

                if not infoFiles:

                    # open infoFiles potential
                    infofiles_ = open_file(filename, self.dirpath)
                    columns = [i for i in infofiles_[0].keys()]

                    if 'filename' in columns:

                        # check 'filepath' and 'participant_id' columns
                        if 'filepath' not in columns:
                            error = ('incompletedInfoFiles', 'filepath')
                        elif 'participant_id' not in columns:
                            error = ('incompletedInfoFiles', 'participant_id')

                        # check 'filename'
                        else:
                            # retrieves all files in the infoFiles potential
                            filesname_ = [f['filepath']+'/'+f['filename'] for f
                                          in infofiles_]

                            # check if all datafiles are present in
                            #  infoFiles potential
                            datafiles_ = [f for f in datafiles if f not
                                          in filesname_]

                            if len(datafiles_)!=0:
                                error = 'missingFilenames'

                        infoFiles = '%s/%s'%(self.dirpath, filename)

        # check if infoFiles exist
        if not infoFiles:
            error = 'noInfoFiles'

        # returns an error if infoFiles is not good
        if error:
            raise InfoFilesError(error, infoFiles, datafiles)

        # change self.infofilesname if infoFiles is good
        else:
            self.infofilesname = infoFiles.split('/')[-1]

    def create_infoFiles(self, dataformat):

        '''
        Create an information file on all the data files present in the
        directory

        Parameters
        ----------
        dataformat: str
            Data format
        '''

        infoFiles = []

        #----------------------------------------------------------------------
        # Retrieves all data files in the directory
        #  and adds them to the infoFiles
        #----------------------------------------------------------------------
        i = 0
        for root, dirs, files in os.walk(self.dirpath):

            for f in files:

                # check if f is data file
                if f[-len(dataformat):]==dataformat:

                    #----------------------------------------------------------
                    # check if eventsfile exist
                    #----------------------------------------------------------
                    filename_ = f[:-len(dataformat)]
                    path_events = os.path.join(root, filename_+'.tsv')
                    events_is_file = os.path.isfile(path_events)

                    if events_is_file:
                        eventsfilename = filename_+'.tsv'
                    else:
                        eventsfilename = None
                    #----------------------------------------------------------

                    path = root.replace(self.dirpath, '')
                    if path!='':
                        path = path[1:]

                    # add data file in infoFiles
                    infoFiles.append(dict(filename=f,
                                          filepath=path,
                                          eventsfilename=eventsfilename,
                                          participant_id='%03d'%(i+1),
                                          ses=None,
                                          task=None,
                                          acq=None,
                                          run=None))
                    i += 1

        # save infoFiles
        save_file(infoFiles, 'infoFiles.tsv', self.dirpath)

        message = "The file %s/infoFiles.tsv "%self.dirpath
        message += "has just been created \n"
        message += "Before continuing, please check "
        message += "that it contains the correct information "

        print(message)

    def completed_infoFiles_participant_id(self, filename):

        '''
        Complete an information files with the participants' identifiers

        Parameters
        ----------
        filename: str
            Name of the file containing the information on the files to be
            BIDSified
        '''

        # open infoFiles
        f = open_file(filename, self.dirpath)

        # update infoFiles with the participant_id column
        file_update = [dict(l, **{'participant_id': '%03d'%(n+1)})
                       for n, l in enumerate(f)]

        # save new infoFiles
        save_file(file_update, filename, self.dirpath)

        message = "The column 'participant_id' has been added "
        message += "to the file %s/%s \n"%(self.dirpath, filename)
        message += "Before continuing, please check that it contains "
        message += "the correct information "

        print(message)

    def sort_infoFiles(self, filename):

        '''
        Sort infoFiles to give a dictionnary of list of settings per file and
        per participant

        Parameters
        ----------
        filename: str
            Name of the file containing the information on the files to be
            BIDSified

        Returns
        -------
        infos: dict
            A dictionnary of list of settings per file and per participant
        '''

        # open infoFiles
        infoFiles = open_file(filename, self.dirpath)

        #----------------------------------------------------------------------
        # task name
        #----------------------------------------------------------------------
        # check if the task is the same for all participants
        taskname = []
        for f in infoFiles:
            if 'task' in f.keys():
                taskname.append(f['task'])
        taskname = list(set(taskname))

        # change self.taskname if the task is the same for all participants
        if len(taskname)==1:
            self.taskname = taskname[0]

        #----------------------------------------------------------------------
        # dictionary of settings per participant
        #----------------------------------------------------------------------
        # list of settings that will not be kept for infos_participant
        does_not_keep = ['filename', 'filepath', 'eventsfilename',
                         'ses', 'task', 'acq', 'run']

        # list of settings that will be kept for infos_participant
        infos = [s for s in infoFiles[0].keys() if s not in does_not_keep]

        dict_participant = {f['participant_id']: {s:[] for s in infos}
                            for f in infoFiles}

        for f in infoFiles:
            for s in dict_participant[f['participant_id']].keys():
                dict_participant[f['participant_id']][s].append(f[s])

        #----------------------------------------------------------------------
        # check if there are settings on the files that are global to a
        #  participant
        #----------------------------------------------------------------------
        # list of settings per participant
        infos_participant = infos.copy()

        for p in dict_participant.keys():
            for s in dict_participant[p].keys():

                # list of data of settings
                list_s = list(set(dict_participant[p][s]))

                # if there is more than one setting data for the same
                #  participant, it is not global setting for the participant
                if len(list_s)!=1:
                    if s in infos_participant:
                        infos_participant.remove(s)

        # list of settings per file
        infos_file = [s for s in infos if s not in infos_participant]

        infos =  {'file': infos_file, 'participant': infos_participant}

        return infos


    #--------------------------------------------------------------------------
    # Settings
    #--------------------------------------------------------------------------
    def settings_init(self):

        '''
        Initialize the settings

        Returns
        -------
        settings: dict
            A dictionary containing the settings of the experiment
        '''

        settings = dict()

        #----------------------------------------------------------------------
        # REQUIRED
        #----------------------------------------------------------------------
        # Name of the task. No two tasks should have the same name. The task
        #  label included in the file name is derived from this TaskName field
        #  by removing all non-alphanumeric (`[a-zA-Z0-9]`) characters.
        #  For example `TaskName` `"faces n-back"` will correspond to task
        #  label `facesnback`. A RECOMMENDED convention is to name resting
        #  state task using labels beginning with `rest`
        settings['TaskName'] = None # string

        #----------------------------------------------------------------------
        # RECOMMENDED
        #----------------------------------------------------------------------
        # The name of the institution in charge of the equipment that produced
        #  the measurements
        settings['InstitutionName'] = None # string

        # The address of the institution in charge of the equipment that
        #  produced the measurements
        settings['InstitutionAddress']  = None # string

        # Manufacturer of the equipment that produced the measurements.
        #  Manufacturer of the eye-tracking system
        #  For example `"SR-Research"`, `"Tobii"`, `"SMI"`, `"Gazepoint"`,
        #  `"Pupil Labs"`, `"Custom built"`, ... , `"Other"`
        settings['Manufacturer'] = None # string

        # Manufacturer's model name of the equipment that produced the
        #  measurements. Manufacturer's designation of the eye-tracker model
        #  For example `"Eye-link 1000"`
        settings['ManufacturersModelName'] = None # string

        # Version of the software that was used to present the stimuli
        settings['SoftwareVersion'] = None # string

        # Longer description of the task.
        settings['TaskDescription'] = None # string

        # Text of the instructions given to participants before the recording.
        #  Text of the instructions given to participants before the experiment
        settings['Instructions'] = None # string

        # [URI](/02-common-principles.html#uniform-resource-indicator) of the
        #  corresponding [Cognitive Atlas](https://www.cognitiveatlas.org/)
        #  Task term.
        #  For example, [Resting State with eyes closed]
        #  (http://www.cognitiveatlas.org/task/id/trm_54e69c642d89b)
        settings['CogAtlasID'] = None # string

        # [URI](/02-common-principles.html#uniform-resource-indicator) of the
        #  corresponding [CogPO](http://www.cogpo.org/) term that describes the
        #  task
        #  For example, [Rest](http://wiki.cogpo.org/index.php?title=Rest)
        settings['CogPOID'] = None # string

        # The serial number of the equipment that produced the measurements.
        #  A pseudonym can also be used to prevent the equipment from being
        #  identifiable, so long as each pseudonym is unique within the dataset
        settings['DeviceSerialNumber'] = None # string

        #----------------------------------------------------------------------
        # REQUIRED
        #----------------------------------------------------------------------
        # Sampling frequency (in Hz) of the corresponding data in the recording
        #  (for example, `1000`). If the sampling frequency change across run,
        #  sidecar JSON document must be created specifying the run number
        settings['SamplingFrequency'] = None # number

        # Unit of individual samples (`"pixel"`, `"mm"` or `"cm"`)
        settings['SampleCoordinateUnit'] = None # string

        # Classical screen-based eye tracking data would be `"gaze-on-screen"`,
        #  but `"eye-in-head"` or `"gaze-in-world"` are also possible
        #  coordinate systems (for example for virtual reality)
        settings['SampleCoordinateSystem'] = None # string

        # Coordinates origin (or zero), for gaze-on-screen coordinates, this
        #  can be for example: `"top-left"` or `"center"`. For virtual reality
        #  this could be, amongst others, spherical coordinates
        settings['EnvironmentCoordinates'] = None # string

        # Screen size in cm (for example `[47.2, 29.5]` for a screen of
        #  47.2-length by 29.5-height cm), if no screen use `n/a`
        settings['ScreenSize'] = None # array of numbers or string "n/a"

        # Screen resolution in pixel (for example `[1920, 1200]` for a screen
        #  of 1920-length by 1080-height pixels), if no screen use `n/a`
        settings['ScreenResolution'] = None # array of numbers
                                                 #  or string "n/a"

        # Screen distance in cm (e.g `60` for a screen distance of 60 cm), if
        #  no screen use `"n/a"`. For MRI, it corresponds to the distance
        #  between the head-coil mirror to the projection screen for example
        settings['ScreenDistance'] = None # array of numbers
                                               #  or string "n/a"

        #----------------------------------------------------------------------
        # RECOMMENDED
        #----------------------------------------------------------------------
        # List of included events with message specifications.
        #  For example, if fixation markers from the EyeLink are included add:
        #  `[[Start of fixation: “SFIX”], [End of fixation: “EFIX”]]`.
        #  If no events are included write `None`
        settings['IncludedEyeMovementEvents'] = None # object of objects
                                                          #  or string "n/a"

        # Name the event detection algorithm. If a detection algorithm is used,
        #  settings SHOULD be present in `DetectionAlgorithmSettings`
        settings['DetectionAlgorithm'] = None # string

        # List of parameter settings used in the `DetectionAlgorithm` for eye
        #  movement events
        settings['DetectionAlgorithmSettings'] = None # object of objects
                                                           #  or string "n/a"

        # The message sent to the eye tracker to indicate the start of each
        #  trial. Could be the start of the presentation of an image, word,
        #  video, and so on
        settings['StartMessage'] = None # string

        # The message sent to the eye tracker to indicate the end of each trial
        #  presentation. Could be the end of the presentation of an image,
        #  word, video, and so on
        settings['EndMessage']  = None # string

        # When the paradigm includes pressing a key, message identifying this
        #  should be included to the sidecar JSON file
        settings['KeyPressMessage'] = None # string

        # Description of the calibration procedure. For example the `"H3"` for
        #  horizontal calibration with 3 positions or `"HV9"` for horizontal
        #  and vertical calibration with 9 positions, or one point calibration
        settings['CalibrationType'] = None # string

        # Unit of `CalibrationPosition`: `"pixel"`, `"mm"` or `"cm"`
        settings['CalibrationUnit'] = None # string

        # Provide a list of X/Y coordinates in the `CalibrationUnit`.
        #  For example, using 5 positions calibration presented on an HD
        #  screen, it could be
        #  `[[960,50],[960,540],[960,1030],[50,540],[1870,540]]`
        settings['CalibrationPosition'] = None # array of number

        # Maximal calibration error in visual degree
        settings['MaximalCalibrationError'] = None # number

        # Average calibration error in visual degree
        settings['AverageCalibrationError'] = None # number

        # List of lists including information for each calibration. This list
        #  includes the calibration type, recorded eye, maximal calibration
        #  error, average calibration error, and time relative to the first
        #  event of the event file
        settings['CalibrationList'] = None # object of object

        # Specification for which eye was tracked
        #  (`"Left"`, `"Right"`, `"Both"`)
        settings['RecordedEye'] = None # string

        # A field to store any settings that influence the resolution and
        #  quality of the eye imagery. Autowhitebalance? Changes in sharpness?
        settings['EyeCameraSettings'] = None # object of object

        # A place to store arbitrary information related to feature detection.
        #  For example Minimum/maximum pupil size.
        settings['FeatureDetectionSettings'] = None # object of object

        # A place to store arbitrary information related to gaze mapping.
        #  For example, if there was a threshold on pupil confidence required
        #  for gaze mapping, one could store that information here
        settings['GazeMappingSettings'] = None # object of object

        # Filter settings applied to eye-movement raw data.
        #  For example Eyelink trackers typically automatically filter the raw
        #  data.
        settings['RawDataFilters'] = None # string

        # Refresh rate of the screen (when used), in Hertz
        #  For example, `60` for 60 Hz.
        settings['ScreenRefreshRate'] = None # number

        # Define, what shape are the AOIs and what coordinates are used.
        #  `[“square”,[“x_start”, “x_stop”, “y_start”, “y_stop”]]`
        #  Other options: `“custom”/”circle”/”triangle”,
        #  [[“x”,”y”],[“x”,”y”],[“x”,”y”],and so on.]`
        settings['AOIDefinition'] = None # object of object

        # The method employed for fitting the pupil:
        #  `"centre-of-mass"` or `"ellipse"`.
        settings['PupilFitMethod'] = None # string

        return settings

    def create_settingsFile(self):

        '''
        Create an setting file in the directory
        '''

        # Initialize the settings
        settings = self.settings_init()

        # save the settings
        save_file(settings, 'settings.json', self.dirpath)

        message = "The file %s/settings.json "%self.dirpath
        message += "has just been created \n"
        message += "Before continuing, please complete it with "
        message += "the correct information "

        print(message)

    def Extract_settings_jsonFile(self, filename, old_settings=None):

        '''
        Process a given json file to extract the settings
        and fill-in the corresponding settings field

        Parameters
        ----------
        filename: str
            Name of the file containing the settings of the data to be
            BIDSified
        old_settings: dict or None (default None)
            A dictionary containing the settings of the experiment

        Returns
        -------
        settings: dict
            A dictionary containing the settings of the experiment
        '''

        if old_settings:
            settings = old_settings
        else:
            settings = self.settings_init()

        # open new settings
        new_settings = open_file(filename, self.dirpath)

        # completes the settings with the new settings
        for s in new_settings.keys():
            if new_settings[s]:
                settings[s] = new_settings[s]

        return settings

    def Extract_settings_infoFiles(self, filename, infofilesname,
                                   list_settings, old_settings=None):

        '''
        Process a given tsv file to extract the settings
        and fill-in the corresponding settings field

        Parameters
        ----------
        filename: str
            Name of the data file to be BIDSified
        infofilesname: str
            Name of the file containing the information on the files to be
            BIDSified
        list_settings: list
            List of settings to be extracted
        old_settings: dict or None (default None)
            A dictionary containing the settings of the experiment

        Returns
        -------
        settings: dict
            A dictionary containing the settings of the experiment
        '''

        if old_settings:
            settings = old_settings
        else:
            settings = self.settings_init()

        # open infoFiles
        infoFiles = open_file(infofilesname, self.dirpath)

        # retrieves the information about the file in infoFiles
        info_file = None
        for f in infoFiles:
            if f['filename']==filename:
                info_file = f

        # check if this information exist
        if not info_file:
            message = "The info file %s/%s "%(self.dirpath, infofilesname)
            message += "does not contain information on %s"%(filename)
            raise ValueError(message)

        # add of this information in settings
        for i in list_settings:
            if i in info_file.keys():
                settings = dict(settings, **{i:info_file[i]})

        return settings

    def Check_required_settings(self, settings):

        '''
        Check that all the required settings are filled.

        Parameters
        ----------
        settings: dict
            A dictionary containing the settings of the experiment
        '''

        # creation of a list of settings required but not filled in
        missing = []
        for s in self.required_setting:
            if not settings[s]:
                missing += [s]

        # print a message if this list is not empty
        if missing:
            print('Missing setting:', missing)


    #--------------------------------------------------------------------------
    # Events
    #--------------------------------------------------------------------------
    def events_init(self):

        '''
        Initialize the events

        Returns
        -------
        events: list
            A dictionary list for each trial containing the events of
            those trials
        '''

        return []

    def Extract_events_tsvFile(self, filename, filepath, old_events=None):

        '''
        Extract the trial events from the tsv file

        Parameters
        ----------
        filename: str
            Name of the events file
        filepath: str
            Path of the events file
        old_events: list or None (default None)
            A dictionary list for each trial containing the events of
            those trials

        Returns
        -------
        events: list
            A dictionary list for each trial containing the events of
            those trials
        '''

        if old_events:
            events = old_events
        else:
            events = self.events_init()


        # open events file
        eventsfile = open_file(filename, filepath)
        if not events:
            events = eventsfile

        else:

            # add trial in events file if not exist
            for t in range(len(eventsfile)):
                if not 'trial' in eventsfile[t].keys():
                    eventsfile[t]['trial'] = t+1

            # add event of eventsfile in events
            for e in eventsfile:
                add_event = False
                for i in range(len(events)):
                    if 'trial' in events[i].keys():
                        if float(events[i]['trial'])==float(e['trial']):
                            events[i] = dict(events[i], **e)
                            add_event = True
                if not add_event:
                    events.append(e)

        return events


    #--------------------------------------------------------------------------
    # infoParticipants
    #--------------------------------------------------------------------------
    def Extract_infoParticipants(self, filename, list_infoparticipants):

        '''
        Extract the participant informations from the tsv file

        Parameters
        ----------
        filename: str
            Name of the information file
        list_infoparticipant: list
            List of participant information to be extracted

        Returns
        -------
        info_participants: list
            A dictionary list for each participant containing the informations
            of those participants
        '''

        # open infoFiles
        infoFiles = open_file(filename, self.dirpath)

        # extract the participant informations from the file
        info_participants = []
        for f in infoFiles:
            i = {k:f[k] for k in list_infoparticipants}
            if i not in info_participants:
                info_participants.append(i)

        return info_participants

