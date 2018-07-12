from quintic_polynomials_planner import quinic_polynomials_planner

import math

class Path:
	def __init__(self, points: list, track_width=None, d_t=0.01):
		self.waypoints = points		
		self.track_width = track_width
		self.d_t = d_t

		self.path = self.left_path = self.right_path = None

	def get_path(self):
		return self.path

	def get_left_path(self):
		return self.left_path

	def get_right_path(self):
		return self.right_path

	def build_path(self):
		self.path = self._calc_main_path()
		if self.track_width is not None:
			self.left_path, self.right_path = self._calc_left_right_paths() 

	def _calc_main_path(self):
		points = list(self.waypoints)
		path_points = []
		last_time = 0
		for i in range(1, len(points)):
		    if points[i].yaw is None:
		        if i < len(points)-1:
		            points[i].append(math.atan2(points[i+1].y - points[i-1].y, points[i+1].x - points[i-1].x))
		        else:
		            points[i].append(math.atan2(points[i].y - points[i-1].y, points[i].x - points[i-1].x))

		    seg_time, seg_x, seg_y, seg_yaw, seg_vel, seg_accel, seg_jerk = quinic_polynomials_planner(
		        sx=points[i - 1].x, 
		        sy=points[i - 1].y, 
		        syaw=points[i - 1].yaw, 
		        sv=0.4 if i > 1 else 0.01,  # 0.3 if i < len(points)-1 else 0.03
		        sa=0.03,  # 0.03

		        gx=points[i].x, 
		        gy=points[i].y, 
		        gyaw=points[i].yaw, 
		        gv=0.4 if i < len(points)-1 else 0.01,  # 0.3 if i < len(points)-1 else 0.03
		        ga=0.03,  # 0.03

		        max_accel=2.0,  # 0.3
		        max_jerk=0.6,  # 0.15
		        dt=self.d_t
		    )
		    for j in range(len(seg_time)):
		    	path_points.append(Pathpoint(
		    		seg_time[j] + last_time, 
		    		seg_x[j], 
		    		seg_y[j], 
		    		seg_yaw[j], 
		    		seg_vel[j], 
		    		seg_accel[j], 
		    		seg_jerk[j], 
		    		points[i-1], 
		    		points[i]
		    	))
		    last_time = path_points[-1].time

		return path_points

	def _calc_left_right_paths(self):
	    left_path = []
	    right_path = []

	    for point in self.path:
	        left_path.append(
	        	Pathpoint(
	        		point.time,
		            point.x - math.sin(point.yaw) * self.track_width / 2,
		            point.y + math.cos(point.yaw) * self.track_width / 2,
		            point.yaw,
		            point.vel,
		            point.accel,
		            point.jerk,
		            point.start_waypoint,
		            point.end_waypoint
		        )
	        )
	        right_path.append(
	        	Pathpoint(
	        		point.time,
		            point.x - math.sin(point.yaw) * -self.track_width / 2,
		            point.y + math.cos(point.yaw) * -self.track_width / 2,
		            point.yaw,
		            point.vel,
		            point.accel,
		            point.jerk,
		            point.start_waypoint,
		            point.end_waypoint
	            )
	       	)

	    return left_path, right_path

	def plot(self, new_plot=True, show=True, plot_middle=True, plot_left=True, plot_right=True, line=None, plot_waypoints=True):
		import matplotlib.pyplot as plt
		if new_plot:
			plt.subplots()
		if plot_middle:
			plt.plot([e.x for e in self.path], [e.y for e in self.path], line if line else "-r")
		if self.left_path and plot_left:
			plt.plot([e.x for e in self.left_path], [e.y for e in self.left_path], line if line else  "-g")
		if self.right_path and plot_right:	
			plt.plot([e.x for e in self.right_path], [e.y for e in self.right_path], line if line else  "-b")
		plt.xlabel("X")
		plt.ylabel("Y")
		plt.grid(True)
		if plot_waypoints:
			plt.plot([e.x for e in self.waypoints], [e.y for e in self.waypoints], 'ro')

		if show:
			plt.show()

class Waypoint:
	def __init__(self, x, y, yaw=None, vel=None):
		self.x = x
		self.y = y
		self.yaw = yaw
		self.vel = vel

	def copy(self):
		return Waypoint(self.x, self.y, self.yaw, self.vel)

class Pathpoint:
	def __init__(self, time, x, y, yaw, vel, accel, jerk, start_waypoint, end_waypoint):
		self.time = time
		self.x = x
		self.y = y
		self.yaw = yaw
		self.vel = vel
		self.accel = accel
		self.jerk = jerk
		self.start_waypoint = start_waypoint
		self.end_waypoint = end_waypoint

	def copy(self):
		return Pathpoint(self.time, self.x, self.y, self.yaw, self.vel, self.accel, self.jerk, self.start_waypoint, self.end_waypoint)

if __name__ == '__main__':
	points = [
		Waypoint(2, 4, 0),
		Waypoint(14, 4, 0),
		Waypoint(20, 12, math.radians(90)),
		Waypoint(20, 17, math.radians(90)),
		Waypoint(24.5, 20.5, math.radians(10))
	]
	path = Path(points, track_width=2)
	path.build_path()
	path.plot()
