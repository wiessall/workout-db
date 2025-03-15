{
  description = "Workout DB packaged with dream2nix";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    dream2nix.url = "github:nix-community/dream2nix";
    sops-nix.url = "github:Mic92/sops-nix";
  };

  outputs = { self, nixpkgs, dream2nix, sops-nix }:
    let
    eachSystem = nixpkgs.lib.genAttrs [
      "aarch64-darwin"
      "aarch64-linux"
      "x86_64-darwin"
      "x86_64-linux"
    ];
    in {
      packages = eachSystem (system: {
        default = dream2nix.lib.evalModules {
          packageSets.nixpkgs = nixpkgs.legacyPackages.${system};
          modules = [
            ./default.nix
            {
              paths.projectRoot = ./.;
              paths.projectRootFile = "flake.nix";
              paths.package = ./.;
            }
          ];
        };
      });
      nixosModules.default = { config, lib, pkgs, ... }:

        with lib;

        let
          cfg = config.services.workout-db;

          parseCSV = text:
            let
              lines = filter (l: l != "") (splitString "\n" text);

              toAttrs = line:
                let
                  cols = splitString "," line;
                  get = i: strings.trim (elemAt cols i);
                in {
                  Machine  = get 0;
                  Exercise = get 1;
                  Reps     = get 2;
                  Weight   = get 3;
                  Date     = get 4;
                  Workout  = get 5;
            };
          in map toAttrs lines;
        in {
          options.services.workout-db = {
            enable = mkEnableOption "Workout DB daemon";

            package = mkOption {
              type = types.package;
              default = self.packages.${pkgs.system}.default;
              description = "The package for the Workout DB application.";
            };

            environmentVariables = mkOption {
              type = types.attrsOf types.str;
              default = {
                DB_NAME = "workout_db";
                DB_USER = "workout_user";
                DB_PASSWORD = "workout";
                DB_HOST = "localhost";
                DB_PORT = "5432";
              };
              description = "Environment variables for Workout DB.";
            };

            chatBotVariables = mkOption {
              type = types.attrsOf types.str;
              default = {
                TELEGRAM_TOKEN = "TOKEN";
                CHAT_ID = "ID";
              };
              description = "Bot token and bot chat id generated following this guide: https://github.com/python-telegram-bot/python-telegram-bot/wiki/Extensions---Your-first-Bot";
            };

            workoutData = mkOption {
              type = types.lines;
              default = ''
                B12     , Rematore con manubrio              ,   12 ,     16 , 1970-01-01 ,       1 
                B12     , Rematore con manubrio              ,   12 ,     18 , 1970-01-01 ,       1 
                B12     , Rematore con manubrio              ,   12 ,     18 , 1970-01-01 ,       1 
                B09     , Lat Machine                        ,    8 ,     45 , 1970-01-01 ,       1 
                B09     , Lat Machine                        ,    8 ,     45 , 1970-01-01 ,       1 
                B09     , Lat Machine                        ,    8 ,     45 , 1970-01-01 ,       1 
                C14     , Rematore T-Bar                     ,    8 ,     20 , 1970-01-01 ,       1 
                C14     , Rematore T-Bar                     ,    8 ,     20 , 1970-01-01 ,       1 
                C14     , Rematore T-Bar                     ,    8 ,     20 , 1970-01-01 ,       1 
                C08     , Scrollatore con bilanciere davanti ,   10 ,     20 , 1970-01-01 ,       1 
                C08     , Scrollatore con bilanciere davanti ,   10 ,     20 , 1970-01-01 ,       1 
                C08     , Scrollatore con bilanciere davanti ,   10 ,     20 , 1970-01-01 ,       1 
                B15     , Rematore con bilanciere            ,    7 ,     20 , 1970-01-01 ,       1 
                B15     , Rematore con bilanciere            ,    7 ,     20 , 1970-01-01 ,       1 
                B15     , Rematore con bilanciere            ,    7 ,     20 , 1970-01-01 ,       1 
                C01     , Butterfly reverse                  ,   12 ,     20 , 1970-01-01 ,       1 
                C01     , Butterfly reverse                  ,   10 ,     20 , 1970-01-01 ,       1 
                C01     , Butterfly reverse                  ,   10 ,     15 , 1970-01-01 ,       1 
                B17     , Deadlift                           ,   10 ,     20 , 1970-01-02 ,       2 
                B17     , Deadlift                           ,   10 ,     30 , 1970-01-02 ,       2 
                B17     , Deadlift                           ,   10 ,     30 , 1970-01-02 ,       2 
                B17     , Deadlift                           ,   10 ,     30 , 1970-01-02 ,       2 
                E10     , Squat                              ,   10 ,     20 , 1970-01-02 ,       2 
                E10     , Squat                              ,   10 ,     20 , 1970-01-02 ,       2 
                E10     , Squat                              ,   10 ,     20 , 1970-01-02 ,       2 
                E08     , Leg Press 45                       ,   12 ,     60 , 1970-01-02 ,       2 
                E08     , Leg Press 45                       ,   10 ,     60 , 1970-01-02 ,       2 
                E08     , Leg Press 45                       ,   12 ,     60 , 1970-01-02 ,       2 
                E04     , Leg Extension                      ,   12 ,     50 , 1970-01-02 ,       2 
                E04     , Leg Extension                      ,   10 ,     50 , 1970-01-02 ,       2 
                E04     , Leg Extension                      ,   10 ,     40 , 1970-01-02 ,       2 
                E05     , Leg Curl                           ,   10 ,     40 , 1970-01-02 ,       2 
                E05     , Leg Curl                           ,   10 ,     40 , 1970-01-02 ,       2 
                E05     , Leg Curl                           ,    8 ,     40 , 1970-01-02 ,       2 
                E16     , Calf Machine                       ,   15 ,     45 , 1970-01-02 ,       2 
                E16     , Calf Machine                       ,   15 ,     45 , 1970-01-02 ,       2 
                E16     , Calf Machine                       ,   15 ,     45 , 1970-01-02 ,       2 
                A02     , Butterfly                          ,   12 ,     20 , 1970-01-03 ,       3 
                A02     , Butterfly                          ,   12 ,     30 , 1970-01-03 ,       3 
                A02     , Butterfly                          ,   10 ,     30 , 1970-01-03 ,       3 
                A02     , Butterfly                          ,    8 ,     30 , 1970-01-03 ,       3 
                F10     , Abdominal Machine                  ,   15 ,     55 , 1970-01-03 ,       3 
                F10     , Abdominal Machine                  ,   15 ,     55 , 1970-01-03 ,       3 
                F10     , Abdominal Machine                  ,   15 ,     50 , 1970-01-03 ,       3 
                F10     , Abdominal Machine                  ,   15 ,     40 , 1970-01-03 ,       3 
                A10     , Incline Bench Press                ,   12 ,     10 , 1970-01-03 ,       3 
                A10     , Incline Bench Press                ,   10 ,     15 , 1970-01-03 ,       3 
                A10     , Incline Bench Press                ,    8 ,     15 , 1970-01-03 ,       3 
                F17     , Leg Raises                         ,   10 ,     bw , 1970-01-03 ,       3 
                F17     , Leg Raises                         ,   10 ,     bw , 1970-01-03 ,       3 
                F17     , Leg Raises                         ,   10 ,     bw , 1970-01-03 ,       3 
                A05     , Bench press                        ,   10 ,     10 , 1970-01-03 ,       3 
                A05     , Bench press                        ,   10 ,     10 , 1970-01-03 ,       3 
                A05     , Bench press                        ,   10 ,     10 , 1970-01-03 ,       3 
                D08     , Curl Concentrato                   ,   10 ,      9 , 1970-01-04 ,       4 
                D08     , Curl Concentrato                   ,    8 ,      9 , 1970-01-04 ,       4 
                D08     , Curl Concentrato                   ,    6 ,      9 , 1970-01-04 ,       4 
                D18     , Triceps                            ,   10 ,      9 , 1970-01-04 ,       4 
                D18     , Triceps                            ,   10 ,      9 , 1970-01-04 ,       4 
                D18     , Triceps                            ,   10 ,      9 , 1970-01-04 ,       4 
                D03     , Cable Curl                         ,   12 ,     20 , 1970-01-04 ,       4 
                D03     , Cable Curl                         ,    8 ,     20 , 1970-01-04 ,       4 
                D03     , Cable Curl                         ,    8 ,     20 , 1970-01-04 ,       4 
                D12     , Push Down                          ,   12 ,     40 , 1970-01-04 ,       4 
                D12     , Push Down                          ,   12 ,     50 , 1970-01-04 ,       4 
                D12     , Push Down                          ,    8 ,     50 , 1970-01-04 ,       4 
                D01     , Biceps Machine                     ,   10 ,     15 , 1970-01-04 ,       4 
                D01     , Biceps Machine                     ,    8 ,     15 , 1970-01-04 ,       4 
                D01     , Biceps Machine                     ,   10 ,     10 , 1970-01-04 ,       4 
                R01     , Rope Skipping                      ,    3 ,     bw , 1970-01-04 ,       4 
                R01     , Rope Skipping                      ,    3 ,     bw , 1970-01-04 ,       4 
                R01     , Rope Skipping                      ,    3 ,     bw , 1970-01-04 ,       4 
                D11     , Triceps Machine                    ,   12 ,     50 , 1970-01-04 ,       4 
                D11     , Triceps Machine                    ,   12 ,     60 , 1970-01-04 ,       4 
                D11     , Triceps Machine                    ,   12 ,     60 , 1970-01-04 ,       4 
                R02     , Shoulder Pull Up                   ,   10 ,     bw , 1970-01-04 ,       4 
                R02     , Shoulder Pull Up                   ,   10 ,     bw , 1970-01-04 ,       4 
                R02     , Shoulder Pull Up                   ,   10 ,     bw , 1970-01-04 ,       4 
                C05     , Multi press                        ,   12 ,      5 , 1970-01-05 ,       5 
                C05     , Multi press                        ,    8 ,     10 , 1970-01-05 ,       5 
                C05     , Multi press                        ,    8 ,     10 , 1970-01-05 ,       5 
                C06     , Croci man panca alta               ,    8 ,     20 , 1970-01-05 ,       5 
                C06     , Croci man panca alta               ,   10 ,     20 , 1970-01-05 ,       5 
                C06     , Croci man panca alta               ,   10 ,     20 , 1970-01-05 ,       5 
                C11     , Shoulder raise                     ,    8 ,     10 , 1970-01-05 ,       5 
                C11     , Shoulder raise                     ,    8 ,     10 , 1970-01-05 ,       5 
                C11     , Shoulder raise                     ,    8 ,     10 , 1970-01-05 ,       5 
                F06     , Sollevamento del tronco            ,   12 ,     22 , 1970-01-05 ,       5 
                F06     , Sollevamento del tronco            ,   15 ,     22 , 1970-01-05 ,       5 
                F06     , Sollevamento del tronco            ,   15 ,     22 , 1970-01-05 ,       5 
                F16     , Cable crunch                       ,   15 ,     15 , 1970-01-05 ,       5 
                F16     , Cable crunch                       ,   12 ,     25 , 1970-01-05 ,       5 
                F16     , Cable crunch                       ,   12 ,     25 , 1970-01-05 ,       5 
                F01     , Crunch                             ,   12 ,     bw , 1970-01-05 ,       5 
                F01     , Crunch                             ,   10 ,      5 , 1970-01-05 ,       5 
                F01     , Crunch                             ,   10 ,      5 , 1970-01-05 ,       5 
              '';
              description = "Path to csv file or CSV-style workout date, no header (Machine, Exercise, Reps, Weight, Date, Workout)";
            };

            launchPattern = mkOption {
              type = types.str;
              default = "OnCalendar=Mon,Tue,Wed,Thu,Fri --* 06:00:00";  # Every day at 6 AM
              description = "Systemd calendar time pattern to schedule the daemon.";
            };
          };

          config = mkIf cfg.enable {
            environment.systemPackages = [ cfg.package ];

            environment.etc."workout-db.env".text = concatStringsSep "\n" (
              mapAttrsToList (name: value: "${name}=${escapeShellArg value}") cfg.environmentVariables
              ++ mapAttrsToList (name: value: "${name}=${escapeShellArg value}") cfg.chatBotVariables
              ++ ["WORKOUT_DATA=${builtins.toJSON (parseCSV cfg.workoutData)}"]
            );
            systemd.services.workout-db = {
              description = "Workout DB Telegram Bot Daemon";
              after = [ "network.target" "postgresql.service" ];
              wants = [  "network.target" "postgresql.service" ];
              serviceConfig = {
                ExecStart = ''/bin/sh -c "${cfg.package}/bin/workout-db  > /tmp/workout-db.log 2>&1"'';
                Restart = "always";
                EnvironmentFile = "/etc/workout-db.env";
                Environment = (mapAttrsToList (name: value: "${name}=${value}") cfg.environmentVariables)
                          ++ (mapAttrsToList (name: value: "${name}=${value}") cfg.chatBotVariables)
                          ++ ["WORKOUT_DATA=${builtins.toJSON (parseCSV cfg.workoutData)}"];

                # ✅ Ensures shell-like behavior so variables are available
                PassEnvironment = "TELEGRAM_TOKEN CHAT_ID";
              };
            };

            systemd.timers.workout-db = {
              description = "Schedule Workout DB Bot";
              wantedBy = [ "timers.target" ];
              timerConfig = {
                OnCalendar = cfg.launchPattern;
                Persistent = true;
              };
            };
            services.postgresql = {
              initialScript = pkgs.writeText "init.sql" ''
                CREATE USER ${cfg.environmentVariables.DB_USER} WITH PASSWORD '${cfg.environmentVariables.DB_PASSWORD}';
                CREATE DATABASE ${cfg.environmentVariables.DB_NAME};
                \c ${cfg.environmentVariables.DB_NAME}
                CREATE TABLE workouts (
                  id SERIAL PRIMARY KEY,
                  Machine TEXT,
                  Exercise TEXT,
                  Weight TEXT,
                  Reps INT,
                  Date DATE DEFAULT CURRENT_DATE,
                  Workout INT
                );
                ALTER TABLE workouts OWNER TO ${cfg.environmentVariables.DB_USER};
              '';
            };
          };
        };

      devShells = eachSystem (system: 
      let
        pkgs = nixpkgs.legacyPackages.${system};
        workout_db = self.packages.${system}.default;
        python = workout_db.config.deps.python;
      in {
        default = pkgs.mkShell {
          packages = [
            pkgs.python312
            pkgs.poetry
            pkgs.postgresql
            pkgs.vscodium
            pkgs.gcc13
            pkgs.glibc
            pkgs.zlib
            pkgs.zeromq
          ];

          shellHook = ''
            export PATH=${pkgs.postgresql}/bin:$PATH
            # Fix Library Paths
            export LD_LIBRARY_PATH=${pkgs.gcc.cc.lib}/lib:${pkgs.glibc.out}/lib:$LD_LIBRARY_PATH

            # Ensure Poetry uses the correct virtual environment
            export VIRTUAL_ENV=$PWD/.venv
            export PATH="$VIRTUAL_ENV/bin:$PATH"

            if [ ! -d "$VIRTUAL_ENV" ]; then
                poetry env use $(which python)
                poetry install
            fi
          '';
        };

        fhs = pkgs.buildFHSUserEnv {
          name = "python-fhs";
          targetPkgs = pkgs: with pkgs; [
            python312
            poetry
            postgresql
            vscodium
            gcc
            glibc
            zlib
            zeromq
          ];
          runScript = "bash";
        };
      }); 
      nixosConfigurations.container = nixpkgs.lib.nixosSystem {
        system = "x86_64-linux";
        modules = [
          sops-nix.nixosModules.sops
          self.nixosModules.default
          ({pkgs, config, ...}: {
            boot.isContainer = true;
            networking.hostName = "test";
            services.postgresql.enable = true;

            sops = {
              defaultSopsFile = ./secrets.yaml;
              age.sshKeyPaths = ["/etc/ssh/ssh_host_ed25519_key"];
              secrets = {
                telegram-token = { };
                telegram-chat-id = { };
              };
            };
            environment.etc."workout-db.env".text = ''
              TELEGRAM_TOKEN=$(cat ${config.sops.secrets.telegram-token.path})
              CHAT_ID=$(cat ${config.sops.secrets.telegram-chat-id.path})
            '';

            services.workout-db = {
              enable = true;
              chatBotVariables = {
                TELEGRAM_TOKEN = "$(cat /etc/workout-db.env | grep TELEGRAM_TOKEN | cut -d '=' -f2)";
                CHAT_ID = "$(cat /etc/workout-db.env | grep CHAT_ID | cut -d '=' -f2)";
              };
              launchPattern = "* *-*-* *:*:*";
            };
 
            environment.systemPackages = [
              self.packages.x86_64-linux.default
              pkgs.python312
            ];
          })
        ];
      };
    };
}


