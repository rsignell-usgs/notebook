# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

a=[u'ntimes', u'ndtfast', u'dt', u'dtfast', u'dstart', u'nHIS', u'ndefHIS', u'nRST', u'ntsAVG', u'nAVG', u'ndefAVG', u'nSTA', u'Falpha', u'Fbeta', u'Fgamma', u'Akt_bak', u'Akv_bak', u'Akk_bak', u'Akp_bak', u'rdrg', u'rdrg2', u'Zob', u'Zos', u'gls_p', u'gls_m', u'gls_n', u'gls_cmu0', u'gls_c1', u'gls_c2', u'gls_c3m', u'gls_c3p', u'gls_sigk', u'gls_sigp', u'gls_Kmin', u'gls_Pmin', u'Charnok_alpha', u'Zos_hsig_alpha', u'sz_alpha', u'CrgBan_cw', u'Znudg', u'M2nudg', u'M3nudg', u'Tnudg', u'FSobc_in', u'FSobc_out', u'M2obc_in', u'M2obc_out', u'Tobc_in', u'Tobc_out', u'M3obc_in', u'M3obc_out', u'rho0', u'gamma2', u'LtracerSrc', u'spherical', u'xl', u'el', u'Vtransform', u'Vstretching', u'theta_s', u'theta_b', u'Tcline', u'hc', u's_rho', u's_w', u'Cs_r', u'Cs_w', u'h', u'f', u'pm', u'pn', u'lon_rho', u'lat_rho', u'lon_u', u'lat_u', u'lon_v', u'lat_v', u'lon_psi', u'lat_psi', u'angle', u'mask_rho', u'mask_u', u'mask_v', u'mask_psi', u'ocean_time', u'zeta', u'u', u'v', u'w', u'omega', u'temp', u'salt', u'dye_01', u'rho', u'AKv', u'AKt', u'AKs', u'tke', u'gls', u'buoy2', u'shear2', u'shflux', u'ssflux', u'latent', u'sensible', u'lwrad', u'EminusP', u'evaporation', u'rain', u'swrad', u'sustr', u'svstr', u'bustr', u'bvstr']

# <codecell>

var='ocean_time'
str = 'foo'

# <codecell>

if var in a:
    try:
        str += '\n<variable name="{:s}">\n'.format(var)
        str += str_att('standard_name',cf[var])
        str += '</variable>\n\n'
    except:
        pass




# <codecell>

str

# <codecell>


