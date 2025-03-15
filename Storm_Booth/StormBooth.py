import fnmatch
import tkinter
import customtkinter
import cv2
from PIL import Image, ImageTk
import datetime
import time
import os
from tkinter import filedialog
import pathlib
import imageio
import platform
import numpy as np
import math
#import mediapipe




################ GLOBAL MEMORY STATES ################

OpSystem = ''

## automatic camera input setting ##
cameraInputNumber = int
for i in reversed(range(2)):
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        cameraInputNumber = i
        print("Camera found: ", cameraInputNumber)
        break
    elif not cap.isOpened():
        print ("No Camera Input: ", i)

## Sets execution type for Windows or MacOS ##

OpSystem = str(platform.system())
if OpSystem == 'Darwin':
    OpSystem = 'MacOS'
print('Executing Storm Booth for ' + OpSystem)

## Resolution Variables ##
screenResolution = (1920, 1080) #[MANUALLY]
start_windowResolution = tuple(int(i/2) for i in screenResolution) # dividing by 2

## Switches ##
viewModeSwitch = False
screenshotSwitch = False
gifSwitch = False
filter1Switch = False
filter2Switch = False
filter3Switch = False
filter4Switch = False
#test=ImageTk.PhotoImage(Image.open('camera.png').resize((40, 40)))
#print(test)

####### Snapshot path #######
if OpSystem == 'Windows':
    path = str(pathlib.Path().resolve()) + '\Snapshots'
elif OpSystem == 'MacOS':
    path = str(pathlib.Path().resolve()) + '/Snapshots'
selectPath = ''

####### Snapshot list #######
lst = []

####### File Format Selection #######
selectedFormat = '.jpg' #default selection

###### GIF ########
gifframes = []
gifCompIndex = 0

## snow filter ##
snow_frames = []
snow_frames_index = 0

## loading snow filter ##
print("Loading Snow Filter...")
if OpSystem == 'Windows':
    vidcap = cv2.VideoCapture('assets\snow_Trim.mp4')
elif OpSystem == 'MacOS':
    vidcap = cv2.VideoCapture('assets/snow_Trim.mp4')
success,image = vidcap.read()
count = 0
success = True
while success:
    success,image = vidcap.read()
    #image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    snow_frames.append(image)
    if cv2.waitKey(10) == 27:  # exit if Escape is hit
        print("Loading Succeded")
        break
    count += 1
print("Loading Succeded")





################ GLOBAL DESIGN STATES ################
customtkinter.set_appearance_mode("dark")
windowBackgroundColor = "#212325"
fg_button_color = "#C9D1D9"
bg_button_color = windowBackgroundColor
hover_button_color ="#343942"
text_button_color = "#000000"
button_corner_radius = 6
button_border_width = 1




############ APP CLASS ##############
#####################################

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.geometry(f"{start_windowResolution[0]}x{start_windowResolution[1]}")
        #self.configure(bg = windowBackgroundColor)
        self.title("Storm Booth")
        
        # TURN ON/OFF WINDOW BORDER
        #self.overrideredirect(True)

    
        ############## GRID LAYOUT ################

        tkinter.Grid.rowconfigure(self, 1, weight=200)
        tkinter.Grid.rowconfigure(self, 2, weight=0)
        tkinter.Grid.rowconfigure(self, 3, weight=1)
        
        tkinter.Grid.columnconfigure(self, 1, weight=1)
        tkinter.Grid.columnconfigure(self, 2, weight=1)
        tkinter.Grid.columnconfigure(self, 3, weight=1)
        tkinter.Grid.columnconfigure(self, 4, weight=1)
        tkinter.Grid.columnconfigure(self, 11, weight=1)
        tkinter.Grid.columnconfigure(self, 12, weight=1)
        tkinter.Grid.columnconfigure(self, 13, weight=1)

        ################ FUNCTIONS ################
        

        ## resize correctly ##
        def resizeImage(img,camLabelWidth,camLabelHeight):
            imgWidth = img.shape[1]
            imgHeight = img.shape[0]
            relOfHeightToWidth = imgHeight/imgWidth
            relOfWidthToHeight = imgWidth/imgHeight
            if camLabelHeight > camLabelWidth:
                img = cv2.resize(img, (camLabelWidth,int(camLabelWidth*relOfHeightToWidth)), interpolation=cv2.INTER_LINEAR)
                return img
            else:
                img = cv2.resize(img, (int(camLabelHeight*relOfWidthToHeight),camLabelHeight), interpolation=cv2.INTER_LINEAR)
                return img

        ## Screenshot ##
        def takeScreenshot(img):
            global screenshotSwitch
            global path

            if viewModeSwitch == False:
                output = img.copy()
                output = cv2.cvtColor(output, cv2.COLOR_RGB2BGR)
                output_name = str(datetime.datetime.now().today()).replace(":", " ") + selectedFormat
                cv2.imwrite(os.path.join(path, f'{output_name}'), output)
                refresh_list()
                screenshotSwitch = False
            else: 
                print('Screenshot not possible in View Mode')
                screenshotSwitch = False
        


        ## List ##
        def refresh_list():
            lst.delete(0, tkinter.END) #delete all list elemts
            list_images = [os.path.join(f)
            for dirpath, dirnames, files in os.walk(path)
                for extension in ['jpg', 'jpeg', 'gif', 'png']
                    for f in fnmatch.filter(files, '*' + extension)]
            for img in list_images:
                lst.insert(tkinter.END, img) 

        def delete_from_list():
            global path
            item = lst.get(tkinter.ANCHOR)
            lst.delete(tkinter.ANCHOR)
            remove_path = f"{path}/{item}"
            os.remove(remove_path)
        
        def select_file_destination():
            global path
            path = filedialog.askdirectory()
            refresh_list()
            pathLabel.configure(text=path)

        def show_from_list(event):
            global viewModeSwitch
            global selectPath
            selection = event.widget.curselection()
            if selection:
                if OpSystem == 'Windows':
                    item = lst.get(tkinter.ANCHOR)
                    selectPath = str(path) + '\\' +  str(item)
                elif OpSystem == 'MacOS':
                    item = lst.get(tkinter.ANCHOR)
                    selectPath = str(path) + '/' +  str(item)
                else: selectPath = 'Could not set destination path.'
            viewModeSwitch = True

        ## GIF ##
        def saveGIF(gifframes):
            global gifCompIndex
            if OpSystem == 'Windows':
                statusLabel.configure(text='Saving GIF ...')
                self.update()
                with imageio.get_writer(path + '\\' + str(datetime.datetime.now().today()).replace(":", " ") + '.gif', mode="I") as writer:
                    for idx,frame in enumerate(gifframes):
                        writer.append_data(frame)
                        idx + 1
                gifCompIndex = 0
                refresh_list()
                statusLabel.configure(text='GIF Saved!')
                self.update()
                time.sleep(1)
                statusLabel.configure(text='')
                self.update()
            elif OpSystem == 'MacOS':
                statusLabel.configure(text='Saving GIF ...')
                self.update()
                with imageio.get_writer(path + '/Snapshots' + str(datetime.datetime.now().today()).replace(":", " ") + '.gif', mode="I") as writer:
                    for idx,frame in enumerate(gifframes):
                        writer.append_data(frame)
                        idx + 1
                gifCompIndex = 0
                refresh_list()
                statusLabel.configure(text='GIF Saved!')
                self.update()
                time.sleep(1)
                statusLabel.configure(text='')
                self.update()



        def showGIF(current_gif_path,camLabelWidth,camLabelHeight):
            statusLabel.configure(text='Loading GIF ...')
            self.update()
            frameCnt = Image.open(selectPath).n_frames ## takes a few secons!
            gifframes_view = [tkinter.PhotoImage(file=selectPath,format = 'gif -index %i' %(gifshowindex)) for gifshowindex in range(frameCnt)]
            statusLabel.configure(text='')
            self.update()
            gifshowindex = 0
            while current_gif_path == selectPath:
                if viewModeSwitch == True:
                    frame = gifframes_view[gifshowindex]
                    #frame = resizeImage(frame,camLabelWidth,camLabelHeight)
                    gifshowindex = gifshowindex+1
                    if gifshowindex == frameCnt:
                        gifshowindex = 0
                    camLabel['image'] = frame
                    self.update()
                    time.sleep(0.2)
                else:
                    statusLabel.configure(text='')
                    self.update()
                    break
            

            
        ## Option Menu ##
        def optionmenu_callback(choice):
            global selectedFormat
            selectedFormat = choice
            if choice == '.gif':
                #recButton.configure(image=ImageTk.PhotoImage(Image.open('./Storm_Booth/icons/rec.png').resize((40, 40))))
                #self.update()
                recButton.configure(text='REC')
                recButton.configure(command=changeGifSwitch)
            elif choice != '.gif':
                #recButton.configure(image=ImageTk.PhotoImage(Image.open('./Storm_Booth/icons/camera.png').resize((40, 40))))
                recButton.configure(text='')
                recButton.configure(command=changeScreenshotSwitch)

        ## Filter ##
        def BlackAndWhite_Filter(img):
            output = img.copy()
            output = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            return output

        def Negative_Filter(img):
            output = img.copy()
            output = cv2.bitwise_not(img) # /output = abs(255-img)
            return output

        def Disco_Filter(img):
            output = img.copy()
            output = cv2.Canny(output, 100, 100)
            (B, G, R) = cv2.split(img)
            B_cny = cv2.Canny(B, 50, 200)
            G_cny = cv2.Canny(G, 50, 200)
            R_cny = cv2.Canny(R, 50, 200)
            output = cv2.merge([B_cny, G_cny, R_cny])
            return output
        
        def Snow_Filter(img):
            global snow_frames_index
            output = img.copy()
            
            if snow_frames_index < (len(snow_frames) - 1):
                currentSnowFrame = snow_frames[snow_frames_index]
                currentSnowFrame = cv2.resize(currentSnowFrame, (img.shape[1],img.shape[0]), interpolation=cv2.INTER_LINEAR)
                currentSnowFrame = cv2.cvtColor(currentSnowFrame, cv2.COLOR_BGR2RGB)
                

                '''
                # better filter, but slow
                black = [0,0,0]
                for x in range(currentSnowFrame.shape[0]-1):
                    for y in range(currentSnowFrame.shape[1]-1):
                            if all(currentSnowFrame[x][y]) == all(black):
                                output[x][y] = currentSnowFrame[x][y] + output[x][y]
                            else: output[x][y]= currentSnowFrame[x][y]
                '''
                
                # worse filter, but fast
                output = output + currentSnowFrame 
                snow_frames_index = snow_frames_index + 1
            else:
                snow_frames_index = 0
                currentSnowFrame = snow_frames[snow_frames_index]
                currentSnowFrame = cv2.resize(currentSnowFrame, (img.shape[1],img.shape[0]), interpolation=cv2.INTER_LINEAR)
                #currentSnowFrame = cv2.cvtColor(currentSnowFrame, cv2.COLOR_BGR2RGB)
                output = output + currentSnowFrame
                snow_frames_index = snow_frames_index + 1
            return output

        
        ## hand gesture recognition
        def recognize_hand(img,ret):

            frame = img
            #frame=cv2.flip(frame,1)
            kernel = np.ones((3,3),np.uint8)
            
            #define region of interest
            roi=frame[100:300, 100:300]
            
            cv2.rectangle(frame,(100,100),(300,300),(0,255,0),0)    
            hsv = cv2.cvtColor(roi, cv2.COLOR_RGB2HSV)

            # define range of skin color in HSV
            lower_skin = np.array([0,20,70], dtype=np.uint8)
            upper_skin = np.array([20,255,255], dtype=np.uint8)
            
            #extract skin colur imagw  
            mask = cv2.inRange(hsv, lower_skin, upper_skin)
            #extrapolate the hand to fill dark spots within
            mask = cv2.dilate(mask,kernel,iterations = 4)
            #blur the image
            mask = cv2.GaussianBlur(mask,(5,5),100) 
            
            
            
            #find contours
            contours,hierarchy= cv2.findContours(mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        
            #find contour of max area(hand)
            cnt = max(contours, key = lambda x: cv2.contourArea(x))
            
            #approx the contour a little
            epsilon = 0.0005*cv2.arcLength(cnt,True)
            approx= cv2.approxPolyDP(cnt,epsilon,True)
        
            
            #make convex hull around hand
            hull = cv2.convexHull(cnt)
            
            #define area of hull and area of hand
            areahull = cv2.contourArea(hull)
            areacnt = cv2.contourArea(cnt)
        
            #find the percentage of area not covered by hand in convex hull
            arearatio=((areahull-areacnt)/areacnt)*100
        
            #find the defects in convex hull with respect to hand
            hull = cv2.convexHull(approx, returnPoints=False)
            defects = cv2.convexityDefects(approx, hull)
            
            # l = no. of defects
            l=0
            
            #code for finding no. of defects due to fingers
            for i in range(defects.shape[0]):
                s,e,f,d = defects[i,0]
                start = tuple(approx[s][0])
                end = tuple(approx[e][0])
                far = tuple(approx[f][0])
                pt= (100,180)
                
                
                # find length of all sides of triangle
                a = math.sqrt((end[0] - start[0])**2 + (end[1] - start[1])**2)
                b = math.sqrt((far[0] - start[0])**2 + (far[1] - start[1])**2)
                c = math.sqrt((end[0] - far[0])**2 + (end[1] - far[1])**2)
                s = (a+b+c)/2
                ar = math.sqrt(s*(s-a)*(s-b)*(s-c))
                
                #distance between point and convex hull
                d=(2*ar)/a
                
                # apply cosine rule here
                angle = math.acos((b**2 + c**2 - a**2)/(2*b*c)) * 57
                
            
                # ignore angles > 90 and ignore points very close to convex hull(they generally come due to noise)
                if angle <= 90 and d>30:
                    l += 1
                    cv2.circle(roi, far, 3, [255,0,0], -1)
                
                #draw lines around hand
                cv2.line(roi,start, end, [0,255,0], 2)
                
                
            l+=1
            
            #print corresponding gestures which are in their ranges
            font = cv2.FONT_HERSHEY_SIMPLEX
            if l==1:
                if areacnt<2000:
                    cv2.putText(frame,'Put hand in the box',(0,50), font, 2, (0,0,255), 3, cv2.LINE_AA)
                else:
                    if arearatio<12:
                        cv2.putText(frame,'0',(0,50), font, 2, (0,0,255), 3, cv2.LINE_AA)
                    elif arearatio<17.5:
                        cv2.putText(frame,'Best of luck',(0,50), font, 2, (0,0,255), 3, cv2.LINE_AA)
                    
                    else:
                        cv2.putText(frame,'1',(0,50), font, 2, (0,0,255), 3, cv2.LINE_AA)
                        
            elif l==2:
                cv2.putText(frame,'2',(0,50), font, 2, (0,0,255), 3, cv2.LINE_AA)
                
            elif l==3:
            
                if arearatio<27:
                        cv2.putText(frame,'3',(0,50), font, 2, (0,0,255), 3, cv2.LINE_AA)
                else:
                        cv2.putText(frame,'ok',(0,50), font, 2, (0,0,255), 3, cv2.LINE_AA)
                        
            elif l==4:
                cv2.putText(frame,'4',(0,50), font, 2, (0,0,255), 3, cv2.LINE_AA)
                
            elif l==5:
                cv2.putText(frame,'5',(0,50), font, 2, (0,0,255), 3, cv2.LINE_AA)
                
            elif l==6:
                cv2.putText(frame,'reposition',(0,50), font, 2, (0,0,255), 3, cv2.LINE_AA)
                
            else :
                cv2.putText(frame,'reposition',(10,50), font, 2, (0,0,255), 3, cv2.LINE_AA)
                
            #show the windows
            cv2.imshow('mask',mask)
            #cv2.imshow('frame',frame)
        
            return frame
        
        
       
        

        


        ################ FILTER SWITCH FUNCTIONS ################
        
        def changeScreenshotSwitch():
            global screenshotSwitch
            global gifSwitch
            if screenshotSwitch == False:
                screenshotSwitch = True
                gifSwitch = False
            else:
                screenshotSwitch = False
        
        def changeGifSwitch():
            global gifSwitch
            global gifframes
            global screenshotSwitch
            if gifSwitch == False:
                gifSwitch = True
                screenshotSwitch = False
            elif gifSwitch == True:
                gifSwitch = False
                saveGIF(gifframes)
                recButton.configure(text='REC')
                gifframes = []
        
        def changeFilter1Switch():
            global filter1Switch
            global filter2Switch
            global filter3Switch
            global filter4Switch
            global viewModeSwitch
            viewModeSwitch = False
            if filter1Switch == False:
                filter1Switch = True
                filter2Switch = False
                filter3Switch = False
                filter4Switch = False
            else:
                filter1Switch = False

        def changeFilter2Switch():
            global filter1Switch
            global filter2Switch
            global filter3Switch
            global filter4Switch
            global viewModeSwitch
            viewModeSwitch = False
            if filter2Switch == False:
                filter1Switch = False
                filter2Switch = True
                filter3Switch = False
                filter4Switch = False
            else:
                filter2Switch = False

        def changeFilter3Switch():
            global filter1Switch
            global filter2Switch
            global filter3Switch
            global filter4Switch
            global viewModeSwitch
            viewModeSwitch = False
            if filter3Switch == False:
                filter1Switch = False
                filter2Switch = False
                filter3Switch = True
                filter4Switch = False
            else:
                filter3Switch = False

        def changeFilter4Switch():
            global filter1Switch
            global filter2Switch
            global filter3Switch
            global filter4Switch
            global viewModeSwitch
            viewModeSwitch = False
            if filter4Switch == False:
                filter1Switch = False
                filter2Switch = False
                filter3Switch = False
                filter4Switch = True
            else:
                filter4Switch = False



        def test():
            print("test")


        
        ################ LABELS ################

        ## Camera Label ##
        camLabel = tkinter.Label(self, bg = windowBackgroundColor )
        camLabel.grid(row=1, column=1, rowspan=2, columnspan=4, sticky='nesw')

        ## File Destination Path Label ##
        pathLabel = customtkinter.CTkLabel(master=self, text=path, corner_radius=0,)
        pathLabel.grid(row=2, column=11, columnspan=3, sticky='w')

        ## Status Label ##
        statusLabel = customtkinter.CTkLabel(master=self, text='', corner_radius=0)
        statusLabel.grid(row=2, column=1, columnspan=4, sticky='ew')



        ################ SCROLLABLE LISTS #################
        
        lst = tkinter.Listbox(self, highlightthickness=0)
        lst.grid(row=1, column=11, columnspan=3, sticky='nesw')
        lst.bind("<<ListboxSelect>>", show_from_list)

        ctk_listbox_scrollbar = customtkinter.CTkScrollbar(self, command=lst.yview)
        ctk_listbox_scrollbar.grid(row=1, column=14, sticky='nes')
        lst.configure(yscrollcommand=ctk_listbox_scrollbar.set)



        ################ OPTION MENUS #################

        formatBox = customtkinter.CTkOptionMenu(master=self,
                                                    values=[".jpg", ".png", ".gif"],
                                                    fg_color=fg_button_color,
                                                    text_color=text_button_color,
                                                    corner_radius=6,
                                                    dropdown_color=fg_button_color,
                                                    dropdown_hover_color=hover_button_color,
                                                    dropdown_text_color=text_button_color,
                                                    button_color=fg_button_color,
                                                    command=optionmenu_callback)
        formatBox.grid(row=2, column=13, sticky='nesw')
        formatBox.set(".jpg")  # set initial value



        ################ BUTTONS ################
        
        ## Filter 1 Button ##
        FilterButton1 = customtkinter.CTkButton(master=self,
                                                   fg_color=fg_button_color,
                                                   #bg_color=windowBackgroundColor,
                                                   hover_color=hover_button_color,
                                                   border_width=button_border_width,
                                                   border_color=windowBackgroundColor,
                                                   corner_radius=button_corner_radius,
                                                   text='Black and White',
                                                   text_color=text_button_color,
                                                   command= changeFilter1Switch)
        FilterButton1.grid(row=3, column=1, sticky='nesw')
        
        ## Filter 2 Button ##
        FilterButton2 = customtkinter.CTkButton(master=self,
                                                   fg_color=fg_button_color,
                                                   #bg_color=windowBackgroundColor,
                                                   hover_color=hover_button_color,
                                                   border_width=button_border_width,
                                                   border_color=windowBackgroundColor,
                                                   corner_radius=button_corner_radius,
                                                   text='Negative',
                                                   text_color=text_button_color,
                                                   command= changeFilter2Switch)
        FilterButton2.grid(row=3, column=2, sticky='nesw')
        
        ## Filter 3 Button ##
        FilterButton3 = customtkinter.CTkButton(master=self,
                                                   fg_color=fg_button_color,
                                                   #bg_color=windowBackgroundColor,
                                                   hover_color=hover_button_color,
                                                   border_width=button_border_width,
                                                   border_color=windowBackgroundColor,
                                                   corner_radius=button_corner_radius,
                                                   text='Disco',
                                                   text_color=text_button_color,
                                                   command= changeFilter3Switch)
        FilterButton3.grid(row=3, column=3, sticky='nesw')

        ## Filter 3 Button ##
        FilterButton3 = customtkinter.CTkButton(master=self,
                                                   fg_color=fg_button_color,
                                                   #bg_color=windowBackgroundColor,
                                                   hover_color=hover_button_color,
                                                   border_width=button_border_width,
                                                   border_color=windowBackgroundColor,
                                                   corner_radius=button_corner_radius,
                                                   text='Let it snow',
                                                   text_color=text_button_color,
                                                   command= changeFilter4Switch)
        FilterButton3.grid(row=3, column=4, sticky='nesw')
        
        ## REC Button ##
        recButton = customtkinter.CTkButton(master=self,
                                                   fg_color=fg_button_color,
                                                   #bg_color=windowBackgroundColor,
                                                   hover_color=hover_button_color,
                                                   border_width=button_border_width,
                                                   border_color=windowBackgroundColor,
                                                   corner_radius=button_corner_radius,
                                                   text='',
                                                   text_color=text_button_color,
                                                   image=ImageTk.PhotoImage(Image.open('./Storm_Booth/icons/camera.png').resize((40, 40))),
                                                   command = changeScreenshotSwitch)
        recButton.grid(row=3, column=11, sticky='nesw')
        
        ## DELETE Button ##
        deleteButton = customtkinter.CTkButton(master=self,
                                                   fg_color=fg_button_color,
                                                   #bg_color=windowBackgroundColor,
                                                   hover_color=hover_button_color,
                                                   border_width=0,
                                                   border_color=windowBackgroundColor,
                                                   corner_radius=button_corner_radius,
                                                   text='DELETE',
                                                   text_color=text_button_color,
                                                   command = delete_from_list)
        deleteButton.grid(row=3, column=12, sticky='nesw')

        ## File Destination Button ##
        fileDestinationButton = customtkinter.CTkButton(master=self,
                                                   fg_color=fg_button_color,
                                                   #bg_color=windowBackgroundColor,
                                                   hover_color=fg_button_color,
                                                   border_width=button_border_width,
                                                   border_color=windowBackgroundColor,
                                                   corner_radius=button_corner_radius,
                                                   text='',
                                                   text_color=text_button_color,
                                                   image=ImageTk.PhotoImage(Image.open('./Storm_Booth/icons/file.png').resize((28, 28))),
                                                   command = select_file_destination)
        fileDestinationButton.grid(row=3, column=13, sticky='nesw')

        


        ################ MAIN VIDEO STREAM ################

        def camLoop():

            while True:
                global viewModeSwitch

                ret, img = cap.read()
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                camLabelWidth, camLabelHeight = camLabel.winfo_width(), camLabel.winfo_height()

                '''
                try:
                    img = recognize_hand(img,ret)
                except: pass
                '''
                    

                ## Checking for Filter 1 Switch
                if filter1Switch == True:
                    img = BlackAndWhite_Filter(img)
                else: pass

                ## Checking for Filter 2 Switch 
                if filter2Switch == True:
                    img = Negative_Filter(img)
                else: pass

                ## Checking for Filter 3 Switch 
                if filter3Switch == True:
                    img = Disco_Filter(img)
                else: pass
                
                ## Checking for Filter 4 Switch 
                if filter4Switch == True:
                    img = Snow_Filter(img)
                else: pass

                ## Check for Screenshot Switch
                if screenshotSwitch == True:
                    takeScreenshot(img)
                    ## Screenshot Animation ##
                    blank_image = np.zeros((img.shape[0],img.shape[1],3), np.uint8)
                    blank_image[:,:] = (255,255,255)
                    blank_image = ImageTk.PhotoImage(Image.fromarray(blank_image))
                    camLabel['image'] = blank_image
                    self.update()
                    time.sleep(0.15)
                else: pass

                ## Check for GIF Switch
                if gifSwitch == True:
                    global gifframes
                    global gifCompIndex
                    recButton.configure(text='recording*')
                    if gifCompIndex % 10 == 0:
                        gifframes.append(img)
                    else: pass
                    gifCompIndex = gifCompIndex + 1
                
                ## check for video switch mode ##
                if viewModeSwitch == True:
                    try:
                        ## if GIF
                        if '.gif' in selectPath:
                            current_gif_path = selectPath
                            showGIF(current_gif_path,camLabelWidth,camLabelHeight)  
                        ## if Foto
                        else:
                            img = cv2.imread(selectPath)
                            img = resizeImage(img,camLabelWidth,camLabelHeight)
                            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                            img = ImageTk.PhotoImage(Image.fromarray(img))
                            camLabel['image'] = img
                    except:
                        viewModeSwitch = False
                        _, img = cap.read()
                        img = resizeImage(img,camLabelWidth,camLabelHeight)
                        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                        img = ImageTk.PhotoImage(Image.fromarray(img))
                        camLabel['image'] = img
                else:
                    img = resizeImage(img,camLabelWidth,camLabelHeight)
                    img = ImageTk.PhotoImage(Image.fromarray(img))
                    camLabel['image'] = img

                self.update()
        



        refresh_list()
        camLoop()




################ CREATE OBJECT OF STORMBOOTH CLASS ################
app = App()