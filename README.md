# Config file

My personal system config.

## Setup script

The `setup-system.sh` file is a bash script that automates some of the
system config setup. To see the usage message, use this command:
```
setup-system.sh
```

The script needs to use one of the target platforms that are located
in the `platforms/` directory. An example:
```
./setup-system.sh -t ./platforms/manjaro-xfce.sh`
```

> The script will prompt for the sudo password if installing packages
> using the system package manager.

Portions of the setup can be skipped with flags. See the usage statement
output by the script for details.
