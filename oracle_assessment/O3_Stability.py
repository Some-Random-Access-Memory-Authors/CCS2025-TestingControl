import re
import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt




# Define patterns to extract the relevant data
pattern_header_time = re.compile(r"Planning header time: (\d+\.\d+)")
pattern_planning_point = re.compile(
    r"Planning point \(by time\) timestamp: (\d+\.\d+)\n"
    r"Planning point \(by time\) x: (-?\d+\.\d+)\n"
    r"Planning point \(by time\) y: (-?\d+\.\d+)\n"
    r"Planning point \(by time\) theta: (-?\d+\.\d+)\n"
    r"Planning point \(by time\) kappa: (-?\d+\.\d+)\n"
    r"Planning point \(by time\) v: (-?\d+\.\d+)\n"
    r"Planning point \(by time\) a: (-?\d+\.\d+)"
)
pattern_current_point = re.compile(
    r"Current point timestamp: (\d+\.\d+)\n"
    r"Current point x: (-?\d+\.\d+)\n"
    r"Current point y: (-?\d+\.\d+)\n"
    r"Current point theta: (-?\d+\.\d+)\n"
    r"Current point kappa: (-?\d+\.\d+)\n"
    r"Current point v: (-?\d+\.\d+)\n"
    r"Current point a: (-?\d+\.\d+)"
)




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

            raw_data = file.read()

            # Extract the data
            header_times = [float(match.group(1)) for match in pattern_header_time.finditer(raw_data)]
            planning_points = [match.groups() for match in pattern_planning_point.finditer(raw_data)]
            current_points = [match.groups() for match in pattern_current_point.finditer(raw_data)]

            # Convert the extracted data to DataFrame
            columns = ["timestamp", "x", "y", "theta", "kappa", "v", "a"]
            df_planning_points = pd.DataFrame(planning_points, columns=columns, dtype=float)
            df_current_points = pd.DataFrame(current_points, columns=columns, dtype=float)

            # Display basic information and head of the DataFrames
            #(df_planning_points.info(), df_planning_points.head(), df_current_points.info(), df_current_points.head())


            ################################################
            # Step 1: Time Adjustment and Unit Correction
            # Shift the timestamps so they start from 0
            df_planning_points["timestamp"] -= df_planning_points["timestamp"].min()
            df_current_points["timestamp"] -= df_current_points["timestamp"].min()

            # Step 2: Find the closest planning point for each current point
            # Initialize lists to store the computed differences
            diffs = {"timestamp": [], "dist": [], "theta": [], "v": [], "a": []}

            # Iterate through each current point
            for _, curr_pt in df_current_points.iterrows():
                # Find the index of the closest planning point in time
                closest_idx = abs(df_planning_points["timestamp"] - curr_pt["timestamp"]).idxmin()
                plan_pt = df_planning_points.iloc[closest_idx]
                
                # Compute the absolute differences and store them
                diffs["timestamp"].append(curr_pt["timestamp"])
                diffs["dist"].append(abs(((curr_pt["x"] - plan_pt["x"])**2 + (curr_pt["y"] - plan_pt["y"])**2)**0.5))
                diffs["theta"].append(abs(curr_pt["theta"] - plan_pt["theta"]))
                diffs["v"].append(abs(curr_pt["v"] - plan_pt["v"]))
                diffs["a"].append(abs(curr_pt["a"] - plan_pt["a"]))

            # Convert the computed differences to a DataFrame
            df_diffs = pd.DataFrame(diffs)

            # Display basic information and head of the DataFrame
            #df_diffs.info(), df_diffs.head()


            # Step 4: Compute the derivatives of the differences with respect to time
            # Initialize a dictionary to store the computed derivatives
            derivatives = {"timestamp": df_diffs["timestamp"][1:]}

            # Compute the derivatives
            for col in ["dist", "theta", "v", "a"]:
                derivatives[f"d{col}/dt"] = df_diffs[col].diff() / df_diffs["timestamp"].diff()

            # Convert the computed derivatives to a DataFrame
            df_derivatives = pd.DataFrame(derivatives)

            # Compute the average and maximum of the derivatives
            derivatives_stats = {
                "Average": df_derivatives.mean().to_dict(),
                "Maximum": df_derivatives.max().to_dict()
            }

            # Display basic information and head of the DataFrame and the statistics
            #(df_derivatives.info(), df_derivatives.head(), derivatives_stats)


            valid_dv_dt = df_derivatives["dv/dt"].replace([np.inf, -np.inf], np.nan).dropna()

            # Statistics for the valid velocity difference derivative
            valid_dv_dt_stats = {
                "Average": valid_dv_dt.mean(),
                "Maximum": valid_dv_dt.max()
            }


            print('************************************')
            print(file_name)
            print("ddist/dt average: ", derivatives_stats['Average']['ddist/dt'])
            print("ddist/dt max: ", derivatives_stats['Maximum']['ddist/dt'])

            print("dtheta/dt average: ", derivatives_stats['Average']['dtheta/dt'])
            print("dtheta/dt max:" , derivatives_stats['Maximum']['dtheta/dt'])

            print("dv/dt average: ", valid_dv_dt_stats['Average'])
            print("dv/dt max: ", valid_dv_dt_stats['Maximum'])

            print("da/dt average:", derivatives_stats['Average']['da/dt'])
            print("da/dt max: ", derivatives_stats['Maximum']['da/dt'])
