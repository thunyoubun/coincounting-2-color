#Download images from https://drive.google.com/file/d/1KqllafwQiJR-Ronos3N-AHNfnoBb8I7H/view?usp=sharing

#Bonus from this challenge https://docs.google.com/document/d/1q96VgmpJXlC95h9we-jiuxonEoYrZoqgTD2wjGk5TlI/edit?usp=sharing

import cv2
import numpy as np

def coinCounting(filename,i):
    im = cv2.imread(filename)
    target_size = (int(im.shape[1]/2),int(im.shape[0]/2))
    im = cv2.resize(im,target_size)
    #img = cv2.cvtColor(im,cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)

    #Erase Glare by threshold
    thresh_img = cv2.threshold(gray, 250, 255, cv2.THRESH_BINARY)[1]
    thresh_img = cv2.erode( thresh_img, None, iterations=1 )
    thresh_img  = cv2.dilate( thresh_img, None, iterations=5 )
    result = cv2.inpaint(im, thresh_img, 21, cv2.INPAINT_TELEA) 
    result_hsv = cv2.cvtColor(result,cv2.COLOR_BGR2HSV)
    
    #Mask Color's Bound
    mask_yellow = cv2.inRange(result_hsv, (22, 100, 100), (38, 255, 255))
    mask_blue = cv2.inRange(result_hsv,(93,50,50),(130,255,255))
    
    #Mask MedianBlur
    mask_yellow_blur = cv2.medianBlur(mask_yellow, 5)
    mask_blue_blur = cv2.medianBlur(mask_blue, 5)
    #Morpho
    kernel = np.ones((1,1), np.uint8)
    mask_yellow = cv2.erode(mask_yellow_blur,  None,iterations = 2)
    mask_blue  = cv2.erode(mask_blue_blur, None,iterations = 2)
    # mask_yellow = cv2.dilate(mask_yellow,  None,iterations = 1)
    # mask_blue  = cv2.dilate(mask_blue, None,iterations = 1)
    mask_yellow = cv2.morphologyEx(mask_yellow,cv2.MORPH_OPEN,None,iterations = 2)
    mask_blue  = cv2.morphologyEx(mask_blue,cv2.MORPH_OPEN, None,iterations = 5)

    #Contours
    contours_yellow, hierarchy_yellow = cv2.findContours(mask_yellow, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours_blue, hierarchy_blue = cv2.findContours(mask_blue, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    im_out_contour = im.copy()
    cv2.drawContours(im_out_contour, contours_yellow, -1, (0, 255, 0), 2)
    cv2.drawContours(im_out_contour, contours_blue, -2, (0, 0, 255), 2)

    area_blue = []
    h_blue = []
    w_blue = []

    for cnt in contours_blue:
        x,y,w,h = cv2.boundingRect(cnt)
        area_blue.append(w*h)
        h_blue.append(h)
        w_blue.append(w)

    area_blue.sort()
    h_blue.sort()
    
    overlap_blue = int(0)
    im_out_boundingbox = im.copy()
    
    for cnt in contours_blue:
        x, y, w, h = cv2.boundingRect(cnt)
        #Overlap 3 circles
        if w*h > average(area_blue)*2 or h > average(h_blue)*1.75:
            overlap_blue += 3
            cv2.rectangle(im_out_boundingbox, (x, y), (x + w, y + h), (255, 255, 0), 2)
            image = cv2.rectangle(im_out_boundingbox, (x, y), (x + w, y + h), (255, 255, 0), 2)
            cv2.putText(image, '3', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255,255,0), 2)
        #Overlap 2 circles
        elif w*h > average(area_blue)*1.55 or h > average(h_blue)*1.5 or w > average(w_blue)*1.5:
            overlap_blue += 2
            cv2.rectangle(im_out_boundingbox, (x, y), (x + w, y + h), (255, 0, 0), 2)
            image = cv2.rectangle(im_out_boundingbox, (x, y), (x + w, y + h), (255, 0, 0), 2)
            cv2.putText(image, '2', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255,0,0), 2)
        # 1 Circle
        else:
            overlap_blue += 1
            cv2.rectangle(im_out_boundingbox, (x, y), (x + w, y + h), (0, 0, 255), 2)
            image = cv2.rectangle(im_out_boundingbox, (x, y), (x + w, y + h), (0, 0, 255), 2)
            cv2.putText(image, '1', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,0,255), 2)

    for cnt in contours_yellow:
        x, y, w, h = cv2.boundingRect(cnt)
        cv2.rectangle(im_out_boundingbox, (x, y), (x + w, y + h), (0, 255, 0), 2)
        image = cv2.rectangle(im_out_boundingbox, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(image, '1', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,255,0), 2)

    
    yellow = len(contours_yellow)
    #blue = len(contours_blue)+overlap_blue
    
    print("##### "+ str(i) + " #####")
    print('Yellow = ',yellow)
    print('Blue = ', overlap_blue)
    
    cv2.imwrite('./output_image/box'+str(i)+'.jpg',im_out_boundingbox)
    cv2.imshow("result",result)
    cv2.imshow('im_out_contour',im_out_contour)
    cv2.imshow('im_out_boundingbox', im_out_boundingbox)
    cv2.imshow('Yellow Coin', mask_yellow)
    cv2.imshow('Blue Coin', mask_blue)
    cv2.waitKey()

    return [yellow,overlap_blue]

def average(list):
    return sum(list)/len(list)

def checking():
    value = [[5,8],[6,3],[2,4],[2,4],[1,7],[3,5],[4,3],[5,5],[2,6],[4,2]]
    result = []
    Perfect = int(0)
    Fail = int(0)
    for i in range(1,11):
        e = coinCounting('.\CoinCounting\coin'+str(i)+'.jpg',i)
        if(e == value[i-1]):
            result.append(True)
            Perfect = Perfect+1
            #print("Perfect")
            
        else:
            result.append(False)
            Fail = Fail+1
            #print("Fail")

    print("Result : ", result)
    print("Perfect : ", Perfect)
    print("Fail : ", Fail)

#Counting Coins
checking()