import unittest
import tempfile
import os
from station_uptime import StationUptimeCalculator, ChargerReport

class TestStationUptimeCalculator(unittest.TestCase):
    """
    Test suite for the StationUptimeCalculator class.
    Tests various scenarios of charger availability and station uptime calculations.
    """

    def setUp(self):
        """
        Test fixture setup.
        Creates a new calculator instance for each test.
        """
        self.calculator = StationUptimeCalculator()
        self.temp_files = []  # Track temporary files for cleanup

    def tearDown(self):
        """
        Test fixture cleanup.
        Removes any temporary files created during tests.
        """
        for temp_file in self.temp_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def create_temp_file(self, content: str) -> str:
        """
        Helper method to create temporary test input files.
        
        Args:
            content: String content to write to the file
            
        Returns:
            Path to the created temporary file
        """
        fd, path = tempfile.mkstemp()
        self.temp_files.append(path)
        with os.fdopen(fd, 'w') as f:
            f.write(content)
        return path

    def test_basic_single_charger(self):
        """
        Tests the simplest case - a single charger that's up for its entire reporting period.
        Expected: 100% uptime as the charger is up the whole time.
        """
        input_content = """[Stations]
0 1000

[Charger Availability Reports]
1000 0 100 true"""
        
        input_file = self.create_temp_file(input_content)
        self.calculator.parse_input_file(input_file)
        results = self.calculator.calculate_station_uptime()
        self.assertEqual(results, [(0, 100)])

    def test_basic_multiple_chargers(self):
        """
        Tests a station with multiple chargers where at least one is up.
        Expected: 100% uptime because one charger being up makes the station up.
        """
        input_content = """[Stations]
0 1000 1001

[Charger Availability Reports]
1000 0 100 true
1001 0 100 false"""
        
        input_file = self.create_temp_file(input_content)
        self.calculator.parse_input_file(input_file)
        results = self.calculator.calculate_station_uptime()
        self.assertEqual(results, [(0, 100)])

    def test_overlapping_periods(self):
        """
        Tests overlapping up periods from different chargers.
        Expected: 100% uptime as there's always at least one charger up during the period.
        Time periods: 0-50 (first charger) and 25-75 (second charger) provide continuous coverage.
        """
        input_content = """[Stations]
0 1000 1001

[Charger Availability Reports]
1000 0 50 true
1001 25 75 true"""
            
        input_file = self.create_temp_file(input_content)
        self.calculator.parse_input_file(input_file)
        results = self.calculator.calculate_station_uptime()
        self.assertEqual(results, [(0, 100)])

    def test_gaps_in_coverage(self):
        """
        Tests non-continuous uptime with gaps between up periods.
        Expected: 75% uptime because there's a gap between 50-75 where the charger is down.
        Total time: 100 units, Up time: 75 units (0-50 and 75-100)
        """
        input_content = """[Stations]
0 1000

[Charger Availability Reports]
1000 0 50 true
1000 75 100 true"""
                
        input_file = self.create_temp_file(input_content)
        self.calculator.parse_input_file(input_file)
        results = self.calculator.calculate_station_uptime()
        self.assertEqual(results, [(0, 75)])

    def test_multiple_stations(self):
        """
        Tests multiple stations with different uptime patterns.
        Tests both up/down transitions and multiple reports per charger.
        
        Station 0: Always up (100%)
        Station 1: Down then up for second half (50%)
        Station 2: Up then down after 25% of time (25%)
        """
        input_content = """[Stations]
0 1000
1 1001
2 1002

[Charger Availability Reports]
1000 0 100 true
1001 0 100 false
1001 50 100 true
1002 0 100 true
1002 25 100 false"""
    
        input_file = self.create_temp_file(input_content)
        self.calculator.parse_input_file(input_file)
        results = self.calculator.calculate_station_uptime()
        self.assertEqual(results, [(0, 100), (1, 50), (2, 25)])

    def test_no_reports_for_station(self):
        """
        Tests station with no availability reports.
        Expected: 0% uptime as no reports means no confirmed up time.
        """
        input_content = """[Stations]
0 1000

[Charger Availability Reports]"""
        
        input_file = self.create_temp_file(input_content)
        self.calculator.parse_input_file(input_file)
        results = self.calculator.calculate_station_uptime()
        self.assertEqual(results, [(0, 0)])

    def test_invalid_file_format(self):
        """
        Tests error handling for completely invalid file format.
        Expected: ValueError as file lacks required sections.
        """
        input_content = "Invalid content"
        input_file = self.create_temp_file(input_content)
        with self.assertRaises(ValueError):
            self.calculator.parse_input_file(input_file)

    def test_invalid_station_format(self):
        """
        Tests error handling for invalid station definition.
        Expected: ValueError as station line lacks charger IDs.
        """
        input_content = """[Stations]
0

[Charger Availability Reports]"""
        
        input_file = self.create_temp_file(input_content)
        with self.assertRaises(ValueError):
            self.calculator.parse_input_file(input_file)

    def test_invalid_report_format(self):
        """
        Tests error handling for invalid report format.
        Expected: ValueError as report line is missing the up/down status.
        """
        input_content = """[Stations]
0 1000

[Charger Availability Reports]
1000 0 100"""
        
        input_file = self.create_temp_file(input_content)
        with self.assertRaises(ValueError):
            self.calculator.parse_input_file(input_file)

    def test_invalid_time_range(self):
        """
        Tests error handling for invalid time range.
        Expected: ValueError as end time is before start time.
        """
        input_content = """[Stations]
0 1000

[Charger Availability Reports]
1000 100 0 true"""
        
        input_file = self.create_temp_file(input_content)
        with self.assertRaises(ValueError):
            self.calculator.parse_input_file(input_file)

    def test_example_1(self):
        """
        Tests complex scenario with multiple stations and reports.
        
        Station 0: Continuous uptime with overlapping reports (100%)
        Station 1: Only downtime reported (0%)
        Station 2: Two separate up periods with gap (25%)
        """
        input_content = """[Stations]
0 1001 1002
1 1003
2 1004

[Charger Availability Reports]
1001 0 50000 true
1001 50000 100000 true
1002 50000 100000 true
1003 25000 75000 false
1004 0 50000 true
1004 100000 200000 true"""
    
        input_file = self.create_temp_file(input_content)
        self.calculator.parse_input_file(input_file)
        results = self.calculator.calculate_station_uptime()
        self.assertEqual(results, [(0, 100), (1, 0), (2, 75)])

    def test_example_2(self):
        """
        Tests alternating up/down periods and instantaneous uptime.
        
        Station 0: Two 10-unit up periods in 30-unit span (66%)
        Station 1: Single instant up report (100%)
        """
        input_content = """[Stations]
0 0
1 1

[Charger Availability Reports]
0 10 20 true
0 20 30 false
0 30 40 true
1 0 1 true"""
        
        input_file = self.create_temp_file(input_content)
        self.calculator.parse_input_file(input_file)
        results = self.calculator.calculate_station_uptime()
        self.assertEqual(results, [(0, 66), (1, 100)])

    def test_zero_duration_period(self):
        """
        Tests handling of zero-duration (instantaneous) reports.
        Expected: 100% uptime as the charger reports being up at that instant.
        """
        input_content = """[Stations]
0 1000

[Charger Availability Reports]
1000 100 100 true"""
        
        input_file = self.create_temp_file(input_content)
        self.calculator.parse_input_file(input_file)
        results = self.calculator.calculate_station_uptime()
        self.assertEqual(results, [(0, 100)])

if __name__ == '__main__':
    unittest.main()