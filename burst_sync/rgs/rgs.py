# -*- coding: utf-8 -*-
"""
Translation of Robust Gaussian Surprise from R to Python
"""

from __future__ import (print_function, division,
                        unicode_literals, absolute_import)

import numpy as np
import scipy.stats as stats
import pandas as pd

from . import R


def Extcenter(x, pc):
    """
    #center of top pc and bottom pc of log transformed data
    """
    probs = np.asarray([pc, 1-pc])
    return np.mean(R.quantile8(np.log(x), probs))


def runEcen(x, k=41, p=.2, pc=.05, **kwargs):
    """
    #x: ISIs of spike train
    #Moving extreme center of pc-quantile with window size max(k,length(x)*p)
    #output: e-center of log transformed isi

    #k: minimum window size
    #p: window size (100*p=percentage of data point in a window)
    #pc: high/low extreme percentage
    """

    n = len(x)
    k = max(k, len(x)*p)
    k = int(k)
    res = np.empty(n)

    if (k < 0):
        raise ValueError("'k' must be positive")
    if (k % 2 == 0):
        k = int(1 + 2 * (k//2))
        print("'k' must be odd!  Changing 'k' to ", k)
    if (k > n):
        k = int(1 + 2 * ((n - 1) % 2))
        print("'k' is bigger than 'n'!  Changing 'k' to ", k)

    kd = (k - 1) // 2   # half window size
    if (n == k):
        res = Extcenter(x, pc=pc)

    if (n > k):
        # end rule constant
        tx1 = Extcenter(x[:k], pc=pc)
        tx2 = Extcenter(x[(n-k):n], pc=pc)
        res[:kd] = tx1
        res[(n-kd):n] = tx2

        # moving center
        for i in range(kd, n-kd):
            res[i] = Extcenter(x[(i-kd):(i+kd+1)], pc=pc)

    return res  # moving e-center of log(isi)


def runmed(x, k=41, p=.2):
    """
    #x: ISIs
    #Moving median with window size max(k,length(x)*p)
    #output: running median of the log transformed isi
    #k: minimum window size
    #p: window size (percentage of data point)
    """

    return R.runmed(x, k=max(k, int(len(x)*p/2)*2+1))


def norm(x, pc=.05, delta=0.1, **kwargs):
    """

    #this function generates the normalized log(isi) using
    #three step central curve for log(isi)

    #step 1: starting line e-center
    #step 2: central moving median of the isis who falls in centeral area
    #from the e-center
    #step 3: if difference between e-center and moving median is large
    #another central moving median based on isis redefine central area
    #from the previous central moving median

    #input: x #isi data
    #output: normalized ISI  (log(isi)-central curve)
    """
    # step 1 E-center
    tyc = runEcen(x, pc=pc, **kwargs)   # e-center of log(isi).

    # step 2 moving median on central portiion
    # standard deviation of normalized isi
    # and running median for +-sd*qnorm(.95)

    smad = R.mad(np.log(x) - tyc)
    lx = np.log(x)[np.abs(np.log(x)-tyc) <= stats.norm.ppf(.95)*smad]
    tyc2 = runmed(lx, k=41)

    # interpolate the tyc2 to all the area
    index = np.abs(np.log(x)-tyc) <= stats.norm.ppf(.95)*smad
    txs = R.seq(np.log(x))

    txs = np.append(1, txs[index])
    txs = np.append(txs, len(x))
    tyc2 = np.append(tyc2[0], tyc2)
    tyc2 = np.append(tyc2, tyc2[-1])
    tyc3 = np.interp(R.seq(x), txs, tyc2)   # linear interpolation

    # Step 3 requires another run of step 2
    #

    smad = R.mad(np.log(x)-tyc3)
    lx = np.log(x)[np.abs(np.log(x)-tyc3) <= stats.norm.ppf(.95)*smad]
    tyc2 = runmed(lx, k=41)

    # interpolate the tyc2 to all the area
    txs = R.seq(np.log(x))[np.abs(np.log(x)-tyc3) <= stats.norm.ppf(.95)*smad]
    txs = np.append(1, txs)
    txs = np.append(txs, len(x))
    tyc2 = np.append(tyc2[0], tyc2)
    tyc2 = np.append(tyc2, tyc2[-1])
    tyc3 = np.interp(R.seq(x), txs, tyc2)   # linear interpolation

    return(np.log(x)-tyc3)


#######################
# initial seeds of bursts
########################
def nb_seed(x, pc=0.05, central=None, thresh=stats.norm.ppf(0.005),
            **kwargs):
    """
    #generates the burst seed intervals whose length <=thresh
    #x: ISIs
    #p: window size of running center or median
    #pc: top or bottom proportions used in E-center
    #central: data.frame to determind the central portion
    #combined normalized ISIs from a group of spike trains
    #must have the variable "norm.length"

    #Output: burst seeds ISIs with normalized ISIs
    #data.frame(name=name,id=te1,cluster=clus2,
    #interval=interval,norm.length=tz[te1])
    """
    tz = norm(x, pc=.05, **kwargs)  # normalized interval length (log unit)

    central_ = np.asarray(central['norm_length'])   # Combined normalized ISIs
    thresh_ = thresh * R.mad(central_)
    # if the normalized interval length is less than threshold
    # burst-seeds: the normalized ISIs less than threshold + center

    center = np.median(tz[abs(tz) <= abs(thresh_)])
    all_ = pd.DataFrame({'id': np.arange(len(x)), 'interval': x,
                         'norm_length': tz})     # original data
    burst = all_[tz <= thresh_+center].copy()
    # if burst is null, smallest interval to the burst
    if (burst.shape[0] == 0):
        min_ = np.min(all_['norm_length'])
        burst = all_[all_['norm_length'] == min_].copy()

    clusid = np.arange(1, len(burst['id'])+1)
    burst.loc[:, 'clusid'] = clusid
    return [burst, all_]


#####################
# pause seed intervals
#####################
def np_seed(x, pc=0.05, central=None, thresh=stats.norm.ppf(0.995),
            **kwargs):
    """
    #detect the pause seeds whose normalized ISI>=thresh*mad(norm.length)
    #x: ISIs
    #p: window size of running center or median
    #pc: top or bottom proportions used in E-center
    #central: data.frame to determind the central portion
    #combined normalized ISIs from a group of spike trains
    #must have the variable "norm.length"

    #Output: tdata=data.frame(name=name,id=te1,cluster=clus2,
    #interval=interval,norm.length=tz[te1])
    """
    tz = norm(x, pc=.05, **kwargs)  # normalized interval length (log unit)
    central_ = np.asarray(central["norm_length"])
    thresh_ = thresh * R.mad(central_)

    # seeds: the normalized interval length > threshold + center

    center = np.median(tz[abs(tz) <= thresh_])
    all_ = pd.DataFrame({'id': np.arange(len(x)), 'interval': x,
                         'norm_length': tz})    # original data
    pause = all_[tz >= thresh_+center].copy()

    # if pause is null, largest interval to the pause
    if (pause.shape[0] == 0):
        max_ = np.max(all_['norm_length'])
        pause = all_[all_['norm_length'] == max_].copy()
    clusid = np.arange(1, len(pause['id'])+1)
    pause.loc[:, 'clusid'] = clusid
    return [pause, all_]


##############
# P-values for the bursts
##############
def np_burst(bcluster, mu=0, sigma=1):
    """
    #calculates the p-value of the burst cluster bcluster
    #input: bcluster: id, length, norm.length #burst candidate
    #output: log(P.value)

    #parameters of the central distribution
    #mu=median(central)
    #sigma=mad(central)
    """
    # Probability of sum of q Normal ISIs being less than time.2
    # sum of q Normal ISIs ~ N(mean=q*mu,sd=sigma*sqrt(q))
    bid1 = bcluster['id']
    time_2 = np.sum(bcluster['norm_length'])    # sum of normalized ISI
    q = bid1.shape[0]
    burst_p1 = stats.norm.logcdf(time_2, loc=q*mu, scale=sigma*np.sqrt(q))
    return burst_p1


##############
# P-values for the pauses
##############

def np_pause(pcluster, mu=0, sigma=1):
    """
    #calculates the p-value of the pause cluster pcluster
    #input: pcluster: id, length, norm.length
    #cenral: combined ISIs
    #output: log(P.value)

    #parameters of the central distribution
    #mu=median(central)
    #sigma=mad(central)
    """

    # Probability of sum of q Normal ISIs being greater than time.2
    # sum of q Normal ISIs ~ N(mean=q*mu,sd=sigma*sqrt(q))
    bid1 = pcluster['id']
    time_2 = np.sum(pcluster['norm_length'])    # sum of normalized ISI
    q = bid1.shape[0]
    pause_p1 = stats.norm.logsf(time_2, loc=q*mu, scale=sigma*np.sqrt(q))
    return pause_p1


##############
# Burst and Pause detection by Robust Gassian Surprise
##############
#
def nbp_RGS(ab, ap, adata, central, cthresh=stats.norm.ppf(.95), **kwargs):
    """
    from the initial burst or pause list (ab or ap) this function extends
    bursts or pauses by adding ISIs that decreases P-value of burst or pause
    cluster

    ab: list of burst seed
    ap: list of pause seed
    adata: ISI data from the spike train
    central: combined isi data.frame from which central parameters to be
             estimated
    the column norm.length is normalized isi

    initial cut-off points for the central distribution
    """
    central1 = np.asarray(central['norm_length'])
    central1 = central1[abs(central1-np.median(central1)) <
                        cthresh*R.mad(central1)]

    # parameters of the central distribution
    mu = np.median(central1)
    sigma = R.mad(central1)
    burst = pd.DataFrame()
    N = adata.shape[0]
    clusterno = np.unique(ab['clusid'])
    if(len(clusterno) > 0):     # initial cluster candidates not empty
        for jj in clusterno:    # jj
            p1 = 1
            p2 = 0
            bid1 = np.asarray(ab['id'][ab['clusid'] == jj])
            # extend to left
            while (p2 < p1) and (bid1[0] > 1):
                p1 = np_burst(bcluster=adata.iloc[bid1], mu=mu, sigma=sigma)
                bid2 = np.append(bid1[0]-1, bid1)
                p2 = np_burst(bcluster=adata.iloc[bid2], mu=mu, sigma=sigma)
                if (p2 < p1):
                    bid1 = bid2

            p1 = 1
            p2 = 0
            # extend to right
            while (p2 < p1) and (bid1[-1] < N-1):
                p1 = np_burst(bcluster=adata.iloc[bid1], mu=mu, sigma=sigma)
                bid2 = np.append(bid1, bid1[-1]+1)
                p2 = np_burst(bcluster=adata.iloc[bid2], mu=mu, sigma=sigma)
                if (p2 < p1):
                    bid1 = bid2

            # P-value of each cluster
            pv1 = np_burst(bcluster=adata.iloc[bid1], mu=mu, sigma=sigma)
            burst0 = adata.iloc[bid1].copy()
            burst0.loc[:, 'clusid'] = jj
            burst0.loc[:, 'P'] = pv1
            burst = burst.append(burst0)

    pause = pd.DataFrame()
    clusterno = np.unique(ap['clusid'])
    if(len(clusterno) > 0):   # for non empty pause set
        for jj in clusterno:
            p1 = 1
            p2 = 0
            bid1 = np.asarray(ap['id'][ap['clusid'] == jj])
            # extend to left
            while (p2 < p1) and (bid1[0] > 1):
                p1 = np_pause(pcluster=adata.iloc[bid1], mu=mu, sigma=sigma)
                bid2 = np.append(bid1[0]-1, bid1)
                p2 = np_pause(pcluster=adata.iloc[bid2], mu=mu, sigma=sigma)
                if (p2 < p1):
                    bid1 = bid2

            p1 = 1
            p2 = 0
            # extend to right
            while (p2 < p1) and (bid1[-1] < N-1):
                p1 = np_pause(pcluster=adata.iloc[bid1], mu=mu, sigma=sigma)
                bid2 = np.append(bid1, bid1[-1]+1)
                p2 = np_pause(pcluster=adata.iloc[bid2], mu=mu, sigma=sigma)
                if (p2 < p1):
                    bid1 = bid2

            # P-value
            pv2 = np_pause(pcluster=adata.iloc[bid1], mu=mu, sigma=sigma)
            pause0 = adata.iloc[bid1].copy()
            pause0.loc[:, 'clusid'] = jj
            pause0.loc[:, 'P'] = pv2
            pause = pause.append(pause0)

    # eliminate overlapped burst-clusters with larger P values
    clusterno = np.unique(ab['clusid'])
    if(len(clusterno) > 0):     # non empty initial cluster candidates
        bp2 = burst
        for w in range(20):     # w: 20 could be changed to any number >10
            clid = np.unique(bp2['clusid'])
            for ii in range(len(clid)-1):  # ii
                d1 = bp2['id'][bp2['clusid'] == clid[ii]]
                d2 = bp2['id'][bp2['clusid'] == clid[ii+1]]
                overlap = np.intersect1d(d1, d2)
                if (len(overlap) >= 1):
                    if(np.mean(bp2['P'][bp2['clusid'] == clid[ii]]) <=
                       np.mean(bp2['P'][bp2['clusid'] == clid[ii+1]])):
                        bp2 = bp2[bp2['clusid'] != clid[ii+1]]
                    else:
                        bp2 = bp2[bp2['clusid'] != clid[ii]]

        burst = bp2
        burst['S'] = -burst['P']
        burst['P'] = np.exp(burst['P'])

    # eliminate overlapped pause-clusters with larger P values
    clusterno = np.unique(ap['clusid'])
    if(len(clusterno) > 0):     # non empty pause set
        bp2 = pause
        for w in range(20):     # w
            clid = np.unique(bp2['clusid'])
            for ii in range(len(clid)-1):   # ii
                d1 = bp2['id'][bp2['clusid'] == clid[ii]]
                d2 = bp2['id'][bp2['clusid'] == clid[ii+1]]
                overlap = np.intersect1d(d1, d2)
                if (len(overlap) >= 1):
                    if(np.mean(bp2['P'][bp2['clusid'] == clid[ii]]) <=
                       np.mean(bp2['P'][bp2['clusid'] == clid[ii+1]])):
                        bp2 = bp2[bp2['clusid'] != clid[ii+1]]
                    else:
                        bp2 = bp2[bp2['clusid'] != clid[ii]]

        pause = bp2
        pause['S'] = -pause['P']
        pause['P'] = np.exp(pause['P'])

    # select bursts with P<0.05 and rename cluster id
    burst = burst[burst['P'] <= 0.05]
    pause = pause[pause['P'] <= 0.05]
    if (burst.shape[0] > 0):
        burst['clusid'] = np.repeat(R.seq(np.unique(burst['clusid'])),
                                    R.table(burst['clusid']))
    if (pause.shape[0] > 0):
        pause['clusid'] = np.repeat(R.seq(np.unique(pause['clusid'])),
                                    R.table(pause['clusid']))

    return [burst, pause]


###################################
# This function summarizes the bursts and pauses for a group of spike trains
# Group of Spike trains (ISIs) are read and stored as list object
# Output is list of bursts and pauses of each spike trains
####################################
#
def bp_summary(data, thresh0=stats.norm.ppf(0.05),
               thresh1=stats.norm.ppf(0.95), k0=41, p0=0.2, pc0=0.05,
               p_thresh=0.01, min_spikes=2):
    """
    This function summarizes the bursts and pauses for a group of spike trains
    generated by RGS method

    INPUT: data: list of spike trains (isi intervals)
    """
    # generate combine normalized isi
    b_Cont = pd.DataFrame()
    for train in data:
        # normalized isi
        zd = np.asarray(train['isi'])
        tnorm = norm(zd, k=k0, p=p0, pc=pc0)
        b_df = pd.DataFrame({'isi': zd, 'norm_length': tnorm})
        b_Cont = pd.concat([b_Cont, b_df])

    # output format
    burst = list()
    pause = list()

    for train in data:
        zd = np.asarray(train['isi'])
        # initial bursts and pauses calculation
        tbmed1_3 = nb_seed(zd, thresh=thresh0, central=b_Cont, pc=pc0, k=k0,
                           p=p0)
        ab2 = tbmed1_3[0]       # burst seeds for zd
        adata = tbmed1_3[1]     # all data
        tpcen1_3 = np_seed(zd, thresh=thresh1, central=b_Cont, pc=pc0, k=k0,
                           p=p0)
        ap2 = tpcen1_3[0]   # pause seeds
        # RGS bursts and pauses detection
        nbp2 = nbp_RGS(ab=ab2, ap=ap2, adata=adata, central=b_Cont,
                       cthresh=stats.norm.ppf(0.95))

        # initial bursts and pauses with P < 0.05
        bp_b = nbp2[0]
        bp_p = nbp2[1]
#        n = len(zd) + 1

        # number of bursts and pauses for Bonferroni adjustment
        Bfactor = len(np.unique(bp_b['clusid']))
        Pfactor = len(np.unique(bp_p['clusid']))
        # Bfactor=dim(ab2)[1]
        # Pfactor=dim(ap2)[1]

        # Bonferroni adjustment
        bp_b['adjP'] = np.where(bp_b['P']*Bfactor >= 1, 1, bp_b['P']*Bfactor)
        bp_p['adjP'] = np.where(bp_p['P']*Pfactor >= 1, 1, bp_p['P']*Pfactor)

        # Surprise value for adjusted P
        bp_b['adjS'] = -np.log(bp_b['adjP'])
        bp_p['adjS'] = -np.log(bp_p['adjP'])

        alpha = p_thresh  # definition of significance

        Csize = R.table(bp_b['clusid'])
        tn = R.seq(Csize)
        TN = tn[Csize >= min_spikes-1]
        # correct to get cluster with one interval
        # One may change the rule such as more than 1 for example
        # TN=as.numeric(tn[Csize>=2])
        # TN=as.numeric(tn[Csize>=3])

        # Select bursts and pauses with adjusted P-value < alpha
        bp_p['S'] = bp_p['adjS']
        bp_p['P'] = bp_p['adjP']
        bp_b['S'] = bp_b['adjS']
        bp_b['P'] = bp_b['adjP']

        if (len(TN) > 0):
            temp = bp_b[bp_b['clusid'].isin(TN)]
            if (temp.shape[0] > 0):
                bp_b = temp[temp['adjP'] <= alpha]

        Csize = R.table(bp_p['clusid'])
        tn = R.seq(Csize)
        TN = tn[Csize >= 1]
        if (len(TN) > 0):
            temp = bp_p[bp_p['clusid'].isin(TN)]
            if (temp.shape[0] > 0):
                bp_p = temp[temp['adjP'] <= alpha]

        tzd = pd.Series(np.cumsum(np.append(0, zd[:-1])))   # spike time
        # other summaries
        temp = tzd[bp_b['id']]
        bp_b.loc[:, 'start'] = temp
        temp = tzd[bp_b.loc[:, 'id']] + bp_b.loc[:, 'interval']
        bp_b.loc[:, 'end'] = temp
        temp = tzd.loc[bp_p.loc[:, 'id']]
        bp_p.loc[:, 'start'] = temp
        temp = tzd[bp_p.loc[:, 'id']] + bp_p.loc[:, 'interval']
        bp_p.loc[:, 'end'] = temp
        if (bp_b.shape[0] > 0):
            del bp_b['P']
            del bp_b['S']

        if (bp_p.shape[0] > 0):
            del bp_p['P']
            del bp_p['S']

        if (bp_b.shape[0] > 0):
            temp = bp_b['clusid']
            bp_b['clusid'] = np.repeat(R.seq(np.unique(temp)), R.table(temp))

        if (bp_p.shape[0] > 0):
            temp = bp_p['clusid']
            bp_p['clusid'] = np.repeat(R.seq(np.unique(temp)), R.table(temp))

        burst.append(bp_b)  # bursts for spike train data[[kk]]
        pause.append(bp_p)  # pauses for spike train data[[kk]]

    # output for data, a set of spike trains
    return [burst, pause]


if __name__ == '__main__':
    # Example run of RGS functions
    filenames = ['../../tests/testdata1.csv', '../../tests/testdata2.csv',
                 '../../tests/testdata3.csv']
#    filenames = ['testdata3.csv']
    data1 = list()
    for fn in filenames:
        temp = pd.read_csv(fn)
        data1.append(temp)

    bursts, pauses = bp_summary(data1, p_thresh=0.001)
#    print(bursts)
#    print(pauses)
