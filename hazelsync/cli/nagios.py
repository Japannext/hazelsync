'''Command line to return Nagios compatible checks'''

import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path

import click

from hazelsync.settings import ClusterSettings, CLUSTER_DIRECTORY
from hazelsync.reports import Report, REPORT_DIRECTORY

STATUS_MAPPING = {
    'success': 'ok',
    'partial': 'warning',
    'failure': 'critical',
    'unknown': 'unknown',
}

EXIT_MAPPING = {
    'ok': 0,
    'warning': 1,
    'critical': 2,
    'unknown': 3,
}

log = logging.getLogger('hazelsync')
logging.basicConfig(level=logging.FATAL)

def merge_status(status: str, other: str) -> str:
    '''Merge two status to obtain global status'''
    order = ['ok', 'warning', 'unknown', 'critical']
    status_order = order.index(status)
    other_order = order.index(other)
    if status_order >= other_order:
        return status
    elif other_order > status_order:
        return other

@click.command()
@click.argument('clusters', nargs=-1)
@click.option('--clusterdir', '-C', default=CLUSTER_DIRECTORY)
@click.option('--reportdir', '-R', default=REPORT_DIRECTORY)
@click.option('--days', '-d', default=1, help='Number in days which we consider the backup as unknown')
def nagios(clusters, clusterdir, reportdir, days):
    '''Return a nagios compatible check for one or several backups'''
    ClusterSettings.directory = Path(clusterdir)
    Report.directory = Path(reportdir)
    if not clusters: # Empty list
        clusters = [cluster for cluster, config in ClusterSettings.list().items() if config['config_status'] == 'success']
    display = []
    status = 'ok'
    reports = {}
    for cluster_name in clusters:
        try:
            report = Report.last_report(cluster_name)
            reports[cluster_name] = report
            display.append(report.to_nagios(days))
            mystatus = STATUS_MAPPING[report.status]
        except Exception as err:
            display.append(f"[UNKNOWN] {cluster_name}: {err}")
            mystatus = 'unknown'
        status = merge_status(status, mystatus)
    print_status = status.upper()
    ok_backups = len([name for name in clusters if name in reports and reports[name].status == 'success'])
    total_backups = len(clusters)
    print(f"{print_status} Hazelsync backups - {ok_backups}/{total_backups}")
    print("\n".join(display))
    sys.exit(EXIT_MAPPING[status])
