"""Run the approved sixteen graph jobs, then analysis, figures and validation."""
import argparse
import json
import os
import traceback
import run_matched_choice_controls as transport
from failure_case_design import OUT,MODEL,freeze,digest
from control_io import atomic_json


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--execute',action='store_true');args=parser.parse_args()
    frozen,jobs=freeze()
    if not args.execute:
        print('Frozen 16 graph jobs and analysis implementation. Dry run: no API requests.');return
    transport.OUT=OUT;transport.MODELS={MODEL:'transcoder-hp'}
    with transport.file_lock(OUT/'runner.lock'):
        status=dict(state='running',pid=os.getpid(),started_at=transport.now(),graphs_complete=0,runner_sha256=digest(__file__))
        atomic_json(OUT/'status.json',status)
        try:
            client=transport.Client()
            for i,job in enumerate(jobs,1):
                status.update(stage='generation',current_job=job['job_id'],updated_at=transport.now());atomic_json(OUT/'status.json',status)
                transport.graph_job(client,MODEL,job,frozen['settings'])
                status['graphs_complete']=i;atomic_json(OUT/'status.json',status)
                print(f'Archived graph {i}/16: {job["job_id"]}',flush=True)
            for stage in ['analysis','figures','validation']:
                status.update(stage=stage,updated_at=transport.now());atomic_json(OUT/'status.json',status)
                if stage=='analysis':
                    from analyze_failure_case_graphs import main as run
                elif stage=='figures':
                    from plot_failure_case_graphs import main as run
                else:
                    from validate_failure_case_graphs import main as run
                run()
            status.update(state='finished',stage='complete',finished_at=transport.now());atomic_json(OUT/'status.json',status)
        except Exception as error:
            status.update(state='blocked',error=str(error),traceback=traceback.format_exc(),updated_at=transport.now())
            atomic_json(OUT/'status.json',status);raise


if __name__=='__main__':main()
