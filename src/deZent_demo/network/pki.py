
from deZent_demo.utils.sys import run, sys_file_exists
from deZent_demo.network.net_stack import IPAddr


class Certificate():
    suite: str = "rsa"
    width: int = 2048

    def __init__(self, name: str, ip: IPAddr, cn: str = "local", ttl_days: int = 365) -> None:
        self.cert_file: str = f"{name}.cert.pem"
        self.key_file: str = f"{name}.key.pem"
        self.ip: IPAddr = ip
        self.cn: str = cn
        self.ttl_days = ttl_days

    def exists(self) -> bool:
        return sys_file_exists(self.cert_file) and sys_file_exists(self.key_file)
    
    def create(self) -> bool:
        if self.exists():
            return True
        run([
            "openssl", "req", "-x509", "-newkey",
            f"{Certificate.suite}:{Certificate.width}", "-nodes",
            "-keyout", f"{self.key_file}",
            "-out", f"{self.cert_file}",
            "-days", f"{self.ttl_days}",
            "-subj", f"/CN={self.cn}",
            "-addext", f"subjectAltName=DNS:{self.cn},IP: {self.ip}"
        ])
        return self.exists()
    
# TODO: smallstep + ACME -> CA, dist, and certbot