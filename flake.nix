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
              version = "4.3";
              pyproject = true;
              src = fetchPypi {
                inherit pname version;
                sha256 = "sha256-R78B5Cnq1UL0a94pZfEIqZUON4PiyCOziWs1H7z7kCg=";
              };
              propagatedBuildInputs = [ requests tqdm urllib3 ];
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

              (pkgs.python310.withPackages (ps: [ ps.pandas pyblio ]))
              pkgs.ruff

            ];
            env.LD_LIBRARY_PATH =
              pkgs.lib.makeLibraryPath [ pkgs.stdenv.cc.cc.lib pkgs.libz ];
          };
        });
    };
}
