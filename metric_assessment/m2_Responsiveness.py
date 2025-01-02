import re
import os
import sys
import matplotlib.pyplot as plt
import numpy as np

# Define a pattern for extracting data
pattern_loose = re.compile(r'Planning header time: (?P<planning_header_time>-?\d+\.\d+)\n'
                           r'\*\*\*\n'
                           r'Planning point \(by time\) timestamp: (?P<planning_time>-?\d+\.\d+)\n'
                           r'Planning point \(by time\) x: (?P<planning_x>-?\d+\.\d+)\n'
                           r'Planning point \(by time\) y: (?P<planning_y>-?\d+\.\d+)\n'
                           r'Planning point \(by time\) theta: (?P<planning_theta>-?\d+\.\d+)\n'
                           r'Planning point \(by time\) kappa: (?P<planning_kappa>-?\d+\.\d+)\n'
                           r'Planning point \(by time\) v: (?P<planning_v>-?\d+\.\d+)\n'
                           r'Planning point \(by time\) a: (?P<planning_a>-?\d+\.\d+)\n'
                           r'\*\*\*\n'
                           r'Current point timestamp: (?P<current_time>-?\d+\.\d+)\n'
                           r'Current point x: (?P<current_x>-?\d+\.\d+)\n'
                           r'Current point y: (?P<current_y>-?\d+\.\d+)\n'
                           r'Current point theta: (?P<current_theta>-?\d+\.\d+)\n'
                           r'Current point kappa: (?P<current_kappa>-?\d+\.\d+)\n'
                           r'Current point v: (?P<current_v>-?\d+\.\d+)\n'
                           r'Current point a: (?P<current_a>-?\d+\.\d+)')


if len(sys.argv) > 1:
    folder_name = sys.argv[1]
    
    try:
        files = os.listdir(folder_name)
    except FileNotFoundError:
        print("The specified folder does not exist.")
        sys.exit(1)
    
    for file_name in files:
        file_path = os.path.join(folder_name, file_name)
        with open(file_path, 'r') as file:
            file_content = file.read()


            # Extract data using the pattern
            matches = pattern_loose.finditer(file_content)

            # Create lists to store extracted data
            data = {
                "planning": {
                    "header_time": [],
                    "time": [],
                    "x": [],
                    "y": [],
                    "theta": [],
                    "kappa": [],
                    "v": [],
                    "a": []
                },
                "current": {
                    "time": [],
                    "x": [],
                    "y": [],
                    "theta": [],
                    "kappa": [],
                    "v": [],
                    "a": []
                }
            }

            # Loop through the matches and append data to lists
            for match in matches:
                for key in data.keys():
                    for sub_key in data[key].keys():
                        data[key][sub_key].append(float(match.group(f"{key}_{sub_key}")))



            E = {
                "theta": max(max(data["planning"]["theta"]), max(data["current"]["theta"])) - 
                         min(min(data["planning"]["theta"]), min(data["current"]["theta"])),
                "v": max(max(data["planning"]["v"]), max(data["current"]["v"])) - 
                     min(min(data["planning"]["v"]), min(data["current"]["v"])),
                "a": max(max(data["planning"]["a"]), max(data["current"]["a"])) - 
                     min(min(data["planning"]["a"]), min(data["current"]["a"]))
            }



            time_diffs = {"theta": [], "v": [], "a": [], "xy": []}

            # Define a threshold for xy (0.2m)
            xy_threshold = 0.2

            # Loop through each planning point
            for i in range(len(data["planning"]["time"])):
                # Get the planning point timestamp
                p_time = data["planning"]["time"][i]
                
                # Find the index of the first current point with a timestamp equal or greater than the planning point
                idx = next((j for j, t in enumerate(data["current"]["time"]) if t >= p_time), None)
                
                # Initialize flags indicating whether a corresponding current point was found for each parameter
                found = {"theta": False, "v": False, "a": False, "xy": False}
                
                # Loop through each subsequent current point
                while idx is not None and idx < len(data["current"]["time"]):
                    # Check for each parameter if a corresponding current point was found
                    if not found["theta"] and abs(data["planning"]["theta"][i] - data["current"]["theta"][idx]) < 0.01 * E["theta"]:
                        time_diffs["theta"].append(data["current"]["time"][idx] - p_time)
                        found["theta"] = True
                    if not found["v"] and abs(data["planning"]["v"][i] - data["current"]["v"][idx]) < 0.01 * E["v"]:
                        time_diffs["v"].append(data["current"]["time"][idx] - p_time)
                        found["v"] = True
                    if not found["a"] and abs(data["planning"]["a"][i] - data["current"]["a"][idx]) < 0.01 * E["a"]:
                        time_diffs["a"].append(data["current"]["time"][idx] - p_time)
                        found["a"] = True
                    if not found["xy"] and np.sqrt((data["planning"]["x"][i] - data["current"]["x"][idx])**2 + 
                                                  (data["planning"]["y"][i] - data["current"]["y"][idx])**2) < xy_threshold:
                        time_diffs["xy"].append(data["current"]["time"][idx] - p_time)
                        found["xy"] = True
                    
                    # If a corresponding current point was found for all parameters, break the loop
                    if all(found.values()):
                        break
                    
                    # Move to the next current point
                    idx += 1
                
                # If no corresponding current point was found for a parameter, set the time difference to infinity
                for param in found.keys():
                    if not found[param]:
                        time_diffs[param].append(float("inf"))

            # Calculate the metrics
            metrics = {param: {} for param in time_diffs.keys()}
            for param, diffs in time_diffs.items():
                metrics[param]["failure rate"] = 100 * diffs.count(float("inf")) / len(diffs)
                finite_diffs = [d for d in diffs if d != float("inf")]
                metrics[param]["mean_finite"] = sum(finite_diffs) / len(finite_diffs) if finite_diffs else float("nan")
                metrics[param]["max_finite"] = max(finite_diffs) if finite_diffs else float("nan")

            print(file_name)
            print(metrics)
            print("-----------------------")


else:
    print("Please provide a folder name as a command-line argument.")








