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

- Modify the `config.yml` file based on your needs. See the section
  [config file](#config-file) for details.

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

## config file

The file `config.yml` defines which changes are applied by the script.

Some groups are broken down into `all`, `personal`, and `work` subgroups.
Values from the `all` group are always applied. The values in the `personal`
group are only applied if the `--personal` CLI argument is provided. Likewise,
`work` items are only applied if the `--work` CLI argument is provided.
Any of these groups can be empty, but the group title should still be present.

| Field | Description |
| - | - |
| user_info.email | Email address used when configuring git. |
| user_info.name | Full name used when configuring git. This can contain spaces. |
| configure_git_global_settings | Will run `git configure --global` commands if True. |
| ssh.generate_ssh_key | Will generate a new ssh key if True. |
| ssh.ssh_algorithm | Encryption algorithm to use when generating the key. |
| ssh.ssh_keyfile_path | Path where the new key is written. |
| ssh.sshd_enabled | Will start the sshd service if True. |
| vundle | Will run vundle to install vim plugins (from .vimrc) if True. |
| config_files | Lists of files that are copied to the system. |

In addition, each target platform has a set of configuration values that define
what applications are installed on that platform. These values are individually
tailored to the target platform. See the code under the `platforms` directory
if you need to dig into the details.

## Testing

### Unit tests

Run unit tests.
```
python3 -m unittest
```

### Manual test with docker

Follow these steps to spin up a docker image and apply config changes to it.

- Build the image. This will copy the config script code into the container.
```shell
docker build -t alpine-test:test -f Dockerfile-test .
```

- Start the container.
```shell
docker run -it alpine-test:test /bin/ash
```

> NOTE: If you get an error about the image platform not matching the host
> platform, try adding `--platform linux/amd64` to the above command.

- Apply configuration changes.
```shell
python3 apply-config.py alpine_linux --personal --work --config-path ./config.yml
```

> NOTE: Alternatively, all of the above commands can be concatenated into one command:
> `docker build -t alpine-test:test -f Dockerfile-test . && docker run -it alpine-test:test /bin/ash -c "python3 apply-config.py alpine_linux --personal --work --config-path ./config.yml; /bin/ash"`

- Verify that the configuration changes are applied.
