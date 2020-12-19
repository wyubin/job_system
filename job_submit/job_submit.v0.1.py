#!/usr/bin/env python
###
### YuBin 2020.06.09 create
###
import os,sys,json
scriptDir = os.path.split(os.path.realpath(__file__))[0]

sys.path.append(os.path.join(scriptDir, '../../python_modules/'))
import job_control

class pkg():
    """job_submit.v0.1.py: 
    submit jobs from commandline
    """
    def __init__(self, args={}):
        "add all options var into self"
        self.args = {}
        self.args.update(args)
        self.vars = {}
        self.prepare()
    
    def prepare(self):
        "prepare"
        self.sample_conf = {}
        path_conf = self.args['conf'].name if self.args['conf'] else os.path.join(scriptDir, '../', 'config.json')
        if os.path.exists(path_conf):
            self.sample_conf = json.load(open(path_conf))

    def ckArgs(self):
        for tkey in ['job_type', 'panel', 'output']:
            if not self.args.get(tkey):
                raise NameError('[WARN] please input "{}" argument!'.format(tkey))

    def main(self):
        self.ckArgs()
        job_dir = self.args['job_dir'] or self.sample_conf.get('confSystem', {}).get('job_dir','-')
        if not os.path.exists(job_dir):
            raise NameError('[WARN] Do not find job_dir:{}'.format(job_dir))
        ## job_control module
        job_control.prepare(job_dir, self.args['work_id'])
        targs = {
            'input': self.args['vcf'].name if self.args['vcf'] else self.args.get('run_barcode'),
            'panel': self.args['panel'],
            'run_barcode':self.args.get('run_barcode'),
            'output':self.args['output'],
            'caller': self.args['caller'],
            'log_name': self.args['log_name'],
        }
        jobNew = job_control.createJob(self.args['job_type'], targs)
        if self.args.get('run_barcode'):
            jobNew['id'] = self.args['run_barcode']
        job_control.moveJob(jobNew, 'wait')
        sys.stderr.write('[INFO] Send job {} complete\n'.format(targs['input']))

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description = pkg.__doc__, formatter_class = argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--work_id', help='tag work id',default='from_job_submit')
    parser.add_argument('--conf','-conf',help='sample config file', type=argparse.FileType('r'))
    parser.add_argument('-d','--job_dir',help='job dir for job control')
    parser.add_argument('-t', '--job_type', help='job type to run')
    parser.add_argument('-v','--vcf',help='vcf file input', type=argparse.FileType('r'))
    parser.add_argument('-r','--run_barcode', help='input run barcode to get assoiated information')
    parser.add_argument('-p','--panel',help='assign job type(s) to run, default run all valid job types')
    parser.add_argument('-c','--caller',default='TVC',help='assign caller if needed')
    parser.add_argument('-l','--log_name',default='annotation',help='assign prefix log name if needed')
    parser.add_argument('-o', '--output', help='output dir')
    args = parser.parse_args()

    a=pkg(vars(args))
    a.main()
