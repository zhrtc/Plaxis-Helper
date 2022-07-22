# All right reserved by syfok25
# https://github.com/syfok25/PlaxisPlateHelper
# Forked here for testing

import tkinter as tk
from tkinter import *
from unittest import skip
from plxscripting.easy import *
from plxscripting.plx_scripting_exceptions import PlxScriptingError 
import xlsxwriter
import os

class MainW(Tk):

    def __init__(self, parent):
        Tk.__init__(self, parent)
        self.parent = parent
        self.mainWidgets()

    def mainWidgets(self):
        self.title('Plaxis Plate Helper v1')
        self.geometry('250x130')
        #variables
        self.outputport = tk.IntVar(value=10000)
        self.password = tk.StringVar()

        #labels
        self.label_port = tk.Label(self, text='Output Port:')
        self.entry_port = tk.Entry(self,textvariable=self.outputport) 
        self.label_pw = tk.Label(self, text='Password:')
        self.entry_pw = tk.Entry(self,textvariable=self.password) 
        self.connect_button = tk.Button(self, text="Connect", command=self.SelectPhases)

        #layout
        self.options = {'padx': 5, 'pady': 5}
        self.label_port.grid(row = 0, column = 0, sticky = tk.NW, **self.options)
        self.entry_port.grid(row = 0, column = 1, sticky = tk.NW, **self.options)
        self.label_pw.grid(row = 1, column = 0, sticky = tk.NW, **self.options)
        self.connect_button.grid(row = 2, column = 1, sticky = tk.NW, **self.options)
        self.entry_pw.grid(row = 1, column = 1, sticky = tk.NW, **self.options)

    def SelectPhases(self):
        try:
            #new window for phase selection
            self.plxinput, self.plxoutput = new_server('localhost', self.outputport.get(), password=self.password.get(), timeout=5)
            self.newWindow = Toplevel(self)
            self.phasecheckbox = tk.Frame(self.newWindow)
            self.phasecheckbox.grid(row = 0, column = 0, sticky = tk.N, **self.options)
            self.phases = tk.Label(self.phasecheckbox, text="Phases",font='Helvetica 12 bold')
            self.phases.grid(row = 0, column = 0, sticky = tk.W, **self.options, columnspan=2)

            #tabulate phases
            self.outputphase={}
            row_n = 1
            for phase in self.plxoutput.Phases[0:]:
                self.outputphase[str(phase.Number)] = tk.IntVar()
                self.checkbox = tk.Checkbutton(self.phasecheckbox, text=phase.Identification, var=self.outputphase[str(phase.Number)])
                self.checkbox.grid(row = row_n, column = 0, sticky = tk.NW, pady = 2)
                row_n += 1
            print("Connected to Plaxis")
            print("Phase Checkbox Created")
            self.SelectPlate()
            try:
                self.label_error.destroy()
            except:
                pass
        except:
            self.label_error = tk.Label(self, text='Connection failed, check port/password')
            self.label_error.grid(row = 3, column = 0, sticky = tk.NW, **self.options, columnspan=2)
            self.newWindow.destroy()
    
    def SelectPlate(self):
        #window for plate selection
        self.selectplate = tk.Frame(self.newWindow)
        self.selectplate.grid(row = 0, column = 1, sticky = tk.NE, **self.options)
        self.plate = tk.Label(self.selectplate, text="Plate",font='Helvetica 12 bold')
        self.plate.grid(row = 0, column = 0, sticky = tk.W, **self.options, columnspan=2)

        #variables
        self.x_co=tk.StringVar()
        self.y_co=tk.StringVar()
        self.MatID=tk.StringVar()
        self.filename=tk.StringVar()
        self.status = tk.StringVar()

        #labels
        self.label_x = tk.Label(self.selectplate, text='X:')
        self.entry_x = tk.Entry(self.selectplate,textvariable=self.x_co) 
        self.label_y = tk.Label(self.selectplate, text='Y:')
        self.entry_y = tk.Entry(self.selectplate,textvariable=self.y_co) 
        self.label_mat = tk.Label(self.selectplate, text='Material ID:')
        self.entry_mat = tk.Entry(self.selectplate,textvariable=self.MatID) 
        self.label_filename = tk.Label(self.selectplate, text='Filename:')
        self.entry_filename = tk.Entry(self.selectplate,textvariable=self.filename)
        self.label_attribute = tk.Label(self.selectplate, text='Attribute:')
        extract_button = tk.Button(self.selectplate, text="Extract", command=self.PrintPlateResults)
        self.label_status = tk.Label(self.newWindow, textvariable=self.status)
        self.status.set("Connected to Plaxis")

        
        #layout
        self.label_x.grid(row = 1, column = 0, sticky = tk.E, **self.options)
        self.entry_x.grid(row = 1, column = 1, sticky = tk.W, **self.options)
        self.label_y.grid(row = 2, column = 0, sticky = tk.E, **self.options)
        self.entry_y.grid(row = 2, column = 1, sticky = tk.W, **self.options)
        self.label_mat.grid(row = 3, column = 0, sticky = tk.E, **self.options)
        self.entry_mat.grid(row = 3, column = 1, sticky = tk.W, **self.options)
        self.label_filename.grid(row = 4, column = 0, sticky = tk.E, **self.options)
        self.entry_filename.grid(row = 4, column = 1, sticky = tk.W, **self.options)
        self.label_attribute.grid(row = 5, column = 0, sticky = tk.E, **self.options)
        

        #Choose attributes to extract
        self.attributes=["Nx2D","Nx_EnvelopeMin2D","Nx_EnvelopeMax2D","Q2D","Q_EnvelopeMin2D","Q_EnvelopeMax2D","M2D","M_EnvelopeMin2D","M_EnvelopeMax2D","Ux","Uy"]
        self.selectedattribute={}
        row_n = 6
        for attribute in self.attributes:
            self.selectedattribute[attribute] = tk.IntVar()
            checkbox = tk.Checkbutton(self.selectplate, text=attribute, var=self.selectedattribute[attribute])
            checkbox.grid(row = row_n, column = 1, sticky = tk.W, **self.options)
            row_n+=1
        extract_button.grid(row = row_n+1, column = 1, sticky = tk.W, **self.options)
        self.label_status.grid(row = row_n+3, column = 0, sticky = tk.W, **self.options, columnspan=2) 

    def PrintPlateResults(self):
        #process input
        self.outputphase_val={a:b.get() for a,b in self.outputphase.items()}
        self.selectedattribute_val={a:b.get() for a,b in self.selectedattribute.items()}
        self.attributesym=["N [kN/m]","N_min [kN/m]","N_max [kN/m]","Q [kN/m]","Q_min [kN/m]","Q_max [kN/m]","M [kNm/m]","M_min [kNm/m]","M_max [kNm/m]","Ux [mm]","Uy [mm]"]
        self.attributesym={self.attributes[i]: self.attributesym[i] for i in range(len(self.attributes))}

        # Path of output spreadsheet
        path=os.path.dirname(os.path.abspath(__file__))+"\\Data"

        #Check of path exists, creat if not
        isExist = os.path.exists(path)
        if not isExist:
            os.makedirs(path)
        
        #Create workbook
        workbook = xlsxwriter.Workbook(path+"\\"+self.filename.get()+'.xlsx')
        worksheet = workbook.add_worksheet()
        col = 0

        #Print attributes
        for phase in self.plxoutput.Phases[0:]:
            if self.outputphase_val[str(phase.Number)]==0:
                continue
            print("Printing Phase: "+str(phase.Identification))
            self.UpdateStatus("Printing Phase: "+str(phase.Identification))
            app.update()

            # Write header
            row = 0
            worksheet.write(row, col, "")
            worksheet.write(row, col, str(phase.Identification))
            row += 1
            worksheet.write(row, col, "X [m]")
            worksheet.write(row, col + 1, "Y [m]")
            col_n = 2
            for i,j in self.selectedattribute_val.items():
                if j==1:
                    worksheet.write(row, col + col_n, self.attributesym[i])
                    col_n += 1
            row += 1

            #Collect plate results
            plateX = self.plxoutput.getresults(phase, self.plxoutput.ResultTypes.Plate.X,'node')
            plateY = self.plxoutput.getresults(phase, self.plxoutput.ResultTypes.Plate.Y, 'node')
            plateN = self.plxoutput.getresults(phase, self.plxoutput.ResultTypes.Plate.Nx2D, 'node')
            plateNmin = self.plxoutput.getresults(phase, self.plxoutput.ResultTypes.Plate.Nx_EnvelopeMin2D, 'node')
            plateNmax = self.plxoutput.getresults(phase, self.plxoutput.ResultTypes.Plate.Nx_EnvelopeMax2D, 'node')
            plateQ = self.plxoutput.getresults(phase, self.plxoutput.ResultTypes.Plate.Q2D, 'node')
            plateQmin = self.plxoutput.getresults(phase, self.plxoutput.ResultTypes.Plate.Q_EnvelopeMin2D, 'node')
            plateQmax = self.plxoutput.getresults(phase, self.plxoutput.ResultTypes.Plate.Q_EnvelopeMax2D, 'node')
            plateM = self.plxoutput.getresults(phase, self.plxoutput.ResultTypes.Plate.M2D, 'node')
            plateMmin = self.plxoutput.getresults(phase, self.plxoutput.ResultTypes.Plate.M_EnvelopeMin2D, 'node')
            plateMmax = self.plxoutput.getresults(phase, self.plxoutput.ResultTypes.Plate.M_EnvelopeMax2D, 'node')
            plateUx = self.plxoutput.getresults(phase, self.plxoutput.ResultTypes.Plate.Ux, 'node')
            plateUy = self.plxoutput.getresults(phase, self.plxoutput.ResultTypes.Plate.Uy, 'node')
            plateMat = self.plxoutput.getresults(phase, self.plxoutput.ResultTypes.Plate.MaterialID, 'node')


            # sort all table by height (Y) if x-coordinate specified
            if bool(self.x_co.get()):
                plate_zip=sorted(zip(plateY, plateX, plateN, plateNmin, plateNmax,plateQ,plateQmin,plateQmax,plateM,plateMmin,plateMmax,plateUx,plateUy,plateMat),reverse=True)
                vert=True
            
            # sort all table by length (X) if y-coordinate specified
            else:
                plate_zip=sorted(zip(plateX, plateY, plateN, plateNmin, plateNmax,plateQ,plateQmin,plateQmax,plateM,plateMmin,plateMmax,plateUx,plateUy,plateMat))
                vert=False

            # write table in excel: 
            for y,x,n,nmin,nmax,q,qmin,qmax,m,mmin,mmax,ux,uy,mat in plate_zip:
                attributevar={"Nx2D":n,"Nx_EnvelopeMin2D":nmin,"Nx_EnvelopeMax2D":nmax,"Q2D":q,"Q_EnvelopeMin2D":qmin,"Q_EnvelopeMax2D":qmax,"M2D":m,"M_EnvelopeMin2D":mmin,"M_EnvelopeMax2D":mmax,"Ux":float(ux)*1000,"Uy":float(uy)*1000}
                col_m = 2

                #check if on x/y-line with corresponding material ID
                if vert==True:
                    diff=abs(x - float(self.x_co.get()))
                else:
                    diff=abs(y - float(self.y_co.get()))

                if diff < 1E-5 and str(mat) in self.MatID.get().split(","):
                    worksheet.write(row, col, x)
                    worksheet.write(row, col + 1, y)
                    for a in attributevar.keys():
                        if self.selectedattribute_val[a]==1:
                            worksheet.write(row, col + col_m, attributevar[a])
                            col_m += 1
                    row += 1

            #get no. of columns
            n_col=sum(self.selectedattribute_val.values())
            col+=int(n_col+3)

        workbook.close()
        print("Done")
        self.UpdateStatus("Done")

    def UpdateStatus(self,text):
        self.status.set(text)

if __name__=="__main__":
    app = MainW(None)
    app.mainloop()