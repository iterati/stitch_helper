import subprocess
import sys

from stitch_helper import aws


SERVICES = {
    "app": {
        "windows": [
            ["watch", ["make docker_logs"]],
        ],
    },
    "connections": {
        "code_dir": "connections-service",
        "layer_name": "connection_service",
        "nrepl": 4003,
        "cider_version": "0.18.0",
        "windows": [
            ["service", ["make docker_logs"]],
            ["db", ["make docker_mysql_shell"]],
        ],
    },
    "core": {
        "code_dir": "core-services",
        "layer_name": "core_service",
        "nrepl": 4009,
        "cider_version": "0.17.0",
        "windows": [
            ["service", ["make docker_logs"]],
            ["db", ["make docker_mysql"]],
        ],
    },
    "gate": {
        "code_dir": "pipeline-gate",
        "layer_name": "gate",
        "nrepl": 4010,
        "cider_version": "0.18.0",
        "windows": [
            ["service", ["make docker_logs"]],
        ],
    },
    "menagerie": {
        "nrepl": 4033,
        "cider_version": "0.18.0",
        "windows": [
            ["service", ["make docker_logs"]],
            ["db", ["export $(cat menagerie.docker.env | xargs)", "make docker_psql"]],
        ],
    },
    "notifications": {
        "code_dir": "notification-service",
        "layer_name": "notification_service",
        "nrepl": 4017,
        "cider_version": "0.18.0",
        "windows": [
            ["service", ["make docker_logs"]],
            ["db", ["make docker_mysql"]],
        ],
    },
    "reckoner": {
        "nrepl": 4036,
        "cider_version": "0.26.0",
        "windows": [
            ["service", ["make docker_logs"]],
        ],
    },
    "scheduler": {
        "nrepl": 4039,
        "cider_version": "0.18.0",
        "windows": [
            ["service", ["make docker_logs"]],
            ["db", ["export $(cat scheduler.docker.env | xargs)", "make docker_psql"]],
        ],
    },
    "spool": {
        "code_dir": "spool-service",
        "layer_name": "spool_service",
        "nrepl": 4032,
        "cider_version": "0.18.0",
        "windows": [
            ["service", ["make docker_logs"]],
            ["db", ["export $(cat spool-service.docker.env | xargs)", "make docker_psql"]],
        ],
    },
    "stats": {
        "code_dir": "stats-service",
        "layer_name": "stats_service",
        "nrepl": 4014,
        "cider_version": "0.18.0",
        "windows": [
            ["service", ["make docker_logs"]],
            ["db", ["export $(cat stats-service.docker.env | xargs)", "make docker_psql"]],
        ],
    },
    "streamery": {
        "code_dir": "pipeline-streamery",
        "nrepl": 4019,
        "cider_version": "0.18.0",
        "windows": [
            ["service", ["make docker_logs"]],
        ],
    },

    "loader-bigquery": {
        "layer_name": "loader_bigquery",
    },
    "loader-bq": {
        "layer_name": "loader_bq",
    },
    "loader-delta": {
        "layer_name" "loader_delta",
    },
    "loader-pg": {
        "layer_name" "loader_pg",
    },
    "loader-s3": {
        "layer_name" "loader_s3",
    },
    "loader-snow": {
        "nrepl": 4035,
        "layer_name": "loader_snow",
        "cider_version": "0.18.0",
        "windows": [
            ["service", ["make docker_logs"]],
            ["db", ["cd /opt/code/spool-service && make docker_psql"]],
        ],
    },
    "loader-sqldw": {
        "layer_name" "loader_sqldw",
    },
    "loader-x": {
        "layer_name" "loader_x",
    },
}


class Service:
    def __init__(self, name, code_dir=None, layer_name=None, nrepl=None, windows=None, cider_version="0.18.0"):
        self.name = name
        self.code_dir = code_dir or name
        self.layer_name = layer_name or name
        self.nrepl = nrepl
        self.windows = windows or []
        self.cider_version = cider_version
        self.layer = None

    @property
    def pwd(self):
        return "/opt/code/{}".format(self.code_dir)

    def get_instances(self):
        if not self.layer_name:
            raise Exception("{} does not have a layer_name".format(self.name))

        if not self.layer:
            layers = aws.get_all_layers()
            if self.layer_name not in layers:
                raise Exception("Missing layer %s".format(self.layer_name))

            self.layer = layers[self.layer_name]

        return aws.get_layer_instances(self.layer['LayerId'])

    def list(self):
        print("\n".join("ssh {PrivateIp:15} # {Hostname}".format(**i) for i in self.get_instances()))

    def ssh(self):
        instance = self.get_instances()[0]
        cmd = 'TERM="xterm-256color" ssh {PrivateIp}'.format(**instance)
        try:
            subprocess.call(cmd, shell=True)
        except KeyboardInterrupt:
            sys.exit(0)

    def db(self):
        instance = self.get_instances()[0]
        cmd = 'TERM="xterm-256color" ssh -t {PrivateIp} connect-db'.format(**instance)
        try:
            subprocess.call(cmd, shell=True)
        except KeyboardInterrupt:
            sys.exit(0)
