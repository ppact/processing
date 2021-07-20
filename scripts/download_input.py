#!/usr/bin/env python
import requests
import pathlib
import re
import os
from urllib.parse import urlparse, unquote

DATA_FILES = {
    "new_orleans_harbor_pd": [
        "https://www.dropbox.com/s/oijixpqskkbm63k/new_orleans_harbor_pd_pprr_1991-2008.csv?dl=1",  # noqa
        "https://www.dropbox.com/s/9orpa67xwfuheia/new_orleans_harbor_pd_pprr_2020.csv?dl=1",  # noqa
        "https://www.dropbox.com/s/37ghr57lpq8d5tw/new_orleans_harbor_pd_cprr_2014-2020.csv?dl=1",  # noqa
    ],
    "new_orleans_csd": [
        "https://www.dropbox.com/sh/ymvc81kjfqqv9m6/AADoEpTWUNef0AMH5GaZxMPea/New%20Orleans_CSD_PPRR_2009_realigned.csv?dl=1",  # noqa
        "https://www.dropbox.com/sh/nv366qnl1vmhgny/AABVFv9T2bwTOI0XuHULfbD-a/Data%20Collected/New%20Orleans%20Civil%20Service%20Department/Administrative%20Data/New%20Orleans_CSD_PPRR_2014.csv?dl=1",  # noqa
    ],
    "new_orleans_da": [
        "https://www.dropbox.com/s/gyalu2tgut5ya2w/new_orleans_da_cprr_2021_brady.csv?dl=1",  # noqa
    ],
    "baton_rouge_pd": [
        "https://www.dropbox.com/sh/rc4a4961qqxu0co/AADmtLqCxY_k5ZlbPKtOmcKHa/Data%20Collected/Baton%20Rouge%20Police%20Department/Baton%20Rouge_PD_CPRR_2018.csv?dl=1",  # noqa
    ],
    "baton_rouge_csd": [
        "https://www.dropbox.com/sh/rc4a4961qqxu0co/AAATpIeZNzv0NJlzfSFOJKqZa/Data%20Collected/Baton%20Rouge%20Civil%20Service%20Department/Baton%20Rouge_CSD_PPRR_2017.csv?dl=1",  # noqa
        "https://www.dropbox.com/sh/rc4a4961qqxu0co/AADEvr8QN4RVb7Gb_xSyT934a/Data%20Collected/Baton%20Rouge%20Civil%20Service%20Department/Baton%20Rouge_CSD_PPRR_2019.csv?dl=1",  # noqa
    ],
    "baton_rouge_fpcsb": [
        "https://www.dropbox.com/sh/qihmr1a6wiswr6f/AAAwyYt429HSaOO6ZlNeNQsca/Baton_Rouge_FPCSB_Logs_1992-2012.csv?dl=1",  # noqa
    ],
    "baton_rouge_so": [
        "https://www.dropbox.com/s/aa8gwwebqfcmbp9/Baton_Rouge_SO_CPRR_2018.csv?dl=1",  # noqa
        "https://www.dropbox.com/s/ntxarlgwzlqoms9/baton_rouge_so_cprr_2016-2020.csv?dl=1",  # noqa
    ],
    "louisiana_state_csc": [
        "https://www.dropbox.com/sh/9zndy2dz3w60etq/AAAqcTxDk8GVj3uvQbUto3XBa/Log%20Records/LouisianaState_CSC_LPRR_1991-2020.csv?dl=1",  # noqa
        "https://www.dropbox.com/s/eidur1nb3od5l55/la_lprr_appellants.csv?dl=1",  # noqa
    ],
    "louisiana_csd": [
        "https://www.dropbox.com/sh/afmp68wb09jbtif/AABIYkrTYK_-pASqMf5Ysibya/louisiana_csd_pprr_demographics_2021.csv?dl=1",  # noqa
        "https://www.dropbox.com/sh/afmp68wb09jbtif/AACTN6MNEjsp6sAs5_zCbUhKa/louisiana_csd_pprr_terminations_2021.csv?dl=1",  # noqa
    ],
    "brusly_pd": [
        "https://www.dropbox.com/sh/s3qchv84i0j5tsd/AAAx1lt_f2iqEERkEjK7wj2_a/Complaints%20Data/Brusly_PD_CPRR_2020.csv?dl=1",  # noqa
        "https://www.dropbox.com/sh/0t6dvicvhztbtya/AAACRW8-Smg0C7TdfMHtHUxua/Brusly_PD_PPRR_2020.csv?dl=1",  # noqa
        "https://www.dropbox.com/sh/rfvtxt3dw204mu0/AAAPRhyKNsN6k0T7khmtxhP2a/brusly_pd_awards_2015-2020_byhand.csv?dl=1",  # noqa
    ],
    "post_council": [
        "https://www.dropbox.com/s/vzm4ihad72pkw2b/POST_PPRR_11-6-2020.csv?dl=1",  # noqa
    ],
    "port_allen_pd": [
        "https://www.dropbox.com/sh/8zs58ak2rpah9iu/AABUS6JdCHYyvjXWWk--RtGLa/Port_Allen_CPRR_2017-2018_byhand.csv?dl=1",  # noqa
        "https://www.dropbox.com/sh/8zs58ak2rpah9iu/AAC6iWLPwTHpXGr6NvEBNzgQa/Port_Allen_CPRR_2019.csv?dl=1",  # noqa
        "https://www.dropbox.com/s/db3fncb1j9tfz4p/Port_Allen_CPRR_2015-2016_byhand.csv?dl=1",  # noqa
    ],
    "port_allen_csd": [
        "https://www.dropbox.com/sh/5znysznypatmig0/AAD4gXEXXJMxnxNcK-TocbPDa/Port_Allen_CSD_PPRR_2020.csv?dl=1",  # noqa
    ],
    "baton_rouge_da": [
        "https://www.dropbox.com/sh/vdpyhf3lbi7lxy9/AAB_Qc3S4usW8QMatRXimi_za/Baton_Rouge_DA_CPRR_2021.csv?dl=1",  # noqa
    ],
    "ipm": [
        "https://www.dropbox.com/sh/1zdvf08kjarefyf/AACXnVrPKERs0F5Hs4c9_3GUa/new_orleans_IAPRO_PPRR_1946-2018.csv?dl=1",  # noqa
        "https://www.dropbox.com/sh/1zdvf08kjarefyf/AAD1_AaJAU5_6Vk8nMMspO0_a/new_orleans_PD_CPRR_actions_taken_1931-2020.csv?dl=1",  # noqa
        "https://www.dropbox.com/sh/1zdvf08kjarefyf/AAB-HhVpDXo0sUazVJvNd7soa/new_orleans_PD_CPRR_allegations_1931-2020.csv?dl=1",  # noqa
        "https://www.dropbox.com/sh/1zdvf08kjarefyf/AADcG1KGz9dJ-OovJ2GrFt_za/new_orleans_PD_PPRR_1946-2018.csv?dl=1",  # noqa
        "https://www.dropbox.com/sh/1zdvf08kjarefyf/AACJmVSIiBlUL5j8cFa8-RuJa/new_orleans_PD_use_of_force_2012-2019.csv?dl=1",  # noqa
    ],
    "new_orleans_so": [
        "https://www.dropbox.com/sh/dsrzc28teybtf4q/AAAq2PQtK_cM5Mt3PpknAoMOa/new_orleans_so_cprr_2019_tabula.csv?dl=1",  # noqa
    ],
    "greenwood_pd": [
        "https://www.dropbox.com/sh/9yu4fe2z6xuwnaf/AAALIGMiq95b2ZylzxFcUdqga/greenwood_pd_cprr_2015-2020_byhand.csv?dl=1",  # noqa
    ],
    "st_tammany_so": [
        "https://www.dropbox.com/sh/mwabzn85manxzo6/AACR-N1crrGx43ZJ2CYdtqUSa/St.Tammany_SO_CPRR_Lists_2015-2019_tabula.csv?dl=1",  # noqa
        "https://www.dropbox.com/sh/mwabzn85manxzo6/AACgbqjIwVL3XetaFcQHo-e5a/st_tammany_department_codes_tabula.csv?dl=1",  # noqa
        "https://www.dropbox.com/s/ir4jad3jm13n6se/st_tammany_so_cprr_2011-2020_tabula.csv?dl=1",  # noqa
        "https://www.dropbox.com/s/5o4z29raa7djvsh/st_tammany_so_cprr_2020-2021_tabula.csv?dl=1",  # noqa
        "https://www.dropbox.com/s/j20pcmebe97ql7y/st._tammany_so_pprr_2020.csv?dl=1",  # noqa
    ],
    "plaquemines_so": [
        "https://www.dropbox.com/s/g1b98kn4e4k1dtr/plaquemines_so_cprr_2019.csv?dl=1",  # noqa
    ],
    "caddo_parish_so": [
        "https://www.dropbox.com/sh/8w4uff2emzbhcvr/AAC4YdwWdPudXeH4pdDvl-Fpa/Caddo%20Parish_SO_PPRR_2020.csv?dl=1",  # noqa
    ],
    "levee_pd": [
        "https://www.dropbox.com/sh/d1j6djl9jb7jvx3/AADgCrm6xbUHZJ0ATwfwZp2Ga/Log%20Records/levee_pd_cprr_2019.csv?dl=1",  # noqa
        "https://www.dropbox.com/sh/d1j6djl9jb7jvx3/AAB5DDSmd4Uo247gktnG3A9Za/Log%20Records/levee_pd_cprr_2020.csv?dl=1",  # noqa
    ],
    "kenner_pd": [
        "https://www.dropbox.com/sh/x1b2ve5ei3mod94/AACL1pMApTujHaUfooMPKoBEa/Kenner_PD_PPRR_2020.csv?dl=1",  # noqa
        "https://www.dropbox.com/sh/x1b2ve5ei3mod94/AADd22L9dZyWKXnxzCHxT-Oqa/Kenner_PD_PPRR_FormerEmployees_Long.csv?dl=1",  # noqa
        "https://www.dropbox.com/sh/x1b2ve5ei3mod94/AAA6YD5qjTmc8iL8ccq5mQZSa/Kenner_PD_PPRR_FormerEmployees_Short.csv?dl=1",  # noqa
    ],
    "harahan_csd": [
        "https://www.dropbox.com/s/kgiidkew18odd7m/Harahan_CSD_PPRR_Roster%20by%20Employment%20Status_2020.csv?dl=1",  # noqa
        "https://www.dropbox.com/s/r60o45dmuqpbnke/Harahan_CSD_PRRR_Roster%20by%20Employment%20Date_2020.csv?dl=1",  # noqa
    ],
    "harahan_pd": [
        "https://www.dropbox.com/s/e95kg68746ndcg9/Harahan_PD_PPRR_2020.csv?dl=1",  # noqa
    ],
    "gretna_pd": [
        "https://www.dropbox.com/s/qr92icxpgtcdcb4/Gretna_PD_PPRR_2018.csv?dl=1",  # noqa
    ],
    "vivian_csd": [
        "https://www.dropbox.com/sh/9wlhj0groq8eg84/AADaXj3Lr0WgxA4Vu8jelRjja/vivian_csd_pprr_2021.csv?dl=1",  # noqa
    ],
    "covington_pd": [
        "https://www.dropbox.com/sh/ngj8aygmmgqy2dg/AABXzZ0uFMy60AGfao0eDkfGa/covington_pd_actions_history.csv?dl=1",  # noqa
        "https://www.dropbox.com/sh/ngj8aygmmgqy2dg/AADa8X7eSd72sbsglvwO0DlWa/covington_pd_pprr_2010.csv?dl=1",  # noqa
        "https://www.dropbox.com/sh/ngj8aygmmgqy2dg/AADYcp9Z9-X_09E9PhYApvLfa/covington_pd_pprr_2011.csv?dl=1",  # noqa
        "https://www.dropbox.com/sh/ngj8aygmmgqy2dg/AADoPfUKgD386icBjXbW_weca/covington_pd_pprr_2012.csv?dl=1",  # noqa
        "https://www.dropbox.com/sh/ngj8aygmmgqy2dg/AAA61eg4XA8B6XGsJmzmr8v9a/covington_pd_pprr_2013.csv?dl=1",  # noqa
        "https://www.dropbox.com/sh/ngj8aygmmgqy2dg/AAC_1x7oC4Ps85x2070f0jXQa/covington_pd_pprr_2014.csv?dl=1",  # noqa
        "https://www.dropbox.com/sh/ngj8aygmmgqy2dg/AADpsk9XZBFJMLXDnofR_Wdla/covington_pd_pprr_2015.csv?dl=1",  # noqa
        "https://www.dropbox.com/sh/ngj8aygmmgqy2dg/AADhl3wSmQdV50QMpfn6aFcha/covington_pd_pprr_2016.csv?dl=1",  # noqa
        "https://www.dropbox.com/sh/ngj8aygmmgqy2dg/AADhEHTt8tHg2XCWzKUhssDMa/covington_pd_pprr_2017.csv?dl=1",  # noqa
        "https://www.dropbox.com/sh/ngj8aygmmgqy2dg/AAAz131JwVZwh74pq8U1nSFza/covington_pd_pprr_2018.csv?dl=1",  # noqa
        "https://www.dropbox.com/sh/ngj8aygmmgqy2dg/AACQhE7V_m8g9-q-UKEq8B8Ka/covington_pd_pprr_2019.csv?dl=1",  # noqa
        "https://www.dropbox.com/sh/ngj8aygmmgqy2dg/AAAfzXvjWo2j3W-Ke9OjomZia/covington_pd_pprr_2020.csv?dl=1",  # noqa
        "https://www.dropbox.com/sh/ngj8aygmmgqy2dg/AAAPr3m_zEV1FTeoK2EbfBu3a/covington_pd_pprr_2021.csv?dl=1",  # noqa
    ],
    "scott_pd": [
        "https://www.dropbox.com/s/a0fw6b3a6505eoi/scott_pd_cprr_2020.csv?dl=1",  # noqa
        "https://www.dropbox.com/s/9xstfdrq7h39cqy/scott_pd_pprr_2021.csv?dl=1"  # noqa
    ],
    "slidell_pd": [
        "https://www.dropbox.com/s/1z09ujt4ja3b4wx/Slidell_PD_PPRR_2009.csv?dl=1",  # noqa
        "https://www.dropbox.com/s/ejgypovnab90z0p/Slidell_PD_PPRR_2019.csv?dl=1",  # noqa
    ],
    "shreveport_pd": [
        "https://www.dropbox.com/sh/d1z41ep6gpmys0d/AABJCO_ZpZF4t3-qahiI6plTa/shreveport_pd_cprr_dispositions_2018.csv?dl=1",  # noqa
        "https://www.dropbox.com/sh/d1z41ep6gpmys0d/AADRaYJj_kFnNZFwpYeYG8Oea/shreveport_pd_cprr_dispositions_2019.csv?dl=1",  # noqa
        "https://www.dropbox.com/sh/d1z41ep6gpmys0d/AADm2ePXquTLK0QkQZUYAsPoa/shreveport_pd_cprr_names_2018.csv?dl=1",  # noqa
        "https://www.dropbox.com/sh/d1z41ep6gpmys0d/AAAeN5dqSyb2woW-B9GTfbXta/shreveport_pd_cprr_names_2019.csv?dl=1",  # noqa
        "https://www.dropbox.com/s/q4etm3yafloqy84/shreveport_codebook.csv?dl=1",  # noqa
    ],
    "tangipahoa_so": [
        "https://www.dropbox.com/s/x034pjdzxamt3zk/tangipahoa_so_cprr_2015_2021.csv?dl=1",  # noqa
    ],
    "madisonville_pd": [
        "https://www.dropbox.com/s/u43a9vfwp3hl99e/Madisonville_PD_CPRR_2010-2020_byhand.csv?dl=1",  # noqa
        "https://www.dropbox.com/s/57mvxvuh9pulalf/Madisonville_CSD_PPRR_2019.csv?dl=1",  # noqa
        "https://www.dropbox.com/s/wsqr83x4fhz5j51/Madisonville_CSD_PPRR_2020.csv?dl=1",  # noqa
    ],
    "mandeville_pd": [
        "https://www.dropbox.com/s/r65gv24wz7xl2ox/mandeville_pd_cprr_2019_byhand.csv?dl=1",  # noqa
        "https://www.dropbox.com/s/07kbandklabka5x/mandeville_csd_pprr_2020.csv?dl=1",  # noqa
    ],
    "grand_isle": [
        "https://www.dropbox.com/s/u5jh3bm14kgz3l0/grand_isle_pd_pprr_2021_byhand.csv?dl=1",  # noqa
    ],
    "lafayette_so": [
        "https://www.dropbox.com/s/4d9m1y5g4pnlmkj/lafayette_so_cprr_2015_2020.csv?dl=1",  # noqa
    ],
    "lafayette_pd": [
        "https://www.dropbox.com/s/mzanvltddi52lpw/lafayette_pd_cprr_2015_2020.csv?dl=1",  # noqa
        "https://www.dropbox.com/s/vea5bh178sn7vpu/lafayette_pd_pprr_2010_2021.csv?dl=1",  # noqa
    ]
}
_current_dir = os.path.dirname(os.path.realpath(__file__))


def download_data_files():
    for folder, urls in DATA_FILES.items():
        data_dir = os.path.join(_current_dir, "../data", folder)
        pathlib.Path(data_dir).mkdir(parents=True, exist_ok=True)
        for url in urls:
            o = urlparse(url)
            filename = unquote(o.path).split("/")[-1].lower()
            filename = re.sub(r'\s+', '_', filename)
            full_filename = os.path.join(data_dir, filename)
            if os.path.isfile(full_filename):
                continue
            resp = requests.get(url, allow_redirects=True)
            if resp.status_code >= 400:
                raise Exception("Error getting %s, status code = %d" %
                                (filename, resp.status_code))
            with open(full_filename, "wb") as f:
                f.write(resp.content)
            print("downloaded data/%s/%s" % (folder, filename))


if __name__ == "__main__":
    download_data_files()
