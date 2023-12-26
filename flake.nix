{
  description = "AOC 2023";
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-23.11";
  inputs.flake-utils.url = "github:numtide/flake-utils";

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
      in
      {
        devShells.default = pkgs.mkShell {
          packages = with pkgs; [
            llvmPackages_6.libcxxabi
            (python311.withPackages (ps: with ps; [
              pip
              python-lsp-server
              python-lsp-black
              pylsp-mypy
              pylsp-rope
              python-lsp-ruff
              ujson
              isort

              more-itertools
              sympy
              networkx
            ]))

            pypy310
          ];
        };
      });
}
