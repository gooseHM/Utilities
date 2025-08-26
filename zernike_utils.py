import numpy as np


def zernike_mode(n, m, r, theta):
    if n == 0 and m == 0:
        return np.ones_like(r)

    elif n == 1 and m == -1:
        return r * np.sin(theta)
    elif n == 1 and m == 1:
        return r * np.cos(theta)

    elif n == 2 and m == -2:
        return r ** 2 * np.sin(2 * theta)
    elif n == 2 and m == 0:
        return 2 * r ** 2 - 1
    elif n == 2 and m == 2:
        return r ** 2 * np.cos(2 * theta)

    elif n == 3 and m == -3:
        return r ** 3 * np.sin(3 * theta)
    elif n == 3 and m == -1:
        return (3 * r ** 3 - 2 * r) * np.sin(theta)
    elif n == 3 and m == 1:
        return (3 * r ** 3 - 2 * r) * np.cos(theta)
    elif n == 3 and m == 3:
        return r ** 3 * np.cos(3 * theta)

    elif n == 4 and m == -4:
        return r ** 4 * np.sin(4 * theta)
    elif n == 4 and m == -2:
        return (4 * r ** 4 - 3 * r ** 2) * np.sin(2 * theta)
    elif n == 4 and m == 0:
        return 6 * r ** 4 - 6 * r ** 2 + 1
    elif n == 4 and m == 2:
        return (4 * r ** 4 - 3 * r ** 2) * np.cos(2 * theta)
    elif n == 4 and m == 4:
        return r ** 4 * np.cos(4 * theta)

    else:
        raise ValueError("Unsupported (n, m) combination for first 15 Zernike modes.")


def zernike_design_matrix(r, theta):
    return np.stack([
    zernike_mode(0, 0, r, theta),
    zernike_mode(1, -1, r, theta),
    zernike_mode(1, 1, r, theta),
    zernike_mode(2, -2, r, theta),
    zernike_mode(2, 0, r, theta),
    zernike_mode(2, 2, r, theta),
    zernike_mode(3, -3, r, theta),
    zernike_mode(3, -1, r, theta),
    zernike_mode(3, 1, r, theta),
    zernike_mode(3, 3, r, theta),
    zernike_mode(4, -4, r, theta),
    zernike_mode(4, -2, r, theta),
    zernike_mode(4, 0, r, theta),
    zernike_mode(4, 2, r, theta),
    zernike_mode(4, 4, r, theta),

    ], axis=1)

def extract_zernike_coeffs(x, y, w, return_fit=False):
    r_raw = np.sqrt(x**2 + y**2)
    r = r_raw / np.max(r_raw)
    theta = np.arctan2(y, x)

    A = zernike_design_matrix(r, theta)
    coeffs, *_ = np.linalg.lstsq(A, w, rcond=None)

    if return_fit:
        w_fit = A @ coeffs
        w_res = w - w_fit
        return coeffs, w_fit, w_res

    return coeffs

def remove_piston_tip_tilt(x, y, w):
    r_raw = np.sqrt(x**2 + y**2)
    r = r_raw / np.max(r_raw)
    theta = np.arctan2(y, x)

    A = zernike_design_matrix(r, theta)
    A_basic = A[:, :3]
    coeffs_basic, *_ = np.linalg.lstsq(A_basic, w, rcond=None)
    return w - A_basic @ coeffs_basic


def zernike_surface_metrics(x, y, w):
    """
    Returns RMS and peak-to-valley values for each Zernike mode in the surface.
    """
    coeffs, _, _ = extract_zernike_coeffs(x, y, w, return_fit=True)

    # Convert to normalized polar coordinates
    r = np.sqrt(x**2 + y**2)
    r /= np.max(r)
    theta = np.arctan2(y, x)

    # Build Zernike design matrix
    A = zernike_design_matrix(r, theta)

    # Compute RMS and PV for each mode
    rms = [np.sqrt(np.mean((A[:, i] * c)**2)) for i, c in enumerate(coeffs)]
    pv = [np.ptp(A[:, i] * c) for i, c in enumerate(coeffs)]  # ptp = max - min

    return np.array(rms), np.array(pv)
