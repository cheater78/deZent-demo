#!/usr/bin/env python3
from __future__ import annotations
import platform
import os
import pty
import selectors
import re
from pathlib import Path
import subprocess
from time import sleep
import shutil
from dataclasses import dataclass
from typing import Callable, Sequence

IPAddr = str

def run_unsafe(cmd: list[str], check: bool = True, debug: bool = True, env: dict[str, str] = {}, input: str = "") -> list[str] | None:
    if debug:
        print(">", " ".join(cmd))
    curr_env: dict[str, str] = os.environ.copy()
    curr_env |= env
    result = subprocess.run(cmd, check=check, input=input, capture_output=True, text=True, env=curr_env)
    if result.returncode != 0:
        return None
    return [str(line) for line in result.stdout.splitlines()]

def run(cmd: list[str], check: bool = True, debug: bool = True, env: dict[str, str] = {}, input: str = "") -> list[str]:
    result: list[str] | None = run_unsafe(cmd, check, debug, env, input)
    if result is None:
        raise RuntimeError(f"Failed to run> {" ".join(cmd)}: Returned non zero exit code!")
    return result

terminal_run: dict[str, list[str]] = {
    "debian": ["gnome-terminal", "--"],
    "arch": ["konsole", "-e"],
}

def run_in_term(cmd: list[str], debug: bool = True) -> None:
    if debug:
        print("TERM>", " ".join(cmd))
    os_flavor: str = sys_distro_flavor()
    if not os_flavor in terminal_run.keys():
        raise RuntimeError(f"Terminal for distro {sys_distro_flavor()} is not defined!")
    full_cmd: list[str] = terminal_run[os_flavor] + ["bash", "-c"] + [" ".join(cmd) + "; exec bash"]
    subprocess.Popen(full_cmd)

def sys_is_root() -> bool:
    return os.geteuid() == 0

def sys_ensure_root() -> None:
    if not sys_is_root():
        raise RuntimeError("This script must be run as root.")

def sys_ensure_linux() -> None:
    if platform.system() != "Linux":
        raise RuntimeError("This script only works on Linux.")

def sys_distro_info() -> dict[str, str]:
    os_release_path: Path = Path("/etc/os-release")
    if not os_release_path.exists():
        raise RuntimeError("/etc/os-release not found; cannot detect distro.")

    os_release: dict[str, str] = {}
    with os_release_path.open("r") as f:
        for line in f:
            line = line.strip()
            if "=" not in line or line.startswith("#"):
                continue
            key, val = line.split("=", 1)
            os_release[key] = val.strip().strip('"') # remove optional quotes
    
    return os_release

def sys_distro_flavor() -> str:
    os_release: dict[str, str] = sys_distro_info()
    id: str = os_release.get("ID", "").lower()
    id_like: str = os_release.get("ID_LIKE", "").lower()

    return id if not id_like else id_like

def sys_pkg_mngr_inst_cmd() -> list[str]:
    sys_pkg_mngr_map: dict[str, list[str]] = {
        "arch": ["pacman", "-S", "--noconfirm", "--needed"],
        "debian": ["apt", "install", "-y"]
    }

    os_flavor: str = sys_distro_flavor()
    sys_pkg_mngr: list[str] | None = sys_pkg_mngr_map.get(os_flavor)
    
    if not sys_pkg_mngr:
        raise RuntimeError(f"Distro: {os_flavor} is not supported!")

    return sys_pkg_mngr

def sys_pkg_mngr_check_lock() -> bool:
    sys_pkg_mngr_locks: dict[str, list[str]] = {
        "arch": ["/var/lib/pacman/db.lck"],
        "debian": ["/var/lib/dpkg/lock", "/var/lib/dpkg/lock-frontend", "/var/cache/apt/archives/lock"],
    }

    os_flavor: str = sys_distro_flavor()
    sys_pkg_mngr_lock: list[str] | None = sys_pkg_mngr_locks.get(os_flavor)
    
    if not sys_pkg_mngr_lock:
        raise RuntimeError(f"Distro: {os_flavor} is not supported!")

    for lock in sys_pkg_mngr_lock:
        if sys_file_exists(lock):
            return False
    return True

def sys_pkg_mngr_check_package_installed(pkg: str) -> bool:
    sys_pkg_mngr_check: dict[str, list[str]] = {
        "arch": ["pacman", "-Q"],
        "debian": ["dpkg", "-s"],
    }
    os_flavor: str = sys_distro_flavor()
    check: list[str] | None = sys_pkg_mngr_check.get(os_flavor)
    if not check:
        raise RuntimeError(f"Distro: {os_flavor} is not supported!")
    result: list[str] | None = run_unsafe(check + [pkg], check=False)
    return result != None

def sys_install(pkgs: dict[str, list[str]], force: bool = False) -> None:
    # determine cmd to run the install
    os_flavor: str = sys_distro_flavor()
    if not os_flavor in pkgs.keys():
        raise RuntimeError(f"Packages for distro {sys_distro_flavor()} were not provided!")
    run_install: list[str] = ([] if sys_is_root() else ["sudo"]) + sys_pkg_mngr_inst_cmd()
    # select packages needed
    new_pkgs: list[str] = []
    if not force:
        for pkg in pkgs[os_flavor]:
            if not sys_pkg_mngr_check_package_installed(pkg):
                new_pkgs.append(pkg)
    else:
        new_pkgs = pkgs[os_flavor]
    if not new_pkgs:
        print(f"packages: {pkgs[os_flavor]} already installed!")
        return
    install_cmd: list[str] = run_install + new_pkgs
    # wait for pkg mng locks
    while not sys_pkg_mngr_check_lock(): # TODO: doesnt work -> still a race condition
        sleep(1)
        print(f"Package Manager busy! ({" ".join(install_cmd)})")
    run(install_cmd)

def sys_netns_exists(netns: str) -> bool:
    try:
        lines: list[str] | None = run_unsafe(["ip", "netns", "list"], debug=False)
        if not lines:
            return False
        namespaces: list[str] = [line.split()[0] for line in lines]
        return netns in namespaces
    except subprocess.CalledProcessError:
        return False
    
def sys_iface_exists(ifname: str, netns: str = ""):
    try:
        run(
            (["ip", "netns", "exec", netns] if netns else []) +
            ["ip", "link", "show", ifname],
            debug=False
        )
        return True
    except subprocess.CalledProcessError:
        return False

def sys_if_ip_addr(ifname: str) -> IPAddr | None:
    pattern = re.compile(r'\binet\s+(\d+\.\d+\.\d+\.\d+)/')

    result: list[str] = run([ "ip", "addr", "show", ifname ], debug=False)
    for line in result:
        match = pattern.search(line)
        if match:
            return match.group(1)
    return None

def sys_file_exists(file: str) -> bool:
    return Path(file).is_file()

def sys_rmdir_r(path: Path) -> bool:
    if path.exists():
        shutil.rmtree(path)
        return True
    return False

def keepalive() -> None:
    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        pass



@dataclass(frozen=True)
class ExpectRule:
    pattern: str
    action: Callable[[PtyProcess], None]

class PtyProcess:
    def __init__(self, cmd: Sequence[str], env: dict[str, str] = {}) -> None:
        self.cmd = cmd
        self.master_fd: int | None = None
        self.slave_fd: int | None = None
        self.proc: subprocess.Popen[bytes] | None = None
        self.env = env

    def start(self) -> None:
        master_fd, slave_fd = pty.openpty()
        self.master_fd = master_fd
        self.slave_fd = slave_fd

        env = os.environ.copy()
        env |= self.env

        self.proc = subprocess.Popen(
            self.cmd,
            stdin=slave_fd,
            stdout=slave_fd,
            stderr=slave_fd,
            close_fds=True,
            env=env
        )

        os.close(slave_fd)

    def write(self, data: str) -> None:
        if self.master_fd is None:
            raise RuntimeError("PTY not started")
        os.write(self.master_fd, data.encode())

    def read_loop(
        self,
        on_output: Callable[[str], None] | None = None,
        rules: list[ExpectRule] | None = None
    ) -> int:
        if self.master_fd is None or self.proc is None:
            raise RuntimeError("PTY not started")

        sel = selectors.DefaultSelector()
        sel.register(self.master_fd, selectors.EVENT_READ)

        buffer = ""

        while True:
            if self.proc.poll() is not None:
                break

            events = sel.select(timeout=0.1)

            for _, _ in events:
                data = os.read(self.master_fd, 1024).decode(errors="ignore")
                if not data:
                    continue
                if on_output:
                    on_output(data)

                buffer += data
                
                if not rules:
                    continue
                for rule in rules:
                    if rule.pattern.lower() in buffer.lower():
                        rule.action(self)
                        buffer = ""

        return self.proc.wait()

    def close(self) -> None:
        if self.master_fd is not None:
            try:
                os.close(self.master_fd)
            except OSError:
                pass
