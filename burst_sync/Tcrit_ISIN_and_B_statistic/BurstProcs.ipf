#pragma rtGlobals=1		// Use modern global access method.


Function FindTauCritical()
	Variable tau1, tau2
	Prompt tau1, "Enter the first time constant"
	Prompt tau2, "Enter the second time constant"
	DoPrompt "Find Tau Critical", tau1, tau2
	if (V_Flag)
		return -1
	endif
	
	print "Tau Critical = ", FindTauCriticalFcn(tau1, tau2)
	
End


Function ProcessBurstData()
	// This function assumes it is being run in the directory above the burst data
	
	String df, CurrentDataFolder = GetDataFolder(1)
	df = CurrentDataFolder + "bursts"
	SetDataFolder df

	ProcessBurstDataFcn()
	
	SetDataFolder CurrentDataFolder
	
End


Function FindTauCriticalFcn(tau1, tau2)
	Variable tau1, tau2
	Make /O/N=2 tau
	tau[0] = tau1
	tau[1] = tau2
	
	FindRoots/Q /L=(tau1)/H=(tau2) TauCriticalFcn, tau
	
	If( V_flag == 0)
		If (V_numroots == 1)
			InsertPoints 2, 1, tau
			tau[2] = V_Root
			return V_Root
		else
			print "two roots", V_Root, V_Root2
			return 0
		endif
	else
		Print "Error", V_flag
		return 0
	endif
	
End


Function TauCriticalFcn(tau, t)
	Wave tau
	Variable t
	
	return 1 - exp(-t/tau[0]) - exp(-t/tau[1])
	
end

	
Function FindBurstsFcn(threshold)
	// This function scans the interspike intervals for each contact
	// and finds bursts defined as two or more ISIs that are less than threshold
	// It creates a new folder called bursts containing the bursts for each contact
	// It assumes that it is being run in the directory above the isi times

	Variable threshold
	String wn,wl, df, bname, cname
	Variable i, index, tot = 0, burstnum = 0, numSpikes = 0, totalBurstNum = 0
	
	Silent 1; PauseUpdate
	
	df = GetDataFolder(1)
	NewDataFolder/O/S bursts
	Make /O/N=0 numSpikesInBurst
	SetDataFolder(df + "isi")
	wl = WaveList("ch*", ";", "")
	index = 0
	do
		wn = StringFromList(index, wl, ";")
		if (strlen(wn) == 0)
			break
		endif

		Wave isi = $wn
		if (numpnts(isi) > 1)
			bname = df + "bursts:" + wn
			cname = df + "cells:" + wn
			bname = ReplaceString("_isi", bname, "_bursts")
			Make /O/N=(0,2) $bname
			Wave burst = $bname
			cname = ReplaceString("_isi", cname, "")
			Wave contact = $cname
			i = 0
			burstnum = 0
			do
				if((isi[i] <= threshold) && (isi[i+1] <= threshold))
					InsertPoints /M=0 (DimSize(burst,0)), 1, burst
					InsertPoints numpnts(numSpikesInBurst), 1, numSpikesInBurst
					burst[burstnum][0] = contact[i]
					i += 1
					numSpikes = 2
					do
						i += 1
						numSpikes += 1
					while ((isi[i] <= threshold) && (i < numpnts(isi)))
					
					burst[burstnum][1] = contact[i]
					numSpikesInBurst[totalBurstNum] = numSpikes
					burstnum += 1
					totalBurstNum += 1
				else
					i += 1
				endif
			while ( i < numpnts(isi))
			
			if (DimSize(burst,0) == 0)
				KillWaves burst
			endif
	
		endif
				
		index += 1
		
	while (1)
	
	SetDataFolder(df)

End


Function ProcessBurstDataFcn()
	//	This function assumes it is being run in the directory with the burst data
	//	burstList[][0] = start time of the burst
	//	burstList[][1] = duration of the burst
	//	burstList[][2] = contact number
	//			networkBursts[][0] = start time
	//			networkBursts[][1] = 1st active contact
	//			networkBursts[][2] = end time
	//			networkBursts[][3] = last active contact
	//			networkBursts[][4] = number of contacts active during the burst
	
	MakeBurstList()
	Wave burstList = burstList
	If (dimsize(burstList,0) > 0)		// There are bursts 
	
		CalculateIBI()				// also plots IBI histogram
	
		Make/O/D/N=(dimsize(burstList, 0)) burstDuration, burstDuration_Hist
		burstDuration = burstList[p][1]
		Histogram /B={0, 0.05, 100}/C burstDuration, burstDuration_Hist
		Display burstDuration_Hist
		ModifyGraph log(left)=1
		ModifyGraph mode=3,marker=8,rgb=(0,0,0)
		Label bottom "Burst Duration (sec)"
		
		FindNetworkBursts()
		Wave networkBursts = networkBursts
	
		if( dimsize(networkBursts, 0) > 1)		// There are NetworkBursts
			Make /O/D/N=(dimsize(networkBursts,0) - 1) networkBursts_IBI
			networkBursts_IBI = networkBursts[p+1][2] - networkBursts[p][0]
	
			duplicate/O networkBursts_IBI, networkBursts_IBI_Hist
			Histogram /B={0,5,30}/C networkBursts_IBI, networkBursts_IBI_Hist
			Display networkBursts_IBI_Hist
			ModifyGraph log(left)=1
			ModifyGraph mode=3,marker=8,rgb=(0,0,0)
			Label bottom "Network Interburst Interval (sec)"
	
			Make/O/D/N=(dimsize(networkBursts,0)) networkBurstsDur, networkBurstsDur_Hist, networkBurstsNumContacts, networkBurstsNumContacts_Hist
			networkBurstsDur = networkBursts[p][2] - networkBursts[p][0]
			histogram /B={0, 0.1, 50}/C networkBurstsDur, networkBurstsDur_Hist
			Display networkBurstsDur_Hist
			ModifyGraph log(left)=1
			ModifyGraph mode=3,marker=8,rgb=(0,0,0)
			Label bottom "Network Burst Duration (sec)"

			networkBurstsNumContacts = networkBursts[p][4]
			Histogram /B={0,1,60}/C networkBurstsNumContacts, networkBurstsNumContacts_Hist
			Display networkBurstsNumContacts_Hist
			ModifyGraph mode=3,marker=8,rgb=(0,0,0)
			Label bottom "Number of Contacts in Burst"
			
			MakeNetworkBurstVector()
			
			MakeBurstLayouts()

		else
			if( dimsize(networkBursts, 0) == 1)
				Print "Sorry, only 1 Network Burst"
			else
				Print "Sorry, No Network Bursts"
			endif
		endif

	else
		print "Sorry, No bursts"
	endif	
	
End


Function MakeBurstList()
	//	This function scans through the lists of bursts for each contact and produces a single wave called burstList
	//	with the following burst information
	//	burstList[][0] = start time of the burst
	//	burstList[][1] = duration of the burst
	//	burstList[][2] = contact number

	String wn, wn2, wl
	Variable len, i, index = 0
	
	Silent 1; PauseUpdate
	
	wl = WaveList("ch*", ";", "")
	If (!(stringmatch(wl, "")))
		Make /O/D/N=(0,3) burstList
	endif
	
	do
		wn = StringFromList(index, wl, ";")
		if (strlen(wn) == 0)
			break
		endif

		Wave localWave = $wn		// remember that these waves have two columns (start time and end time)
		len = dimsize(burstList,0)	// use dimsize rather than numpnts
		InsertPoints len, dimsize(localWave,0), burstList
		
		for( i=0; i < dimsize(localWave,0); i += 1)
			burstList[len + i][ 0] = localWave[i][0]
			burstList[len + i][ 1] = localWave[i][1] - localWave[i][0]
			burstList[len + i][2] = ConvertWaveNameToContact(wn)
		endFor
						
		index += 1
		
	while (1)

End


Function CalculateIBI()
	// This function calculates the interburst interval for each contact
	// and stores in a subdirectory called ibi in the spike directory
	// It also creates a summary histogram of IBI's for all contacts
	// It assumes that it is being run in the directory with the burst times

	String wn,wl, df, ibi, folder
	Variable i, len, tot = 0, index = 0
	
	Silent 1; PauseUpdate
	
	folder = GetDataFolder(1)
	df  = ReplaceString(":bursts", folder, "")
	SetDataFolder df
	NewDataFolder/O ibi
	Make/O/N=0 $(df + "ibi:" + "IBI_Histogram")
	Wave hist = $(df + "ibi:" + "IBI_Histogram")
	Make/O/N=0 $(df + "ibi:" + "IBIList")
	Wave IBIList = $(df + "ibi:" + "IBIList")

	SetDataFolder folder
	
	wl = WaveList("ch*", ";", "")
	do
		wn = StringFromList(index, wl, ";")
		if (strlen(wn) == 0)
			break
		endif

		Wave localWave = $wn
		if (dimsize(localWave,0) > 1)
			ibi = df+ "ibi:" + wn + "_ibi"
			Make /O/N=(dimsize(localWave,0) - 1) $ibi
			Wave localibi = $ibi
			localibi = localWave[p+1][0] - localWave[p][1]
			tot += dimsize(localibi,0)
		
			if (numpnts(hist) == 0)
				Histogram/B={0, 0.05, 100} localibi, hist
			else
				Histogram/A localibi, hist
			endif
			
			len = numpnts(IBIList)
			InsertPoints len, numpnts(localibi), IBIList
			for(i = 0; i < numpnts(localibi); i += 1)
				IBIList[len + i] = localibi[i]
			endfor			
		endif
				
		index += 1
		
	while (1)
	
	hist /= tot
	Display hist
	ModifyGraph log(left)=1
	ModifyGraph mode=3,marker=8
	ModifyGraph rgb=(0,0,0)
	Label left "probability"
	Label bottom "Inter-burst interval (sec)"
	index = numpnts(hist) - 1
//	CurveFit/Q/NTHR=0 /TBOX=(1+256+512) dblexp_XOffset  hist[1, index] /D	

End


Function ReCalcIBIHistogram(binSize, numBins,startPoint)
	// This function calculates the interburst interval histogram
	// It assumes that it is being run in the directory with the ibi data

	Variable binSize, numBins, startPoint
	String wn, wl
	Variable i, tot = 0, index = 0
	
	Silent 1; PauseUpdate
	
	Make/O/N=0 summaryHistogram
	Wave hist = summaryHistogram
	
	wl = WaveList("ch*", ";", "")
	
	do
		wn = StringFromList(index, wl, ";")
		if (strlen(wn) == 0)
			break
		endif

		Wave localWave = $wn
		tot += numpnts(localWave)
		
		if (numpnts(hist) == 0)
			Histogram/B={0, binSize,numBins} localWave, hist
		else
			Histogram/A localWave, hist
		endif
										
		index += 1
		
	while (1)
	
	hist /= tot
	Display hist
	ModifyGraph log(left)=1
	ModifyGraph mode=3,marker=8
	ModifyGraph rgb=(0,0,0)
	Label left "probability"
	Label bottom "Inter-burst interval (sec)"
	index = numpnts(hist) - 1
	CurveFit/Q/NTHR=0 /TBOX=(1+256+512) dblexp_XOffset  hist[startPoint, index] /D	

End


Function CondenseBurstData()
	// This function deletes waves for contacts with no bursts and combines the burst_start and burst_end
	// waves for each contact into a single wave with two columns

	String wn, wn2, wl, dummy
	Variable index = 0
	
	Silent 1; PauseUpdate
	
	wl = WaveList("ch*", ";", "")
	do
		wn = StringFromList(index, wl, ";")
		if (strlen(wn) == 0)
			break
		endif

		wn2 = StringFromList(index+1, wl, ";")
		Wave localWave = $wn
		Wave localWave2 = $wn2
		sprintf dummy, "%g", localWave[0]		//kludge because testing for equality to NaN didn't work
		if (!stringmatch(dummy, "nan"))
			redimension /N=(-1, 2) localWave
			localWave[][1] = localWave2[p]
			
			wn = ReplaceString("_start", wn, "")		//remove "_start" from the wavename
			Rename localWave, $wn
			
			KillWaves localWave2				// kill the "_end" wave that is no longer needed

		else
			KillWaves localWave				// delete waves for contacts with no bursts
			KillWaves localWave2
		endif
				
		index += 2
		
	while (1)
			
End


Function FindNetworkBursts()
	Wave sortedBurstList
	// Find network bursts defined as anytime there are overlapping bursts in two or more contacts
	// This function sorts the burstlist by starting time and scans for network bursts
	// network burst data is stored in a wave called bursts where
	//			networkBursts[][0] = start time
	//			networkBursts[][1] = 1st active contact
	//			networkBursts[][2] = end time
	//			networkBursts[][3] = last active contact
	//			networkBursts[][4] = number of contacts active during the burst
	//
	// It assumes it is being run in the directory with the burstList
	
	Variable counter, i, numContacts, startTime, endTime, startContact, endContact
	
	SortBurstList()
	Wave sortedBurstList = burstList
	Make /O/D/N=(0, 5) networkBursts
	counter = 0
	numContacts = 1
	startTime = sortedBurstList[0][0]
	endTime = startTime + sortedBurstList[0][1]
	startContact = sortedBurstList[0][2]
	endContact = startContact
	i = 1
	do
		if (sortedBurstList[i][0] < endTime)	// must still be in a burst
			If (endTime < (sortedBurstList[i][0] + sortedBurstList[i][1]))		//burstlet i end after burstlet i-1
				endTime = sortedBurstList[i][0] + sortedBurstList[i][1]
				endContact = sortedBurstList[i][2]
				if (startTime == sortedBurstList[i][0])
					startContact = sortedBurstList[i][2]
				endif
			endif
			numContacts += 1
			i += 1
		else
			if (numContacts > 1)		// there was a burst
				InsertPoints counter, 1, networkBursts
				networkBursts[counter][0] = startTime
				networkBursts[counter][1] = startContact
				networkBursts[counter][2] = endTime
				networkBursts[counter][3] = endContact
				networkBursts[counter][4] = numContacts
				counter +=1
			endif
			
			startTime = sortedBurstList[i][0]
			endTime = startTime + sortedBurstList[i][1]
			startContact = sortedBurstList[i][2]
			endContact = startContact
			numContacts = 1	
			i += 1		
		endif
	while (i < dimsize(sortedBurstList, 0))
		
	if (numContacts > 1)		// the last burstlet was part of a burst
		InsertPoints counter, 1, networkBursts
		networkBursts[counter][0] = startTime
		networkBursts[counter][1] = startContact
		networkBursts[counter][2] = endTime
		networkBursts[counter][3] = endContact
		networkBursts[counter][4] = numContacts
		counter +=1
	endif
	
End


Function SortBurstList()
	// Creates temporary 1-D waves for each column of burstList and sorts the three waves based on
	// the first column wave. The waves are then copied back into the columns of burstList
	// This function assumes it is being run in the directory with the burstList
	
	Wave burstList = burstList
	Make /O/D/N=(dimsize(burstList,0)) BLTime, BLDur, BLContact
	BLTime = burstList[p][0]
	BLDur = burstList[p][1]
	BLContact = burstList[p][2]
	
	sort BLTime, BLTime, BLDur, BLContact
	burstList[][0] = BLTime[p]
	burstList[][1] = BLDur[p]
	burstList[][2] = BLContact[p]
	
	KillWaves BLTime, BLDur, BLContact
		
End


Function MakeNetworkBurstVector()
	// This function creates an array in which each row represents a contact 
	// and each column is the corresponding network burst
	// each cell contains number of spikes in the corresponding contact during the corresponding network burst
	 
	Wave networkBursts = networkBursts
	Variable burstNum = 0, contact, numContacts = 0
	String wn, wl, df, CurrentDataFolder = GetDataFolder(1)

	wl = WaveList("ch*", ";", "")
	
	Do
		wn = StringFromList(numContacts, wl, ";")
		if (strlen(wn) == 0)
			break
		endif
		
		numContacts += 1
	While(1)
	
	Make/O/D/N=(numContacts, dimsize(networkBursts, 0)) networkBurstVector = 0
	Make/O/D/N=(dimsize(networkBursts,0)) numSpikesInNB = 0
			
	Do
		contact = 0
		Do
			wn = StringFromList(contact, wl, ";")
			if (strlen(wn) == 0)
				break
			endif

			df = ReplaceString("surprise:", CurrentDataFolder, "")
			If (StringMatch(df, CurrentDataFolder))
				df = ReplaceString("ThreeHz:", CurrentDataFolder, "")
			endif
			If(StringMatch(df, CurrentDataFolder))
				df = ReplaceString("bursts:", CurrentDataFolder, "")
			endif
			
			df = df + "cells:"
			wn = df + ReplaceString("_bursts", wn, "")		//remove "_bursts" from the wavename
						
			networkBurstVector[contact][burstNum] = CountSpikes(networkBursts[burstNum][0], networkBursts[burstNum][2], wn)
			numSpikesInNB[burstNum] += networkBurstVector[contact][burstNum]
			contact += 1
		
		while (1)
		
	burstNum += 1
	
	While (burstNum < dimsize(networkBursts, 0))
End


Function CountSpikes(startTime, endTime, contactName)
	Variable startTime, endTime
	String contactName
	// This function count the number of spikes from startTime to endTime in contact contactName
	// It assumes that contact name includes the correct directory information
		
	Variable i, count
	
	Wave localWave = $contactName
	
	i = 0
	count = 0
	
	
	if (localWave[0] < startTime)
		do
			i += 1
		while  ((localWave[i]< startTime) && (i < numpnts(localWave)))
			
		if (i < numpnts(localWave))
			if (localWave[i] <= endTime)
				do
					count += 1
					i += 1
				while ((localWave[i] <= endTime) && (i < numpnts(localWave)))
			endif
		endif
	else
		if(localWave[i] <= endTime)
			do
				count += 1
				i += 1
			while ((localWave[i] <= endTime) && (i < numpnts(localWave)))
		endif
	endif
	
	return count
End



Function MakeBurstLayouts()
	String win, wlist = WinList("*", ";", "WIN:1")	//list of graphs
	Variable i
	
	NewLayout /P=Landscape
	for (i=3; i <=7; i+=1)
		win = StringFromList(i, wlist)
		AppendLayoutObject graph $win
	endfor
	Execute /Q "SummaryLayout_1_Style()"

	NewLayout /P=Landscape
	for (i=0; i <=2; i+=1)
		win = StringFromList(i, wlist)
		AppendLayoutObject graph $win
	endfor
	Execute /Q "SummaryLayout_2_Style()"

End


Proc SummaryLayout_1_Style() : LayoutStyle
	PauseUpdate; Silent 1		// modifying window...
	ModifyLayout/Z frame=1
	ModifyLayout/Z left[0]=396,top[0]=72,width[0]=360,height[0]=180
	ModifyLayout/Z left[1]=396,top[1]=252,width[1]=360,height[1]=180
	ModifyLayout/Z left[2]=36,top[2]=396,width[2]=360,height[2]=180
	ModifyLayout/Z left[3]=36,top[3]=234,width[3]=360,height[3]=162
	ModifyLayout/Z left[4]=36,top[4]=72,width[4]=360,height[4]=162
	ModifyLayout/Z left[5]=278.25,top[5]=44.25,width[5]=231.75,height[5]=27
	ModifyLayout/Z left[6]=471.75,top[6]=500.25,width[6]=187.5,height[6]=20.25
EndMacro


Proc SummaryLayout_2_Style() : LayoutStyle
	PauseUpdate; Silent 1		// modifying window...
	ModifyLayout/Z frame=1
	ModifyLayout/Z left[0]=36,top[0]=252,width[0]=360,height[0]=180
	ModifyLayout/Z left[1]=396,top[1]=72,width[1]=360,height[1]=180
	ModifyLayout/Z left[2]=36,top[2]=72,width[2]=360,height[2]=180
EndMacro


Proc NoBurstsStyle() : LayoutStyle
	PauseUpdate; Silent 1		// modifying window...
	ModifyLayout/Z frame=1
	ModifyLayout/Z left[0]=36,top[0]=396,width[0]=360,height[0]=180
	ModifyLayout/Z left[1]=36,top[1]=234,width[1]=360,height[1]=162
	ModifyLayout/Z left[2]=36,top[2]=72,width[2]=360,height[2]=162
	ModifyLayout/Z left[3]=222.75,top[3]=38.25,width[3]=330.75,height[3]=33
	ModifyLayout/Z left[4]=509.25,top[4]=470.25,width[4]=162,height[4]=26.25
EndMacro
