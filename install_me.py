#!/usr/bin/env python

__author__ = ('Imam Omar Mochtar', ('iomarmochtar@gmail.com',))

"""
Easy install for mailman3 core and web admin dashboard (postorious & hyperkitty)
"""

import os
import sys
import string
import random
import subprocess
import tempfile
from time  import sleep


BASE_PATH = "/opt/mailman3"
REQ_PACKAGES = "wget git-core gcc bzip2 xz gcc-c++ nginx openssl"
MINICONDA_URL = "https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh"
MINICONDA_PATH = os.path.join(BASE_PATH, "conda")
TEMP_DIR = "/root/mailman3_setup"
MAILMAN3EI_REPO = "https://github.com/iomarmochtar/mailman3_ei"
DELAY = 1
LOG_FILE = tempfile.mktemp()

def runCmd(cmd, ignore=False):
    """
    runCmdute system command
    """
    print("Running command: %s"%cmd)

    kwargs = dict(universal_newlines=True, shell=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    cmd = "%s >> %s 2>&1"%(cmd, LOG_FILE)
    output, err = subprocess.Popen(cmd, **kwargs).communicate()
    if not ignore and err:
        print("Error detected, see log file %s for more information"%LOG_FILE)
        open(LOG_FILE, 'aw').write(err)
        #sys.stderr.write("%s [ERROR]\n"%err)
        sys.exit(1)
    sleep(DELAY)

def gen_secret():
    """
    Modified from https://coderwall.com/p/bkkjgw/oneliner-to-generate-a-django-secret-key
    """
    # all character except double quote 
    uni=string.ascii_letters+string.digits+string.punctuation.replace("\"", '')
    return repr(''.join([random.SystemRandom().choice(uni) for i in range(random.randint(45,50))]))

def prompt(txt):
    print("%s %s"%("="*15, txt))

def main():

    print("Log file %s"%LOG_FILE)

    # install required packages
    prompt("Make sure epel repo has been installed")
    runCmd("yum install -y epel-release")

    prompt("Installing required packages (%s)"%REQ_PACKAGES)
    runCmd("yum install -y %s"%REQ_PACKAGES)
  
    # close repository directly if not exist 
    if not os.path.isdir(BASE_PATH):
        prompt("Repo directory %s not found, do clone repository"%BASE_PATH)
        runCmd("git clone %s %s"%(MAILMAN3EI_REPO, BASE_PATH))
 
    # create temp dir
    prompt("Creating temporary (%s)"%TEMP_DIR)
    runCmd("mkdir -p %s"%TEMP_DIR)

    # folders
    prompt("Create mandatory folders")
    runCmd("mkdir -p %s/var/{data/pid,logs}"%(BASE_PATH))

    # download minconda
    mconda_installer = os.path.join(TEMP_DIR, os.path.basename(MINICONDA_URL))
    prompt("Downloading miniconda (python3)")
    if not os.path.isfile(mconda_installer):
        runCmd("wget -c %s -O %s"%(MINICONDA_URL, mconda_installer))
    runCmd("chmod +x %s"%mconda_installer)
    
    # installing miniconda
    prompt("Installing miniconda in %s"%MINICONDA_PATH)
    runCmd("mkdir -p %s"%(os.path.split(MINICONDA_PATH)[0]))
    runCmd("sh %s -b -p %s"%(mconda_installer, MINICONDA_PATH), True)

    # python virtualenv
    conda_bin = os.path.join(MINICONDA_PATH, "bin/conda")
    prompt("Create mailman3_core and mailman3_ext virtual environment")
    runCmd("%s create --name mailman3_core -y"%conda_bin)
    runCmd("%s create --name mailman3_ext python=2 -y"%conda_bin)

    # python libs for core and ext
    prompt("Installing required python libs")
    pip_py3 = os.path.join(MINICONDA_PATH, "bin/pip")
    pip_py2 = os.path.join(MINICONDA_PATH, "envs/mailman3_ext/bin/pip")
    req_core = os.path.join(BASE_PATH, "misc/mailman3_core_requirements.txt")
    req_ext = os.path.join(BASE_PATH, "misc/mailman3_ext_requirements.txt")
    
    runCmd("%s install -r %s"%(pip_py3, req_core))
    runCmd("%s install -r %s"%(pip_py2, req_ext))


    # Generate self sign certificate
    prompt("Generating Certificate for HTTPS")
    cert_path = os.path.join(BASE_PATH, "etc/nginx/certs")
    private_key = os.path.join(cert_path, "ssl.key")
    public_key = os.path.join(cert_path, "ssl.cert")
    sub = "/C=ID/ST=DKI Jakarta/L=South of Jakarta/O=JBT/OU=IT Department/CN=mailman.jbt.id"
    runCmd("mkdir -p %s"%cert_path)
    runCmd("openssl req -x509 -nodes -days 3650 -newkey rsa:2048 -keyout %s -out %s -subj \"%s\""%(private_key, public_key, sub), True)

    # Generate django secret key
    prompt("Generating django secret key")
    webui_base = os.path.join( BASE_PATH, 'webui/webui'  )
    runCmd("mkdir -p %s"%webui_base)
    secret_file = open( os.path.join(webui_base, 'settings_secret.py'), 'w')
    secret_file.write("SECRET_KEY=%s"%gen_secret())
    secret_file.close()
     
    # Collect static
    prompt("Collecting static files for webui")
    py2 = os.path.join(MINICONDA_PATH, "envs/mailman3_ext/bin/python")
    webui_manage = os.path.join(BASE_PATH, "webui/manage.py")
    runCmd("%s %s collectstatic --noinput"%(py2, webui_manage))

    # Migrating database
    prompt("Migrating mailman3 webui database")
    runCmd("%s %s migrate"%(py2, webui_manage))

    # Installing init script
    prompt("Installing int script for mailman3 core and webui")
    inits = ["mailman3", "mailman3_webui"]
    for _init in inits:
        tgt = "/etc/init.d/%s"%_init
        if os.path.isfile(tgt):
            continue
        src = os.path.join(BASE_PATH, "misc/%s_init"%_init)
        runCmd("cp %s %s"%(src, tgt))


    print("[DONE]")
    cmd_admin = "%s %s createsuperuser"%(py2, webui_manage)
    print("""You may create admin user by running following command
%s

to run mailman3 services:
service mailman3 start
service mailman3_webui start


Further more please read mailman3 documentation (http://docs.mailman3.org/en/latest/)

Note: 
- Please change self sign certicate with commercial one.
- if there are any issue,suggestion or forking visit this repo script %s

"""%(cmd_admin, MAILMAN3EI_REPO))
    

if __name__ == '__main__':
    main()
