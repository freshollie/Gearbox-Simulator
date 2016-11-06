# Gearbox noises for CCD written by freshollie

import pygame
import random
import os
import winsound
# Define some colors
print('Please ignore this window')
BLACK    = (   0,   0,   0)
WHITE    = ( 255, 255, 255)
 
# This is a simple class that will help us print to the screen
# It has nothing to do with the joysticks, just outputing the
# information. This class was written by:

# Simpson College Computer Science
# http://programarcadegames.com/
# http://simpson.edu/computer-science/

class TextPrint:
    def __init__(self):
        self.reset()
        self.font = pygame.font.SysFont("Arial", 16)
 
    def printNl(self, screen, textString):
        textBitmap = self.font.render(textString, True, BLACK)
        screen.blit(textBitmap, [self.x, self.y])
        self.y += self.line_height
         
    def reset(self):
        self.x = 10
        self.y = 10
        self.line_height = 15
         
    def indent(self):
        self.x += 10
         
    def unindent(self):
        self.x -= 10

# All of this was written by me:


class GearStick:
    sounds=['sound 1.wav',
            'sound 2.wav',
            'sound 3.wav',
            'sound 4.wav']
    short='Short.wav'
    
    def __init__(self,joystick,clutchJoystick,buttons,clutchAxis,highLow):
        self.joystick=joystick
        self.high=highLow[1]
        self.low=highLow[0]
        self.modifier=1
        if self.high<self.low:
            self.modifier=-1
        self.clutchJoystick=clutchJoystick
        self.buttons=buttons
        self.clutchAxis=clutchAxis
        self.inGear=False
        self.tryingInGear=False
        self.currentSound=None
        self.lastValues=self.getAllButtons()

    def getAllButtons(self):
        values=[]
        for button in self.buttons:
            values.append(self.joystick.get_button(button))
        return values

    def checkGears(self):
        if not self.inGear:
            buttonStatus=self.getAllButtons()
            for i in range(len(buttonStatus)):
                if buttonStatus[i]==1 and self.lastValues[i]==0:
                    if self.clutchJoystick.get_axis(self.clutchAxis)*self.modifier>abs(self.low+((self.high-self.low)*0.7)):
                        self.inGear=True
                        self.tryingInGear=False
                    else:
                        self.tryingInGear=True
                        winsound.PlaySound(random.choice(self.sounds),winsound.SND_FILENAME|winsound.SND_ASYNC)
        else:
            buttonStatus=self.getAllButtons()
            for i in range(len(buttonStatus)):
                if buttonStatus[i]==0 and self.lastValues[i]==1:
                    if self.clutchJoystick.get_axis(self.clutchAxis)*self.modifier<abs(self.low+((self.high-self.low)*0.7)):
                        winsound.PlaySound(self.short,winsound.SND_FILENAME|winsound.SND_ASYNC)
                    self.inGear=False
        if self.tryingInGear:
            if self.clutchJoystick.get_axis(self.clutchAxis)*self.modifier>abs(self.low+((self.high-self.low)*0.7)):
                winsound.PlaySound("None.wav",winsound.SND_FILENAME|winsound.SND_ASYNC)
                self.tryingInGear=False
                self.inGear=True
        self.lastValues=buttonStatus

class App:

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode([500, 300])
        self.clock = pygame.time.Clock()
        pygame.display.set_caption("City Car Driving clutch noises - By freshollie")
        pygame.joystick.init()
        self.textPrint = TextPrint()
        self.joysticks=[]
        self.gearbuttons=[]
        self.gettingButtonInputs=False
        self.gettingAxisInputs=False
        self.clutch=None
        self.gearJoy=None
        self.gearstick=None
        self.clutchLowHigh=[]
        self.allAxis=[]
        self.stage=0
        for i in range(pygame.joystick.get_count()):
            self.joysticks.append(pygame.joystick.Joystick(i))
            self.joysticks[-1].init()
        self.run()

    def clutchPeddleAssignment(self):
        self.gettingButtonInputs=False
        self.gettingAxisInputs=True

    def findPressedKey(self):
        for j in range(len(self.joysticks)):
            for i in range(self.joysticks[j].get_numbuttons()):
                if self.joysticks[j].get_button(i):
                    if i not in self.gearbuttons:
                        self.gearbuttons.append(i)
                        self.gearJoy=j
                        return

    def findAllAxis(self):
        self.allAxis=[]
        for j in range(len(self.joysticks)):
            for i in range(self.joysticks[j].get_numaxes()):
                self.allAxis.append((j,i,self.joysticks[j].get_axis(i)))

    def findPressedAxis(self):
        for axis in self.allAxis:
            if abs(self.joysticks[axis[0]].get_axis(axis[1])-axis[2])>0.005:
                self.clutch=(axis[0],axis[1])
                return

    def setUpGearStick(self):
        self.gearstick=GearStick(self.joysticks[self.gearJoy],self.joysticks[self.clutch[0]],self.gearbuttons,self.clutch[1],self.clutchLowHigh)

    def run(self):
        done=False
        loadedSave=False
        loaded=False
        while not done:
            self.textPrint.reset()
            self.screen.fill(WHITE)
            self.textPrint.printNl(self.screen, "Welcome To freshollie's City Car Driving Clutch Noise addon")
            self.textPrint.printNl(self.screen, " ")
            self.textPrint.printNl(self.screen, "This addon will make a grinding noise if the user tries to")
            self.textPrint.printNl(self.screen, "change gear without holding down the clutch.")
            self.textPrint.printNl(self.screen, " ")
            self.textPrint.printNl(self.screen, "%s Joysticks found!" %pygame.joystick.get_count())
            self.textPrint.printNl(self.screen, " ")
            if pygame.joystick.get_count()==0:
                self.textPrint.printNl(self.screen, "Sorry, currently this addon only supports joysticks")
                self.textPrint.printNl(self.screen, "AKA Wheels, Gamepads, shifters.. :(")
                self.stage=9
            else:
                if "Clutch Save.txt" in os.listdir('.'):
                    self.textPrint.printNl(self.screen, "Load Previous Save Y/N?")
                    save=True
                else:
                    save=False
                    self.textPrint.printNl(self.screen, "Press any key to continue")
                self.textPrint.printNl(self.screen, " ")
                self.textPrint.indent()

            if self.stage==1:    
                self.textPrint.printNl(self.screen, "Please shift into each gear (No particlular order).")
                self.textPrint.printNl(self.screen, "Please ensure that when you do this no other buttons")
                self.textPrint.printNl(self.screen, "are being pressed.")
                self.textPrint.indent()
                self.textPrint.printNl(self.screen, "Current Gear Buttons; ")
                self.textPrint.indent()
                if self.gearJoy!=None:
                    joystickName=self.joysticks[self.gearJoy].get_name()

                else:
                    joystickName="None"
                self.textPrint.printNl(self.screen, "Joystick: %s" %joystickName)
                self.textPrint.indent()
                self.textPrint.printNl(self.screen, "Gears: %s" %self.gearbuttons)
                for i in range(3):
                    self.textPrint.unindent()
                self.textPrint.printNl(self.screen, "")
                self.textPrint.printNl(self.screen, "Press any key when complete")
                self.gettingButtonInputs=True
                
            elif self.stage==2:
                self.textPrint.printNl(self.screen, "Please press the clutch axis (For now this will not work with buttons)")
                self.textPrint.printNl(self.screen, "Please ensure that when you do this no other buttons are being pressed")
                self.clutchPeddleAssignment()

            elif self.stage==3:
                self.gettingAxisInputs=False
                self.textPrint.printNl(self.screen, "Clutch Pedal;")
                self.textPrint.indent()
                self.textPrint.printNl(self.screen, "Joystick found: %s" %self.joysticks[self.clutch[0]].get_name())
                self.textPrint.indent()
                self.textPrint.printNl(self.screen, "Axis %s: %s" %(self.clutch[1],self.joysticks[self.clutch[0]].get_axis(self.clutch[1])))#
                for i in range(2):
                    self.textPrint.unindent()
                self.textPrint.printNl(self.screen, "")
                self.textPrint.printNl(self.screen, "Is this the correct axis Y/N?")
            elif self.stage==4:
                self.textPrint.printNl(self.screen, "Please let go of the clutch and press any key to continue")
                
            elif self.stage==5:
                self.textPrint.printNl(self.screen, "Please press the clutch to the floor and press any key to continue")

            elif self.stage==6:
                if loadedSave:
                    if not loaded:
                        with open("Clutch Save.txt", "r") as save:
                            listedSave=eval(save.read())

                        self.gearJoy=listedSave[0]
                        self.clutch=listedSave[1]
                        self.gearbuttons=listedSave[2]
                        self.clutchLowHigh=listedSave[3]
                        loaded=True
                    self.textPrint.printNl(self.screen, "Loading Save... ")
                else:
                    if not loaded:
                        with open("Clutch Save.txt", "w") as save:
                            save.write(str([self.gearJoy,self.clutch,self.gearbuttons,self.clutchLowHigh]))
                        loaded=True
                    self.textPrint.printNl(self.screen, "Config Saved...")
                        
                            
                        
                self.textPrint.printNl(self.screen, "The program is now running...")
                if not self.gearstick:
                    self.setUpGearStick()
            
                
            for event in pygame.event.get(): # User did something
                if event.type == pygame.QUIT: # If user clicked close
                    done=True # Flag that we are done so we exit this loop
                 
                # Possible joystick actions: JOYAXISMOTION JOYBALLMOTION JOYBUTTONDOWN JOYBUTTONUP JOYHATMOTION
                if event.type == pygame.JOYBUTTONDOWN:
                    if self.gettingButtonInputs:
                        self.findPressedKey()
                        
                elif event.type == pygame.JOYAXISMOTION:
                    if self.gettingAxisInputs and self.stage==2:
                        self.findPressedAxis()
                        self.stage+=1
                elif event.type == pygame.KEYDOWN:
                    if self.stage==3:
                        if event.key==pygame.K_y:
                            self.stage+=1
                        elif event.key==pygame.K_n:
                            self.stage-=1
                    elif self.stage==1:
                        if self.gearbuttons:
                            self.stage+=1
                    elif self.stage==4:
                        self.clutchLowHigh.append(self.joysticks[self.clutch[0]].get_axis(self.clutch[1]))
                        self.stage+=1
                    elif self.stage==5:
                        self.clutchLowHigh.append(self.joysticks[self.clutch[0]].get_axis(self.clutch[1]))
                        self.stage+=1
                    elif self.stage==9:
                        done=True
                    elif self.stage==6:
                        pass
                    elif save:
                        if event.key==pygame.K_y:
                            self.stage=6
                            loadedSave=True
                        elif event.key==pygame.K_n:
                            self.stage+=1
                    else:   
                        self.stage+=1
                    

            if self.gearstick:
                self.gearstick.checkGears()
            
            if self.stage==2:  
                self.findAllAxis()

            self.clock.tick(20)
            pygame.display.flip()

App()
pygame.quit()
