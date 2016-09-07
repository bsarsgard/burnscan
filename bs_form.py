"""
    BurnScan ticket barcode scanner
    Copyright (C) 2010 Ben Sarsgard

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import wx
import wx.media
import ConfigParser
import random
import sys
import xml.dom.minidom
from datetime import datetime
from datetime import timedelta
from xml.dom.minidom import Node

ID_ABOUT = 1110
ID_EXIT = 1112

ID_BUTTON_0 = 2110
ID_BUTTON_1 = 2111
ID_BUTTON_2 = 2112
ID_BUTTON_3 = 2113
ID_BUTTON_4 = 2114
ID_BUTTON_5 = 2115
ID_BUTTON_6 = 2116
ID_BUTTON_7 = 2117
ID_BUTTON_8 = 2118
ID_BUTTON_9 = 2119
ID_BUTTON_DEL = 2121
ID_BUTTON_LOOKUP = 2210
ID_BUTTON_BUY = 2211
ID_BUTTON_SCHEDULES = 2212
ID_BUTTON_NEWGREETER = 2213
ID_BUTTON_SEARCHGO = 2310
ID_BUTTON_CODEGO = 2311

ID_STATICTEXT_SOLDLABEL = 3110
ID_STATICTEXT_SOLDVALUE = 3111
ID_STATICTEXT_USEDLABEL = 3112
ID_STATICTEXT_USEDVALUE = 3113

ID_TEXTCTRL_CODE = 4110
ID_TEXTCTRL_SEARCHFILTER = 4111
ID_TEXTCTRL_RESULT = 4112

ID_LISTBOX_SEARCHRESULTS = 5110

XML_FILENAME = "brt_ticket_export.xml"

class MainWindow(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, size=(948,738))
        #self.panel = wx.Panel(self)
        #self.panel.Bind(wx.EVT_KEY_UP, self.on_key_up)

        #self.crypt_config()
        self.load_config()

        self.doc = xml.dom.minidom.parse(XML_FILENAME)

        # create the menus
        fileMenu = wx.Menu()
        fileMenu.Append(ID_ABOUT, "&About", " About this program")
        fileMenu.AppendSeparator()
        fileMenu.Append(ID_EXIT, "E&xit", " Exit the program")

        menuBar = wx.MenuBar()
        menuBar.Append(fileMenu, "&File")

        # create fonts
        self.font_med = wx.Font(16, wx.SWISS, wx.NORMAL, wx.NORMAL, False, u'Sans Serif')
        self.font_big = wx.Font(18, wx.SWISS, wx.NORMAL, wx.NORMAL, False, u'Sans Serif')
        self.SetFont(self.font_med)

        # create the form elements
        self.textctrl_code = wx.TextCtrl(self, ID_TEXTCTRL_CODE)
        self.textctrl_code.SetEditable(True)
        self.textctrl_code.SetFont(self.font_big)
        self.button_codego = wx.Button(self, ID_BUTTON_CODEGO, "Go")

        self.textctrl_result = wx.TextCtrl(self, ID_TEXTCTRL_RESULT, "Ready to scan")
        self.textctrl_result.SetEditable(False)
        self.textctrl_result.SetFont(self.font_big)
        self.textctrl_result.SetBackgroundColour(wx.WHITE)

        self.statictext_soldlabel = wx.StaticText(self, ID_STATICTEXT_SOLDLABEL, "Tix Sold: ")
        self.statictext_soldvalue = wx.StaticText(self, ID_STATICTEXT_SOLDVALUE, "0")
        self.statictext_usedlabel = wx.StaticText(self, ID_STATICTEXT_USEDLABEL, "Tix Used: ")
        self.statictext_usedvalue = wx.StaticText(self, ID_STATICTEXT_USEDVALUE, "0")
        self.textctrl_searchfilter = wx.TextCtrl(self, ID_TEXTCTRL_SEARCHFILTER)
        self.button_searchgo = wx.Button(self, ID_BUTTON_SEARCHGO, "&Go")
        self.listbox_searchresults = wx.ListBox(self, ID_LISTBOX_SEARCHRESULTS)

        self.button_0 = wx.Button(self, ID_BUTTON_0, "&0")
        self.button_1 = wx.Button(self, ID_BUTTON_1, "&1")
        self.button_2 = wx.Button(self, ID_BUTTON_2, "&2")
        self.button_3 = wx.Button(self, ID_BUTTON_3, "&3")
        self.button_4 = wx.Button(self, ID_BUTTON_4, "&4")
        self.button_5 = wx.Button(self, ID_BUTTON_5, "&5")
        self.button_6 = wx.Button(self, ID_BUTTON_6, "&6")
        self.button_7 = wx.Button(self, ID_BUTTON_7, "&7")
        self.button_8 = wx.Button(self, ID_BUTTON_8, "&8")
        self.button_9 = wx.Button(self, ID_BUTTON_9, "&9")
        self.button_del = wx.Button(self, ID_BUTTON_DEL, "&del")
        self.button_lookup = wx.Button(self, ID_BUTTON_LOOKUP, "&Look Up")
        self.button_buy = wx.Button(self, ID_BUTTON_BUY, "&Buy Tickets")
        self.button_schedules = wx.Button(self, ID_BUTTON_SCHEDULES, "&Schedules")
        self.button_newgreeter = wx.Button(self, ID_BUTTON_NEWGREETER, "New &Greeter")

        # populate the data
        #self.list_people()

        # add form controls
        self.CreateStatusBar()
        self.SetMenuBar(menuBar)

        self.sizer_controls = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer_panel = wx.BoxSizer(wx.VERTICAL)

        self.sizer_panel_stats = wx.BoxSizer(wx.VERTICAL)
        self.sizer_panel_stats_sold = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer_panel_stats_sold.Add(self.statictext_soldlabel, 2, wx.EXPAND)
        self.sizer_panel_stats_sold.Add(self.statictext_soldvalue, 1, wx.EXPAND)
        self.sizer_panel_stats_used = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer_panel_stats_used.Add(self.statictext_usedlabel, 2, wx.EXPAND)
        self.sizer_panel_stats_used.Add(self.statictext_usedvalue, 1, wx.EXPAND)
        self.sizer_panel_stats.Add(self.sizer_panel_stats_sold, 1, wx.EXPAND)
        self.sizer_panel_stats.Add(self.sizer_panel_stats_used, 1, wx.EXPAND)

        self.sizer_panel_search = wx.BoxSizer(wx.VERTICAL)
        self.sizer_panel_search_filter = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer_panel_search_filter.Add(self.textctrl_searchfilter, 2, wx.EXPAND)
        self.sizer_panel_search_filter.Add(self.button_searchgo, 1, wx.EXPAND)
        self.sizer_panel_search_results = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer_panel_search_results.Add(self.listbox_searchresults, 1, wx.EXPAND)
        self.sizer_panel_search.Add(self.sizer_panel_search_filter, 0, wx.EXPAND)
        self.sizer_panel_search.Add(self.sizer_panel_search_results, 1, wx.EXPAND)

        self.sizer_panel.Add(self.sizer_panel_stats, 1, wx.EXPAND)
        self.sizer_panel.Add(self.sizer_panel_search, 7, wx.EXPAND)

        self.sizer_functions = wx.BoxSizer(wx.VERTICAL)
        self.sizer_functions.Add(self.button_lookup, 1, wx.EXPAND)
        self.sizer_functions.Add(self.button_buy, 1, wx.EXPAND)
        self.sizer_functions.Add(self.button_schedules, 1, wx.EXPAND)
        self.sizer_functions.Add(self.button_newgreeter, 1, wx.EXPAND)

        self.sizer_keypad = wx.BoxSizer(wx.VERTICAL)
        self.sizer_keypad_row1 = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer_keypad_row2 = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer_keypad_row3 = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer_keypad_row4 = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer_keypad_row1.Add(self.button_7, 1, wx.EXPAND)
        self.sizer_keypad_row1.Add(self.button_8, 1, wx.EXPAND)
        self.sizer_keypad_row1.Add(self.button_9, 1, wx.EXPAND)
        self.sizer_keypad_row2.Add(self.button_4, 1, wx.EXPAND)
        self.sizer_keypad_row2.Add(self.button_5, 1, wx.EXPAND)
        self.sizer_keypad_row2.Add(self.button_6, 1, wx.EXPAND)
        self.sizer_keypad_row3.Add(self.button_1, 1, wx.EXPAND)
        self.sizer_keypad_row3.Add(self.button_2, 1, wx.EXPAND)
        self.sizer_keypad_row3.Add(self.button_3, 1, wx.EXPAND)
        self.sizer_keypad_row4.Add(self.button_0, 2, wx.EXPAND)
        self.sizer_keypad_row4.Add(self.button_del, 1, wx.EXPAND)
        self.sizer_keypad.Add(self.sizer_keypad_row1, 1, wx.EXPAND)
        self.sizer_keypad.Add(self.sizer_keypad_row2, 1, wx.EXPAND)
        self.sizer_keypad.Add(self.sizer_keypad_row3, 1, wx.EXPAND)
        self.sizer_keypad.Add(self.sizer_keypad_row4, 1, wx.EXPAND)

        self.sizer_controls.Add(self.sizer_panel, 1, wx.EXPAND)
        self.sizer_controls.Add(self.sizer_keypad, 1, wx.EXPAND)
        #self.sizer_controls.Add(self.sizer_functions, 1, wx.EXPAND)

        self.sizer_code = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer_code.Add(self.textctrl_code, 1, wx.EXPAND)
        self.sizer_code.Add(self.button_codego, 0, wx.EXPAND)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.sizer_code, 0, wx.EXPAND)
        self.sizer.Add(self.textctrl_result, 0, wx.EXPAND)
        self.sizer.Add(self.sizer_controls, 1, wx.EXPAND)

        self.SetSizer(self.sizer)
        self.SetAutoLayout(1)
        self.sizer.Fit(self)

        # attach events
        wx.EVT_MENU(self, ID_ABOUT, self.on_about)
        wx.EVT_MENU(self, ID_EXIT, self.on_exit)
        wx.EVT_BUTTON(self, ID_BUTTON_0, self.on_button_0)
        wx.EVT_BUTTON(self, ID_BUTTON_1, self.on_button_1)
        wx.EVT_BUTTON(self, ID_BUTTON_2, self.on_button_2)
        wx.EVT_BUTTON(self, ID_BUTTON_3, self.on_button_3)
        wx.EVT_BUTTON(self, ID_BUTTON_4, self.on_button_4)
        wx.EVT_BUTTON(self, ID_BUTTON_5, self.on_button_5)
        wx.EVT_BUTTON(self, ID_BUTTON_6, self.on_button_6)
        wx.EVT_BUTTON(self, ID_BUTTON_7, self.on_button_7)
        wx.EVT_BUTTON(self, ID_BUTTON_8, self.on_button_8)
        wx.EVT_BUTTON(self, ID_BUTTON_9, self.on_button_9)
        wx.EVT_BUTTON(self, ID_BUTTON_DEL, self.on_button_del)
        wx.EVT_BUTTON(self, ID_BUTTON_CODEGO, self.on_button_code_go)
        wx.EVT_BUTTON(self, ID_BUTTON_SEARCHGO, self.on_button_search_go)
        wx.EVT_LEFT_DCLICK(self.listbox_searchresults, self.on_left_dclick_search_results)
        wx.EVT_KEY_UP(self.textctrl_searchfilter, self.on_key_up_search_filter)
        wx.EVT_KEY_UP(self.textctrl_code, self.on_key_up_code)
        #wx.EVT_KEY_UP(self, self.on_key_up)

        #self.Show(True)
        self.ShowFullScreen(True, style=wx.FULLSCREEN_ALL)
        self.set_stats()
        self.load_sound()
        self.textctrl_code.SetFocus()

    def save_xml(self):
        fp = open(XML_FILENAME,"w")
        self.doc.writexml(fp, "", "", "", "UTF-8")

    def load_config(self):
        config = ConfigParser.RawConfigParser()
        config.read('BurnScan.cfg')
        seed = config.getint('General', 'seed') * -1
        self.password = crypt(config.get('Security', 'password'), seed)

    def load_sound(self):
        self.player_accept = wx.Sound('accept.wav')
        self.player_reject = wx.Sound('reject.wav')

    def on_about(self, e):
        d = wx.MessageDialog(self, "BurnScan ticket scanning station\n"
            "Created by Benjamin Sarsgard"
            , "About BurnScan", wx.OK)
        d.ShowModal()
        d.Destroy()
        self.textctrl_code.SetFocus()

    def authenticate(self):
        authorized = False
        dialog = wx.PasswordEntryDialog(self, 'Password:', 'authenticate yourself')
        if dialog.ShowModal() == wx.ID_OK:
            if str(dialog.GetValue()) == str(self.password):
                authorized = True
            else:
                dialog = wx.MessageDialog(self, 'Invalid Password', 'Authentication Failed')
                dialog.ShowModal()
        dialog.Destroy()
        return authorized

    def on_exit(self, e):
        self.Close(True)

    def on_button_0(self, e):
        self.textctrl_code.AppendText("0")
        self.textctrl_code.SetFocus()

    def on_button_1(self, e):
        self.textctrl_code.AppendText("1")
        self.textctrl_code.SetFocus()

    def on_button_2(self, e):
        self.textctrl_code.AppendText("2")
        self.textctrl_code.SetFocus()

    def on_button_3(self, e):
        self.textctrl_code.AppendText("3")
        self.textctrl_code.SetFocus()

    def on_button_4(self, e):
        self.textctrl_code.AppendText("4")
        self.textctrl_code.SetFocus()

    def on_button_5(self, e):
        self.textctrl_code.AppendText("5")
        self.textctrl_code.SetFocus()

    def on_button_6(self, e):
        self.textctrl_code.AppendText("6")
        self.textctrl_code.SetFocus()

    def on_button_7(self, e):
        self.textctrl_code.AppendText("7")
        self.textctrl_code.SetFocus()

    def on_button_8(self, e):
        self.textctrl_code.AppendText("8")
        self.textctrl_code.SetFocus()

    def on_button_9(self, e):
        self.textctrl_code.AppendText("9")
        self.textctrl_code.SetFocus()

    def on_button_del(self, e):
        self.textctrl_code.Remove(len(self.textctrl_code.GetValue()) - 1, len(self.textctrl_code.GetValue()))
        self.textctrl_code.SetFocus()

    def on_key_up_search_filter(self, e):
        if e.GetKeyCode() == wx.WXK_RETURN:
            if self.authenticate():
                self.list_people()

        e.StopPropagation()

    def on_key_up_code(self, e):
        if e.GetKeyCode() == wx.WXK_RETURN and\
                self.textctrl_code.GetValue() != "":
            self.check_code()
            self.listbox_searchresults.Clear()

        e.StopPropagation()

    def on_key_up(self, e):
        key_code = e.GetKeyCode()
        if key_code == wx.WXK_RETURN:
            self.check_code()
            self.listbox_searchresults.Clear()
        elif chr(key_code) == '0' or chr(key_code) == '1' or chr(key_code) == '2' or chr(key_code) == '3' or chr(key_code) == '4' or chr(key_code) == '5' or chr(key_code) == '6' or chr(key_code) == '7' or chr(key_code) == '8' or chr(key_code) == '9':
            self.textctrl_code.AppendText(chr(key_code))
            self.textctrl_code.SetFocus()
        if key_code == wx.WXK_BACK or key_code == wx.WXK_DELETE:
            self.textctrl_code.Remove(len(self.textctrl_code.GetValue()) - 1, len(self.textctrl_code.GetValue()))
            self.textctrl_code.SetFocus()

    def on_button_code_go(self, e):
        self.check_code()
        self.listbox_searchresults.Clear()

    def on_button_search_go(self, e):
        if self.authenticate():
            self.list_people()
            
        e.StopPropagation()

    def on_left_dclick_search_results(self, e):
        tickets = []
        email = self.listbox_searchresults.GetStringSelection()
        for ticket in self.doc.getElementsByTagName("ticket"):
            match = False
            for user_email in ticket.getElementsByTagName("user_email"):
                try:
                    if user_email.childNodes[0].data == email:
                        match = True
                except:
                    pass
            for name in ticket.getElementsByTagName("assigned_name"):
                try:
                    if name.childNodes[0].data == email:
                        match = True
                except:
                    pass
            if match:
                tier = ticket.parentNode.parentNode
                tier_code = tier.getAttribute("code")
                ticket_number = ticket.getAttribute("number")
                for ticket_code_node in ticket.getElementsByTagName("code"):
                    ticket_code = ticket_code_node.childNodes[0].data
                code = "%s%05i%s" % (tier_code, int(ticket_number), ticket_code)
                entered = ticket.getAttribute("entered")
                if entered and entered != "":
                    entered_date = datetime.strptime(entered,
                            "%Y-%m-%d %H:%M:%S")
                    code = "ENTERED %s" % code
                tickets.append(code)

        dialog = wx.SingleChoiceDialog(self, "Select the ticket to enter",
            "Tickets", tickets)

        if dialog.ShowModal() == wx.ID_OK:
            ticket_code = dialog.GetStringSelection()
            self.textctrl_code.Clear()
            self.textctrl_code.AppendText(ticket_code)
            self.check_code()

        dialog.Destroy()

    def list_people(self):
        self.listbox_searchresults.Clear()
        email_match = self.textctrl_searchfilter.GetValue()
        last_person = ''
        for ticket_node in self.doc.getElementsByTagName("ticket"):
            person = ''
            try:
                user_email_node = ticket_node.getElementsByTagName("user_email")
                user_email = user_email_node[0].childNodes[0].data
                if email_match == '' or email_match.lower() in\
                        user_email.lower():
                    person = user_email
            except:
                pass
            try:
                name_node = ticket_node.getElementsByTagName("assigned_name")
                name = name_node[0].childNodes[0].data
                if email_match == '' or email_match.lower() in name.lower():
                    person = name
            except:
                pass
            if person != '' and person != last_person:
                self.listbox_searchresults.Append(person)
                last_person = person
        self.textctrl_code.SetFocus()

    def set_stats(self):
        tickets_sold = 0
        tickets_used = 0
        for node in self.doc.getElementsByTagName("ticket"):
            tickets_sold += 1
            entered = node.getAttribute("entered")
            if entered and entered != "":
                tickets_used += 1

        self.statictext_soldvalue.SetLabel(str(tickets_sold))
        self.statictext_usedvalue.SetLabel(str(tickets_used))
        self.textctrl_code.SetFocus()

    def check_code(self):
        try:
            code = self.textctrl_code.GetValue()
            check_tier_code = code[0]
            check_ticket_number = code[1:6]
            check_ticket_code = code[6:10]
            found = False
            
            for tier in self.doc.getElementsByTagName("tier"):
                tier_code = tier.getAttribute("code")
                if tier_code and tier_code == check_tier_code:
                    for ticket in tier.getElementsByTagName("ticket"):
                        ticket_number = ticket.getAttribute("number")
                        if ticket_number and int(ticket_number) ==\
                                int(check_ticket_number):
                            if self.check_ticket(ticket, check_ticket_code):
                                found = True
                                break
            
            if not found:
                self.textctrl_result.SetValue("Not Found")
                self.textctrl_result.SetBackgroundColour(wx.BLUE)
                self.player_reject.Play()

            self.textctrl_code.Clear()
            self.set_stats()
            self.textctrl_code.SetFocus()
        except Exception:
            self.textctrl_code.Clear()
            self.textctrl_result.SetValue("Error")
            self.textctrl_result.SetBackgroundColour(wx.BLUE)
            self.player_reject.Play()
            self.textctrl_code.SetFocus()
    
    def check_ticket(self, ticket, check_ticket_code):
        self.textctrl_result.SetValue("Please Wait")
        for ticket_code_node in ticket.getElementsByTagName("code"):
            if ticket_code_node.childNodes[0].data == check_ticket_code:
                is_entered = True
                entered = ticket.getAttribute("entered")
                if entered and entered != "":
                    entered_date = datetime.strptime(entered,
                            "%Y-%m-%d %H:%M:%S")
                    since_entered = datetime.now() - entered_date
                    entered_expiration = timedelta(seconds=10)
                    if since_entered > entered_expiration:
                        is_entered = False
                        self.textctrl_result.SetValue(
                                "Already entered: %s" % entered_date.strftime(
                                    "%a, %H:%M"))
                        self.textctrl_result.SetBackgroundColour(wx.RED)
                        self.player_reject.Play()
                        return True
                    else:
                        is_entered = False
                        self.textctrl_result.SetValue(
                                "Check double scan: %s" % entered_date.strftime(
                                    "%a, %H:%M"))
                        return True

                if is_entered:
                    self.textctrl_result.SetBackgroundColour(wx.GREEN)
                    ticket.setAttribute("entered",
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    self.save_xml()
                    self.textctrl_result.SetValue("Accepted")
                    self.player_accept.Play()
                    return True
            else:
                #self.textctrl_result.SetValue("Invalid code!")
                #self.textctrl_result.SetBackgroundColour(wx.RED)
                #self.player_reject.Play()
                return False

def crypt(sequence, key):
    sign = (key > 0) * 2 - 1
    random.seed(abs(key * sign))
    s = ''
    for i in xrange(len(sequence)):
        r = random.randint(0, 255)
        s += chr((ord(sequence[i]) + r * sign) % 256)

    return s

def crypt_config():
    new_config = ConfigParser.RawConfigParser()
    old_config = ConfigParser.RawConfigParser()
    old_config.read('BurnScan_raw.cfg')
    seed = random.randint(1, 255)

    new_config.add_section('General')
    new_config.add_section('Security')
    new_config.set('General', 'seed', seed)
    new_config.set('Security', 'password',
            crypt(old_config.get('Security', 'password'), seed))
    configfile = open('BurnScan.cfg', 'wb')
    new_config.write(configfile)

app = wx.PySimpleApp()
for arg in sys.argv:
    if arg == 'crypt_config':
        crypt_config()
        print "encrypted"
        sys.exit()

frame = MainWindow(None, wx.ID_ANY, 'BurnScan')
app.MainLoop()
