# job_scan(annotation)

掃描 job dir 將合乎的 jobType 列出後，取出能夠承擔的 jobs 分配資源去進行

## Usage

```sh
usage: job_scan.py [-h] [-conf conf] [-d JOB_DIR] [-t THREADS]

job_scan.v0.1.py: scan jobs from job control

optional arguments:
  -h, --help            show this help message and exit
  -conf conf            sample config file (default: None)
  -d JOB_DIR, --job_dir JOB_DIR
                        job dir for job control (default: None)
  -t THREADS, --threads THREADS
                        set thread number (default: 32)
```

## Job types

jobType | 子程式 | 描述 | cpuJob(最低需要的核心數)
--- | --- | --- | ---
anno_pipeline | act_annotation_pipeline.py | 執行一個 sample 的 annotation 全流程 | 4
annotation_ion | act_annotation_pipeline_IVD.py | 執行一個 torrent sample 的 annotation 全流程 | 4

## Design history

SRS ID | Description
--- | ---
SRS-1 | 依據設定的 job dir 將 request job 抽出，並依照能夠提供的核心數進行分配並平行運算
SRS-2 | 可依據不同 job type 設計不同的運作模板，以方便切換不同類型的 job 進行不同程式的運作
SRS-3 | 當程式輸出異常時，可依照各類型 job 偵測各執行狀況是否正常

SDS ID | Related source | Specification
--- | --- | ---
SDS-1 | SRS-1 | 依照設定的 job dir 讀入 request job
SDS-2 | SRS-1 | 設計 thread 參數，依照所設定的 thread 評估能夠接受的 job 並進行分析
SDS-3 | SRS-2 | 建立 jobTemplate 可切換不同執行程式及參數設定
SRS-4 | SRS-3 | 當 parallel 執行異常時，需要偵測各個 job 是否有正常輸出而回覆其狀態，若 job fail 則轉到 fail 資料夾
