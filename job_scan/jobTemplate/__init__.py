"""
run template of each job type
"""
import os
from datetime import datetime
import glob

_formatTime = "%Y%m%d%H%M%S"
appConf = {}

def prepare(tconf):
    appConf.update(tconf)
    appConf['job2script'] = {
        'anno_pipeline': args_anno_pipeline,
        'annotation_ion': args_annotation_ion,
    }
    appConf['job2ck'] = {
        'annotation_ion': ck_annotation_ion,
    }

def job2cmd(infoJob):
    "based job info to get script"
    typeJob = infoJob.get('target')
    pathScript = appConf['tools']['conf_tools'].conf_path(typeJob,appConf['confScript']['path'])
    if not os.path.exists(pathScript):
        return False
    if typeJob in appConf['job2script']:
        return appConf['job2script'][typeJob](infoJob, pathScript)

def args_anno_pipeline(infoJob, pathScript):
    pathLog = os.path.join(infoJob['args']['output'], 'annotation.log')
    targs = {
        'input': ' '.join(infoJob['args']['input']),
        'threads': str(infoJob['args']['threads']),
        'panel': infoJob['args']['panel'],
        'output': infoJob['args']['output'],
    }
    if not os.path.exists(infoJob['args']['output']):
        os.makedirs(infoJob['args']['output'])
    return '{} {} 2> {}'.format(pathScript, ' '.join(['--{} {}'.format(x, y) for x, y in targs.items()]), pathLog)


def args_annotation_ion(infoJob, pathScript):
    dirLog = os.path.join(infoJob['args']['output'], 'log_files')
    if not os.path.exists(dirLog):
        os.makedirs(dirLog)
    strTime = datetime.now().strftime(_formatTime)
    pathLog = os.path.join(dirLog, '{}_{}.log'.format(infoJob['args'].get('log_name',''),strTime))
    targs = {
        'threads': str(infoJob['args']['threads']),
        'panel': infoJob['args']['panel'],
        'caller': infoJob['args']['caller'],
    }
    if os.path.exists(infoJob['args']['input']):
        targs.update({'vcf': infoJob['args']['input']})
    else:
        targs.update({'run_barcode': infoJob['args']['input']})
    if infoJob['args'].get('output'):
        targs.update({'output': infoJob['args']['output']})
    return '{} {} 2> {}'.format(pathScript, ' '.join(['--{} {}'.format(x, y) for x, y in targs.items()]), pathLog)


def ck_annotation_ion(infoJob):
    if not infoJob['args'].get('output'):
        return True
    
    pathXlsx = os.path.join(infoJob['args']['output'], 'annotation_result_v*','*.xlsx')
    if glob.glob(pathXlsx):
        return True
    
    return False
