'''Test reports'''

from datetime import datetime
from pathlib import Path
from freezegun import freeze_time

from hazelsync.reports import Report

def dummy_report():
    report = Report(
        cluster='mycluster',
        job_type='backup',
        job_name='rsync',
        start_time=datetime(year=2020, month=11, day=22, hour=1),
        end_time=datetime(year=2020, month=11, day=22, hour=2),
        status='success',
        slots=[],
    )
    return report

DUMMY_REPORT1 = '''cluster: mycluster
end_time: '2020-11-22T02:00:00'
job_name: rsync
job_type: backup
slots: []
start_time: '2020-11-22T01:00:00'
status: success
'''

class TestReport:
    def test_init(self):
        report = dummy_report()
        assert isinstance(report, Report)

    def test_get(self, tmp_path):
        Report.directory = tmp_path
        cluster_path = tmp_path / 'mycluster'
        cluster_path.mkdir()
        filepath1 = cluster_path / '2020-11-22T01:00:00.yaml'
        filepath1.write_text(DUMMY_REPORT1)
        dummy_report1 = dummy_report()
        reports = Report.get('mycluster', datetime(year=2020, month=11, day=22), datetime(year=2020, month=11, day=23))
        report = reports[0]
        assert report.cluster == 'mycluster'
        assert report.start_time == datetime(year=2020, month=11, day=22, hour=1)
        assert report.end_time == datetime(year=2020, month=11, day=22, hour=2)
        assert report.job_type == 'backup'
        assert report.job_name == 'rsync'

    def test_read(self, tmp_path):
        Report.directory = tmp_path
        cluster_path = tmp_path / 'mycluster'
        cluster_path.mkdir()
        filepath1 = cluster_path / '2020-11-22T01:00:00.yaml'
        filepath1.write_text(DUMMY_REPORT1)
        report = Report.read(filepath1)
        assert report.cluster == 'mycluster'
        assert report.start_time == datetime(year=2020, month=11, day=22, hour=1)
        assert report.end_time == datetime(year=2020, month=11, day=22, hour=2)
        assert report.job_type == 'backup'
        assert report.job_name == 'rsync'

    def test_make_path(self, tmp_path):
        Report.directory = tmp_path
        report = dummy_report()
        filepath = report.make_path()
        cluster_path = tmp_path / 'mycluster'
        assert filepath == cluster_path / '2020-11-22T01:00:00.yaml'
        assert cluster_path.is_dir()

    def test_write(self, tmp_path):
        Report.directory = tmp_path
        report = dummy_report()
        report.write()
        clusterpath = tmp_path / 'mycluster'
        assert clusterpath.is_dir()
        filepath = clusterpath / '2020-11-22T01:00:00.yaml'
        assert filepath.is_file()
        text = filepath.read_text(encoding='utf-8')
        assert text == DUMMY_REPORT1

    @freeze_time('2020-11-22T12:00:00+09:00')
    def test_to_nagios(self):
        report = dummy_report()
        text = report.to_nagios(1)
        assert text == "[OK] mycluster: slots 0/0 succeeded"
