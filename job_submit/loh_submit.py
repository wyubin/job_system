#!/usr/bin/env python
###
### YuBin 2020.06.09 create
###
import os,sys,json
scriptDir = os.path.split(os.path.realpath(__file__))[0]

sys.path.append(os.path.join(scriptDir, '../../python_modules/'))
import job_control,file_module

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
        file_module.prepare(self.sample_conf)

    def main(self):
        job_dir = self.sample_conf.get('confSystem', {}).get('job_dir','-')
        if not os.path.exists(job_dir):
            sys.stderr.write('[WARN] Do not find job_dir:{}'.format(job_dir))
            sys.exit(1)
        panel = self.sample_conf.get('panel',self.args['panel'])
        if not panel:
            sys.stderr.write('[WARN] no panel name setup!\n')
            sys.exit(1)
        ## check run_name
        if not self.sample_conf.get('run_name'):
            strBarcode = os.path.basename(self.args['input'].name)
            fileMod = file_module.id2mod(strBarcode)
            infoBase = fileMod.getBaseInfo(strBarcode)
            self.sample_conf.update(infoBase)
        ## job_control module
        job_control.prepare(job_dir, 'annotation_pipeline')
        run_barcode = '{}_{}'.format(self.sample_conf.get('run_name','NA'),self.sample_conf.get('barcode','NA'))
        targs = {
            'input': [run_barcode],
            'panel': panel,
        }
        jobNew = job_control.createJob(self.args['job_type'], targs)
        jobNew['id'] = run_barcode
        job_control.moveJob(jobNew, 'wait')
        sys.stderr.write('[INFO] Send LOH job {} complete\n'.format(targs['input']))

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description = pkg.__doc__, formatter_class = argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--conf',help='sample config file',metavar='conf', type=argparse.FileType('r'))
    parser.add_argument('-i','--input',help='input table file',metavar='input', type=argparse.FileType('r'),default=sys.stdin)
    parser.add_argument('-p','--panel',help='input custom panel name')
    parser.add_argument('-j', '--job_type', help='input custom job_type', default='cnv2loh')
    parser.add_argument('-o','--output',help='output tagged table file',metavar='output', type=argparse.FileType('w'),default=sys.stdout)
    args = parser.parse_args()

    a=pkg(vars(args))
    a.main()
