#pragma rtGlobals=1		// Use modern global access method.
#include ":BurstProcs"
#include ":Summary Proc"
#include ":Utilities"

Menu "Macros"
	"Process Data", ProcessData()
	"Summarize Data", SummarizeData()
	"Redraw Raster Plot", RedrawRasterPlot()
	"Recalculate ISI Histogram", ReCalculateISIHistogram()
	"Recalculate IBI Histograms", ReCalculateIBIHistogram()
end
	


Function ProcessData()

	Variable tstart=0, tend, tcrit = 0.15
	String CurrentDataFolder = GetDataFolder(1)
	SetDataFolder "cells"
	
	Wave Sweep_Stop = Sweep_Stop
	tend = Sweep_Stop[0]
	
	DisplayRasterPlot(tstart, tend - 1)
	CalculateASDR()
	Display ASDR
	Label left "spikes per second"
	Label bottom "sec"
	
	CalculateB(tstart, tend + 1)	// often collect an extra second+ of data
	
	SetDataFolder CurrentDataFolder
	CalculateISI()	
	FindBurstsFcn(tcrit)
	ProcessBurstData()

End


Function RedrawRasterPlot()
	variable startTime = 0, endTime = 150
	Prompt startTime, "Start Time: "
	Prompt endTime, "End TIme: "
	DoPrompt "Redraw Raster Plot", startTime, endTime
	if (V_Flag)
		return -1
	endif

	String df = GetDataFolder(1)
	SetDataFolder "cells"
	DisplayRasterPlot(startTime, endTime)
	SetDataFolder df
End


Function ReCalculateISIHistogram()
	Variable binSize = 0.02, numBins = 500, startPoint = 1
	Prompt binSize, "Bin Size"
	Prompt numBins, "Number of Bins"
	Prompt startPoint, "1st point to include in the fit"
	DoPrompt "Enter ISI Histogram Parameters", binSize, numBins, startPoint
	if (V_Flag)
		return -1
	endif

	String df = GetDataFolder(1)
	SetDataFolder "isi"
	CalcSummaryISIHistogram(binSize, numBins, startPoint)
	SetDataFolder df
End


Function CalculateASDR()
	// This function calculates the array-wide spike detection rate and stores in the wave ASDR
	// Wagenaar et al BMC Neuroscience 7:11 2006
	// It assumes that it is being run in the directory with the spike times

	String wn,wl
	Variable i, t, index = 0
	
	Silent 1; PauseUpdate

	Wave Sweep_Stop
	Variable tstart = 0, tend = floor(Sweep_Stop[0])
	if (numpnts(Sweep_Stop) == 2)
		tstart = floor(Sweep_Stop[1])
	endif
	
	Make /O/N=(tend - tstart) ASDR = 0	
	SetScale x tstart, tend, ASDR	
	wl = WaveList("ch*", ";", "")
	do
		wn = StringFromList(index, wl, ";")
		if (strlen(wn) == 0)
			break
		endif

		Wave localWave = $wn
		t = 1
		for (i = 0; i < numpnts(localWave); i += 1)
			If ((localWave[i] > t + tstart - 1) & (localWave[i] <= t + tstart))
				ASDR[t] += 1
			else
				if (localWave[i] > t + tstart - 1)
					do
						t += 1
					while (localWave[i] > t + tstart)
					ASDR[t] += 1
				endif
			endif
		endFor
				
		index += 1
		
	while (1)
//	ASDR /= index
			
End




Function CalculateB(start, endtime)
	Variable start, endtime
	//  This function calculates the interspike synchrony measure called B in Bogaard J Neurosci 2009
	//  that was taken from Tiesinga and Sejnowski  Neural Computation 2004.
	//  The value is zero for asynchronous activity and 1 for completely synchronous activity.
	//  This function creates a wave B that is the value calculated over the entire dataset.
	//  It assumes that it is being run in the directory with the spike times

	String wn,wl
	Variable i, j, numcells, totalpts = 0, index = 0
	Silent 1; PauseUpdate

//	Wave Sweep_Stop
//	Make /O/N=(floor(Sweep_Stop[0]) - 1) B = 0	
	Make /O/N=(1) B = 0
	
	wl = WaveList("ch*", ";", "")

	//	count the number of active channels and the total number of spikes
	do
		wn = StringFromList(index, wl, ";")
		if (strlen(wn) == 0)
			break
		endif

		Wave localWave = $wn
		totalpts += numpnts(localWave)
		index += 1		
	while (1)
	numcells = index
	
	Make /O/N=(totalpts) spiketimes
	
	//	concatenate spike times
	index = 0
	i = 0
	do
		wn = StringFromList(index, wl, ";")
		if (strlen(wn) == 0)
			break
		endif

		Wave localWave = $wn
		j = numpnts(localWave)
		spiketimes[i, i+j-1] = localWave[p-i]
		i += j
		index += 1		
	while (1)
	
	//	cut out the desired range of spike times
	sort spiketimes, spiketimes
	Variable startP, endP, lastP
	Wave Sweep_Stop
	if ((start == 0) || (spiketimes[0] > start))
		startP = 0
	else
		Findlevel /P/Q spiketimes, start
		startP = floor(V_LevelX) + 1
		print startP
	endif
	
	lastP = numpnts(spiketimes) - 1
	if (endtime >= spiketimes[lastP])
		endP = lastP
	else
		Findlevel /P/Q spiketimes, endtime
		endP = floor(V_LevelX)
	endif
	
//	print start, startP, endtime, endP	
	Duplicate /O spiketimes fullspiketimes
	Duplicate /O/R=[startp, endP] fullspiketimes spiketimes
	
	//	calculate tau's (= isi), tau_sqaured's and corresponding time
	Make /O/N=(numpnts(spiketimes) - 1) isi, isitime, isisq
	isi = spiketimes[p+1] - spiketimes[p]
	isitime = (spiketimes[p] + spiketimes[p+1])/2
	isisq = isi^2

//	//	calculate B in 1 second intervals
//	Variable p1 = -1, p2 = 0, tbar = 0, tsqbar = 0
//	for (index = 0; index < numpnts(B); index += 1)
//		if ((isitime[p2] < index + 1) && (p2 < numpnts(B)))
//			do
//				tbar += isi[p2]
//				tsqbar += isisq[p2]
//				p2 += 1
//			while ((isitime[p2] < index + 1) && (p2 < numpnts(B)))
//			tbar /= (p2 - p1 - 1)
//			tsqbar /= (p2 - p1 - 1)
//			B[index] = ((sqrt(tsqbar - tbar^2)/tbar) - 1)/sqrt(p2 - p1 -1)
//			tbar = 0
//			tsqbar = 0
//			p1 = p2 - 1
//		else
//			B[index] = 0
//		endif
//	endfor
	
	//	calculate B for the entire dataset
	Variable tbar, tsqbar
	WaveStats/Q isi
	tbar = V_avg
	WaveStats /Q isisq
	tsqbar = V_avg
	
	KillWaves fullspiketimes, spiketimes, isi, isisq, isitime 
	B[0] = ((sqrt(tsqbar - tbar^2)/tbar) - 1)/sqrt(numcells)
		
End


Function DisplayRasterPlot(startTime, endTime)
	Variable startTime, endTime
	// This function creates an empty wave and displays it to provide a graph
	// It then uses drawing functions to draw a vertical line for each spike
	// This produces a much smaller graph than creating a set of waves with values at every timepoint
	// at the cost of not being able to expand the graph in the usual fashion

	Variable i, j
	Variable x0,y0,x1,y1
	String wn,wl
	Variable delta, index = 0
	Variable maxTime = 500
	
	Silent 1; PauseUpdate

	Make /O/N=0 RasterPlotWave = 0	
	Display RasterPlotWave
	SetAxis bottom startTime, endTime
	SetAxis left 0,60
	Label bottom "sec"
	Label left "Contact"

	SetDrawLayer ProgFront
	SetDrawEnv fillfgc = (0,0,0)
	
	wl = WaveList("ch*", ";", "")
	if (endTime - startTime < maxTime)
		do
			wn = StringFromList(index, wl, ";")
			if (strlen(wn) == 0)
				break
			endif

			Wave localWave = $wn
			y0 = ConvertWaveNameToContact(wn)
			y0 = 1 - (y0/60)
			y1 = y0 - (0.75/60)
			for (i = 0; i < numpnts(localWave); i += 1)
				If ((localWave[i] >= startTime) & (localWave[i] <=endTime))
					x0 = (localWave[i] - startTime)/(endTime - startTime)
					x1 = x0
					SetDrawEnv fillfgc = (0,0,0)
					Drawline x0, y0, x1, y1
				endif
			endFor
				
			index += 1
		
		while (1)
	else
		do
			wn = StringFromList(index, wl, ";")
			if (strlen(wn) == 0)
				break
			endif

			Wave localWave = $wn
			y0 = ConvertWaveNameToContact(wn)
			y0 = 1 - (y0/60)
			y1 = y0 - (0.75/60)
			Make /O/N=(maxTime) dummy = 0
			delta = (endTime - startTime)/MaxTime

			for (i=0; i < numpnts(localWave); i += 1)
				if ((localWave[i] >= startTime) & (localWave[i] <= endTime))
					j = floor((localWave[i] - startTime)/delta)
					dummy[j] = 1
				endif
			endFor
			
			for (i = 0; i < maxTime; i += 1)
				If (dummy[i] == 1)
					x0 = (i/maxTime) + (1/(2*maxTime))
					x1 = x0
					SetDrawEnv fillfgc = (0,0,0)
					Drawline x0, y0, x1, y1
				endif
			endFor
				
			index += 1
		
		while (1)
		KillWaves dummy
		
	endif
	
			
End


Function CalculateISI()
	// This function calculates the interspike interval for each contact
	// and stores in a subdirectory called isi in the spike directory
	// It also creates a summary histogram of ISI's for all contacts
	// It assumes that it is being run in the directory with the spike times

	String wn,wl, df, isi
	Variable i, index = 0
	
	Silent 1; PauseUpdate
	
	df = GetDataFolder(1)
	NewDataFolder/O isi
	SetDataFolder "cells"
	wl = WaveList("ch*", ";", "")
	do
		wn = StringFromList(index, wl, ";")
		if (strlen(wn) == 0)
			break
		endif

		Wave localWave = $wn
		if (numpnts(localWave) > 1)
			isi = df+ "isi:" + wn + "_isi"
			Make /O/N=(numpnts(localWave) - 1) $isi
			Wave localisi = $isi
			localisi = localWave[p+1] - localWave[p]		
		endif
				
		index += 1
		
	while (1)
	
	SetDataFolder df
	SetDataFolder "isi"
	CalcSummaryISIHistogram(0.02, 500, 1)
	SetDataFolder df
End


Function CalcSummaryISIHistogram(binSize, numBins, startPoint)
	Variable binSize, numBins, startPoint
	// This function calculates the summary interspike interval histogram
	// and stores it in summaryHistogram
	// It assumes that it is being run in the directory with the isi times
	
	String wn, wl
	Variable index = 0, tot = 0
	
	Silent 1; PauseUpdate
	
	Make/O/N=0 summaryHistogram = 0
	wl = WaveList("ch*", ";", "")
	do
		wn = StringFromList(index, wl, ";")
		if (strlen(wn) == 0)
			break
		endif

		Wave localISI = $wn
		tot += numpnts(localISI)
		
		if (numpnts(summaryHistogram) == 0)
			Histogram/C/B={0, binSize, numBins}/C localISI, summaryHistogram
		else
			Histogram/A localISI, summaryHistogram
		endif
						
		index += 1
		
	while (1)
	summaryHistogram /= tot
	Display summaryHistogram
	ModifyGraph log(left)=1
	SetAxis left 0.00001,1	
	ModifyGraph mode=3,marker=8,rgb=(0,0,0)
	Label left "probability"
	Label bottom "ISI (sec)"
	index = numpnts(summaryHistogram) - 1
	Duplicate /O summaryHistogram weights
	weights = (summaryHistogram[p] == 0) ? 1 : sqrt(summaryHistogram[p])
	CurveFit/Q/NTHR=0 /TBOX=(1+256+512) dblexp_XOffset  summaryHistogram[startPoint,index] /I=1 /W=weights /D	
	KillWaves weights
End


Function DisplayISIHistograms()
	// This function displays interspike interval histograms for each contact
	// It assumes that it is being run in the directory with the ISI data

	String wn, wl, hist
	Variable index = 0
	
	Silent 1; PauseUpdate
	
	wl = WaveList("ch*", ";", "")
	do
		wn = StringFromList(index, wl, ";")
		if (strlen(wn) == 0)
			break
		endif

		Wave localWave = $wn
		if (numpnts(localWave) > 10)
			hist = "histogram_" + wn
			Make /O/N=0 $hist
			Wave localHist = $hist
			Histogram/B={0, 0.05, 40} localWave, localHist
			localHist /= numpnts(localWave)
			Display localHist
			ModifyGraph log(left)=1
			SetAxis bottom 0,1
			SetAxis left 0.0001,1		
		endif
				
		index += 1
		
	while (1)
	
End
