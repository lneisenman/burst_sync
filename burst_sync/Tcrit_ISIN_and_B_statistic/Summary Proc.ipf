#pragma rtGlobals=1		// Use modern global access method.

Proc SummarizeData()
	String cdf = GetDataFolder(1)
	
	SummarizeDataFcn()
	SetDataFolder "summary"
	
// Display Graphs		
	Display ASDR vs conditions
	SetAxis left 0,*
	ModifyGraph hbFill=2,rgb=(0,0,0);DelayUpdate
	ErrorBars ASDR Y,wave=(ASDR_SEM,)
	Label left "ASDR (spikes/second)"

	Display numBursts vs conditions
	SetAxis left 0,*
	ModifyGraph hbFill=2,rgb=(0,0,0);DelayUpdate
	Label left "number of bursts"

	Display burstDur vs conditions
	SetAxis left 0,*
	ModifyGraph hbFill=2,rgb=(0,0,0);DelayUpdate
	ErrorBars burstDur Y,wave=(burstDur_SEM,)
	Label left "burst duration (sec)"

	Display IBI vs conditions
	SetAxis left 0,*
	ModifyGraph hbFill=2,rgb=(0,0,0);DelayUpdate
	ErrorBars IBI Y,wave=(IBI_SEM,)
	Label left "interburst interval (sec)"

	Display spikeRateInBurst vs conditions
	SetAxis left 0,*
	ModifyGraph hbFill=2,rgb=(0,0,0);DelayUpdate
	ErrorBars spikeRateInBurst Y,wave=(spikeRIB_SEM,)
	Label left "burst firing rate (spikes/sec)"

	Display numSpikesInBurst vs conditions
	SetAxis left 0,*
	ModifyGraph hbFill=2,rgb=(0,0,0);DelayUpdate
	ErrorBars numSpikesInBurst Y,wave=(numSIB_SEM,)
	Label left "spikes per burst"

	Display numNB vs conditions
	SetAxis left 0,*
	ModifyGraph hbFill=2,rgb=(0,0,0);DelayUpdate
	Label left "number of network bursts"

	Display durationNB vs conditions
	SetAxis left 0,*
	ModifyGraph hbFill=2,rgb=(0,0,0);DelayUpdate
	ErrorBars durationNB Y,wave=(durationNB_SEM,)
	Label left "network burst duration (sec)"

	Display INBI vs conditions
	SetAxis left 0,*
	ModifyGraph hbFill=2,rgb=(0,0,0);DelayUpdate
	ErrorBars INBI Y,wave=(INBI_SEM,)
	Label left "inter network burst interval"

	Display numSpikesInNB vs conditions
	SetAxis left 0,*
	ModifyGraph hbFill=2,rgb=(0,0,0);DelayUpdate
	ErrorBars numSpikesInNB Y,wave=(numSpikesInNB_SEM,)
	Label left "spikes per network burst"

	Display numContactsInNB vs conditions
	SetAxis left 0,*
	ModifyGraph hbFill=2,rgb=(0,0,0);DelayUpdate
	ErrorBars numContactsInNB Y,wave=(numContactsInNB_SEM,)
	Label left "contacts per network burst"
	
	MakeSummaryLayouts()
	
	Edit conditions, ASDR, ASDR_SEM, numBursts, burstDur, burstDur_SEM, IBI, IBI_SEM, spikeRateInBurst, spikeRIB_SEM, numSpikesInBurst, numSIB_SEM
	Edit conditions, numNB, durationNB, durationNB_SEM, numSpikesInNB, numSpikesInNB_SEM, numContactsInNB, numContactsInNB_SEM, INBI, INBI_SEM

	SetDataFolder cdf

End


Function MakeSummaryLayouts()
	String win, wlist = WinList("*", ";", "WIN:1")	//list of graphs
	Variable i
	
	NewLayout /P=Landscape
	for (i=5; i <=10; i+=1)
		win = StringFromList(i, wlist)
		AppendLayoutObject graph $win
	endfor
	TextBox "\\Z24HD burst summary"
	Execute /Q "FinalSummary_1_Style()"

	NewLayout /P=Landscape
	for (i=0; i <=4; i+=1)
		win = StringFromList(i, wlist)
		AppendLayoutObject graph $win
	endfor
	TextBox "\\Z24HD network burst summary"
	Execute /Q "FinalSummary_2_Style()"

End


Proc ReSummarizeData()

	SummarizeDataFcn()
	
End


Function SummarizeDataFcn()
	String wn, wn2, df, fn, cdf = GetDataFolder(1)
	variable Counter, Index, numFolders, numDel
	
	numFolders = CountObjects(":", 4)		//count folders

	NewDataFolder/O/S summary
	Make /O/T/N=(numFolders) conditions, names
	Make /O/N=(numFolders) ASDR, ASDR_SEM, numBursts, burstDur, burstDur_SEM, IBI, IBI_SEM, spikeRateInBurst, spikeRIB_SEM, numSpikesInBurst, numSIB_SEM
	Make /O/N=(numFolders) numNB, durationNB, durationNB_SEM, numSpikesInNB, numSpikesInNB_SEM, numContactsInNB, numContactsInNB_SEM, INBI, INBI_SEM, NBCompare, NBCompare_SEM
	Make /O/N=(numFolders) B
	
	names[0] = "base"
	names[1] = "Tx"
	numDel = 0
	for (Index = 0; Index < numFolders; Index += 1)
		conditions[Index] = GetIndexedObjName(cdf, 4, Index + numDel)
		if(cmpstr(conditions[Index], "summary") == 0)
			print "Index =", Index, " and folder is", conditions[Index]
			DeletePoints Index, 1, conditions, names
			DeletePoints Index, 1, ASDR, ASDR_SEM, numBursts, burstDur, burstDur_SEM, IBI, IBI_SEM, spikeRateInBurst, spikeRIB_SEM, numSpikesInBurst, numSIB_SEM
			DeletePoints Index, 1, numNB, durationNB, durationNB_SEM, numSpikesInNB, numSpikesInNB_SEM, numContactsInNB, numContactsInNB_SEM, INBI, INBI_SEM, NBCompare, NBCompare_SEM
			DeletePoints Index, 1, B
			numFolders -= 1
			Index -= 1
			numDel += 1
		else
			wn = cdf + conditions[Index] + ":cells:ASDR"
			Wave w1 = $wn
			WaveStats/Q w1
			ASDR[Index] = V_avg
			ASDR_SEM[Index] = V_sdev/sqrt(V_npnts)
	
			wn = cdf + conditions[Index] + ":cells:B"
			Wave w1 = $wn
			If (WaveExists(w1))
				B[Index] = w1[0]
			else
				df = cdf + conditions[Index] + ":cells"
				SetDataFolder df
				Wave Sweep_Stop = Sweep_Stop
				CalculateB(0, Sweep_Stop[0] + 1)	// often collects an extra second+ of data
				SetDataFolder cdf
				Wave w1 = $wn		// It didn't exist the last time this statement was executed!
				B[Index] = w1[0]
			endif				

			// bursts folder
			df = cdf +  conditions[Index] + ":bursts:"
			wn = df + "burstDuration"
			Wave w1 = $wn
			if (WaveExists(w1))
				numBursts[Index] = numpnts(w1)
				WaveStats /Q w1
				burstDur[Index] = V_avg
				burstDur_SEM[Index] = V_sdev/sqrt(V_npnts)
			
				wn = df +"numSpikesInBurst"
				Wave w1 = $wn
				WaveStats/Q w1
				numSpikesInBurst[Index] = V_avg
				numSIB_SEM[Index] = V_sdev/sqrt(V_npnts)
			
				wn2 = df + "spikeRateInBurst"
				Duplicate /O $wn, $wn2
				wn = df + "burstDuration"
				Wave w1 = $wn
				Wave w2 = $wn2
				w2 /= w1
				WaveStats/Q w2
				spikeRateInBurst[Index] = V_avg
				spikeRIB_SEM[Index] = V_sdev/sqrt(V_npnts)
			
				wn = df + "networkBursts"
				Wave w1 = $wn
				if (DimSize(w1, 0) > 1)		// no network burst analysis unless at least 2 NB
					numNB[Index] =  DimSize(w1,0)
				
					wn = df + "networkBurstsDur"
					Wave w1 = $wn
					WaveStats/Q w1
					durationNB[Index] = V_avg
					durationNB_SEM[Index] = V_sdev/sqrt(V_npnts)
				
					wn = df + "numSpikesInNB"
					Wave w1 = $wn
					WaveStats/Q w1
					numSpikesInNB[Index] = V_avg
					numSpikesInNB_SEM[Index] = V_sdev/sqrt(V_npnts)
				
					wn = df + "networkBurstsNumContacts"
					Wave w1 = $wn
					WaveStats/Q w1
					numContactsInNB[Index] = V_avg
					numContactsInNB_SEM[Index] = V_sdev/sqrt(V_npnts)
				
					wn = df + "networkBursts_IBI"
					Wave w1 = $wn
					WaveStats/Q w1
					INBI[Index] = V_avg
					INBI_SEM[Index] = V_sdev/sqrt(V_npnts)
				
				else
					numNB[Index] =  0
				
					durationNB[Index] = 0
					durationNB_SEM[Index] = 0
				
					numSpikesInNB[Index] = 0
					numSpikesInNB_SEM[Index] = 0
				
					numContactsInNB[Index] = 0
					numContactsInNB_SEM[Index] = 0
				
					INBI[Index] = 0
					INBI_SEM[Index] = 0
				
					NBCompare[Index] = 0
					NBCompare_SEM[Index] = 0
					
				endif
		
				// ibi folder
				df = cdf +  conditions[Index] + ":ibi:"
				wn = df + "IBIList"
				Wave w1 = $wn
				if (numpnts(w1) > 0)
					WaveStats/Q w1
					IBI[Index] = V_avg
					IBI_SEM[Index] = V_sdev/sqrt(V_npnts)
				else
					IBI[Index] = 0
					IBI_SEM = 0
				endif
				
			else
				burstDur[Index] = 0
				burstDur_SEM[Index] = 0
			
				numSpikesInBurst[Index] = 0
				numSIB_SEM[Index] = 0
			
				spikeRateInBurst[Index] = 0
				spikeRIB_SEM[Index] = 0
	
				numNB[Index] =  0
			
				durationNB[Index] = 0
				durationNB_SEM[Index] = 0
			
				numSpikesInNB[Index] = 0
				numSpikesInNB_SEM[Index] = 0
			
				numContactsInNB[Index] = 0
				numContactsInNB_SEM[Index] = 0
			
				INBI[Index] = 0
				INBI_SEM[Index] = 0
			
				NBCompare[Index] = 0
				NBCompare_SEM[Index] = 0
				
				IBI[Index] = 0
				IBI_SEM[Index] = 0
			
			endif
		endif
	endfor

	SetDataFolder cdf
		
End 
	

Proc FinalSummary_1_Style() : LayoutStyle
	PauseUpdate; Silent 1		// modifying window...
	ModifyLayout/Z frame=1
	ModifyLayout/Z left[0]=396,top[0]=396,width[0]=360,height[0]=162
	ModifyLayout/Z left[1]=396,top[1]=234,width[1]=360,height[1]=162
	ModifyLayout/Z left[2]=396,top[2]=72,width[2]=360,height[2]=162
	ModifyLayout/Z left[3]=36,top[3]=396,width[3]=360,height[3]=162
	ModifyLayout/Z left[4]=36,top[4]=234,width[4]=360,height[4]=162
	ModifyLayout/Z left[5]=36,top[5]=72,width[5]=360,height[5]=162
	ModifyLayout/Z left[6]=228.75,top[6]=36,width[6]=334.5,height[6]=33
EndMacro


Proc FinalSummary_2_Style() : LayoutStyle
	PauseUpdate; Silent 1		// modifying window...
	ModifyLayout/Z frame=1
	ModifyLayout/Z left[0]=396,top[0]=234,width[0]=360,height[0]=162
	ModifyLayout/Z left[1]=396,top[1]=72,width[1]=360,height[1]=162
	ModifyLayout/Z left[2]=36,top[2]=396,width[2]=360,height[2]=162
	ModifyLayout/Z left[3]=36,top[3]=234,width[3]=360,height[3]=162
	ModifyLayout/Z left[4]=36,top[4]=72,width[4]=360,height[4]=162
	ModifyLayout/Z left[5]=185.25,top[5]=35.25,width[5]=428.25,height[5]=33
EndMacro
