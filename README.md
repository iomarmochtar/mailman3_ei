Mailman3 Easy Install
---------------------

This repo aims to make installation for mailman3 and it's web dashboard management (Hyperkitty & Postorious) easy for Centos (or redhat-like OS).


Thanks to Conda project (https://conda.io) to make multiversion python installation easy (and fun).

Tested in:
- Centos 6.9 (fresh installation)
- Centos 7 (fresh installation)


### Preinstallation

Make sure following points are checked before do the installation:

- Stable internet connection.
- SELINUX status is disabled.
- Has enough space for path **/opt**
- **git-core** package has been installed


### Installation

Clone repository to mailman3_ei base path (**/opt/mailman3**)
```sh
git clone https://github.com/iomarmochtar/mailman3_ei /opt/mailman3
```

Run installation script
```sh
python /opt/mailman3/install_me.py
```

