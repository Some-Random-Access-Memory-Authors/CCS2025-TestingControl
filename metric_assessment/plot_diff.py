import matplotlib.pyplot as plt
import re
import sys


#plt.rcParams["font.family"] = "Times New Roman"
#plt.rcParams["font.family"] = "serif"

#plt.rcParams["font.family"] = "serif"
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman'] + plt.rcParams['font.serif']


def extract_data(file_path):
    with open(file_path, 'r') as file:
        file_content = file.read()

    planning_point_regex = re.compile(r"Planning point \(by time\) timestamp: (\d+\.\d+)\n" +
                                      r"Planning point \(by time\) x: (-?\d+\.\d+)\n" +
                                      r"Planning point \(by time\) y: (-?\d+\.\d+)\n" +
                                      r"Planning point \(by time\) theta: (-?\d+\.\d+)\n" +
                                      r"Planning point \(by time\) kappa: (-?\d+\.\d+)\n" +
                                      r"Planning point \(by time\) v: (-?\d+\.\d+)\n" +
                                      r"Planning point \(by time\) a: (-?\d+\.\d+)")
    current_point_regex = re.compile(r"Current point timestamp: (\d+\.\d+)\n" +
                                     r"Current point x: (-?\d+\.\d+)\n" +
                                     r"Current point y: (-?\d+\.\d+)\n" +
                                     r"Current point theta: (-?\d+\.\d+)\n" +
                                     r"Current point kappa: (-?\d+\.\d+)\n" +
                                     r"Current point v: (-?\d+\.\d+)\n" +
                                     r"Current point a: (-?\d+\.\d+)")

    planning_points = [{"timestamp": float(match[0]), "x": float(match[1]), "y": float(match[2]), 
                        "theta": float(match[3]), "kappa": float(match[4]), "v": float(match[5]), "a": float(match[6])} 
                       for match in planning_point_regex.findall(file_content)]
    current_points = [{"timestamp": float(match[0]), "x": float(match[1]), "y": float(match[2]), 
                       "theta": float(match[3]), "kappa": float(match[4]), "v": float(match[5]), "a": float(match[6])} 
                      for match in current_point_regex.findall(file_content)]

    return planning_points, current_points



def plot_comparison(planning_points, current_points, x_limits=None, y_limits=None):
    initial_time = planning_points[0]['timestamp']

    for point in planning_points:
        point['timestamp'] -= initial_time
        #if point['theta'] < 0:
        #    point['theta'] += 2 * 3.141592653589793

    for point in current_points:
        point['timestamp'] -= initial_time
        #if point['theta'] < 0:
        #    point['theta'] += 2 * 3.141592653589793

    variables_to_plot = ['x', 'y', 'theta', 'v', 'a']
    y_label_dic = {'x': 'X position (m)', 'y' : 'Y position (m)', 'theta' : 'Heading Angle (rad)', 'v' : 'Velocity (m/s)', 'a': 'Acceleration (m2/s)'}
    titles = ['Comparison of x', 'Comparison of y', 'Comparison of theta', 'Comparison of v', 'Comparison of a']
    
    for idx, var in enumerate(variables_to_plot):
        plt.figure(figsize=(5, 4))
        plt.plot([p['timestamp'] for p in planning_points], [p[var] for p in planning_points], 
                 label='Planned Trajectory', linestyle='-', color='b', linewidth=1)
        plt.plot([p['timestamp'] for p in current_points], [p[var] for p in current_points], 
                 label='Actual Trajectory', linestyle='-.', color='r', linewidth=1)
        #plt.title(titles[idx])
        plt.xlabel('Timestamp (s)')
        plt.ylabel(y_label_dic[var])
        plt.legend()
        plt.grid(True)
        if x_limits:
            plt.xlim(x_limits)
        if y_limits:
            plt.ylim(y_limits)
        plt.tight_layout()
        suffix = '_zoomed' if x_limits or y_limits else ''
        plt.savefig(f'comparison_{var}{suffix}.pdf')



def plot_comparison_match(planning_points, current_points, x_limits=None, y_limits=None, line_interval=50):
    initial_time = planning_points[0]['timestamp']

    for point in planning_points:
        point['timestamp'] -= initial_time

    for point in current_points:
        point['timestamp'] -= initial_time
        if point['theta'] < 0:
            point['theta'] += 2 * 3.141592653589793

    variables_to_plot = ['x', 'y', 'theta', 'v', 'a']
    titles = ['Comparison of x', 'Comparison of y', 'Comparison of theta', 'Comparison of v', 'Comparison of a']
    
    for idx, var in enumerate(variables_to_plot):
        plt.figure(figsize=(8, 3))
        plt.plot([p['timestamp'] for p in planning_points], [p[var] for p in planning_points], 
                 label='Planning Point', linestyle='-', color='b', linewidth=1, marker='o', markersize=1)
        plt.plot([p['timestamp'] for p in current_points], [p[var] for p in current_points], 
                 label='Current Point', linestyle='--', color='r', linewidth=1, marker='o', markersize=1)

        for i, (p, c) in enumerate(zip(planning_points, current_points)):
            if i % line_interval == 0:
                plt.arrow(c['timestamp'], c[var], p['timestamp'] - c['timestamp'], p[var] - c[var], 
                          color='g', alpha=0.5, width=0.05, head_width=0.5, head_length=0.2, overhang=0.5, length_includes_head=True)
                #plt.plot([p['timestamp'], c['timestamp']], [p[var], c[var]], linestyle=':', linewidth=1, color='g')

        plt.title(titles[idx])
        plt.xlabel('Timestamp (s)')
        plt.ylabel(var)
        plt.legend()
        plt.grid(True)
        if x_limits:
            plt.xlim(x_limits)
        if y_limits:
            plt.ylim(y_limits)
        plt.tight_layout()
        suffix = '_zoomed' if x_limits or y_limits else ''
        plt.savefig(f'comparison_{var}{suffix}.pdf')




def plot_trajectories(planning_points, current_points, x_limits=None, y_limits=None, aspect_ratio=None):
    plt.figure(figsize=(7, 4))
    plt.plot([p['x'] for p in planning_points], [p['y'] for p in planning_points], 
             label='Planned Trajectory', linestyle='-', color='b', linewidth=1, marker='o', markersize=1)
    plt.plot([p['x'] for p in current_points], [p['y'] for p in current_points], 
             label='Actual Trajectory', linestyle='-', color='r', linewidth=1)
    plt.xlabel('X position (m)')
    plt.ylabel('Y position (m)')
    #plt.title('Comparison of Trajectories')
    plt.legend()
    plt.grid(True)
    if aspect_ratio:
        plt.gca().set_aspect(aspect_ratio, adjustable='box')
    else:
        plt.gca().set_aspect('equal', adjustable='box')
    if x_limits:
        plt.xlim(x_limits)
    if y_limits:
        plt.ylim(y_limits)
    plt.tight_layout()
    suffix = '_zoomed' if x_limits or y_limits else ''
    plt.savefig(f'trajectory_plot{suffix}.pdf')



def plot_trajectories_match(planning_points, current_points, x_limits=None, y_limits=None, aspect_ratio=None, line_interval=50):
    plt.figure(figsize=(10, 10))
    plt.plot([p['x'] for p in planning_points], [p['y'] for p in planning_points], 
             label='Planning Point Trajectory', linestyle='-', color='b', linewidth=1, marker='o', markersize=1)
    plt.plot([p['x'] for p in current_points], [p['y'] for p in current_points], 
             label='Current Point Trajectory', linestyle='--', color='r', linewidth=1, marker='o', markersize=1)

    for i, (p, c) in enumerate(zip(planning_points, current_points)):
        if i % line_interval == 0:
            plt.arrow(c['x'], c['y'], p['x'] - c['x'], p['y'] - c['y'], 
                      color='g', alpha=0.5, width=0.05, head_width=0.2, head_length=0.2, overhang=0.5, length_includes_head=True)
            #plt.plot([p['x'], c['x']], [p['y'], c['y']], linestyle=':', linewidth=1, color='g', marker='o', markersize=1)

    plt.xlabel('X position (m)')
    plt.ylabel('Y position (m)')
    plt.title('Comparison of Trajectories')
    plt.legend()
    plt.grid(True)
    if aspect_ratio:
        plt.gca().set_aspect(aspect_ratio, adjustable='box')
    else:
        plt.gca().set_aspect('equal', adjustable='box')
    if x_limits:
        plt.xlim(x_limits)
    if y_limits:
        plt.ylim(y_limits)
    plt.tight_layout()
    suffix = '_zoomed' if x_limits or y_limits else ''
    plt.savefig(f'trajectory_plot{suffix}.pdf')



if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script_name.py <path_to_file> [<x_min> <x_max> <y_min> <y_max>]")
        sys.exit(1)

    file_path = sys.argv[1]
    planning_points, current_points = extract_data(file_path)
    
    x_limits = None
    y_limits = None
    
    if len(sys.argv) == 6:
        x_limits = (float(sys.argv[2]), float(sys.argv[3]))
        y_limits = (float(sys.argv[4]), float(sys.argv[5]))
    
    #plot_comparison_match(planning_points, current_points, x_limits, y_limits)
    #plot_trajectories_match(planning_points, current_points, x_limits, y_limits)

    plot_comparison(planning_points, current_points, x_limits, y_limits)
    plot_trajectories(planning_points, current_points, x_limits, y_limits, aspect_ratio=0.6)


