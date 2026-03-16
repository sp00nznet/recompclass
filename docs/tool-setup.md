# Tool Setup and Environment Prerequisites

This guide covers everything you need installed and configured before starting the labs. The course targets a workflow where you write recompiler tooling in Python and compile generated C code with a standard C compiler.

---

## Required Tools

### C Compiler (GCC, Clang, or MSVC)

A C11-capable compiler is needed to compile the C code that our recompiler generates.

- **Windows**: Install Visual Studio 2022 (Community edition is free) with the "Desktop development with C++" workload. Alternatively, install MSYS2 and use its GCC toolchain.
- **Linux**: Install GCC via your package manager (`sudo apt install build-essential` on Debian/Ubuntu, `sudo dnf install gcc` on Fedora).
- **macOS**: Install Xcode Command Line Tools (`xcode-select --install`), which provides Apple Clang.

Official docs:
- GCC: gcc.gnu.org
- Clang: clang.llvm.org
- MSVC: learn.microsoft.com/en-us/cpp

### Python 3.8+

Python is used for the recompiler scripts, disassembly tooling, and analysis utilities.

- **Windows**: Download from python.org. Check "Add Python to PATH" during installation.
- **Linux**: Usually pre-installed. If not, `sudo apt install python3 python3-pip`.
- **macOS**: Install via Homebrew (`brew install python3`) or download from python.org.

### Git

Version control is required to clone course repos and track your work.

- **Windows**: Download from git-scm.com or use the Git that ships with MSYS2.
- **Linux**: `sudo apt install git`
- **macOS**: Included with Xcode Command Line Tools, or install via Homebrew.

### Make or CMake

Build automation for compiling generated C projects.

- **Make**: Included on Linux/macOS. On Windows, available through MSYS2 or as part of the Visual Studio tools (`nmake`).
- **CMake**: Download from cmake.org. Version 3.16+ recommended.

---

## Recommended Tools

### Ghidra

Ghidra is an open-source reverse engineering suite from the NSA. We use it for binary analysis, cross-referencing our recompiler's output, and investigating function boundaries.

- Download from ghidra-sre.org (requires JDK 17+).
- No installation needed; extract and run.

### Capstone Disassembly Framework

Capstone is the disassembly engine we use in our Python-based recompiler tooling. It supports many architectures (MIPS, PowerPC, x86, ARM, and more) with a clean Python API.

- Install the Python bindings: `pip install capstone`
- Official docs: capstone-engine.org

### Hex Editor

A hex editor is invaluable for inspecting binary file headers, verifying byte order, and debugging recompiler output.

- **HxD** (Windows, free): mh-nexus.de/en/hxd
- **xxd** (Linux/macOS): included with most systems
- **ImHex** (cross-platform, free): available on GitHub

---

## Python Packages

Install the required Python packages:

```
pip install capstone pefile
```

Summary of packages used in the course:

| Package    | Source  | Purpose                                       |
|------------|---------|-----------------------------------------------|
| `capstone` | PyPI    | Multi-architecture disassembly engine          |
| `pefile`   | PyPI    | Parsing PE/XBE executable headers and sections |
| `struct`   | stdlib  | Packing/unpacking binary data (built-in)       |
| `os`       | stdlib  | File and path operations (built-in)            |
| `argparse` | stdlib  | Command-line argument parsing (built-in)       |

No need to install `struct`, `os`, or `argparse` -- they ship with Python.

---

## Platform Notes

### Windows

- If using MSVC, run commands from a "Developer Command Prompt" or "Developer PowerShell" so that `cl.exe` is on your PATH.
- If using MSYS2/MinGW, use the MINGW64 shell for a Unix-like experience with `gcc`, `make`, and standard Unix tools.
- Python from the Microsoft Store can sometimes cause PATH issues. Prefer the python.org installer.

### Linux

- Most distributions ship with everything you need or make it available through the package manager.
- Ensure `python3` and `pip3` are available (some distros separate them into different packages).

### macOS

- Apple Clang works for all labs. You do not need to install upstream LLVM/Clang unless you want to.
- Homebrew is the easiest way to install any missing tools: brew.sh

---

## Verifying Your Setup

Run the following commands to confirm your environment is ready. Each should print a version number without errors.

```bash
# C compiler (use whichever you installed)
gcc --version        # or: clang --version / cl

# Python
python3 --version    # or: python --version (Windows)

# Git
git --version

# Make / CMake
make --version       # or: cmake --version

# Capstone Python bindings
python3 -c "import capstone; print(capstone.cs_version())"

# pefile
python3 -c "import pefile; print('pefile OK')"
```

If any command fails, revisit the installation steps for that tool above.

---

## Optional: Docker Container for Lab Environment

If you prefer a reproducible, pre-configured environment (or want to avoid installing tools globally), a Docker-based setup is available.

### Building the image

Create a file named `Dockerfile` in the course root with the following content:

```dockerfile
FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install capstone pefile

WORKDIR /recompclass
```

Build and run:

```bash
docker build -t recompclass .
docker run -it -v $(pwd):/recompclass recompclass
```

This mounts your local course directory into the container so you can edit files on your host and compile/run inside the container.

### Notes on Docker usage

- Ghidra is not included in the Docker image (it requires a GUI). Run Ghidra on your host machine.
- The container uses GCC on Linux. Generated C code may need minor adjustments if you normally develop on Windows with MSVC.
- You can extend the Dockerfile to add additional architectures' cross-compilers if needed for later labs.
