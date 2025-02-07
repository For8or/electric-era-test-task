import sys
from typing import List, Dict, Set, Tuple

class ChargerReport:
    """
    Represents a single status report for a charger.
    Contains information about when the charger was up or down during a specific time period.
    """
    def __init__(self, charger_id: int, start_time: int, end_time: int, is_up: bool):
        self.charger_id = charger_id    # Unique identifier for the charger
        self.start_time = start_time    # Start time of the reporting period
        self.end_time = end_time        # End time of the reporting period
        self.is_up = is_up              # True if charger was up during this period, False if down

class StationUptimeCalculator:
    """
    Main class for calculating uptime percentages for charging stations.
    A station is considered "up" if any of its chargers is available.
    """
    def __init__(self):
        # Maps station IDs to their set of charger IDs
        self.station_chargers: Dict[int, Set[int]] = {}  
        # Maps charger IDs to their list of status reports
        self.charger_reports: Dict[int, List[ChargerReport]] = {}   

    def parse_input_file(self, filepath: str) -> None:
        """
        Parses the input file containing station configurations and charger reports.
        
        Args:
            filepath: Path to the input file
            
        Raises:
            ValueError: If file format is invalid or missing required sections
        """
        try:
            # Read and split file content into lines
            with open(filepath, 'r') as f:
                content = f.read().strip().split('\n')

            # Find section markers
            try:
                stations_start = content.index('[Stations]')
                reports_start = content.index('[Charger Availability Reports]')
            except ValueError:
                raise ValueError("Missing required sections")

            # Parse Stations section
            for line in content[stations_start + 1:reports_start]:
                if line.strip():
                    parts = line.split()
                    if len(parts) < 2:
                        raise ValueError("Invalid station line format")
                    station_id = int(parts[0])
                    charger_ids = set(map(int, parts[1:]))
                    self.station_chargers[station_id] = charger_ids

            # Parse Charger Reports section
            for line in content[reports_start + 1:]:
                if line.strip():
                    parts = line.split()
                    if len(parts) != 4:
                        raise ValueError("Invalid report line format")
                    
                    charger_id = int(parts[0])
                    start_time = int(parts[1])
                    end_time = int(parts[2])
                    is_up = parts[3].lower() == 'true'

                    # Validate time range
                    if start_time > end_time:
                        raise ValueError("Start time cannot be greater than end time")

                    # Create and store report
                    report = ChargerReport(charger_id, start_time, end_time, is_up)
                    if charger_id not in self.charger_reports:
                        self.charger_reports[charger_id] = []
                    self.charger_reports[charger_id].append(report)

        except (IOError, ValueError, IndexError) as e:
            raise ValueError(f"Error parsing input file: {str(e)}")

    def _merge_intervals(self, intervals: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """
        Merges overlapping time intervals into non-overlapping intervals.
        
        Args:
            intervals: List of (start, end) time tuples
            
        Returns:
            List of merged non-overlapping intervals
        """
        if not intervals:
            return []
        
        # Sort intervals by start time
        intervals.sort()
        
        merged = [intervals[0]]
        for interval in intervals[1:]:
            if interval[0] <= merged[-1][1]:
                # Intervals overlap, update end time
                merged[-1] = (merged[-1][0], max(merged[-1][1], interval[1]))
            else:
                # No overlap, add new interval
                merged.append(interval)
        return merged

    def calculate_station_uptime(self) -> List[Tuple[int, int]]:
        """
        Calculates uptime percentages for all stations.
        A station is considered up if any of its chargers is up.
        
        Returns:
            List of (station_id, uptime_percentage) tuples, sorted by station_id
        """
        results = []
        
        for station_id in sorted(self.station_chargers.keys()):
            charger_ids = self.station_chargers[station_id]
            
            # Initialize tracking variables
            min_time = float('inf')
            max_time = float('-inf')
            has_reports = False
            
            # Track intervals per charger to handle down periods correctly
            charger_up_intervals = {}  # charger_id -> list of intervals
            
            # Process each charger's reports
            for charger_id in charger_ids:
                if charger_id in self.charger_reports:
                    # Sort reports by time, with down reports processed before up reports
                    reports = sorted(self.charger_reports[charger_id], 
                                key=lambda x: (x.start_time, not x.is_up))
                    if reports:
                        has_reports = True
                        min_time = min(min_time, min(r.start_time for r in reports))
                        max_time = max(max_time, max(r.end_time for r in reports))
                        
                        # Process reports for this charger
                        charger_intervals = []
                        for r in reports:
                            if r.is_up:
                                # Add new up interval
                                charger_intervals.append((r.start_time, r.end_time))
                            else:
                                # Down report splits any overlapping up intervals
                                new_intervals = []
                                for start, end in charger_intervals:
                                    if end <= r.start_time or start >= r.end_time:
                                        # No overlap with down period
                                        new_intervals.append((start, end))
                                    else:
                                        # Add non-overlapping parts
                                        if start < r.start_time:
                                            new_intervals.append((start, r.start_time))
                                        if end > r.end_time:
                                            new_intervals.append((r.end_time, end))
                                charger_intervals = new_intervals
                        
                        if charger_intervals:
                            charger_up_intervals[charger_id] = charger_intervals
            
            # Handle stations with no reports
            if not has_reports:
                results.append((station_id, 0))
                continue

            # Handle instantaneous reports
            if min_time == max_time:
                is_up = any(
                    any(start <= min_time <= end for start, end in intervals)
                    for intervals in charger_up_intervals.values()
                )
                results.append((station_id, 100 if is_up else 0))
                continue

            # Combine all up intervals from all chargers
            all_intervals = []
            for intervals in charger_up_intervals.values():
                all_intervals.extend(intervals)
                
            # Merge overlapping intervals
            merged_intervals = self._merge_intervals(all_intervals)
            
            # Calculate uptime percentage
            total_up_time = sum(end - start for start, end in merged_intervals)
            total_time = max_time - min_time
            uptime_percentage = int((total_up_time / total_time) * 100)
            results.append((station_id, uptime_percentage))

        return results

def main():
    """
    Main entry point. Processes command line arguments and outputs results.
    Expects a single argument: the path to the input file.
    Outputs either station uptimes or "ERROR" on failure.
    """
    if len(sys.argv) != 2:
        print("ERROR")
        sys.exit(1)

    calculator = StationUptimeCalculator()
    try:
        calculator.parse_input_file(sys.argv[1])
        results = calculator.calculate_station_uptime()
        
        # Output results in required format
        for station_id, uptime in results:
            print(f"{station_id} {uptime}")
            
    except Exception as e:
        print("ERROR")
        sys.exit(1)

if __name__ == "__main__":
    main()