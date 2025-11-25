# This flake setup the dev environment for working with textX docs.
# Install nix (https://nixos.org/download/).
#
# Be sure to configure flake feature by adding:
# experimental-features = nix-command flakes
# to ~/.config/nix/nix.conf
# See more here: https://nixos.wiki/wiki/flakes

# Now, run:
#
# nix develop

# A shell prompt with installed dependencies will be run. To serve the docs locally use:

# mdbook serve
{
  description = "A flake for textX docs shell";
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs?ref=24.11";
    flake-utils.url = "github:numtide/flake-utils";
		mdbook-theme = {
			url = "github:zjp-CN/mdbook-theme?ref=v0.1.5";
			flake = false;
		};
    mdbook-bib = {
			url = "github:francisco-perez-sorrosal/mdbook-bib?ref=v0.0.6";
			flake = false;
    };
  };
  outputs = { self, nixpkgs, flake-utils, mdbook-theme, mdbook-bib, ... }@inputs:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};

        mdbook-theme-pkg = pkgs.rustPlatform.buildRustPackage {
          pname = "mdbook-theme";
          version = "0.1.5";
          cargoLock.lockFile = mdbook-theme.outPath + "/Cargo.lock";
          src = mdbook-theme;
        };

        mdbook-bib-pkg = pkgs.rustPlatform.buildRustPackage {
          pname = "mdbook-bib";
          version = "0.0.6";
          cargoLock.lockFile = mdbook-bib.outPath + "/Cargo.lock";
          src = mdbook-bib;

          # Required build inputs
          nativeBuildInputs = with pkgs; [
            pkg-config
            openssl
          ];

          buildInputs = with pkgs; [
            openssl
          ];

          # Environment variables for OpenSSL
          OPENSSL_DIR = "${pkgs.openssl.dev}";
          OPENSSL_LIB_DIR = "${pkgs.openssl.out}/lib";
          PKG_CONFIG_PATH = "${pkgs.openssl.dev}/lib/pkgconfig";


        };

      in {
        devShells.default = pkgs.mkShell {
          name = "textx-docs";

          buildInputs = with pkgs; [
            mdbook
            mdbook-theme-pkg
            mdbook-admonish
            mdbook-linkcheck
            mdbook-bib-pkg
          ];
        };
      });
}
