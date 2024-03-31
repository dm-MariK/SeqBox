#!/usr/bin/python3
# dm.pyOuthy.V.1
# *** 
# This little program is a [partial] replacement for the Google Authenticator.
#   See here: https://ru.wikipedia.org/wiki/Google_Authenticator (or the 'en' version of the article)
# It realises Time-based One-time Password Algorithm (TOTP)
#   See here: 
#     TOTP, i.e. Time-based One-Time Password Algorithm: https://tools.ietf.org/html/rfc6238
#     https://ru.wikipedia.org/wiki/Time-based_One-time_Password_Algorithm (or the 'en' version of the article)
# Actually, it is a GUI for this library/project:
#   https://github.com/pyauth/pyotp
# The name of the program is inspired by the project known as "Authy"
#   https://authy.com/
# IMHO, the Authy is one of the best replacements for the Google Authenticator
# that is suitable for usage both on mobile and desktop platforms (including GNU/Linux).
# The "A" letter is replaced by the "O" in the program's name. 
# It is done, first of all, to avoid violation of the Authy developers' copyright.
# Also, the "O" is the abbreviation of "OTP", i.e. One-Time Password.
# ***
# To Generate your Time-based One-time Password (TOTP) you must put your so called "Shared Secret"  
# to the corresponding entry. The "Shared Secret" is expected to be Base32 encoded string.
# (Customary as a rule, the "Shared Secret" is supplied in two formats: Base32 string and QR-code.) 
# Actually, the "Shared Secret" is the "seed" that is used to generate your TOTPs. Any TOTP is 
# a kind of hash generated using your "Shared Secret" and the current time [rounded to 30 seconds]. 
# For details see the links above.
# All that means that the "Shared Secret" is the most sensitive and valuable secret you must keep;
# everyone who knows your "Shared Secret" can unlimitedly generate your TOTPs as you can.
# ***
# In contrast to the famous others - this program does NOT store your "Shared Secret": 
# nither locally, i.e. on your local hard drive - as Google Authenticator do - nor in some protected
# [by a Password, or may be not such protected, or even not protected at all -- who knows???] - as 
# Authy do/ claims to do.
# You must store your "Shared Secret" by yourself somewhere else
# (using, for example, some kind of an encrypted archive/volume or else ;-))
# * This program keeps your "Shared Secret" in RAM only! * 
# Also there is an ability to Hide your "Shared Secret" - not to be displayed by the GUI in the 
# corresponding entry. To achieve this press 'Hide' Button and the "Shared Secret" you put will 
# be hidden. If the "Shared Secret" is hidden the 'Hide' Button's text is re-colored to red and the 
# "Shared Secret" entry becomes clear. In this case the hidden "Shared Secret" (i.e. stored 
# internally in RAM) is used to generate TOTPs. If the 'Hide' Button's text is black than the actual
# "Shared Secret" entry's content is used as the "Shared Secret". You can clear hidden "Shared Secret"
# from the program's memory by pressing 'Clear' Button.
# Good luck! :-)
#===================================================================================================
# Copyright (c) 2021, Denis I. Markov aka MariK
# < dm DOT marik DOT 230185 AT gmail DOT com >
# < t DOT me / dm_MariK >
# All rights reserved.
# 
# This code is multi-licensed under:  
# * CC BY-SA version 4.0 or later;
# * GNU GPL version 3 or later;
# * GNU Lesser GPL version 2.1 or later.
# Verbatim copy of any of these licenses can be found in the Internet on the corresponding resources.
# You are allowed to choose any of or any number of these licenses on your taste. ;-)
# 
# The author preserves the right for his own to change the license to MIT License 
# or any other permissive license at any moment he wants.
#  * The term "permissive license" is used here in the exactly same sense as the term 
# "lax permissive license" has been used in the article 'License Compatibility and Relicensing' 
# by Richard Stallman [ https://www.gnu.org/licenses/license-compatibility.en.html ].
#===================================================================================================

import pyotp
import tkinter as tk
from tkinter import font

titleStr = 'dm.pyOuthy.V.1'

class AppGui:
  def __init__(self, parent):
    self.secretSAVED = ''
    self.isSaved = False
    self.secretStr = tk.StringVar()
    self.secretStr.set('')
    self.otpStr = tk.StringVar()
    self.otpStr.set('')
    
    self.dfltFont = font.Font(family='Helvetica', size=-14, weight='normal')
    self.boldFont = font.Font(family='Helvetica', size=-14, weight='bold')
    # ...
    
    parent.option_add("*Font", self.dfltFont) # CHECK THIS !!!
    
    # ----------------------------------- Setup .grid() Layout ----------------------------------- #
    # -------------------------------------------------------------------------------------------- #
    # Will use 2 columns grid on the parent Widget. The 1-st (#0) is rigid while 
    # the 2-nd (#1) is stretchable.
    #parent.columnconfigure(0, weight=1)
    parent.columnconfigure(1, weight=1)
    
    # Row 0: Shared secret HEADER
    self.lblSharedSecret = tk.Label(parent, text='Shared secret:', fg='black') #, font=self.headerFont)
    self.lblSharedSecret.grid(row=0, column=0, columnspan=2, sticky=tk.SW, pady=5, padx=7) #sticky=tk.SE
    
    # Row 1: Shared secret ENTRY
    self.entSecret = tk.Entry(parent, textvariable=self.secretStr) # width=45, 
    self.entSecret.grid(row=1, column=0, columnspan=2, sticky=tk.W+tk.E, ipady=3, padx=5)
    # --- PostCheckFcn ---
    #self.entIn1Path.PostCheckFcn = self._doPostCheckIn1Path
    
    # Row 2: "Hide" and "Clear" Buttons
    self.btnHide = tk.Button(parent, text='Hide', command=self.btnHideClick, fg='black')
    self.btnHide.grid(row=2, column=0, pady=5, padx=5, sticky=tk.W+tk.E)
    # 
    self.btnClear = tk.Button(parent, text='Clear', command=self.btnClearClick, fg='black')
    self.btnClear.grid(row=2, column=1, pady=5, padx=5, sticky=tk.W)
    
    # Row 3: "Gen OTP" Button and OTP-entry
    self.btnGenOTP = tk.Button(parent, text='Gen OTP', command=self.btnGenOTPClick, fg='black')
    self.btnGenOTP.grid(row=3, column=0, pady=5, padx=5)
    #
    self.entOTP = tk.Entry(parent, textvariable=self.otpStr) #  width=45,
    self.entOTP.grid(row=3, column=1, sticky=tk.W+tk.E, ipady=3, pady=5, padx=5)

    
  # -------------------------------- Handle Commands (Callbacks) --------------------------------- #
  # ---------------------------------------------------------------------------------------------- #
  
  def btnHideClick(self):
    '''Save and hide Shared secret sring'''
    self.secretSAVED = self.secretStr.get()
    self.isSaved = True
    self.secretStr.set('')
    # Not forget to change color and font of "Hide" Button!
    self.btnHide.config(font=self.boldFont, fg='red')
  
  def btnClearClick(self):
    '''Clears all Entries and saved Shared secret sring'''
    self.secretSAVED = ''
    self.isSaved = False
    self.secretStr.set('')
    self.otpStr.set('')
    # Not forget to change back color and font of "Hide" Button!
    self.btnHide.config(font=self.dfltFont, fg='black')

  def btnGenOTPClick(self):
    '''Generate One Time Password'''
    #totp = pyotp.TOTP('TheSharedSecret')
    if self.isSaved:
      s = self.secretSAVED
    else:
      s = self.secretStr.get()
    totp = pyotp.TOTP(s)
    self.otpStr.set(totp.now())

# ==================================================================================================
# ==================================================================================================

def makeTheGUI():
  root = tk.Tk()
  root.title(titleStr)
  #root.geometry("350x200+10+10")
  gui = AppGui(root)
  root.mainloop()
  return gui

def main():
  theGui = makeTheGUI()
  
if __name__ == '__main__':
  main()