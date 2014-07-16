from __future__ import print_function
import sys
import argparse
import json
import os
import subprocess
import datetime
import gzip

sys_files = ['<stdout>', '<stderr>']


def parse(input_file, valid_output_dir, error_output_dir, audit_output_dir):
    output_file = get_output_file(valid_output_dir, input_file, sys.stdout, gzip_output=True)
    error_file = get_output_file(error_output_dir, input_file, sys.stderr, gzip_output=True)
    audit_file = get_output_file(audit_output_dir, input_file, sys.stdout)

    hash = md5_sum(input_file)

    current_line = 0
    invalid_line_offsets = []

    with get_input_file(input_file) as f:
        for line in f:
            current_line = current_line + 1
            try:
                parsed = json.loads(line)
                print(line, end="", file=output_file)
            except:
                invalid_line_offsets.append(current_line)
                print(line, end="", file=error_file)

    conditional_close(output_file)
    conditional_close(error_file)

    audit = dict(input_file_name=input_file.rstrip('\n'),
                 input_file_hash=hash,
                 discarded_lines=len(invalid_line_offsets),
                 processed_at_utc=str(datetime.datetime.utcnow()),
                 valid_file_name=output_file.name,
                 error_file_name=error_file.name,
                 invalid_line_offsets=invalid_line_offsets
    )

    print(json.dumps(audit), end="", file=audit_file)
    conditional_close(audit_file)


def get_input_file(filename):
    if filename.endswith("gz"):
        file = gzip.GzipFile(filename, "r+b")
    else:
        file = open(filename, "r+b")

    return file


def get_output_file(output_dir, input_file, fallback, gzip_output=False):
    if output_dir and input_file:

        if input_file.endswith("gz") and not gzip_output:
            input_file, extension = os.path.splitext(input_file)

        if not gzip_output:
            file = open("{dir}/{basename}".format(dir=output_dir, basename=os.path.basename(input_file)), 'w+')
        else:
            file = gzip.GzipFile("{dir}/{basename}".format(dir=output_dir, basename=os.path.basename(input_file)), 'w+')

    else:
        file = fallback

    return file


def conditional_close(file):
    if file.name not in sys_files:
        file.close()


def md5_sum(filename):
    sum, file = subprocess.check_output(['md5sum', filename]).split()
    return sum


if __name__ == '__main__':
    description = 'Iterates over JSON tracking logs discarding invalid JSON lines' \
                  ' and outputing a valid file, error file and audit report'

    parser = argparse.ArgumentParser(description=description)

    msg = 'Valid output file directory.'
    parser.add_argument('--valid-output-dir', help=msg)

    msg = 'Error output file directory.'
    parser.add_argument('--error-output-dir', help=msg)

    mage = 'Audit report output directory'
    parser.add_argument('--audit-output-dir', help=msg)

    msg = 'The input file to process.'
    parser.add_argument('input_file', help=msg)

    args = parser.parse_args()

    input_file = args.input_file
    valid_output_dir = args.valid_output_dir
    error_output_dir = args.error_output_dir
    audit_output_dir = args.audit_output_dir

    parse(input_file, valid_output_dir, error_output_dir, audit_output_dir)
