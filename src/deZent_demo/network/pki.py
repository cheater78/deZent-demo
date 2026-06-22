from pathlib import Path

from deZent_demo.network.address import NetAddr
from deZent_demo.utils.sys import run, run_unsafe, sys_rmdir_r, PtyProcess, ExpectRule

def __step_cli_cmd__() -> str:
    step_cli_cmds: list[str] = [ "step", "step-cli" ]
    
    for step_cli_cmd in step_cli_cmds:
        if run_unsafe(["which", step_cli_cmd], check=False, debug=False):
            return step_cli_cmd
    raise RuntimeError(f"Any cmd of {step_cli_cmds} wasnt found!")

class Certificate:

    def __init__(self,
                 name: str,
                 cert_file: str | None = None,
                 key_file: str | None = None):
        self.name: str = name
        self.cert_file: str = cert_file if cert_file else f"{self.name}.crt"
        self.key_file: str = key_file if key_file else f"{self.name}.key"

    def exists(self) -> bool:
        return Path(self.cert_file).exists() and Path(self.key_file).exists()

    def delete(self):
        Path(self.cert_file).unlink(missing_ok=True)
        Path(self.key_file).unlink(missing_ok=True)

    def fingerprint(self) -> str:
        return run([__step_cli_cmd__(), "certificate", "fingerprint", self.cert_file])[0]

default_cert_server_host: NetAddr = NetAddr("10.0.0.1", 9001)
default_cert_server_name: str = "deZent-ca"
default_cert_server_provisioner: str = "deZent-tofu"
default_cert_server_passwd: str = "deZentlyStrongPassword" # NOTE: this is a demo, calm breaths
default_cert_server_path: Path = Path("./cert/ca/")

class CertServer:

    def __init__(
        self,
        name: str = default_cert_server_name,
        host: NetAddr = default_cert_server_host,
        provisioner: str = default_cert_server_provisioner,
        path: Path = default_cert_server_path
    ):
        self.name = name
        self.host = host
        self.provisioner = provisioner
        self.path = path
        self.passwd_file: Path = self.__create_passwd_file__()

    @property
    def url(self) -> str:
        return f"https://{self.host.ip}:{self.host.port}"

    def init(self) -> None:
        if self.exists():
            self.fini()
        run([
            __step_cli_cmd__(), "ca", "init",
            "--name", self.name,
            "--address", f"{self.host.ip}:{self.host.port}",
            "--dns", self.host.ip,
            "--password-file", str(self.passwd_file),
            "--provisioner", self.provisioner,
            "--deployment-type=standalone"
        ], env=self.__cmd_env__())

    def fini(self) -> None:
        sys_rmdir_r(self.__step_path__())

    def exists(self) -> bool:
        return self.__get_config_file__().exists()

    def start(self):
        if not self.exists():
            self.init()
        print(f"Root fingerprint: {self.fingerprint()}")
        config_file: Path = self.__get_config_file__()
        with open(self.passwd_file, "r") as f:
            passwd = f.readline()

        proc = PtyProcess([f"step-ca", str(config_file) ])
        proc.start()

        def printer(data: str) -> None:
            print(data, end="")

        rules = [
            ExpectRule(
                pattern="Please enter the password to decrypt ",
                action=lambda p: p.write(passwd + "\n\r") # type: ignore
            ),
        ]

        try:
            code = proc.read_loop(printer, rules)
            return code
        finally:
            proc.close()

    def fingerprint(self) -> str:
        root_cert_file: Path = self.__step_path__() / "certs" / "root_ca.crt"
        return run([
            __step_cli_cmd__(), "certificate",
            "fingerprint", str(root_cert_file)
        ], env=self.__cmd_env__())[0]

    def __cmd_env__(self) -> dict[str, str]:
        return {
            "STEPPATH": str(self.path.resolve()),
        }
    
    def __step_path__(self) -> Path:
        path_str: str = run([ __step_cli_cmd__(), "path" ], debug=False, env=self.__cmd_env__())[0]
        return Path(path_str).resolve()
    
    def __create_passwd_file__(self) -> Path:
        step_path: Path = self.__step_path__()
        passwd_file: Path = step_path / "passwd.txt"

        passwd_file.parent.mkdir(parents=True, exist_ok=True)
        with open(passwd_file, "w") as f:
            f.write(default_cert_server_passwd)
        run([ "chmod", "600", str(passwd_file) ], env=self.__cmd_env__())
        return passwd_file
    
    def __get_config_file__(self) -> Path:
        config_file: Path = self.__step_path__() / "config" / "ca.json"
        return config_file


default_cert_client_path: Path = Path("./cert/")

class CertClient:

    def __init__(
        self,
        node_id: str,
        fingerprint: str,
        ca: NetAddr = default_cert_server_host,
        provisioner: str = default_cert_server_provisioner,
        path: Path = default_cert_client_path):
        self.node_id = node_id
        self.ca = ca
        self.fingerprint = fingerprint
        self.provisioner = provisioner
        self.path: Path = path if path != default_cert_client_path else default_cert_client_path / f"{node_id}"

        self.cert = Certificate(self.node_id)

    def bootstrap(self):
        if self.path.exists():
            sys_rmdir_r(self.path)
        run([
            __step_cli_cmd__(), "ca", "bootstrap",
            "--ca-url", f"{self.ca.ip}:{self.ca.port}",
            "--fingerprint", self.fingerprint,
        ], env=self.__cmd_env__())
    
    def enroll(self):
        """
        Node proves possession of private key
        and gets CA-signed cert.
        """

        with open(default_cert_server_path / "passwd.txt", "r") as f:
            passwd = f.readline()

        proc = PtyProcess([
            __step_cli_cmd__(), "ca", "certificate",
            self.node_id,
            self.cert.cert_file,
            self.cert.key_file,
            "--provisioner", self.provisioner,
        ], env=self.__cmd_env__())
        proc.start()

        def printer(data: str) -> None:
            print(data, end="")

        rules = [
            ExpectRule(
                pattern="Please enter the password to decrypt the provisioner key: ",
                action=lambda p: p.write(passwd + "\n\r") # type: ignore
            ),
        ]

        try:
            code = proc.read_loop(printer, rules)
            return code
        finally:
            proc.close()

    def renew(self):
        if not self.cert.exists():
            self.enroll()
            return
        proc = PtyProcess([
            __step_cli_cmd__(), "ca", "renew",
            self.cert.cert_file,
            self.cert.key_file,
        ], env=self.__cmd_env__())
        proc.start()

        def printer(data: str) -> None:
            print(data, end="")
        
        try:
            code = proc.read_loop(printer)
            return code
        finally:
            proc.close()

    def ensure_cert(self):
        """
        Called at node startup + periodically.
        """

        if not Path(self.cert.cert_file).exists():
            self.enroll()
        else:
            self.renew()

    def tls_paths(self):
        return self.cert.cert_file, self.cert.key_file
    
    def __cmd_env__(self) -> dict[str, str]:
        return {
            "STEPPATH": str(self.path.resolve()),
        }