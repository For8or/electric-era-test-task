 # Charging Station Uptime Calculator

## Overview
This project implements a station uptime calculator for a charging network. It calculates the percentage of time that charging stations are available based on individual charger status reports.

## Problem Description
The calculator processes input files containing:
1. Station configurations (which chargers belong to which stations)
2. Charger availability reports (when chargers were up or down)

A station is considered "up" if any of its chargers is available. The uptime percentage is calculated as the proportion of time a station had at least one charger available.

## Solution

### Implementation
The solution consists of two main classes:
- `ChargerReport`: Data structure for individual charger status reports
- `StationUptimeCalculator`: Main calculator class that processes reports and calculates uptimes

Key features:
- Handles overlapping time periods
- Processes multiple chargers per station
- Supports multiple reports per charger
- Correctly handles edge cases (zero duration, gaps in coverage)

### Time Complexity
- Parsing: O(n) where n is number of lines in input file
- Calculation: O(m log m) where m is number of reports per station (due to interval merging)

### Space Complexity
- O(n) where n is total number of reports

## Usage

### Input File Format
```
[Stations]
<Station ID> <Charger ID 1> <Charger ID 2> ... <Charger ID n>
...

[Charger Availability Reports]
<Charger ID> <start time> <end time> <up (true/false)>
...
```

### Running the Program
```bash
python station_uptime.py path/to/input/file
```

### Output Format
```
<Station ID> <Uptime Percentage>
...
```
Uptime percentages are integers from 0 to 100.

## Testing
The solution includes comprehensive test cases covering:
- Basic functionality
- Multiple chargers/stations
- Overlapping periods
- Edge cases (zero duration, gaps)
- Error handling

Run tests with:
```bash
python -m unittest test_station_uptime.py
```

## Edge Cases Handled
1. Zero duration reports (instantaneous status)
2. Gaps in coverage
3. Overlapping up/down periods
4. Multiple chargers reporting simultaneously
5. Invalid input formats
6. Missing or malformed reports

## Error Handling
The program outputs "ERROR" and exits with status code 1 for:
- Invalid file format
- Missing required sections
- Invalid time ranges
- Malformed input lines

## Implementation Details

### Key Algorithms
1. **Report Processing**:
   - Sort reports chronologically
   - Track intervals per charger
   - Handle up/down transitions

2. **Interval Merging**:
   - Combine overlapping "up" periods
   - Handle gaps in coverage
   - Calculate total uptime

3. **Percentage Calculation**:
   - Based on total reporting period
   - Rounds down to nearest integer
   - Handles edge cases properly

### Design Decisions
1. **Separate Classes**:
   - Clear separation of concerns
   - Easy to maintain and extend
   - Modular design

2. **Error Handling**:
   - Robust input validation
   - Clear error messages
   - Graceful failure modes

3. **Testing**:
   - Comprehensive test suite
   - Edge case coverage
   - Clear test documentation

## Requirements
- Python 3.6+
- No external dependencies required

## Development Notes
- Type hints used for better code understanding
- Comprehensive documentation
- Clean code practices followed
- Extensive test coverage

## Limitations and Future Improvements
1. Potential Improvements:
   - Parallel processing for large datasets
   - Memory optimization for huge files
   - Real-time report processing
   - More detailed error reporting

2. Current Limitations:
   - Assumes input fits in memory
   - Single-threaded processing
   - Integer-only time values