#!/usr/bin/env python

# wujian@2020

import numpy as np

from itertools import permutations

from pypesq import pesq
from pystoi import stoi
from museval.metrics import bss_eval_images


def aps_sisnr(s, x, eps=1e-8, remove_dc=True, fs=None):
    """
    Compute Si-SNR (scaled invariant SNR)
    Args:
        s: vector, reference signal (ground truth)
        x: vector, enhanced/separated signal
    """

    def vec_l2norm(x):
        return np.linalg.norm(x, 2)

    # zero mean, seems do not hurt results
    if remove_dc:
        x_zm = x - np.mean(x)
        s_zm = s - np.mean(s)
        t = np.inner(x_zm, s_zm) * s_zm / (vec_l2norm(s_zm)**2 + eps)
        n = x_zm - t
    else:
        t = np.inner(x, s) * s / (vec_l2norm(s)**2 + eps)
        n = x - t
    return 20 * np.log10(vec_l2norm(t) / (vec_l2norm(n) + eps) + eps)


def aps_pesq(ref, est, fs=16000):
    """
    Wrapper for pypesq.pesq
    """
    return pesq(ref, est, fs=fs)


def aps_stoi(ref, est, fs=16000):
    """
    Wrapper for pystoi.stoi
    """
    return stoi(ref, est, fs_sig=fs)


def _permute_eval(eval_func, ref, est, compute_permutation=False, fs=None):
    """
    Wrapper for computation of SiSNR/PESQ/STOI in permutation/non-permutation mode
    Args:
        eval_func: function to compute metrics
        ref: array, reference signal (N x S or S, ground truth)
        est: array, enhanced/separated signal (N x S or S)
    """

    def eval_sum(ref, est):
        return sum([eval_func(s, x, fs=fs) for s, x in zip(ref, est)])

    if est.ndim == 1:
        return eval_func(ref, est, fs=fs)

    N, _ = est.shape
    if N != ref.shape[0]:
        raise RuntimeError(
            "Size do not match between estimated and reference signal")
    metric = []
    perm = []
    for order in permutations(range(N)):
        est_permu = np.stack([est[n] for n in order])
        metric.append(eval_sum(ref, est_permu) / N)
        perm.append(order)
    if not compute_permutation:
        return max(metric)
    else:
        max_idx = np.argmax(metric)
        return max(metric), perm[max_idx]


def permute_metric(name, ref, est, compute_permutation=False, fs=None):
    """
    Computation of SiSNR/PESQ/STOI in permutation/non-permutation mode
    Args:
        ref: array, reference signal (N x S or S, ground truth)
        est: array, enhanced/separated signal (N x S or S)
    """
    if name == "sisnr":
        return _permute_eval(aps_sisnr,
                             ref,
                             est,
                             compute_permutation=compute_permutation,
                             fs=fs)
    elif name == "pesq":
        return _permute_eval(aps_pesq,
                             ref,
                             est,
                             compute_permutation=compute_permutation,
                             fs=fs)
    elif name == "stoi":
        return _permute_eval(aps_stoi,
                             ref,
                             est,
                             compute_permutation=compute_permutation,
                             fs=fs)
    elif name == "sdr":
        if ref.ndim == 1:
            ref, est = ref[None, :], est[None, :]
        sdr, _, _, _, ali = bss_eval_images(ref[..., None],
                                            est[..., None],
                                            compute_permutation=True)
        if compute_permutation:
            return sdr.mean(), ali[:, 0].tolist()
        else:
            return sdr[0, 0]
    else:
        raise ValueError(f"Unknown name of the metric: {name}")
