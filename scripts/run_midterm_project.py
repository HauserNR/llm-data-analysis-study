"""Chapter 08: run from raw inputs; outputs are scoped to chapter08/."""
from pathlib import Path
import sys
import os
os.environ.setdefault('MPLBACKEND','Agg')
os.environ.setdefault('MPLCONFIGDIR','/tmp/ch08-matplotlib')
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'chapter08'))
from src.midterm_project import run_midterm_project
from src.evidence import input_manifest, extra_evidence

def main():
    out=ROOT/'chapter08'/'reports'
    before=input_manifest(ROOT)
    result=run_midterm_project(raw_dir=ROOT/'data/raw',processed_dir=ROOT/'chapter08/data/processed',report_dir=out,figure_dir=ROOT/'chapter08/images')
    extra=extra_evidence(result['raw_data'], result['processed_data'],result['analysis_tables'],out)
    after=input_manifest(ROOT)
    assert before.equals(after),'Input files changed'
    after.to_csv(out/'ch08_input_manifest.csv',index=False)
    print('Python:',sys.version.split()[0])
    for label,table in [('Final Validation',result['project_validation']),('Additional Validation',extra),('Total consistency',result['analysis_tables']['total_consistency_check'])]:
        print(label);print(table.to_string(index=False))
    print('Input preservation: PASS; raw + existing processed unchanged')
    print('Project Validation: PASS')

if __name__=='__main__':
    main()
