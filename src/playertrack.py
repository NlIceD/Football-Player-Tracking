import numpy as np
import cv2
import cv
import time
import datetime
import topview
import sideline
import huematcher
import playerDistance
import matplotlib.path as path

bg_filpath = '..//img//side-view.jpg'
vid_filepath = '..//vid//panorama.mov'
writeVedioName = '..//vid//offside.avi'

def track_player(hg_matrix):
	bg_img = cv2.imread(bg_filpath)
	gray_bg_img = cv2.cvtColor(bg_img, cv2.COLOR_BGR2GRAY)
	vid_cap = cv2.VideoCapture(vid_filepath)
	frame_height = vid_cap.get(cv.CV_CAP_PROP_FRAME_HEIGHT)
	frame_width = vid_cap.get(cv.CV_CAP_PROP_FRAME_WIDTH)
	frame_count = vid_cap.get(cv.CV_CAP_PROP_FRAME_COUNT)

	#create a new video to draw lines for indicating offside players
	fps = vid_cap.get(cv.CV_CAP_PROP_FPS)
	# videoWriter = cv2.VideoWriter(writeVedioName, -1, int(fps), (int(frame_width), int(frame_height)))

    #flag to indicate whether computing player moving distance done
	flag = True

	fieldPolygon = path.Path(np.array([[140,313],[1065,50],[1675,50],[2562,263],[1093,264]]))
	first_player_pos = list()
	firstFrame = True
	while True:
		aval, img = vid_cap.read()
		if not aval:
			break

		gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

		bg_delta = cv2.absdiff(gray_bg_img, gray_img)

		

		threshold = cv2.threshold(bg_delta, 30, 255, cv2.THRESH_BINARY)[1]
		

		kernel = np.matrix([[0,0,0],[1,1,1],[0,0,0]],np.uint8)
		threshold = cv2.dilate(threshold, None, iterations=3)
		
		contours, _ = cv2.findContours(threshold.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
		players_pos = list()
		
		c = 0 
		for cn in contours:

			(x, y, w, h) = cv2.boundingRect(cn)
			feet_coord = [float(x + int(w/2.0)), float(y + h)]
			
			rect_area = cv2.contourArea(cn)
			if(not fieldPolygon.contains_point((feet_coord[0], feet_coord[1]))):
				continue

			if(y > frame_height/4):
				if(rect_area < 40):
					continue
			
			if(w > h*1.4 or rect_area < 10):
				continue

			player_hue = huematcher.average_hue(x, y, w, h, img)

			if(huematcher.is_red_player(player_hue)):
				cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)
			elif(huematcher.is_blue_player(player_hue)):
				cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
			elif(huematcher.is_green_keeper(player_hue)):
				cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 5)
			elif(huematcher.is_white_keeper(player_hue)):
				cv2.rectangle(img, (x, y), (x + w, y + h), (255, 255, 255), 5)
			else:
				cv2.rectangle(img, (x, y), (x + w, y + h), (255, 255, 255), 1)
			players_pos.append(feet_coord)
			c +=1

		if(firstFrame):
			first_player_pos = list(players_pos)
			firstFrame = False
		top_img = topview.create_topview(hg_matrix, players_pos)
		img=cv2.resize(img,(0,0),fx=0.6,fy=0.6)
		cv2.imshow("Player detection", img)
		cv2.imshow("Top image", top_img)
		key = cv2.waitKey(41) & 0xFF
	playerDistance.compute(players_pos, vid_filepath)
	vid_cap.release()
	cv2.destroyAllWindows()