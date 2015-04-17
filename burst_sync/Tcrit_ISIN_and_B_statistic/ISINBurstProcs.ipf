#pragma rtGlobals=3		// Use modern global access method.
#include ":Utilities"
#include ":BurstProcs"


Menu "Macros"
	"Find ISI_N Bursts", ISIN()
	"Summaraize ISIN Trial", SummarizeTrialISIN()
end

Function ISIN()
	Variable N=10
	Variable ISI_N = 0.2
	
	CreateISINSpikeList(N)
	CalculateISIN(N)
	FindISINBursts(N, ISI_N)
End


Function SummarizeTrialISIN()
	Variable N=10
	
	SummarizeISINData(N)
End


Function CreateISINSpikeList(N)
	// This function combines all of the spike times in the cells folder into a single
	// spiketimes wave with a companion spikechannel wave in the ISIN folder
	// It assumes it is being run in the directory above the cells directory
	Variable N
	
	Silent 1; PauseUpdate

	String cdf, fn, wn, wl
	Variable total, len, num, index
	cdf = GetDataFolder(1)
	fn = cdf + "ISI_" + num2istr(N)
	NewDataFolder /O/S $fn
	Make /O/N=0 spikeTimes, contact
	SetDataFolder cdf

	SetDataFolder cells
	wl = WaveList("ch*", ";", "")
	total = 0
	index = 0
	do
		wn = StringFromList(index, wl, ";")
		if (strlen(wn) == 0)
			break
		endif

		Wave channel = $wn
		len = numpnts(channel)
		if (len > 0)
			num = ConvertWaveNameToContact(wn)
			InsertPoints total, len, spikeTimes, contact
			spikeTimes[total, ] = channel[p - total]
			contact[total, ] = num
			total += len
		endif
		
		index += 1
		
	while (1)

	Sort spikeTimes, spikeTimes, contact
	
	SetDataFolder cdf
End


Function CalculateISIN(N)
	// This function calculates ISI_N as defined by Bakkum et al 2013 Front Comput Neurosci 7, 193.
	// It assumes it is being run in the directory above the ISIN directory
	Variable N
	
	String wn, fn, cdf
	Variable len
	
	Silent 1; PauseUpdate
	
	cdf = GetDataFolder(1)
	fn = cdf + "ISI_" + num2istr(N)
	SetDataFolder $fn
	wn = "isi_" + num2str(N)
	Wave spikeTimes
	len = numpnts(spikeTimes)
	Make /O /N=(len - N + 1) $wn
	Wave isi = $wn
	isi = spikeTimes[p + N - 1] - spikeTimes[p]
	
	SetDataFolder cdf
	
End


Function FindISINBursts(N, ISI_N)
	// This function bursts as defined by Bakkum et al 2013 Front Comput Neurosci 7, 193.
	// It assumes it is being run in the directory above the ISIN directory
	Variable N, ISI_N

	String wn, cdf, fn
	Variable len, i, start,  count
	Silent 1; PauseUpdate
	
	cdf = GetDataFolder(1)
	fn = cdf + "ISI_" + num2istr(N)
	SetDataFolder $fn
	wn = "isi_" + num2str(N)
	Wave spikeTimes
	Wave isi = $wn
	len = numpnts(isi)
	Make /O/N=(len+N) burstNum
	burstNum = -1
	i = 0
	count = 1
	
	// look for bursts
	do
		if (isi[i] < ISI_N)
			burstNum[i, i+N-1] = count
			for(i += 1; (i < len) && (isi[i] <= ISI_N); i +=1)
				// scanning forward in current burst
				burstNum[i+N-1] = count
			endfor
			count += 1
			i += N - 2
		endif
		i += 1
		
	while(i < len)
	
	if (count > 1)		// test to see if any bursts were identified
		// calculate burst characteristics
		Make /O/N=(count-1) burstStart, burstEnd, burstDur, numSpikesInBurst, spikeRateInBurst
		Make /O/N=(count-1, 61) burstContacts = 0
		Wave spikeTimes
		Wave contact
		len += N -1
		count = 0
		
		// find burst start time, end time and track contacts in each burst
		for (i = 0; i < len; i += 1)
			if (burstNum[i] > count)
				burstStart[count] = spikeTimes[i]
				burstContacts[count][contact[i]] = 1
				start = i
				count += 1
				for (i += 1; (i < len ) && (burstNum[i] == count); i += 1)
					// scanning current burst
					burstContacts[count-1][contact[i]] = 1
				endfor
				i -= 1
				burstEnd[count-1] = spikeTimes[i]
				numSpikesInBurst[count-1] = i - start + 1
			endif
		endfor
		
		// calculate burst durations, contacts per burst and ibi
		burstDur = burstEnd - burstStart
		spikeRateInBurst = numSpikesInBurst / burstDur
		MatrixOp /O numContactsInBurst = sumRows(burstContacts)
		if (numpnts(burstStart) > 1)	// make sure there is more than one burst before trying to calculate ibi
			Make /O/N=(numpnts(burstStart)-1) ibi
			ibi = burstStart[p+1] - burstEnd[p]
		endif
	endif
	
	SetDataFolder cdf

End


Function SummarizeISINData(N)
	// collect ISIN data from each trial into a subfolder in the summary folder
	// This function assumes it is being run at the level above the experiment folders
	Variable N
	String wn, wn2, df, fn, cdf = GetDataFolder(1)
	Variable Counter, Index, numFolders, numDel
	
	numFolders = CountObjects(":", 4)		//count folders

	fn = "ISI_" + num2istr(N)
	NewDataFolder/O/S summary
	NewDataFolder/O/S $fn
	Make /O/T/N=(numFolders) conditions
	Make /O/N=(numFolders) numBursts, burstDur, burstDur_SEM, IBI, IBI_SEM, spikeRateInBurst, spikeRateInBurst_SEM
	Make /O/N=(numFolders)  numSpikesInBurst, numSpikesInBurst_SEM, numContactsInBurst, numContactsInBurst_SEM
	
	numDel = 0
	for (Index = 0; Index < numFolders; Index += 1)
		conditions[Index] = GetIndexedObjName(cdf, 4, Index + numDel)
		if(cmpstr(conditions[Index], "summary") == 0)
			print "Index =", Index, " and folder is", conditions[Index]
			DeletePoints Index, 1, conditions
			DeletePoints Index, 1, numBursts, burstDur, burstDur_SEM, IBI, IBI_SEM, spikeRateInBurst, spikeRateInBurst_SEM
			DeletePoints Index, 1, numSpikesInBurst, numSpikesInBurst_SEM, numContactsInBurst, numContactsInBurst_SEM
			numFolders -= 1
			Index -= 1
			numDel += 1
		else
			df = cdf +  conditions[Index] + ":ISI_" + num2istr(N)
			wn = df + ":burstDur"
			print wn
			Wave w1 = $wn
			if (WaveExists(w1))
				numBursts[Index] = numpnts(w1)
				WaveStats /Q w1
				burstDur[Index] = V_avg
				burstDur_SEM[Index] = V_sdev/sqrt(V_npnts)
			
				wn = df + ":numSpikesInBurst"
				Wave w1 = $wn
				WaveStats/Q w1
				numSpikesInBurst[Index] = V_avg
				numSpikesInBurst_SEM[Index] = V_sdev/sqrt(V_npnts)
			
				wn = df + ":spikeRateInBurst"
				Wave w1 = $wn
				WaveStats/Q w1
				spikeRateInBurst[Index] = V_avg
				spikeRateInBurst_SEM[Index] = V_sdev/sqrt(V_npnts)
			
				wn = df + ":numContactsInBurst"
				Wave w1 = $wn
				WaveStats/Q w1
				numContactsInBurst[Index] = V_avg
				numContactsInBurst_SEM[Index] = V_sdev/sqrt(V_npnts)
				
				wn = df + ":ibi"
				Wave w1 = $wn
				if (numpnts(w1) > 0)
					WaveStats/Q w1
					IBI[Index] = V_avg
					IBI_SEM[Index] = V_sdev/sqrt(V_npnts)
				else
					IBI[Index] = 0
					IBI_SEM[Index] = 0
				endif
				
			else
				numBursts[Index] = 0
				
				burstDur[Index] = 0
				burstDur_SEM[Index] = 0
			
				numSpikesInBurst[Index] = 0
				numSpikesInBurst_SEM[Index] = 0
			
				spikeRateInBurst[Index] = 0
				spikeRateInBurst_SEM[Index] = 0
				
				numSpikesInBurst[Index] = 0
				numSpikesInBurst_SEM[Index] = 0
			
				numContactsInBurst[Index] = 0
				numContactsInBurst_SEM[Index] = 0
							
				IBI[Index] = 0
				IBI_SEM[Index] = 0
							
			endif
		endif
	endfor

	Edit conditions, numBursts, burstDur, burstDur_SEM, IBI, IBI_SEM, spikeRateInBurst, spikeRateInBurst_SEM, numSpikesInBurst, numSpikesInBurst_SEM

	SetDataFolder cdf
		
End 


Function CreateISINHistogramPlot(first, last)
	// This function creates an ISI_N histogram as shown in Figure 2A of Bakkum et al 2013 Front Comput Neurosci 7, 193.
	// after first creating the ISI_N folders and calculating the corresponding isi
	// It assumes it is being run in the directory above the cells directory
	Variable first, last
	Variable i
	
	for(i = first; i <= last; i += 1)
		CreateISINSpikeList(i)
		CalculateISIN(i)
	endfor
	
	RePlotISINHistogram(first, last)

End


Function RePlotISINHistogram(first, last)
	// This function creates an ISI_N histogram as shown in Figure 2A of Bakkum et al 2013 Front Comput Neurosci 7, 193.
	// It assumes it is being run in the directory above the ISIN directories which have already been created
	Variable first, last
	Variable i, startDecade=-4, numDecades=5, binsPerDecade=20, numBins, logDeltaX
	String fn, wn, destXWave, destYWave, cdf = GetDataFolder(1)

	numBins= numDecades * binsPerDecade
	logDeltaX=1/binsPerDecade // Log delta X (1 gives 1 decade per bin)
	
	for(i = first; i <= last; i += 1)
		fn = "ISI_" + num2istr(i)
		SetDataFolder $fn
		wn = "isi_" + num2istr(i)
		destXWave = wn + "_hx"
		destYWave = wn + "_hy"
		Make/O/N=(numBins+1) $destXWave=0, $destYWave=0
		DoLogHist($wn, $destXWave, $destYWave, startDecade, logDeltaX)
		if (i == first)
			Display $destYWave vs $destXWave
		else
			AppendToGraph $destYWave vs $destXWave
		endif
		SetDataFolder cdf
	endfor
	
End


// From the Igor Manual
// DoLogHist(sw, dwX, dwY, startX, logDeltaX)
// Creates the logarithmic histogram of the source wave by summing the
// appropriate numbers into the destination y wave.
// sw is the source wave.
// dwX is the destination x wave.
// dwY is the destination y wave.
// startX, logDeltaX are explained below in LogHist().
Function DoLogHist(sw, dwX, dwY, startX, logDeltaX)
	Wave sw, dwX, dwY
	Variable startX, logDeltaX
	Variable pt, pp, dpnts, spnts
	// first find bin edges and put them in dwX
	dpnts = numpnts(dwX)
	for (pt = 0; pt < dpnts; pt += 1)
		dwX[pt]= 10^(pt*logDeltaX+startX) // this value is 10^startX when p == 0
	endfor
	// now find which bin of dwY each Y value in sw belongs in and increment it.
	spnts = numpnts(sw)
	for (pt = 0; pt < spnts; pt += 1)
		pp = (log(sw[pt]) - startX) / logDeltaX
		if( pp == limit(pp,0,dpnts) ) // unless it is out of range or NaN
			dwY[pp] += 1
		endif
	endfor
End


// From the Igor Manual
// LogHist(sourceWave, numDecades, startDecade, binsPerDecade)
// Creates XY pair of waves that represent the logarithmic histogram of the
// source wave. If the source wave is named "data" then the output waves will
// be named "data_hx" and "data_hy".
// The product of numDecades and binsPerDecade specifies the number of bins in
// the histogram.
// startDecade specifies the X coordinate of the left edge of first bin. The bin
// starts at 10^startDecade.
// binsPerDecade specifies the bin width. Values less than 1 result in bins that
// span multiple decades. For example, set binsPerDecade to 0.5 to create bins
// that span two decades.
// Example
// Make/N=100 test = 10^(1+abs(gnoise(3)))
// Display test; ModifyGraph log(left)=1, mode=8,msize=2
// LogHist("test",12,0,1)
Function LogHist()
	String sourceWave= StrVarOrDefault("root:Packages:LogHist:sourceWave","_demo_")
	Variable numDecades = NumVarOrDefault("root:Packages:LogHist:numDecades",10)
	// first bin at 0.0001
	Variable startDecade = NumVarOrDefault("root:Packages:LogHist:startDecade",-4)
	Variable binsPerDecade= NumVarOrDefault("root:Packages:LogHist:binsPerDecade",1)
	Prompt sourceWave, "Source wave", popup "_demo_;"+WaveList("*", ";", "")
	Prompt startDecade, "start decade (first bin starts at 10^startDecade)"
	Prompt numDecades, "Number of decades in destination waves"
	Prompt binsPerDecade, "bins per decade"
	DoPrompt "Log Histogram", sourceWave, numDecades, startDecade, binsPerDecade
	if( CmpStr(sourceWave,"_demo_") == 0 )
		sourceWave= "demoData"
		Make/O/N=100 $sourceWave=0.0001+10^(gnoise(2)) // about 10^-4 to 10^6
		CheckDisplayed/A $sourceWave
		if( V_Flag == 0 )
			Display $sourceWave; ModifyGraph log(left)=1, mode=8,msize=2
		endif
		startDecade=-4
		numDecades=10
		binsPerDecade=1
	endif
	if( binsPerDecade < 0 )
		binsPerDecade = 1
	endif
	// Save values for next attempt
	NewDataFolder/O root:Packages
	NewDataFolder/O root:Packages:LogHist
	String/G root:Packages:LogHist:sourceWave = sourceWave
	Variable/G root:Packages:LogHist:numDecades= numDecades
	Variable/G root:Packages:LogHist:startDecade= startDecade
	Variable/G root:Packages:LogHist:binsPerDecade= binsPerDecade
	String destXWave, destYWave
	// Concoct names for dest waves.
	// This does not work if sourceWave is a full or partial path requiring single
	// quotes (e.g., root:Data:'wave 0').
	Variable numBins= numDecades * binsPerDecade
	Variable logDeltaX=1/binsPerDecade // Log delta X (1 gives 1 decade per bin)
	destXWave = sourceWave + "_hx"
	destYWave = sourceWave + "_hy"
	Make/O/N=(numBins+1) $destXWave=0, $destYWave=0
	DoLogHist($sourceWave, $destXWave, $destYWave, startDecade, logDeltaX)
	print "made histogram"
	CheckDisplayed/A $destYWave
	if( V_Flag == 0 )
		Display $destYWave vs $destXWave
		AutoPositionWindow/E/M=1
		ModifyGraph mode=4, marker=19, log(bottom)=1
	endif
End


