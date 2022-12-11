import gzip
import shutil
with gzip.open('RW-20210606.tar.gz', 'rt') as f_in:
    with open('RW-20210606.txt', 'wt') as f_out:
        shutil.copyfileobj(f_in, f_out)