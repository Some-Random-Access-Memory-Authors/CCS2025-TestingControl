import pandas as pd
import re
import os
import sys
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman'] + plt.rcParams['font.serif']

pattern_planning_header_time = re.compile(r"Planning header time: (\d+\.\d+)")
pattern_planning_point = re.compile(r"Planning point \(by time\) timestamp: (\d+\.\d+)\n"
                                    r"Planning point \(by time\) x: (-?\d+\.\d+)\n"
                                    r"Planning point \(by time\) y: (-?\d+\.\d+)\n"
                                    r"Planning point \(by time\) theta: (-?\d+\.\d+)\n"
                                    r"Planning point \(by time\) kappa: (-?\d+\.\d+)\n"
                                    r"Planning point \(by time\) v: (-?\d+\.\d+)\n"
                                    r"Planning point \(by time\) a: (-?\d+\.\d+)")
pattern_current_point = re.compile(r"Current point timestamp: (\d+\.\d+)\n"
                                   r"Current point x: (-?\d+\.\d+)\n"
                                   r"Current point y: (-?\d+\.\d+)\n"
                                   r"Current point theta: (-?\d+\.\d+)\n"
                                   r"Current point kappa: (-?\d+\.\d+)\n"
                                   r"Current point v: (-?\d+\.\d+)\n"
                                   r"Current point a: (-?\d+\.\d+)")




if len(sys.argv) > 1:
    folder_name = sys.argv[1]
    
    try:
        files = os.listdir(folder_name)
    except FileNotFoundError:
        print("The specified folder does not exist.")
        sys.exit(1)

    files.sort()
    
    for file_name in files:
        file_path = os.path.join(folder_name, file_name)
        with open(file_path, 'r') as file:
            raw_data = file.read()

            # Define patterns for data extraction

            # Extract data using patterns
            planning_header_times = [float(match.group(1)) for match in pattern_planning_header_time.finditer(raw_data)]
            planning_points = [(float(match.group(1)), float(match.group(2)), float(match.group(3)), float(match.group(4)), 
                                float(match.group(5)), float(match.group(6)), float(match.group(7))) 
                               for match in pattern_planning_point.finditer(raw_data)]
            current_points = [(float(match.group(1)), float(match.group(2)), float(match.group(3)), float(match.group(4)), 
                               float(match.group(5)), float(match.group(6)), float(match.group(7))) 
                              for match in pattern_current_point.finditer(raw_data)]

            # Convert extracted data to DataFrame
            data = pd.DataFrame({
                'planning_header_time': planning_header_times,
                'planning_timestamp': [pt[0] for pt in planning_points],
                'planning_x': [pt[1] for pt in planning_points],
                'planning_y': [pt[2] for pt in planning_points],
                'planning_theta': [pt[3] for pt in planning_points],
                'planning_kappa': [pt[4] for pt in planning_points],
                'planning_v': [pt[5] for pt in planning_points],
                'planning_a': [pt[6] for pt in planning_points],
                'current_timestamp': [cp[0] for cp in current_points],
                'current_x': [cp[1] for cp in current_points],
                'current_y': [cp[2] for cp in current_points],
                'current_theta': [cp[3] for cp in current_points],
                'current_kappa': [cp[4] for cp in current_points],
                'current_v': [cp[5] for cp in current_points],
                'current_a': [cp[6] for cp in current_points]
            })

            # Normalize timestamps to start from 0
            min_timestamp = min(data['planning_header_time'].min(), data['planning_timestamp'].min(), data['current_timestamp'].min())
            data[['planning_header_time', 'planning_timestamp', 'current_timestamp']] -= min_timestamp

            # Display first few rows of the data
            #data.head(), data.shape


            # Ensure that timestamps are unique and sorted
            unique_data = data.drop_duplicates(subset='current_timestamp')
            unique_data = unique_data.sort_values(by='current_timestamp').reset_index(drop=True)

            # Compute the first derivative of current_theta (angular velocity)
            angular_velocity = np.gradient(unique_data['current_theta'], unique_data['current_timestamp'], edge_order=2)

            # Compute the second derivative of current_theta (angular acceleration)
            angular_acceleration = np.gradient(angular_velocity, unique_data['current_timestamp'], edge_order=2)

            # Get the average and maximum of angular acceleration
            avg_angular_acceleration = np.mean(angular_acceleration)
            max_angular_acceleration = np.max(angular_acceleration)

            # Get the average and maximum of linear acceleration
            avg_linear_acceleration = unique_data['current_a'].mean()
            max_linear_acceleration = unique_data['current_a'].max()

            avg_angular_acceleration_abs = np.mean( np.abs(angular_acceleration) )
            max_angular_acceleration_abs = np.max(np.abs(angular_acceleration))

            # Get the average and maximum of linear acceleration
            avg_linear_acceleration_abs = np.abs(unique_data['current_a'].mean())
            max_linear_acceleration_abs = np.abs(unique_data['current_a'].max())

            #print(file_name[:5], avg_angular_acceleration, max_angular_acceleration, avg_linear_acceleration, max_linear_acceleration)
            print(file_name[:2]+'\\_'+file_name[3:5], ' & ', format(avg_angular_acceleration_abs, ".2f") , ' & ' , 
             format(max_angular_acceleration_abs, ".2f") , ' & ' , format( (max_angular_acceleration_abs/avg_angular_acceleration_abs)*100, ".2f")+'\%' , ' & ',
             format(avg_linear_acceleration_abs, ".6f") , ' & ', 
             format(max_linear_acceleration_abs, ".2f") , ' & ', format( (max_linear_acceleration_abs/avg_linear_acceleration_abs)*100, ".2f")+'\%' , '\\\\' )
            
            #print("%")
