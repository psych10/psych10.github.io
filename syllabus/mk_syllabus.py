"""
generate markdown version of syllabus
"""

import os
import collections
import re
import time
import pandas
from get_syllabus2 import get_syllabus
import subprocess
from datetime import date, timedelta

def run_shell_cmd(cmd,cwd=[],verbose=False):
    """ run a command in the shell using Popen
    """
    stdout_holder = []
    stderr_holder = []

    if cwd:
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE,cwd=cwd)
    else:
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE)

    for line in process.stdout:
        if verbose:
             print(line.strip().decode('UTF-8'))
        stdout_holder.append(line.strip().decode('UTF-8'))
    for line in process.stderr:
        if verbose:
            print(line.strip().decode('UTF-8'))
        stderr_holder.append(line.strip().decode('UTF-8'))

    process.wait()
    return (stdout_holder,stderr_holder)


def replacemany(adict, astring):
    # from https://stackoverflow.com/questions/2392623/replace-multiple-string-in-a-file # noqa
    pat = '|'.join(re.escape(s) for s in adict)
    there = re.compile(pat)
    def onerepl(mo): return adict[mo.group()]
    return there.sub(onerepl, astring)


lecturebase = '../lectures'
if not os.path.exists(lecturebase):
    os.mkdir(lecturebase)

syll = get_syllabus()

df = pandas.DataFrame(syll[1:],columns=syll[0])
df = df.loc[df.Week!='', :]  # remove empty rows


# save objectives to write to a separate file listing all of them
objectives = collections.OrderedDict()

outfile = 'index.md'
prospectus_file = '../prospectus/index.md'

# first open prospectus and add it
with open (prospectus_file) as f:
    prospectus_lines = f.readlines()

# columns to use for syllabus
syll_columns = ['Learning goals', 'Readings', 'Lecture videos', 'Tutorials', 'Problem set']

start_date = '2021-01-11'

start_date_dt = date.fromisoformat(start_date)

with open(outfile, 'w') as f:
    f.write('---\nlayout: default\ntitle: Psych 10/Stats 60 Syllabus - Winter 2021\n---\n\n') # noqa
    for p in prospectus_lines:
        f.write(p)

    f.write('## Course modules\n\nNote: This schedule is a guide for the course and is subject to change with advance notice.\n\n')

    for module_idx in df.index:
        module_start_date = (start_date_dt + timedelta(days = 7 * module_idx)).strftime('%B %d')
        module_due_date = (start_date_dt + timedelta(days = 7 * (module_idx + 1) - 1)).strftime('%B %d')
        module_avail_date = (start_date_dt + timedelta(days = -21 * module_idx)).strftime('%B %d')
        if module_avail_date < start_date_dt:
            module_avail_date = start_date_dt
        f.write(f'## Module {df.loc[module_idx, "Week"]}: {df.loc[module_idx, "Module Topic"]}\n\n') # noqa

        f.write(f'*Start date*: {module_start_date}\n\n')
        f.write(f'*Due date for all components*: {module_due_date}\n\n')
        f.write(f'*Available as of*: {module_avail_date}\n\n')
    
        for section in syll_columns:
            if len(df.loc[module_idx, section]) > 0:
                f.write(f'### {section}:\n\n')
                f.write(f"{df.loc[module_idx, section]}\n")
                f.write('\n')

margin_cm = 2
args = {'pdf': f'-V geometry:margin={margin_cm}cm',
        'html': ''}
for output_type in ['pdf', 'html']:
    cmd_output = run_shell_cmd(f'pandoc -s {outfile} -o syllabus.{output_type} {args[output_type]}')
    print(cmd_output)
