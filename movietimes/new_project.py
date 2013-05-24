import os, sys
import shutil
import subprocess

def sed_callback(arg, dirname, fnames):
    for fname in fnames:
        new_file = os.path.join(dirname, fname)
        if fname.endswith(".py"):
            print subprocess.call(['sed','-i', '', 's/movietimes/' + arg + '/g',  new_file])
        elif fname.endswith(".pyc"):
            os.remove(new_file)

        #sed -i "" 's/movietimes/hawkbot/g' ./movietimes/database.py

def rename_callback(arg, dirname, fnames):
    pass

def main(args):
    source = os.path.dirname(os.path.abspath(__file__))
    dest = args[0]
    project_name = os.path.basename(dest)
    shutil.copytree(source, dest)
    shutil.rmtree(os.path.join(dest, '.git'))
    shutil.rmtree(os.path.join(dest, 'venv'))
    os.path.walk(dest, sed_callback, project_name)
    os.rename(os.path.join(dest, 'movietimes'), os.path.join(dest,project_name))

if __name__ == '__main__':
    main(sys.argv[1:])

#sed -i "" 's/movietimes/hawkbot/g' ./movietimes/database.py
