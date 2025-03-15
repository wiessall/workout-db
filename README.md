# Workout Bot
Simple telegram chat bot retrieving and inserting workout information from a postgresql database.

I use this project to learn more hands-on on these subjects:
  - async Mock testing
    - figuring out how 100% test coverage might look like for a simple project
  - python SQL interactions
  - python development on nix(os)
    - devShell with FHS
    - direnv for automatic devShell activation
    - poetry and dream2nix for compatability with non-nix development
    - nix-containers
    - nix flake and module packaging

# TODOS
  - [ ] test if the service executes as and when expected
  - [ ] /done does not seem to close app
  - [ ] some tests missing
  - [ ] logging
  - [ ] set_variable test not mocked
  - [ ] add docstrings and typing
  - [ ] test deployment outside nixos-container
  - [ ] passing of env variables is a bit hacky currently 
    - systemd-creds
    - systemd LoadCredential
    - figure out how to pass environment variables to the service without env file
  - [ ] check if SQL injections possible
  - [ ] refactor flake