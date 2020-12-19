"""
job operation
"""
###
### YuBin 2020.04.13 create
###
import os
import sys
import json
import re
import uuid
import glob
from datetime import datetime
import socket

scriptDir = os.path.split(os.path.realpath(__file__))[0]
sys.path.append(os.path.join(scriptDir,'..'))
import exec_tools

appConf = {
    'statusJob':['wait','proceed','complete','fail'],
}
_formatTime = "%Y%m%d%H%M%S"

def prepare(dirJobs,id='NA'):
    "setup job dirs if not exists"
    if not os.path.exists(dirJobs):
        raise NameError('Please check [dirJob] {} exists!'.format(dirJobs))
    
    ck_dirJobs(dirJobs)
    appConf.update({'dirJobs': dirJobs})
    appConf['rid'] = '{}_{}'.format(socket.gethostname(), id)

def log_ck():
    "search log and return True/False"
    pathUp,pathDown = [os.path.join(appConf['dirJobs'],'log','{}_{}.log'.format(appConf['rid'],x)) for x in ['up','down']]
    if appConf.get('fileLog'):
        return appConf['fileLog']
    if os.path.exists(pathUp):
        return False
    if os.path.exists(pathDown):
        os.rename(pathDown, pathUp)
    appConf['fileLog'] = open(pathUp, 'a')
    return appConf['fileLog']


def log_write(tMsg):
    if appConf.get('fileLog'):
        exec_tools.log_time(tMsg, None, appConf['fileLog'])
        appConf['fileLog'].flush()


def log_down():
    if appConf.get('fileLog'):
        appConf['fileLog'].close()
        pathDown = os.path.join(appConf['dirJobs'],'log','{}_down.log'.format(appConf['rid']))
        os.rename(appConf['fileLog'].name, pathDown)
    else:
        sys.stderr.write('[WARN] No log file\n')

def ck_dirJobs(dirJobs):
    for nameDir in appConf['statusJob'] + ['log']:
        tDir = os.path.join(dirJobs, nameDir)
        if os.path.exists(tDir):
            continue
        
        os.mkdir(tDir)
        os.chmod(tDir, int('777', 8))


def tagTime(tObj,tType='add'):
    tObj['{}Time'.format(tType)] = datetime.now().strftime(_formatTime)
    return tObj

def createJob(nameTarget, args):
    "return json obj by target and args"
    tObj = {
        'from': appConf['rid'],
        'target': nameTarget,
        'args':args,
    }

    return tagTime(tObj)


def moveJob(objJob, statusJob):
    if statusJob not in appConf['statusJob']:
        sys.stderr.write('[WARN] No status "{}" exists\n'.format(statusJob))
        return False
    ## save json
    path_src = objJob.get('path','')
    tmpName = nameJob(objJob) if not path_src else os.path.basename(path_src)
    pathJob = os.path.join(appConf['dirJobs'], statusJob, tmpName)
    ## exit if already in
    if os.path.exists(pathJob):
        sys.stderr.write('[WARN] Job path "{}" exists\n'.format(pathJob))
        return False
    if statusJob == 'complete':
        tagTime(objJob, 'complete')
    json.dump(objJob, open(pathJob,'w'))
    ## remove src path
    if path_src:
        os.unlink(path_src)
    ## record new path
    objJob['path'] = pathJob
    ## log
    log_write('move job:"{}" to "{}"'.format(tmpName, statusJob))
    return objJob


def nameJob(objJob,fmt='{addTime}_{target}_{idJob}'):
    "format file name"
    idJob = objJob.get('id') or uuid.uuid1()
    tinfo = {'addTime': objJob['addTime'], 'target': objJob['target'], 'idJob':idJob}
    return fmt.format(**tinfo) + '.json'

def loadJob(pathJob):
    objJob = json.load(open(pathJob))
    objJob.update({'path': pathJob})
    
    return objJob


def removeJob(objJob):
    pathJob = objJob.get('path', '')
    if os.path.exists(pathJob):
        os.unlink(pathJob)
        log_write('remove job:"{}"'.format(os.path.basename(pathJob)))
    elif pathJob:
        sys.stderr.write('[WARN] no job in {}\n'.format(pathJob))

def loadJobs(nameTargets, statusJob=[]):
    jobs = []
    for tStatus in statusJob or appConf['statusJob']:
        dirstatus = os.path.join(appConf['dirJobs'], tStatus)
        for listPath in glob.glob(os.path.join(dirstatus,'*.json')):
            tObj = loadJob(listPath)
            if tObj.get('target') not in nameTargets:
                continue
            jobs.append(tObj)
    ## sorting by addTime
    jobs.sort(key=lambda x: datetime.strptime(x['addTime'], _formatTime))
    
    return jobs
