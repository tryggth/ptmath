#
#   WinTaxDivisor.py - animate the tax collector program
#       Based on initial program from Gemini
#
#   Buttons or labels for each number - click to green, click to take
#   Big "Take Home" and "Tax" boxes with totals
#   Buttons clear, undo, done, new
#

import tkinter as tk
import tkinter.font as tkFont

from tkinter import messagebox


class NumButton:
    BG_GREEN = "#aaffaa"
    BG_RED   = "#ffaaaa"
    BG_DISABLED = "#aaaaaa"
    BG_FROZEN = "#ccccff"
    BG_HIDDEN = "#444444"
    
    ST_UNSELECTED = 0
    ST_TAKING = 1
    ST_TAXING = 2
    
    def __init__(self, n, btn):
        self.number = n
        self.button = btn
        self.status = 0         # 0 = default, 1 = take, 2 = tax,
                                # 3 = disabled, 4 = hidden
        self.frozen = False
        self.disabled = False
        self.alreadyUsed = False
        self.hidden = False

        if n == 1:
            self.freeze()
            
        return

    def setTaking(self):
        self.status = self.ST_TAKING
        self.button['background'] = self.BG_GREEN
        return

    def setTaxing(self):
        self.status = self.ST_TAXING
        self.button['background'] = self.BG_RED
        return

    def setClear(self):
        self.status = self.ST_UNSELECTED
        if self.frozen or self.disabled:
            self.frozen = False
            self.enable()
        if self.hidden:
            self.unhide()
        self.button['background'] = "SystemButtonFace"
        return

    def disable(self):
        self.disabled = True
        self.button['background'] = self.BG_DISABLED
        self.button.config(state=tk.DISABLED)
        return

    def enable(self):
        self.disabled = False
        self.button.config(state=tk.NORMAL)
        self.setClear()
        return

    def hide(self):
        self.hidden = True
        self.button['background'] = self.BG_HIDDEN
##        self.button['text'] = "        "
        self.button.config(state=tk.DISABLED)
        return

    def unhide(self):
        self.hidden = False
        self.button['background'] = "SystemButtonFace"
        self.button.config(state=tk.NORMAL)
##        self.button['text'] = "   $" + str(self.number) + "   "
##        self.setClear()
        return

    def freeze(self):
        self.frozen = True
        self.disable()
        self.button['background'] = self.BG_FROZEN
        return

    def unfreeze(self):
        self.frozen = False
        
    def isClear(self):
        return self.status == self.ST_UNSELECTED

    def isTaking(self):
        return self.status == self.ST_TAKING

    def isTaxing(self):
        return self.status == self.ST_TAXING

    def isSelected(self):
        return not self.isClear()
    
    def isDisabled(self):
        return self.disabled

    def isFrozen(self):
        return self.frozen
    
    def isHidden(self):
        return self.hidden

    def isUsed(self):
        return self.alreadyUsed


#
#   Layout:
#       Two labeled bins - Take and Tax with totals
#           Bins show "$n" for each envelope
#       Two or four rows of "number butons" for envelope selection
#       Row of action buttons: New, Undo, Take, and Done
#
#   Non-widget structures:
#       History
#           Bin texts and totals
#           Taken and taxed lists
#       Button status
#
#   Actions:
#       Select - click on a number button
#           Clear all current selections from "taking" or "taxing" status
#               with default background
#           Set button status to "taking" with green background
#           Set button status for available divisors to "taxing"
#               with red background
#           ??? How to indicate selection with no divisors ???
#               Disable?
#       New - click on "New" button
#           Clear bins and totals
#           Clear history
#           Enable all number buttons in unselected state
#       Take - click on "Take" button
#           Add current bin taken and taxed texts and totals,
#               and taking and taxing lists to history
#           Add to taken and taxed texts in bins
#           Update bin totals
#           Disable / hide taken and taxed number buttons
#       Done - click on "Done" button
#           "Tax" all remaining numbers
#       Undo - click on "Undo" button
#           Back up one level of history if possible
#    
class TaxDivisorApp:
    def __init__(self, root, size=12):
        self.root = root
        self.root.title("Tax Divisor - " + str(size))
##        self.root.geometry("800x600")
        self.root.columnconfigure(0, weight=1)

        # Configuration - Number Buttons
        self.size = size
        self.rows = size // 6
        self.cols = 6
        self.text_widgets = [] # List to store the text box objects
        self.numButtons = []

        # Create the UI
        self.windowWidth = 600
        self.createBins()
        self.createNumberButtons()
        self.createActionButtons()

        #   Handy dictionary of divisors
        self.divDict = {}
        for n in range(1, self.size + 1):
            divs = []
            for d in range(1, n):
                if n % d == 0:
                    divs.append(d)
            self.divDict[n] = divs
            
        #   Status: available (all), taken, taxed
        #
        self.statusHistory = []
        available = list(range(1, self.size + 1))
        taken = []
        taxed = []
        self.statusHistory.append((available, taken, taxed))

        self.refreshDisplay()
        
        return

    #-----------------------------------------------------------------
    def createBins(self):   #????
        btnFont = tkFont.Font(size = 15)
        fontSize = 15

        frameBins = tk.Frame(self.root, padx=10, pady=10)
        for c in range(2):
            frameBins.columnconfigure(c, weight=1)
        frameBins.grid(row=0, column=0, sticky=tk.NSEW)


##        frameTaken = tk.Frame(frameBins, padx=10, pady=10, \
##                              bd=3, relief=tk.RAISED \
##                              )
##        frameTaken.grid(row = 0, column = 0, sticky=tk.NSEW)
##
##        frameTaxed = tk.Frame(frameBins, padx=10, pady=10, \
##                              bd=3, relief=tk.RAISED \
##                              )
##        frameTaxed.grid(row = 0, column = 1, sticky=tk.NSEW)

        wrapSize = self.windowWidth * 9 // 10 // 2
        self.lblTakeTotal = tk.Label(frameBins, text="Taken = $0", \
                                     font=fontSize, padx=20, pady=5)
        self.lblTakeTotal.grid(row = 0, column = 0)
        
        self.lblTakenDisplay = tk.Label(frameBins, text="Take $", \
                                        font=fontSize, \
                                        justify=tk.LEFT, \
                                        bg=NumButton.BG_GREEN, \
                                        bd=5, \
                                        relief=tk.GROOVE, \
                                        wraplength=wrapSize, \
                                        padx=20, pady=10)
        self.lblTakenDisplay.grid(row = 1, column = 0, sticky=tk.NSEW)
        

        self.lblTaxTotal = tk.Label(frameBins, text="Taxed = $0", \
                                    font=fontSize, padx=20, pady=5)
        self.lblTaxTotal.grid(row = 0, column = 1)
        
        self.lblTaxDisplay = tk.Label(frameBins, text="Tax $", \
                                      font=fontSize,\
                                      justify=tk.LEFT, \
                                      bg=NumButton.BG_RED, \
                                      bd=5, \
                                      relief=tk.GROOVE, \
                                      wraplength=wrapSize, \
                                      padx=20, pady=10)
        self.lblTaxDisplay.grid(row = 1, column = 1, sticky=tk.NSEW)

        return

    #---------------------------------------------------------------
    #   Setup Number Buttons
    def createNumberButtons(self):
        """Generates the grid of text boxes."""
        frameNumbers = tk.Frame(self.root, padx=10, pady=10)
        for c in range(self.cols):
            frameNumbers.columnconfigure(c, weight=1)
        frameNumbers.grid(row = 1, column = 0, sticky=tk.EW)

        btnFont = tkFont.Font(size = 20)

        # Create a loop to generate the array
        bValue = 0
        for r in range(self.rows):
            for c in range(self.cols):
                
                # Button 1: Fill
                bValue += 1
                buttonText = self.moneyText(bValue)
                bEntry = tk.Button(frameNumbers, text=buttonText, \
                                   font = btnFont, \
                                   relief = tk.RIDGE, \
                                   command=lambda x = bValue - 1 : self.nbSelect(x))
                bEntry.grid(row = self.rows - r, column = c, \
                            padx = 5, pady = 2, \
                            ipadx = 10)
                numBtn = NumButton(bValue, bEntry)
                self.numButtons.append(numBtn)

            
            # Add this row to our main list
            self.text_widgets.append(self.numButtons)
        return


    #---------------------------------------------------------------
    #   Setup Action Buttons
    def createActionButtons(self):
        """Creates the four functional buttons."""
        frame_buttons = tk.Frame(self.root, padx=10, pady=10)
        frame_buttons.grid(row = 2, column = 0)
##        frame_buttons.pack(fill='x', side='bottom')

        actFont = 8
        
        # Button 1: New
        btn_fill = tk.Button(frame_buttons, text="New", font=actFont, \
                             command=self.actNew)
        btn_fill.pack(side='left', expand=True, fill='x', padx=5, pady=10)

        # Button 2: Undo
        btn_clear = tk.Button(frame_buttons, text="Undo", font=actFont, \
                              command=self.actUndo)
        btn_clear.pack(side='left', expand=True, fill='x', padx=5, pady=10)

        # Button 3: Take
        btn_print = tk.Button(frame_buttons, text="Take", font=actFont, \
                              command=self.actTake)
        btn_print.pack(side='left', expand=True, fill='x', padx=5, pady=10)

        # Button 4: Done
        btn_upper = tk.Button(frame_buttons, text="Done", font=actFont, \
                              command=self.actDone)
        btn_upper.pack(side='left', expand=True, fill='x', padx=5, pady=10)

        return

    #---------------------------------------------------
    #   Number Buttons    
    def moneyText(self, n):
        return " $" + str(n) + " "

    def clearAvailable(self, available):
        for n in available:
            nIdx = n - 1
            btn = self.numButtons[nIdx]
            self.numButtons[nIdx].setClear()
        self.refreshFrozen(available)
        return

    def anyDivisors(self, n, available):
        divs = self.divDict[n]
        for d in divs:
            if d in available:
                return True
        return False

    def refreshFrozen(self, available):
        for n in available:
            nIdx = n - 1
            if not self.anyDivisors(n, available):
                self.numButtons[nIdx].freeze()
        return

    def refreshDisplay(self):
        available, taken, taxed = self.statusHistory[-1]
        self.clearAvailable(available)
        takeTotal = sum(taken)
        taxTotal = sum(taxed)
        takeDisplay = ""
        for n in taken:
            takeDisplay += self.moneyText(n)
        taxDisplay = ""
        for n in taxed:
            taxDisplay += self.moneyText(n)
        self.lblTakeTotal['text'] = "Taken = $" + str(takeTotal)
        self.lblTakenDisplay['text'] = takeDisplay
        self.lblTaxTotal['text'] = "Taxed = $" + str(taxTotal)
        self.lblTaxDisplay['text'] = taxDisplay
        return

    
    def nbSelect(self, idx):
        available, taken, taxed = self.statusHistory[-1]

        iValue = idx + 1
        b = self.numButtons[idx]

        #   Currently chosen, so clear instead
        if b.isTaking():
            self.clearAvailable(available)
##            for k in range(len(self.numButtons)):
##                kValue = k + 1
##                kBtn = self.numButtons[k]
##                if not kBtn.isDisabled():
##                    kBtn.setClear()
##            self.refreshFrozen(available)
##            self.numButtons[0].freeze()

        #   Not currently chosen, select and mark all available divisors
        else:
            self.clearAvailable(available)
            divs = self.divDict[iValue]
            for n in available:
                nIdx = n - 1
                if n == iValue:
                    self.numButtons[nIdx].setTaking()
                elif n in divs:
                    self.numButtons[nIdx].setTaxing()
##            for k in range(len(self.numButtons)):
##                kValue = k + 1
##                kBtn = self.numButtons[k]
##                if not kBtn.isUsed():
##                    if k == idx:
##                        kBtn.setTaking()
##                    elif iValue % kValue == 0:
##                        kBtn.setTaxing()
##                    else:
##                        kBtn.setClear()
        return


    #----------------------------------------------------------------
    #   Action Buttons
    def actNew(self):
        self.statusHistory = self.statusHistory[:1]
        self.refreshDisplay()
        return

    
    def actUndo(self):
        if len(self.statusHistory) > 1:
            self.statusHistory = self.statusHistory[:-1]
            self.refreshDisplay()
        return


    def actTake(self):
        available, taken, taxed = self.statusHistory[-1]
        newAvailable = []
        newTaken = taken + []
        newTaxed = taxed + []
        for n in available:
            nIdx = n - 1
            nBtn = self.numButtons[nIdx]
            if nBtn.isTaking():
                newTaken.append(n)
                nBtn.hide()
            elif nBtn.isTaxing():
                newTaxed.append(n)
                nBtn.hide()
            else:
                newAvailable.append(n)
        self.statusHistory.append((newAvailable, newTaken, newTaxed))
        self.refreshDisplay()
                
        return


    def actDone(self):
        available, taken, taxed = self.statusHistory[-1]
        if len(available) > 0:
            newAvailable = []
            newTaken = taken + []
            newTaxed = taxed + []
            for n in available:
                nIdx = n - 1
                nBtn = self.numButtons[nIdx]
                newTaxed.append(n)
                nBtn.hide()
            self.statusHistory.append((newAvailable, newTaken, newTaxed))
            self.refreshDisplay()
        
        return


#=======================================================================
def main(n=12):
    root = tk.Tk()
    app = TaxDivisorApp(root, n)
    root.mainloop()
    return


if __name__ == "__main__":
    main(12)
    main(24)

