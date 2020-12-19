#!/usr/bin/env python
###
### YuBin 2020.04.20 create
###       2020.06.11 check -r in typesJob and add check job fail or not
###
import os,sys,json
scriptDir = os.path.split(os.path.realpath(__file__))[0]

sys.path.append(scriptDir)
import jobTemplate

sys.path.append(os.path.join(scriptDir, '../../python_modules/'))
import exec_tools,conf_tools,job_control

class pkg():
    """job_scan.v0.1.py: 
    scan jobs from job control
    """
    def __init__(self, args={}):
        "add all options var into self"
        self.args = {}
        self.args.update(args)
        self.vars = {
            'idScript': 'annotation_scan',
            'typesJob': set(['anno_pipeline', 'annotation_ion']),
        }
        self.prepare()
    
    def prepare(self):
        "prepare"
        file_conf = self.args['conf'] or open(os.path.join(scriptDir,'../','config.json'))
        self.sample_conf = json.load(file_conf)
        self.sample_conf['scriptDir'] = scriptDir
        conf_tools.prepare(self.sample_conf)
        job_dir = self.args.get('job_dir') or conf_tools.conf_path('confSystem:job_dir')
        job_control.prepare(job_dir, self.vars['idScript'])
        self.vars['confScript'] = json.load(open(os.path.join(scriptDir, '../../settings/annotation_pipeline/job_scan/conf.json')))
        jobTemplate.prepare({'tools': {'conf_tools':conf_tools}, 'confScript':self.vars['confScript']})

    def jobCollect(self):
        jobsRes = []
        typeScan = set()
        if self.args.get('run'):
            typeScan = self.vars['typesJob'].intersection(self.args.get('run'))
        else:
            typeScan = self.vars['typesJob']
        self.vars['typeScan'] = typeScan
        jobsTmp = job_control.loadJobs(typeScan, ['wait'])
        if len(jobsTmp) == 0:
            return jobsRes
        ## filter by threads
        threads = []
        threadMax = self.args['threads']
        threadNeed = 0
        confMincpu = self.vars['confScript']['mincpu']
        for tjob in jobsTmp:
            if threadNeed >= threadMax:
                break
            tTarget = tjob['target']
            num_input = len(tjob['args']['input']) if type(tjob['args']['input']) == list else 1
            threadnum = num_input * confMincpu.get(tTarget, confMincpu['default'])
            jobsRes.append(tjob)
            threads.append(threadnum)
            threadNeed += threadnum
        
        ## appned thread to jobs
        threadNum = sum(threads)
        for indT, threadT in enumerate(threads):
            jobsRes[indT]['args'].update({'threads': int(threadMax*threadT/threadNum)})
        
        return jobsRes

    def main(self):
        job2ck = jobTemplate.appConf.get('job2ck',[])
        ## check log
        if not job_control.log_ck():
            exec_tools.log_time('[WARN] "{}" already running!'.format(self.vars['idScript']))
            return False
        while 1:
            jobs = self.jobCollect()
            if not jobs:
                exec_tools.log_time('[INFO] No more job associated "{}"'.format(','.join(self.vars['typeScan'])))
                job_control.log_down()
                return True
            ## run jobs
            cmds,jobsExec = [],[]
            for tJob in jobs:
                tCmd = jobTemplate.job2cmd(tJob)
                job_control.moveJob(tJob, 'proceed')
                if tCmd:
                    cmds.append(tCmd)
                    jobsExec.append(tJob)

            exec_tools.log_time('[INFO] start run {} job(s)...'.format(len(cmds)))
            proc = exec_tools.PopenParallel(cmds)
            proc.wait()
            countC,countF = 0,0
            if proc.returncode != 0:
                for tJob in jobsExec:
                    if tJob['target'] in job2ck and not job2ck[tJob['target']](tJob):
                        job_control.moveJob(tJob, 'fail')
                        countF += 1
                    else:
                        job_control.moveJob(tJob, 'complete')
                        countC += 1
            else:
                [job_control.moveJob(x, 'complete') for x in jobsExec]
                countC = len(jobsExec)
            exec_tools.log_time('[INFO] complete {} job(s) and fail {} job(s)'.format(countC, countF))

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description = pkg.__doc__, formatter_class = argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--conf','-conf',help='sample config file', type=argparse.FileType('r'))
    parser.add_argument('-d','--job_dir',help='job dir for job control')
    parser.add_argument('-t','--threads',help='set thread number',default=32,type=int)
    parser.add_argument('-r','--run', nargs='+',help='assign job type(s) to run, default run all valid job types')
    args = parser.parse_args()

    a=pkg(vars(args))
    a.main()
