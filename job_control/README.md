# job_control

因應不同 pipeline 可能會需要接收其他pipeline 的資訊所想出的溝通方法，因此設計出一個共通的 job 資料格式及操作方法，以方便各個 pipeline 的子程式進行job 操作。

## Usage

```python
import job_control
job_control.prepare('/mnt/Shared_Space_B/illumina_data/job_control')
targs = {'input':'/mnt/Shared_Space_B/illumina_data/NextSeq550_A_Output/AANB01_50/AANB01_50_IDX70055002_ACT0871/varcall/AANB01_50_IDX70055002_ACT0871.final.vcf','panel':'PA037_ACTHRDv1'}
ajob = job_control.createJob('annotation',targs)
## save it in wait
job_control.moveJob(ajob,'wait')
## move it to proceed
job_control.moveJob(ajob,'proceed')
## get jobs with annotation(proceed)
jobsAnno = job_control.loadJobs('annotation',['proceed'])
## remove all
[job_control.removeJob(x) for x in jobsAnno]
## log ck and log down
if not job_control.log_ck():
    sys.stderr.write('[WARN] "{}" already running!\n'.format(self.vars['idScript']))
jobs = self.jobCollect()
if not jobs:
    sys.stderr.write('[INFO] No more job associated "{}"\n'.format(','.join(self.vars['typesJob'])))
    job_control.log_down()
```

## Design history

SRS ID | Description
--- | ---
SRS-1 | 建立一個共通的 job 資料格式，讓各個 pipeline 能夠接受訊息
SRS-2 | 建立一個 job 操作的 module 讓各個 pipeline 使用在收集大量跑資料的程式中
SRS-3 | 增加一個 log 資料夾存放在不同 host(VM) 操作時可以管控及紀錄
SRS-4 | 需要能夠放置 fail job 的資料夾

SDS ID | Related source | Specification
--- | --- | ---
SDS-1 | SRS-1 | 設定 job 物件中需要儲存的參數，並以 json 格式存於檔案中。
SDS-2 | SRS-1 | 建立一個檔案結構來分類各個 job 進行的狀態。
SDS-3 | SRS-2 | 建立模組來進行 job 的建立，搬移，刪除，讀取等等操作。
SDS-4 | SRS-3 | 建立幾個 log 操作的方法來確認及偵測不同host 在不同流程使用 job control 的 log。
SDS-5 | SRS-4 | 建立fail 資料夾放置 fail jobs。
