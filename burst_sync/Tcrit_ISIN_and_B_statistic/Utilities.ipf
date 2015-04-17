#pragma rtGlobals=1		// Use modern global access method.

Function ConvertWaveNameToContact(wn)
	String wn
	// converts the wavename "ch_XY_unit_0" to a contact number from 0 to 59
	// where X is the row number and Y is the column number of the contact
	
	variable contact = 0
	
	If (str2num(wn[3]) == 1)			// first row (only has 6 contacts)
		contact = str2num(wn[4]) - 2
	elseif (str2num(wn[3]) == 8)		// last row (only has 6 contacts)
		contact = 52 + str2num(wn[4]) 
	else								// rows 2-7 have 8 contacts each
		contact = 5 + 8*(str2num(wn[3])-2) + str2num(wn[4])
	endif
	
	return contact
	
end


Function LayoutGraphs(first, last)
	Variable first, last
	String win, wlist = WinList("*", ";", "WIN:1")	//list of graphs
	Variable i
	
	NewLayout /P=Landscape
	for (i=first; i <=last; i+=1)
		win = StringFromList(i, wlist)
		AppendLayoutObject graph $win
	endfor
	
End


Function KillAllWindows()
	Variable index = 0
	String wn, wl
	
	wl = WinList( "*", ";", "")
	Do
		wn = StringFromList(index, wl)
		if (strlen(wn) == 0)
			break
		endif
		KillWindow $wn
		index += 1
	While (1)
End