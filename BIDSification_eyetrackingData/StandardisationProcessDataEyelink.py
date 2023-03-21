#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .File import open_file
from .StandardisationProcess import *


class StandardisationProcessDataEyelink:

    '''
    Processes to standardise data eyelink

    Parameters
    ----------
    dirpath: str
        Path of the data directory to BIDSified
    StartMessage: str
        Message marking the start of the trial
    EndMessage: str
        Message marking the end of the trial
    '''

    def __init__(self, dirpath, StartMessage, EndMessage,):

        self.process = StandardisationProcess(dirpath)

        # global variables
        self.StartMessage = StartMessage
        self.EndMessage = EndMessage


    #--------------------------------------------------------------------------
    # Settings
    #--------------------------------------------------------------------------
    def Extract_settings_ascFile(self, filename, filepath, old_settings=None):

        '''
        Process a given run file (in .asc format) to extract the settings
        and fill-in the corresponding settings field.

        Parameters
        ----------
        filename: str
            Name of the data file to be BIDSified
        filepath: str
            Path of the data file to be BIDSified
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
            settings = self.process.settings_init()

        settings['Manufacturer'] = "SR-Research"
        settings['DetectionAlgorithm'] = "SR-Research"

        # open file asc
        file_asc = open_file(filename, filepath)

        # extract settings in the file asc
        for line in file_asc:

            l = line[:-1]

            if '** EYELINK' in l:
                k = 'ManufacturersModelName'
                v = l[3:]
                settings[k] = v

            if 'VERSION:' in l:
                k = 'SoftwareVersion'
                v = l.split('VERSION: ')[1]
                settings[k] = v

            if 'SERIAL NUMBER:' in l:
                k = 'DeviceSerialNumber'
                v = l.split('SERIAL NUMBER: ')[1]
                settings[k] = v

            if 'CAMERA:' in l:
                k = 'EyeCameraSettings'
                v = l.split('CAMERA: ')[1]
                settings[k] = v

            if 'DISPLAY_COORDS' in l:
                k = 'ScreenResolution'
                v = [float(l.split(' ')[-2]) +1, float(l.split(' ')[-1]) +1]
                settings[k] = v

            if 'ELCL_PROC' in l:
                k = 'PupilFitMethod'
                v = l.split('ELCL_PROC ')[-1]
                settings[k] = v

            if 'CALIBRATION' in l:
                k = 'CalibrationType'
                v = l.split('CALIBRATION ')[1].split(' ')[0]
                settings[k] = v

            if 'RATE' in l:
                k = 'SamplingFrequency'
                v = float(l.split('RATE')[1].split('\t')[1])
                settings[k] = v

            if 'FILTER' in l:
                k = 'RawDataFilters'
                num_filter = int(l.split('FILTER')[1].split('\t')[1])
                if num_filter==0: v = 'off'
                elif num_filter==1: v = 'standard'
                elif num_filter==2: v = 'extra'
                settings[k] = v

            if 'SAMPLES'==l.split('\t')[0]:

                k = ['SampleCoordinateSystem', 'SampleCoordinateUnit']
                if 'GAZE' in l: v = ['gaze-on-screen', 'pixels']
                elif 'HREF' in l: v = ['eye-in-head', 'degree']
                elif 'PUPIL' in l: v = ['eye-in-camera', 'data raw']
                for k_, v_ in zip(k, v): settings[k_] = v_

                k = 'RecordedEye'
                if 'LEFT' in l and 'RIGHT' in l: v = 'Both'
                elif 'LEFT' in l: v = 'Left'
                elif 'RIGHT' in l: v = 'Right'
                settings[k] = v

            if '!CAL VALIDATION' in l and 'GOOD' in l:
                k = 'CalibrationList'
                v = l
                if not settings[k]: settings[k] = [v]
                else: settings[k].append(v)

            #------------------------------------------------------------------
            # Eye Movement Events
            #------------------------------------------------------------------
            eye_events = ['SFIX', 'EFIX', 'SSACC', 'ESACC', 'SBLINK', 'EBLINK']
            if l.split(' ')[0] in eye_events:
                k = 'IncludedEyeMovementEvents'
                if not settings[k]: settings[k] = []

                event = l.split(' ')[0]
                if event not in [e[1] for e in settings[k]]:
                    if event=='SFIX': v = ["Start of fixation", "SFIX"]
                    elif event=='EFIX': v = ["End of fixation", "EFIX"]
                    elif event=='SSACC': v = ["Start of saccade", "SSACC"]
                    elif event=='ESACC': v = ["End of saccade", "ESACC"]
                    elif event=='SBLINK': v = ["Start of blink", "SBLINK"]
                    elif event=='EBLINK': v = ["End of blink", "EBLINK"]
                    settings[k].append(v)

            #------------------------------------------------------------------
            # StartMessage
            #------------------------------------------------------------------
            if self.StartMessage in l:
                k = 'StartMessage'
                v = self.StartMessage + l.split(self.StartMessage)[1]
                if not settings[k]:
                    settings[k] = [v]
                    t_0 = int(l.split('\t')[1].split(' ')[0])
                else:
                    if not v in settings[k]:
                        settings[k].append(v)

            #------------------------------------------------------------------
            # EndMessage
            #------------------------------------------------------------------
            if self.EndMessage:
                if self.EndMessage in l:
                    k = 'EndMessage'
                    v = self.EndMessage + l.split(self.EndMessage)[1]
                    if not settings[k]:
                        settings[k] = [v]
                    else:
                        if not v in settings[k]:
                            settings[k].append(v)
            #------------------------------------------------------------------

        del file_asc

        if not settings['StartMessage']:
            raise ValueError('The StartMessage variable given is not correct!')

        #----------------------------------------------------------------------
        # CalibrationList
        #----------------------------------------------------------------------
        if settings['CalibrationList']:
            k = 'CalibrationList'
            for n, l in enumerate(settings[k]):
                # calibration type
                cali = l.split('VALIDATION ')[1].split(' ')[0]
                # recorded eye
                eye = l.split(' GOOD')[0].split(' ')[-1]
                # maximal calibration error
                max_ = float(l.split(' max')[0].split(' ')[-1])
                # average_calibration_error
                avg_ = float(l.split(' avg.')[0].split(' ')[-1])
                # time relative to the first events of the event file
                time = int(l.split('\t')[1].split(' ')[0]) - t_0
                time /= settings['SamplingFrequency']

                settings[k][n] = [cali, eye, max_, avg_, time]
        #----------------------------------------------------------------------

        return settings


    #--------------------------------------------------------------------------
    # data
    #--------------------------------------------------------------------------
    def Extract_data_ascFile(self, filename, filepath):

        '''
        Process a given run file (in .asc format) to extract the data
        and fill-in the corresponding data field.

        Parameters
        ----------
        filename: str
            Name of the data file to be BIDSified
        filepath: str
            Path of the data file to be BIDSified

        Returns
        -------
        data: list
            A dictionary list for each trial containing the data of
            those trials
        '''

        # open file asc
        file_asc = open_file(filename, filepath)


        # Reminder for eyelink recordings
        '''
        |---------------------------------------------------------------------|
        | Notation          | Description                                     |
        |-------------------|-----------------------------------------------  |
        | "time"            | timestamp in milliseconds                       |
        |                   |                                                 |
        | "xpl", "ypl"      | left eye X and Y position data                  |
        | "xpr", "ypr"      | right eye X and Y position data                 |
        |                   |                                                 |
        | "psl"             | left pupil size (area or diameter)              |
        | "psr"             | right pupil size (area or diameter)             |
        |                   |                                                 |
        | "xvl", "yvl"      | left eye instantaneous velocity (degrees/sec)   |
        | "xvr", "yvr"      | right eye instantaneous velocity (degrees/sec)  |
        |                   |                                                 |
        | "xr", "yr"        | X and Y resolution (position units/degree)      |
        |---------------------------------------------------------------------|

        |---------------------------------------------------------------------|
        | Recordings                      | sample_line_formats               |
        |---------------------------------|-----------------------------------|
        | Monocular right eye             | ["time",                          |
        |                                 |  "xpr", "ypr", "psr"]             |
        |                                 |                                   |
        | Monocular right eye,            | ["time",                          |
        |    with velocity                |  "xpr", "ypr", "psr",             |
        |                                 |  "xvr", "yvr"]                    |
        |                                 |                                   |
        | Monocular right eye,            | ["time",                          |
        |    with resolution              |   "xpr", "ypr", "psr",            |
        |                                 |   "xr", "yr"]                     |
        |                                 |                                   |
        | Monocular right eye,            | ["time",                          |
        |    with velocity and resolution |  "xpr", "ypr", "psr",             |
        |                                 |  "xvr", "yvr",                    |
        |                                 |  "xr", "yr"]                      |
        |                                 |                                   |
        |---------------------------------|-----------------------------------|
        | Monocular left eye              | ["time",                          |
        |                                 |  "xpl", "ypl", "psl"]             |
        |                                 |                                   |
        | Monocular left eye,             | ["time",                          |
        |    with velocity                |  "xpl", "ypl", "psl",             |
        |                                 |  "xvl", "yvl"]                    |
        |                                 |                                   |
        | Monocular left eye,             | ["time",                          |
        |    with resolution              |   "xpl", "ypl", "psl",            |
        |                                 |   "xr", "yr"]                     |
        |                                 |                                   |
        | Monocular left eye,             | ["time",                          |
        |    with velocity and resolution |  "xpl", "ypl", "psl",             |
        |                                 |  "xvl", "yvl",                    |
        |                                 |  "xr", "yr"]                      |
        |                                 |                                   |
        |---------------------------------|-----------------------------------|
        | Binocular                       | ["time",                          |
        |                                 |  "xpl", "ypl", "psl",             |
        |                                 |  "xpr", "ypr", "psr"]             |
        |                                 |                                   |
        | Binocular,                      | ["time",                          |
        |    with velocity                |  "xpl", "ypl", "psl",             |
        |                                 |  "xpr", "ypr", "psr",             |
        |                                 |  "xvl", "yvl",                    |
        |                                 |  "xvr", "yvr"]                    |
        |                                 |                                   |
        | Binocular,                      | ["time",                          |
        |    with and resolution          |  "xpl", "ypl", "psl",             |
        |                                 |  "xpr", "ypr", "psr",             |
        |                                 |  "xr", "yr"]                      |
        |                                 |                                   |
        | Binocular,                      | ["time",                          |
        |    with velocity and resolution |  "xpl", "ypl", "psl",             |
        |                                 |  "xpr", "ypr", "psr",             |
        |                                 |  "xvl", "yvl",                    |
        |                                 |  "xvr", "yvr",                    |
        |                                 |  "xr", "yr"]                      |
        |---------------------------------------------------------------------|
        '''

        # extract data in the file asc
        data = []
        line_formats = None

        for line in file_asc:

            l = line[:-1].split('\t')

            # Search for line formats
            if not line_formats:

                if l[0]=='SAMPLES':

                    line_formats = ["time"]

                    # position data and pupil size
                    if 'LEFT' in l:
                        line_formats.extend(["xpl", "ypl", "psl"])
                    if 'RIGHT' in l:
                        line_formats.extend(["xpr", "ypr", "psr"])

                    # velocity data
                    if 'VEL' in l:
                        if 'LEFT' in l:
                            line_formats.extend(["xvl", "yvl"])
                        if 'RIGHT' in l:
                            line_formats.extend(["xvr", "yvr"])

                    # resolution data
                    if 'RES' in l:
                        line_formats.extend(["xr", "yr"])

            try:
                # add line in data
                if int(l[0]):
                    line = {}
                    for n, d in enumerate(line_formats):
                        try: line[d] = float(l[n])
                        except: line[d] = None
                    data.append(line)
            except:
                pass

        return data


    #--------------------------------------------------------------------------
    # Events
    #--------------------------------------------------------------------------
    def Extract_events_ascFile(self, filename, filepath, saved_events,
                               settings=None, old_events=None):

        '''
        Extract the trial events from the asc file

        Parameters
        ----------
        filename: str
            Name of the data file to be BIDSified
        filepath: str
            Path of the data file to be BIDSified
        saved_events: list
            List of events to be extracted from the trials
        settings: dict or None (default None)
            A dictionary containing the settings of the experiment
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
            events = self.process.events_init()

        # open file asc
        file_asc = open_file(filename, filepath)

        #----------------------------------------------------------------------
        # add event names at saved_events
        #----------------------------------------------------------------------
        for n, e in enumerate(["onset", "duration", "sample", "trial",
                               "eventIdentifier"]):
            if e not in saved_events:
                saved_events.insert(n, e)

        # add Eye Movement Events
        if settings:
            if settings["IncludedEyeMovementEvents"]:
                for x in settings["IncludedEyeMovementEvents"]:
                    if x[1] not in saved_events:
                        saved_events.append(x[1])
        #----------------------------------------------------------------------


        # function initializing events_trial
        def start_events(l, saved_events):

            events_trial = {}
            for e in saved_events:
                events_trial[e] = None

            t_start = int(l.split('\t', 1)[1].split(' ')[0])
            events_trial["sample"] = t_start

            event_ID = l.split('\t', 1)[1].split(' ', 1)[1]
            events_trial["eventIdentifier"] = event_ID

            return events_trial, t_start


        # extract events in the file asc
        started = False
        trialend = False

        t_0 = None
        trial = 1
        for line in file_asc:

            l = line[:-1]

            if not started:

                #--------------------------------------------------------------
                # Check if the trial has started
                #--------------------------------------------------------------
                if self.StartMessage in line:
                    # initialise events_trial
                    events_trial, t_start = start_events(l, saved_events)
                    if not t_0: t_0 = t_start
                    started = True
                #--------------------------------------------------------------

            else:

                #--------------------------------------------------------------
                # Check if the trial has finished
                #--------------------------------------------------------------
                if self.EndMessage != None:
                    if self.EndMessage in line:
                        started = False
                        trialend = True
                else:
                    if (self.StartMessage in line) or (line==file_asc[-1]):
                        started = True
                        trialend = True
                #--------------------------------------------------------------

                if trialend:

                    t_end = int(l.split('\t', 1)[1].split(' ')[0])
                    events_trial["onset"] = (t_start-t_0)/1000
                    events_trial["duration"] = (t_end-t_start)/1000
                    events_trial["trial"] = trial

                    for e in events_trial.keys():
                        if type(events_trial[e])==list:
                            if len(events_trial[e])==1:
                                events_trial[e] = events_trial[e][0]

                    #----------------------------------------------------------
                    # add event of events_trial in events
                    #----------------------------------------------------------
                    add_event = False
                    for i in range(len(events)):
                        if 'trial' in events[i].keys():
                            if float(events[i]['trial'])==float(trial):
                                events[i] = dict(events[i], **events_trial)
                                add_event = True
                    if not add_event:
                        events.append(events_trial)

                    #----------------------------------------------------------
                    # Check if the trial has started
                    #----------------------------------------------------------
                    if started:
                        # initialise events_trial
                        events_trial, t_start = start_events(l, saved_events)
                    #----------------------------------------------------------

                    trial += 1
                    trialend = False

            if started:

                for event in saved_events:
                    if event in line:
                        if not events_trial[event]:
                            events_trial[event] = []

                        #------------------------------------------------------
                        # EyeMovementEvents
                        #------------------------------------------------------
                        if l.split(' ')[0]==event:
                            l = l.split(' ')

                            # Start
                            if l[0][0]=='S':
                                e = int(l[-1])
                                events_trial[event].append(e)

                            # End
                            elif l[0][0]=='E':
                                for x in l:
                                    if len(x.split('\t'))>1:
                                        if x.split('\t')[1]!='':
                                            e = float(x.split('\t')[1])
                                            events_trial[event].append(e)

                        #------------------------------------------------------
                        # OtherEvents
                        #------------------------------------------------------
                        elif l.split('\t')[0]=="MSG":
                            l = l.split('\t', 1)[1].split(' ')
                            e = int(l[0])
                            events_trial[event].append(e)

        return events

