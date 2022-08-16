# Config file

A python script to automatically apply configuration to unix-like systems.

## Usage

> NOTE: Run the command `python3 apply-config.py -h` to see command line options.

-Get the script using one of these options:
  - Clone the repository.
  - Download the zipped release and extract it. This option is useful if you
    don't have git installed yet (which is something the configuration script
    will do).

- Change to the script directory.
```shell
cd config
```

- Modify the `config.yml` file based on your needs. See the section `config.yml`
  for details.

- Run the script.
  - Specify the target platform.
  - Use the `--work` and `--personal` flags to install those packages based on
    what machine you're configuring. You can use both flags at the same time.
  - Examples:
    ```shell
    # Setting up a work machine.
    python3 apply-config.py macos --work

    # Setting up a personal machine.
    python3 apply-config.py manjaro_linux --personal
    ```

> NOTE: The script will prompt for the sudo password if installing packages
> using the system package manager.

## config.yml

The file `config.yml` contains the 

> TODO

## Testing

### Unit tests

> TODO

### Manual test with docker

> TODO
