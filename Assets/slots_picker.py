import cv2 as cv
import pickle


width,height = 168,335

try:
	with open('CarParkPos','rb') as f:
		posList = pickle.load(f)

except:
	posList = []

def mouseClick(events,x,y,flags,params):
	if events == cv.EVENT_LBUTTONDOWN:
		posList.append((x,y))

	if events == cv.EVENT_RBUTTONDOWN:
		for i,pos in enumerate(posList):
			x1,y1 = pos
			if x1<x<x1+width and y1<y<y1+height:
				posList.pop(i)
	with open('CarParkPos','wb') as f:
        	pickle.dump(posList,f)


while True:
	im = cv.imread('slot.jpg')
	ims = cv.resize(im, (720, 640)) 

	for pos in posList:
		cv.rectangle(ims,pos,(pos[0]+width,pos[1]+height),(255,0,255),2)
	cv.imshow('Image',ims)
	cv.setMouseCallback('Image',mouseClick)
	cv.waitKey(1)
