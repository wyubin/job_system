# job_submit(annotation)

藉由外部指定的參數，將相對應的 job 存到 job control 中

## Usage

```sh
usage: job_submit.v0.1.py [-h] [--work_id WORK_ID] [-d JOB_DIR] [-t JOB_TYPE]
                          [-v VCF] [-r RUN_BARCODE] [-p PANEL] [-o OUTPUT]

job_submit.v0.1.py: submit jobs from commandline

optional arguments:
  -h, --help            show this help message and exit
  --work_id WORK_ID     tag work id (default: from_job_submit)
  -d JOB_DIR, --job_dir JOB_DIR
                        job dir for job control (default: None)
  -t JOB_TYPE, --job_type JOB_TYPE
                        job type to run (default: None)
  -v VCF, --vcf VCF     vcf file input (default: None)
  -r RUN_BARCODE, --run_barcode RUN_BARCODE
                        input run barcode to get assoiated information
                        (default: None)
  -p PANEL, --panel PANEL
                        assign job type(s) to run, default run all valid job
                        types (default: None)
  -o OUTPUT, --output OUTPUT
                        output dir (default: None)
```

## Design history

SRS ID | Description
--- | ---
SRS-1 | 依據設定的 job_type 及參數，將 job info 送進 Quene
SRS-2 | 可使用預設的設定，而可以不需要輸入 job_dir

SDS ID | Related source | Specification
--- | --- | ---
SDS-1 | SRS-1 | 直接依據送進來的參數將其編輯成 job control 格式等待 crontab 執行
SDS-2 | SRS-2 | 當沒有指定 job_dir 時，使用 sample_conf 內的設定
