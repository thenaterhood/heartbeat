#!/usr/bin/env python

from pkg_resources import resource_string
import argparse
import os
import sys
import shutil
import stat


def uninstall_all(root):
    hb_cfg_dir = os.path.join(root, "etc", "heartbeat")
    systemd_service = os.path.join(root, "usr", "lib", "systemd", "system", "heartbeat.service")
    sysvinit_service = os.path.join(root, "etc", "init.d", "heartbeat")

    try:
        os.remove(systemd_service)
    except OSError as err:
        print("Error removing systemd service: {:s}".format(err.strerror))

    try:
        os.remove(sysvinit_service)
    except OSError as err:
        print("Error removing Sysvinit service: {:s}".format(err.strerror))

    try:
        shutil.copy(hb_cfg_dir, os.path.expanduser(os.path.join("~", "heartbeat-cfg-backup")))
        shutil.rmtree(hb_cfg_dir)
    except OSError as err:
        print("Error removing cfg directory: {:s}".format(err.strerror))

def install_cfg_dir(root, overwrite):
    hbconf = resource_string(
        "heartbeat.resources.cfg",
        "heartbeat.conf"
        ).decode("UTF-8")

    notconf = resource_string(
        "heartbeat.resources.cfg",
        "notifying.conf"
        ).decode("UTF-8")

    monconf = resource_string(
        "heartbeat.resources.cfg",
        "monitoring.conf"
        ).decode("UTF-8")

    directory = os.path.join(root, "etc", "heartbeat")
    if os.path.exists(directory) and not overwrite:
        print(
            "Heartbeat configuration appears to already exist. Pass the overwrite flag or delete the directory."
        )
    else:
        if not os.path.exists(directory):
            os.mkdir(directory)

        hbconf_path = os.path.join(directory, "heartbeat.conf")
        monconf_path = os.path.join(directory, "monitoring.conf")
        notconf_path = os.path.join(directory, "notifying.conf")

        with open(hbconf_path, "w") as hbconf_file:
            hbconf_file.write(hbconf)

        with open(monconf_path, "w") as monconf_file:
            monconf_file.write(monconf)

        with open(notconf_path, "w") as notconf_file:
            notconf_file.write(notconf)

def install_systemd_service(root, overwrite):
    resource = resource_string(
        "heartbeat.resources.service",
        "systemd"
        ).decode("UTF-8")

    path = os.path.join(root, "usr", "lib", "systemd", "system", "heartbeat.service")
    if os.path.exists(path) and not overwrite:
        print(
            "systemd service file already exists. You may overwrite it by passing the --overwrite flag."
        )
    else:
        with open(path, "w") as servicefile:
            servicefile.write(resource)

def install_sysvinit_service(root, overwrite):
    resource = resource_string(
        "heartbeat.resources.service",
        "sysvinit"
        ).decode("UTF-8")

    path = os.path.join(root, "etc", "init.d", "heartbeat")
    if os.path.exists(path) and not overwrite:
        print(
            "sysvinit service file already exists. You may overwrite it by passing the --overwrite flag."
            )
    else:
        with open(path, "w") as init_script:
            init_script.write(resource)

        st = os.stat(path)
        os.chmod(path, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

        print("sysvinit service file has been installed to " + path)

def main():
    parser = argparse.ArgumentParser()

    if sys.platform == "win32":
        default_path = os.path.join(os.environ['PROGRAMDATA'], 'Heartbeat')
    else:
        default_path = "/"

    parser.add_argument(
        '--root',
        required=False,
        default=default_path,
        help="Root path for installing files. Defaults to " + default_path
        )

    parser.add_argument(
        '--install-systemd',
        required=False,
        default=False,
        action='store_true',
        help="Install systemd service for Heartbeat."
        )
    parser.add_argument(
        '--install-sysvinit',
        required=False,
        default=False,
        action='store_true',
        help="Install sysvinit script for Heartbeat."
    )
    parser.add_argument(
        '--install-cfg',
        required=False,
        default=False,
        action='store_true',
        help="Install the configuration directory and files for Heartbeat."
    )
    parser.add_argument(
        '--overwrite',
        required=False,
        default=False,
        action='store_true',
        help="Pass this flag to force the install script to overwrite existing files. If not passed, the install script will avoid overwriting anything."
    )
    parser.add_argument(
        '--uninstall-all',
        required=False,
        default=False,
        action='store_true',
        help="Uninstall the service and config files. Config files will be backed up to your home directory. This will not disable the services if enabled."
    )

    args = parser.parse_args()

    if args.uninstall_all:
        uninstall_all(root=args.root)

    if args.install_cfg:
        install_cfg_dir(root=args.root, overwrite=args.overwrite)

    if args.install_systemd:
        install_systemd_service(root=args.root, overwrite=args.overwrite)

    if args.install_sysvinit:
        install_sysvinit_service(root=args.root, overwrite=args.overwrite)

if __name__ == "__main__":
    main()
