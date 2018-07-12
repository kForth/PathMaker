from path import Path, Waypoint, Pathpoint
import math

class Profile:
	def __init__(self, waypoints, max_vel, max_accel, max_jerk, d_t, track_width):
		self.waypoints = waypoints
		self.max_vel = max_vel
		self.max_accel = max_accel
		self.max_jerk = max_jerk
		self.d_t = d_t
		self.track_width = track_width

		self.path = None

	def generate_path(self):
		self.path = Path(self.waypoints, self.track_width)
		self.path.build_path()

		# self.raw_left_profile = self._calc_profile(self.path.get_left_path())
		# self.raw_right_profile = self._calc_profile(self.path.get_right_path())
		self.raw_middle_profile = self._calc_profile(self.path.get_path())
		self.raw_left_profile, self.raw_right_profile = self._calc_dual_profile(self.raw_middle_profile, self.path.get_left_path(), self.path.get_right_path())

	def _calc_profile(self, path):
		last_angle = None

		points = [Profilepoint(0, 0, 0, 0, 0, path[0].x, path[0].y)]
		last_time = 0
		for i in range(1, len(path)):
			pnt = path[i]
			pnt2 = path[i-1]
			seg_dist = math.sqrt((pnt.x - pnt2.x)**2 + (pnt.y - pnt2.y)**2)
			seg_angle = math.atan2((pnt.y - pnt2.y), (pnt.x - pnt2.x))
			if last_angle is not None and seg_angle - last_angle > 100:
				seg_dist *= -1.0

			d_t = self.d_t
			# if seg_dist / d_t > self.max_vel:
			# 	d_t = seg_dist / self.max_vel

			dist = points[-1].dist + seg_dist
			vel = seg_dist / d_t
			if i == 1:
				points[0].vel = vel
			accel = (vel - points[-1].vel) / d_t
			jerk = (accel - points[-1].accel) / d_t
			points.append(Profilepoint(
				time=last_time + d_t,
				dist=dist,
				vel=vel,
				accel=accel,
				jerk=jerk
			))

			last_angle = seg_angle
			last_dist = seg_dist
			last_time = last_time + d_t

		return points

	def _calc_dual_profile(self, cprofile, lpath, rpath):
		l_last_angle = None
		r_last_angle = None

		lpoints = [Profilepoint(0, 0, 0, 0, 0, lpath[0].x, lpath[0].y)]
		rpoints = [Profilepoint(0, 0, 0, 0, 0, rpath[0].x, rpath[0].y)]
		last_time = 0

		d_t = 0.01 / min([
			self.max_accel / max([e.accel for e in self._calc_profile(lpath) + self._calc_profile(rpath)]),
			self.max_vel / max([e.vel for e in self._calc_profile(lpath) + self._calc_profile(rpath)])
		])

		print(
			self.max_accel / max([e.accel for e in self._calc_profile(lpath) + self._calc_profile(rpath)]),
			self.max_vel / max([e.vel for e in self._calc_profile(lpath) + self._calc_profile(rpath)])
		)

		for i in range(1, len(lpath)):
			lpnt = lpath[i]
			lpnt2 = lpath[i-1]
			lseg_dist = math.sqrt((lpnt.x - lpnt2.x)**2 + (lpnt.y - lpnt2.y)**2)
			lseg_angle = math.atan2((lpnt.y - lpnt2.y), (lpnt.x - lpnt2.x))
			if l_last_angle is not None and lseg_angle - l_last_angle > 100:
				lseg_dist *= -1.0

			rpnt = rpath[i]
			rpnt2 = rpath[i-1]
			rseg_dist = math.sqrt((rpnt.x - rpnt2.x)**2 + (rpnt.y - rpnt2.y)**2)
			rseg_angle = math.atan2((rpnt.y - rpnt2.y), (rpnt.x - rpnt2.x))
			if r_last_angle is not None and rseg_angle - r_last_angle > 100:
				rseg_dist *= -1.0

			ldist = lpoints[-1].dist + lseg_dist
			lvel = lseg_dist / d_t
			if i == 1:
				lpoints[0].vel = lvel
			laccel = (lvel - lpoints[-1].vel) / d_t
			ljerk = (laccel - lpoints[-1].accel) / d_t
			lpoints.append(Profilepoint(
				time=last_time + d_t,
				dist=ldist,
				vel=lvel,
				accel=laccel,
				jerk=ljerk,
				x=lpnt.x,
				y=lpnt.y
			))

			rdist = rpoints[-1].dist + rseg_dist
			rvel = rseg_dist / d_t
			if i == 1:
				rpoints[0].vel = rvel
			raccel = (rvel - rpoints[-1].vel) / d_t
			rjerk = (raccel - rpoints[-1].accel) / d_t
			rpoints.append(Profilepoint(
				time=last_time + d_t,
				dist=rdist,
				vel=rvel,
				accel=raccel,
				jerk=rjerk,
				x=rpnt.x,
				y=rpnt.y
			))

			l_last_angle = lseg_angle
			l_last_dist = lseg_dist

			r_last_angle = rseg_angle
			r_last_dist = rseg_dist

			last_time = last_time + d_t

		return lpoints, rpoints

class Profilepoint:
	def __init__(self, time, dist, vel, accel, jerk=0, x=0, y=0):
		self.time = time
		self.dist = dist
		self.vel = vel
		self.accel = accel
		self.jerk = jerk
		self.x = x
		self.y = y

	def to_list(self):
		return [self.time, self.dist, self.vel, self.accel, self.jerk, self.x, self.y]

	
