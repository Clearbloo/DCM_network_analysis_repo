{
  description = "Default dev flake";

  # Nixpkgs / NixOS version to use.
  inputs.nixpkgs.url = "nixpkgs/nixos-24.05";

  outputs = { nixpkgs, ... }:
    let
      # System types to support.
      supportedSystems =
        [ "x86_64-linux" "x86_64-darwin" "aarch64-linux" "aarch64-darwin" ];
      # Helper function to generate an attrset '{ x86_64-linux = f "x86_64-linux"; ... }'.
      forAllSystems = nixpkgs.lib.genAttrs supportedSystems;
      # nixpkgs.config.allowUnfree = true;

    in {
      devShells = forAllSystems (system:
        let
          pkgs = import nixpkgs {
            inherit system;
            config.allowUnfree = true;
          };
          pyblio = with pkgs.python310Packages;
            buildPythonPackage rec {
              pname = "pybliometrics";
              version = "3.1.0";
              pyproject = true;
              src = fetchPypi {
                inherit pname version;
                sha256 = "sha256-qWcJX7Obandn0ZM9WRACbnKyn+0BQqFtIktLwtEBHIY=";
              };
              propagatedBuildInputs = [ requests tqdm urllib3 pbr simplejson ];
              nativeBuildInputs = [ setuptools setuptools-scm ];
              doCheck = true;
            };

          R-with-packages = with pkgs;
            rWrapper.override {
              packages = with rPackages; [
                readr
                dplyr
                ggplot2
                stringr
                tibble
                plyr
                igraph
                tidygraph
                ggraph
                visNetwork
                languageserver
              ];
            };

        in {
          default = pkgs.mkShell {
            buildInputs = [
              R-with-packages
              pkgs.vscode
              pkgs.vscode-extensions.reditorsupport.r

              (pkgs.python310.withPackages
                (ps: [ ps.pandas ps.simplejson pyblio ps.pip ]))
              pkgs.ruff
            ];
            env.LD_LIBRARY_PATH =
              pkgs.lib.makeLibraryPath [ pkgs.stdenv.cc.cc.lib pkgs.libz ];
          };
        });
    };
}
