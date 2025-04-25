# Modification of uv2nix Hello World flake found at https://pyproject-nix.github.io/uv2nix/usage/hello-world.html

{
  description = "Impure Manim flake using uv2nix";

  inputs = {
    nixpkgs.url = "nixpkgs";

    flake-utils.url = "github:numtide/flake-utils";

    pyproject-nix = {
      url = "github:pyproject-nix/pyproject.nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    uv2nix = {
      url = "github:pyproject-nix/uv2nix";
      inputs.pyproject-nix.follows = "pyproject-nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    pyproject-build-systems = {
      url = "github:pyproject-nix/build-system-pkgs";
      inputs.pyproject-nix.follows = "pyproject-nix";
      inputs.uv2nix.follows = "uv2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs =
    {
      self,
      nixpkgs,
      flake-utils,
      
      uv2nix,
      pyproject-nix,
      pyproject-build-systems,
      ...
    }: flake-utils.lib.eachDefaultSystem(
      system:
      let
        inherit (nixpkgs) lib;

        # Load a uv workspace from a workspace root.
        # Uv2nix treats all uv projects as workspace projects.
        workspace = uv2nix.lib.workspace.loadWorkspace { workspaceRoot = ./.; };

        # Create package overlay from workspace.
        overlay = workspace.mkPyprojectOverlay {
          # Prefer prebuilt binary wheels as a package source.
          # Sdists are less likely to "just work" because of the metadata missing from uv.lock.
          # Binary wheels are more likely to, but may still require overrides for library dependencies.
          sourcePreference = "wheel"; # or sourcePreference = "sdist";
          # Optionally customise PEP 508 environment
          # environ = {
          #   platform_release = "5.10.65";
          # };
        };

        # Extend generated overlay with build fixups
        #
        # Uv2nix can only work with what it has, and uv.lock is missing essential metadata to perform some builds.
        # This is an additional overlay implementing build fixups.
        # See:
        # - https://pyproject-nix.github.io/uv2nix/FAQ.html
        pyprojectOverrides = _final: _prev: {
          # Implement build fixups here.
          # Note that uv2nix is _not_ using Nixpkgs buildPythonPackage.
          # It's using https://pyproject-nix.github.io/pyproject.nix/build.html
        };

        pkgs = nixpkgs.legacyPackages.${system};

        # Use Python 3.12 from nixpkgs
        python = pkgs.python312; # .withPackages (ps: with ps; [
        #   python-lsp-server 
        # ]);

        # Construct package set
        pythonSet =
          # Use base package set from pyproject.nix builders
          (pkgs.callPackage pyproject-nix.build.packages {
            inherit python;
          }).overrideScope
            (
              lib.composeManyExtensions [
                pyproject-build-systems.overlays.default
                overlay
                pyprojectOverrides
              ]
            );

        tex = (pkgs.texlive.combine {
          inherit (pkgs.texlive) scheme-basic
            amsmath babel-english cbfonts-fd cm-super count1to ctex doublestroke dvisvgm everysel
            fontspec frcursive fundus-calligra gnu-freefont jknapltx latex-bin
            mathastext microtype multitoc physics preview prelim2e ragged2e relsize rsfs
            setspace standalone tipa wasy wasysym xcolor xetex xkeyval;
        });

      in
      {
        # Package a virtual environment as our main application.
        #
        # Enable no optional dependencies for production build.
        packages.${system}.default = pythonSet.mkVirtualEnv "hello-world-env" workspace.deps.default;

        # Make hello runnable with `nix run`
        apps.${system} = {
          default = {
            type = "app";
            program = "${self.packages.${system}.default}/bin/hello";
          };
        };

        # This example provides two different modes of development:
        # - Impurely using uv to manage virtual environments
        # - Pure development using uv2nix to manage virtual environments
        devShells.default = 
          # It is of course perfectly OK to keep using an impure virtualenv workflow and only use uv2nix to build packages.
          # This devShell simply adds Python and undoes the dependency leakage done by Nixpkgs Python infrastructure.
          pkgs.mkShell {
            packages = [
              python
              pkgs.ruff
              pkgs.basedpyright
              
              pkgs.uv
              pkgs.pkg-config
              pkgs.cairo
              pkgs.ffmpeg
              tex
            ];
            env =
              {
                # Prevent uv from managing Python downloads
                UV_PYTHON_DOWNLOADS = "never";
                # Force uv to use nixpkgs Python interpreter
                UV_PYTHON = python.interpreter;
              }
              // lib.optionalAttrs pkgs.stdenv.isLinux {
                # Python libraries often load native shared objects using dlopen(3).
                # Setting LD_LIBRARY_PATH makes the dynamic library loader aware of libraries without using RPATH for lookup.
                LD_LIBRARY_PATH = lib.makeLibraryPath pkgs.pythonManylinuxPackages.manylinux1;
              };
            shellHook = ''
              unset PYTHONPATH
            '';
          };

      });
}
