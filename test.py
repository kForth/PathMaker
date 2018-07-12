from profile import Profile, Waypoint
import math	
import matplotlib.pyplot as plt

if __name__ == "__main__":
	points = [
		Waypoint(0.6, 1.2, 0),
		Waypoint(4.2, 1.2, 0),
		Waypoint(6, 3, math.radians(90)),
		Waypoint(5.9, 15*0.3, math.radians(95)),
		Waypoint(24.5*0.3, 20.5*0.3, math.radians(-10))
	]

	profile = Profile(points, 3, 7, 50, 0.01, 0.6)
	profile.generate_path()
	profile.path.plot(show=False)
	print([e.time for e in profile.raw_left_profile])	
	plt.subplots()

	plt.plot([e.time for e in profile.raw_left_profile], [e.dist for e in profile.raw_left_profile], '-g')
	plt.plot([e.time for e in profile.raw_left_profile], [e.vel for e in profile.raw_left_profile], ':g')
	plt.plot([e.time for e in profile.raw_left_profile], [e.accel for e in profile.raw_left_profile], '-.g')

	plt.plot([e.time for e in profile.raw_right_profile], [e.dist for e in profile.raw_right_profile], '-b')
	plt.plot([e.time for e in profile.raw_right_profile], [e.vel for e in profile.raw_right_profile], ':b')
	plt.plot([e.time for e in profile.raw_right_profile], [e.accel for e in profile.raw_right_profile], '-.b')

	# plt.plot([e.time for e in profile.raw_middle_profile], [e.dist for e in profile.raw_middle_profile], '-r')
	# plt.plot([e.time for e in profile.raw_middle_profile], [e.vel for e in profile.raw_middle_profile], ':r')
	# plt.plot([e.time for e in profile.raw_middle_profile], [e.accel for e in profile.raw_middle_profile], '-.r')

	plt.xlabel("s")
	plt.ylabel("m")
	plt.show()