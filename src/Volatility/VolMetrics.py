import numpy as np
from numba import jit 
from sklearn.cluster import kmeans_plusplus

def get_volatilty_methods(ohlc, period):
    """
    Compute all Volatility Metrics
    """

    hv, ov, iv = vol_methods(ohlc, period)

    hv_clusters, _ = kmeans_plusplus(hv.reshape(-1, 1), n_clusters = 3, random_state = 0)
    ov_clusters, _ = kmeans_plusplus(ov.reshape(-1, 1), n_clusters = 3, random_state = 0)
    iv_clusters, _ = kmeans_plusplus(iv.reshape(-1, 1), n_clusters = 3, random_state = 0)

    return hv, ov, iv, hv_clusters, ov_clusters, iv_clusters

def get_vol_of_vol_methods(hv, ov, iv, period):
    """
    Compute all Volatility of Volatility Metrics
    """

    hvv, ivv, ovv = get_vol_of_vol(hv, ov, iv, period)

    hv_clusters, _ = kmeans_plusplus(hvv.reshape(-1, 1), n_clusters = 3, random_state = 0)
    ov_clusters, _ = kmeans_plusplus(ovv.reshape(-1, 1), n_clusters = 3, random_state = 0)
    iv_clusters, _ = kmeans_plusplus(ivv.reshape(-1, 1), n_clusters = 3, random_state = 0)

    return hvv, ivv, ovv, hv_clusters, ov_clusters, iv_clusters

@jit(nopython = True)
def vol_methods(ohlc, period):

    hv = h_vol(ohlc, period)
    ov = o_vol(ohlc, period)
    iv = i_vol(ohlc, period)

    return hv, ov, iv

@jit(nopython = True)
def get_vol_of_vol(hv, iv, ov, period):
    """
    Compute all Vol of Vol Metrics
    """

    hvv = compute_vol_of_vol(hv, period)
    ovv = compute_vol_of_vol(ov, period)
    ivv = compute_vol_of_vol(iv, period)

    return hvv, ovv, ivv 

@jit(nopython = True)
def get_correlation_vol(open, high, low, close, period):
    """
    Compute Volatility of Correlation
    """

    open = compute_vol_of_vol(open, period)
    high = compute_vol_of_vol(high, period)
    low = compute_vol_of_vol(low, period)
    close = compute_vol_of_vol(close, period)

    return open, high, low, close

@jit(nopython = True, parallel = True)
def h_vol(ohlc, period):
    """
    Close to Close Volatility
    """

    log_returns = np.zeros(len(ohlc.close) - 1)

    for i in range(len(log_returns)):

        log_returns[i] = np.log(ohlc.close[i + 1] / ohlc.close[i])

    index = 0
    vol = np.zeros(len(log_returns) - period)

    for i in range(period, len(log_returns)):

        avg = 0

        for j in range(i, i - period, -1):

            avg += log_returns[j]

        s = 0
        avg /= period

        for k in range(i, i - period, -1):

            s += (log_returns[k] - avg)**2

        variance = s / period
        vol[index] = np.sqrt(variance) * np.sqrt(252)
        index+=1

    return vol

@jit(nopython = True, parallel = True)
def o_vol(ohlc, period):
    """
    Overnight Volatility
    """

    log_returns = np.zeros(len(ohlc.close) - 1)

    for i in range(len(log_returns)):

        log_returns[i] = np.log(ohlc.open[i + 1] / ohlc.close[i])

    index = 0
    vol = np.zeros(len(log_returns) - period)

    for i in range(period, len(log_returns)):

        avg = 0

        for j in range(i, i - period, -1):

            avg += log_returns[j]

        s = 0
        avg /= period

        for k in range(i, i - period, -1):

            s += (log_returns[k] - avg)**2

        vol[index] = np.sqrt(s / period) * np.sqrt(252)
        index+=1

    return vol

@jit(nopython = True, parallel = True)
def i_vol(ohlc, period):
    """
    Intraday Volatility
    """

    log_returns = np.zeros(len(ohlc.close) - 1)

    for i in range(len(log_returns)):

        log_returns[i] = np.log(ohlc.close[i] / ohlc.open[i])

    index = 0
    vol = np.zeros(len(log_returns) - period)

    for i in range(period, len(log_returns)):

        avg = 0

        for j in range(i, i - period, -1):

            avg += log_returns[j]

        s = 0
        avg /= period

        for k in range(i, i - period, -1):

            s += (log_returns[k] - avg)**2

        vol[index] = np.sqrt(s / period) * np.sqrt(252)
        index+=1

    return vol


@jit(nopython = True, parallel = True)
def compute_vol_of_vol(vol, period):

    index = 0
    vvol = np.zeros(len(vol) - period)

    for i in range(period, len(vol)):

        avg = 0

        for j in range(i, i - period, -1):

            avg += vol[j]

        s = 0
        avg /= period

        for k in range(i, i - period, -1):

            s += (vol[k] - avg)**2

        variance = s / period
        vvol[index] = np.sqrt(variance)
        index+=1

    return vvol


