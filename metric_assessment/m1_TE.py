import os
import re
import sys
import numpy as np

def find_closest_planning_point_index(current_timestamp, planning_points):
    timestamps = [p['timestamp'] for p in planning_points]
    return np.argmin(np.abs(np.array(timestamps) - current_timestamp))

def analyze_data(file_path):
    with open(file_path, 'r') as file:
        data = file.read()

    planning_point_pattern = re.compile(r'Planning point \(by time\) timestamp: (.+)\n'
                                         r'Planning point \(by time\) x: (.+)\n'
                                         r'Planning point \(by time\) y: (.+)\n'
                                         r'Planning point \(by time\) theta: (.+)\n'
                                         r'Planning point \(by time\) kappa: (.+)\n'
                                         r'Planning point \(by time\) v: (.+)\n'
                                         r'Planning point \(by time\) a: (.+)\n')
    current_point_pattern = re.compile(r'Current point timestamp: (.+)\n'
                                       r'Current point x: (.+)\n'
                                       r'Current point y: (.+)\n'
                                       r'Current point theta: (.+)\n'
                                       r'Current point kappa: (.+)\n'
                                       r'Current point v: (.+)\n'
                                       r'Current point a: (.+)\n')

    planning_points_data = planning_point_pattern.findall(data)
    current_points_data = current_point_pattern.findall(data)

    planning_points = [{'timestamp': float(p[0]), 'x': float(p[1]), 'y': float(p[2]), 'theta': float(p[3]), 
                        'kappa': float(p[4]), 'v': float(p[5]), 'a': float(p[6])} for p in planning_points_data]
    current_points = [{'timestamp': float(c[0]), 'x': float(c[1]), 'y': float(c[2]), 'theta': float(c[3]), 
                       'kappa': float(c[4]), 'v': float(c[5]), 'a': float(c[6])} for c in current_points_data]

    errors = {'distance': [], 'theta': [], 'v': [], 'a': []}

    for current_point in current_points:
        closest_index = find_closest_planning_point_index(current_point['timestamp'], planning_points)
        planning_point = planning_points[closest_index]
        
        distance_error = np.sqrt((current_point['x'] - planning_point['x'])**2 + 
                                 (current_point['y'] - planning_point['y'])**2)
        errors['distance'].append(distance_error)
        
        theta_error = abs(current_point['theta'] - planning_point['theta'])
        errors['theta'].append(theta_error)
        
        v_error = abs(current_point['v'] - planning_point['v'])
        errors['v'].append(v_error)
        
        a_error = abs(current_point['a'] - planning_point['a'])
        errors['a'].append(a_error)

    mean_values = {'theta': np.mean([point['theta'] for point in current_points]),
                   'v': np.mean([point['v'] for point in current_points]),
                   'a': np.mean([point['a'] for point in current_points])}

    analysis_results = {error_type: {'max_error': np.max(errors[error_type]),
                                     'mean_error': np.mean(errors[error_type])} 
                        for error_type in errors}

    for error_type in ['theta', 'v', 'a']:
        analysis_results[error_type]['max_error_percentage'] = \
            (analysis_results[error_type]['max_error'] / mean_values[error_type]) * 100
        analysis_results[error_type]['mean_error_percentage'] = \
            (analysis_results[error_type]['mean_error'] / mean_values[error_type]) * 100

    return analysis_results, mean_values

if __name__ == "__main__":
    
    folder_name = sys.argv[1]
    
    try:
        files = os.listdir(folder_name)
    except FileNotFoundError:
        print("The specified folder does not exist.")
        sys.exit(1)
    
    for file_name in files:
        file_path = os.path.join(folder_name, file_name)
        analysis_results, mean_values = analyze_data(file_path)

        print('Analyzed file: ', file_name)
        print("Analysis Results:")
        print(analysis_results)
        print("\nMean Values:")
        print(mean_values)
        print("\n******************************")


