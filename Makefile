current_dir = $(shell pwd)
export PYTHONPATH := $(current_dir):$(PYTHONPATH)

.PHONY: all

all: data/fuse/per_new_orleans_harbor_pd.csv data/fuse/event_new_orleans_harbor_pd.csv data/fuse/com_new_orleans_harbor_pd.csv
all: data/fuse/per_baton_rouge_pd.csv data/fuse/event_baton_rouge_pd.csv data/fuse/com_baton_rouge_pd.csv data/fuse/app_baton_rouge_pd.csv
all: data/fuse/per_baton_rouge_so.csv data/fuse/event_baton_rouge_so.csv data/fuse/com_baton_rouge_so.csv
all: data/fuse/per_brusly_pd.csv data/fuse/event_brusly_pd.csv data/fuse/com_brusly_pd.csv
all: data/fuse/per_port_allen_pd.csv data/fuse/event_port_allen_pd.csv data/fuse/com_port_allen_pd.csv
all: data/fuse/per_madisonville_pd.csv data/fuse/event_madisonville_pd.csv data/fuse/com_madisonville_pd.csv
all: data/fuse/per_greenwood_pd.csv data/fuse/com_greenwood_pd.csv data/fuse/event_greenwood_pd.csv
all: data/fuse/com_new_orleans_pd.csv data/fuse/uof_new_orleans_pd.csv data/fuse/per_new_orleans_pd.csv data/fuse/event_new_orleans_pd.csv
all: data/match/cprr_new_orleans_da_2021.csv
all: data/fuse/per_st_tammany_so.csv data/fuse/event_st_tammany_so.csv data/fuse/com_st_tammany_so.csv
all: data/fuse/com_plaquemines_so.csv data/fuse/per_plaquemines_so.csv data/fuse/event_plaquemines_so.csv
# all: data/fuse/per_louisiana_state_police.csv data/fuse/event_louisiana_state_police.csv data/fuse/app_louisiana_state_police.csv
all: data/match/cprr_baton_rouge_da_2021.csv
all: data/fuse/per_caddo_parish_so.csv data/fuse/event_caddo_parish_so.csv
all: data/fuse/event_mandeville_pd.csv data/fuse/com_mandeville_pd.csv data/fuse/per_mandeville_pd.csv
all: data/fuse/event_levee_pd.csv data/fuse/com_levee_pd.csv data/fuse/per_levee_pd.csv
all: data/fuse/per_grand_isle_pd.csv data/fuse/event_grand_isle_pd.csv
all: data/fuse/per_gretna_pd.csv data/fuse/event_gretna_pd.csv
all: data/fuse/per_kenner_pd.csv data/fuse/event_kenner_pd.csv
all: data/fuse/per_vivian_pd.csv data/fuse/event_vivian_pd.csv
all: data/fuse/per_covington_pd.csv data/fuse/event_covington_pd.csv
all: data/fuse/per_slidell_pd.csv data/fuse/event_slidell_pd.csv
all: data/fuse/per_scott_pd.csv data/fuse/event_scott_pd.csv data/fuse/com_scott_pd.csv
all: data/fuse/per_tangipahoa_so.csv data/fuse/event_tangipahoa_so.csv data/fuse/com_tangipahoa_so.csv
all: data/fuse/per_new_orleans_so.csv data/fuse/event_new_orleans_so.csv data/fuse/com_new_orleans_so.csv
all: data/fuse/per_shreveport_pd.csv data/fuse/event_shreveport_pd.csv data/fuse/com_shreveport_pd.csv
all: data/fuse/event_lafayette_so.csv data/fuse/per_lafayette_so.csv data/fuse/com_lafayette_so.csv
all: data/fuse/per_lafayette_pd.csv data/fuse/com_lafayette_pd.csv data/fuse/event_lafayette_pd.csv

data/fuse/per_new_orleans_harbor_pd.csv data/fuse/event_new_orleans_harbor_pd.csv data/fuse/com_new_orleans_harbor_pd.csv: fuse/new_orleans_harbor_pd.py data/match/post_event_new_orleans_harbor_pd_2020.csv data/match/cprr_new_orleans_harbor_pd_2020.csv data/clean/pprr_new_orleans_harbor_pd_1991_2008.csv data/clean/pprr_new_orleans_harbor_pd_2020.csv
	python fuse/new_orleans_harbor_pd.py

data/fuse/per_baton_rouge_pd.csv data/fuse/event_baton_rouge_pd.csv data/fuse/com_baton_rouge_pd.csv data/fuse/app_baton_rouge_pd.csv: fuse/baton_rouge_pd.py data/match/pprr_baton_rouge_csd_2017.csv data/match/pprr_baton_rouge_csd_2019.csv data/match/cprr_baton_rouge_pd_2018.csv data/match/lprr_baton_rouge_fpcsb_1992_2012.csv data/match/event_post_baton_rouge_pd.csv
	python fuse/baton_rouge_pd.py

data/fuse/per_baton_rouge_so.csv data/fuse/event_baton_rouge_so.csv data/fuse/com_baton_rouge_so.csv: fuse/baton_rouge_so.py data/match/cprr_baton_rouge_so_2018.csv data/clean/pprr_post_2020_11_06.csv
	python fuse/baton_rouge_so.py

data/fuse/per_brusly_pd.csv data/fuse/event_brusly_pd.csv data/fuse/com_brusly_pd.csv: fuse/brusly_pd.py data/match/post_event_brusly_pd_2020.csv data/match/cprr_brusly_pd_2020.csv data/clean/pprr_brusly_pd_2020.csv data/match/award_brusly_pd_2021.csv
	python fuse/brusly_pd.py

data/fuse/per_port_allen_pd.csv data/fuse/event_port_allen_pd.csv data/fuse/com_port_allen_pd.csv: fuse/port_allen_pd.py data/match/cprr_port_allen_pd_2019.csv data/match/pprr_port_allen_csd_2020.csv data/match/cprr_port_allen_pd_2017_2018.csv data/match/cprr_port_allen_pd_2015_2016.csv data/match/post_event_port_allen_pd.csv
	python fuse/port_allen_pd.py

data/fuse/per_madisonville_pd.csv data/fuse/event_madisonville_pd.csv data/fuse/com_madisonville_pd.csv: fuse/madisonville_pd.py data/match/cprr_madisonville_pd_2010_2020.csv data/match/post_event_madisonville_csd_2019.csv data/clean/pprr_madisonville_csd_2019.csv
	python fuse/madisonville_pd.py

data/fuse/per_greenwood_pd.csv data/fuse/com_greenwood_pd.csv data/fuse/event_greenwood_pd.csv: fuse/greenwood_pd.py data/match/cprr_greenwood_pd_2015_2020.csv data/clean/pprr_post_2020_11_06.csv
	python fuse/greenwood_pd.py

data/fuse/com_new_orleans_pd.csv data/fuse/uof_new_orleans_pd.csv data/fuse/per_new_orleans_pd.csv data/fuse/event_new_orleans_pd.csv: fuse/new_orleans_pd.py data/clean/pprr_new_orleans_pd_1946_2018.csv data/clean/cprr_new_orleans_pd_1931_2020.csv data/clean/cprr_actions_new_orleans_pd_1931_2020.csv data/clean/uof_new_orleans_pd_2012_2019.csv data/match/post_event_new_orleans_pd.csv
	python fuse/new_orleans_pd.py

data/fuse/per_st_tammany_so.csv data/fuse/event_st_tammany_so.csv data/fuse/com_st_tammany_so.csv: fuse/st_tammany_so.py data/match/cprr_st_tammany_so_2011_2021.csv data/match/post_event_st_tammany_so_2020.csv data/clean/pprr_st_tammany_so_2020.csv
	python fuse/st_tammany_so.py

data/fuse/com_plaquemines_so.csv data/fuse/per_plaquemines_so.csv data/fuse/event_plaquemines_so.csv: fuse/plaquemines_so.py data/match/cprr_plaquemines_so_2019.csv data/clean/pprr_post_2020_11_06.csv
	python fuse/plaquemines_so.py

data/fuse/per_louisiana_state_police.csv data/fuse/event_louisiana_state_police.csv data/fuse/app_louisiana_state_police.csv: fuse/louisiana_state_csc.py data/match/lprr_louisiana_state_csc_1991_2020.csv data/match/post_event_louisiana_state_police_2020.csv data/clean/pprr_louisiana_csd_2021.csv
	python fuse/louisiana_state_csc.py

data/match/post_event_new_orleans_pd.csv: match/new_orleans_pd.py data/clean/pprr_post_2020_11_06.csv data/clean/pprr_new_orleans_pd_1946_2018.csv
	python match/new_orleans_pd.py

data/fuse/per_caddo_parish_so.csv data/fuse/event_caddo_parish_so.csv: fuse/caddo_parish_so.py data/clean/pprr_caddo_parish_so_2020.csv data/match/post_event_caddo_parish_so.csv
	python fuse/caddo_parish_so.py

data/fuse/event_mandeville_pd.csv data/fuse/com_mandeville_pd.csv data/fuse/per_mandeville_pd.csv: fuse/mandeville_pd.py data/clean/pprr_mandeville_csd_2020.csv data/match/post_event_mandeville_pd_2019.csv data/match/cprr_mandeville_pd_2019.csv
	python fuse/mandeville_pd.py

data/fuse/event_levee_pd.csv data/fuse/com_levee_pd.csv data/fuse/per_levee_pd.csv: fuse/levee_pd.py data/match/cprr_levee_pd.csv data/clean/pprr_post_2020_11_06.csv
	python fuse/levee_pd.py

data/fuse/per_grand_isle_pd.csv data/fuse/event_grand_isle_pd.csv: fuse/grand_isle_pd.py data/clean/pprr_grand_isle_pd_2021.csv data/match/post_event_grand_isle_pd.csv
	python fuse/grand_isle_pd.py

data/fuse/per_gretna_pd.csv data/fuse/event_gretna_pd.csv: fuse/gretna_pd.py data/match/post_event_gretna_pd_2020.csv data/clean/pprr_gretna_pd_2018.csv
	python fuse/gretna_pd.py

data/fuse/per_kenner_pd.csv data/fuse/event_kenner_pd.csv: fuse/kenner_pd.py data/match/post_event_kenner_pd_2020.csv data/clean/pprr_kenner_pd_2020.csv
	python fuse/kenner_pd.py

data/fuse/per_vivian_pd.csv data/fuse/event_vivian_pd.csv: fuse/vivian_pd.py data/match/post_event_vivian_pd_2020.csv data/clean/pprr_vivian_pd_2021.csv
	python fuse/vivian_pd.py

data/fuse/per_covington_pd.csv data/fuse/event_covington_pd.csv: fuse/covington_pd.py data/match/post_event_covington_pd_2020.csv data/clean/actions_history_covington_pd_2021.csv data/clean/pprr_covington_pd_2021.csv
	python fuse/covington_pd.py

data/fuse/per_slidell_pd.csv data/fuse/event_slidell_pd.csv: fuse/slidell_pd.py data/match/post_event_slidell_pd_2020.csv data/clean/pprr_slidell_pd_2019.csv
	python fuse/slidell_pd.py

data/fuse/per_scott_pd.csv data/fuse/com_scott_pd.csv data/fuse/event_scott_pd.csv: fuse/scott_pd.py data/match/post_event_scott_pd_2021.csv data/clean/pprr_scott_pd_2021.csv
	python fuse/scott_pd.py

data/fuse/per_tangipahoa_so.csv data/fuse/com_tangipahoa_so.csv data/fuse/event_tangipahoa_so.csv: fuse/tangipahoa_so.py data/match/cprr_tangipahoa_so_2015_2021.csv data/clean/pprr_post_2020_11_06.csv
	python fuse/tangipahoa_so.py

data/fuse/per_new_orleans_so.csv data/fuse/event_new_orleans_so.csv data/fuse/com_new_orleans_so.csv: fuse/new_orleans_so.py data/clean/pprr_post_2020_11_06.csv data/match/cprr_new_orleans_so_2019.csv
	python fuse/new_orleans_so.py

data/fuse/per_shreveport_pd.csv data/fuse/event_shreveport_pd.csv data/fuse/com_shreveport_pd.csv: fuse/shreveport_pd.py data/clean/pprr_post_2020_11_06.csv data/match/cprr_shreveport_pd_2018_2019.csv
	python fuse/shreveport_pd.py

data/fuse/event_lafayette_so.csv data/fuse/per_lafayette_so.csv data/fuse/com_lafayette_so.csv: fuse/lafayette_so.py data/clean/cprr_lafayette_so_2015_2020.csv data/clean/pprr_post_2020_11_06.csv
	python fuse/lafayette_so.py
	
data/fuse/per_lafayette_pd.csv data/fuse/com_lafayette_pd.csv data/fuse/event_lafayette_pd.csv: fuse/lafayette_pd.py data/match/cprr_lafayette_pd_2015_2020.csv data/clean/pprr_lafayette_pd_2010_2021.csv data/match/post_event_lafayette_pd_2020.csv
	python fuse/lafayette_pd.py



data/match/cprr_new_orleans_harbor_pd_2020.csv data/match/post_event_new_orleans_harbor_pd_2020.csv: match/new_orleans_harbor_pd.py data/clean/cprr_new_orleans_harbor_pd_2020.csv data/clean/pprr_new_orleans_harbor_pd_2020.csv
	python match/new_orleans_harbor_pd.py

data/match/cprr_new_orleans_da_2021.csv: match/new_orleans_da.py data/clean/cprr_new_orleans_da_2021.csv data/clean/pprr_new_orleans_pd_1946_2018.csv data/clean/pprr_post_2020_11_06.csv
	python match/new_orleans_da.py

data/match/pprr_baton_rouge_csd_2017.csv data/match/pprr_baton_rouge_csd_2019.csv data/match/cprr_baton_rouge_pd_2018.csv data/match/lprr_baton_rouge_fpcsb_1992_2012.csv data/match/event_post_baton_rouge_pd.csv: match/baton_rouge_pd.py data/clean/pprr_baton_rouge_csd_2017.csv data/clean/pprr_baton_rouge_csd_2019.csv data/clean/cprr_baton_rouge_pd_2018.csv data/clean/pprr_post_2020_11_06.csv data/clean/lprr_baton_rouge_fpcsb_1992_2012.csv
	python match/baton_rouge_pd.py

data/match/cprr_brusly_pd_2020.csv data/match/post_event_brusly_pd_2020.csv data/match/award_brusly_pd_2021.csv: match/brusly_pd.py data/clean/pprr_brusly_pd_2020.csv data/clean/cprr_brusly_pd_2020.csv data/clean/award_brusly_pd_2021.csv
	python match/brusly_pd.py

data/match/cprr_madisonville_pd_2010_2020.csv data/match/post_event_madisonville_csd_2019.csv: match/madisonville_pd.py data/clean/cprr_madisonville_pd_2010_2020.csv data/clean/pprr_madisonville_csd_2019.csv data/clean/pprr_post_2020_11_06.csv
	python match/madisonville_pd.py

data/match/cprr_greenwood_pd_2015_2020.csv: match/greenwood_pd.py data/clean/cprr_greenwood_pd_2015_2020.csv data/clean/pprr_post_2020_11_06.csv
	python match/greenwood_pd.py

data/match/pprr_port_allen_csd_2020.csv data/match/cprr_port_allen_pd_2019.csv data/match/cprr_port_allen_pd_2017_2018.csv data/match/cprr_port_allen_pd_2015_2016.csv data/match/post_event_port_allen_pd.csv: match/port_allen_pd.py data/clean/pprr_port_allen_csd_2020.csv data/clean/pprr_post_2020_11_06.csv data/clean/cprr_port_allen_pd_2019.csv data/clean/cprr_port_allen_pd_2017_2018.csv data/clean/cprr_port_allen_pd_2015_2016.csv
	python match/port_allen_pd.py

data/match/cprr_baton_rouge_so_2018.csv: match/baton_rouge_so.py data/clean/cprr_baton_rouge_so_2018.csv data/clean/pprr_post_2020_11_06.csv
	python match/baton_rouge_so.py

data/match/cprr_baton_rouge_da_2021.csv: match/baton_rouge_da.py data/clean/cprr_baton_rouge_da_2021.csv data/match/pprr_baton_rouge_csd_2019.csv data/match/pprr_baton_rouge_csd_2017.csv data/match/cprr_baton_rouge_so_2018.csv
	python match/baton_rouge_da.py

data/match/cprr_st_tammany_so_2011_2021.csv data/match/post_event_st_tammany_so_2020.csv: match/st_tammany_so.py data/clean/cprr_st_tammany_so_2011_2021.csv data/clean/pprr_st_tammany_so_2020.csv data/clean/pprr_post_2020_11_06.csv
	python match/st_tammany_so.py

data/match/cprr_plaquemines_so_2019.csv: match/plaquemines_so.py data/clean/cprr_plaquemines_so_2019.csv
	python match/plaquemines_so.py

data/match/lprr_louisiana_state_csc_1991_2020.csv data/match/post_event_louisiana_state_police_2020.csv: match/louisiana_state_csc.py data/clean/lprr_louisiana_state_csc_1991_2020.csv data/clean/pprr_post_2020_11_06.csv data/clean/pprr_louisiana_csd_2021.csv
	python match/louisiana_state_csc.py

data/match/post_event_mandeville_pd_2019.csv data/match/cprr_mandeville_pd_2019.csv: match/mandeville_pd.py data/clean/pprr_mandeville_csd_2020.csv data/clean/pprr_post_2020_11_06.csv data/clean/cprr_mandeville_pd_2019.csv
	python match/mandeville_pd.py

data/match/post_event_caddo_parish_so.csv: match/caddo_parish_so.py data/clean/pprr_post_2020_11_06.csv data/clean/pprr_caddo_parish_so_2020.csv
	python match/caddo_parish_so.py

data/match/cprr_levee_pd.csv: match/levee_pd.py data/clean/cprr_levee_pd.csv data/clean/pprr_post_2020_11_06.csv
	python match/levee_pd.py

data/match/post_event_grand_isle_pd.csv: match/grand_isle_pd.py data/clean/pprr_grand_isle_pd_2021.csv data/clean/pprr_post_2020_11_06.csv
	python match/grand_isle_pd.py

data/match/post_event_gretna_pd_2020.csv: match/gretna_pd.py data/clean/pprr_gretna_pd_2018.csv data/clean/pprr_post_2020_11_06.csv
	python match/gretna_pd.py

data/match/post_event_kenner_pd_2020.csv: match/kenner_pd.py data/clean/pprr_kenner_pd_2020.csv data/clean/pprr_post_2020_11_06.csv
	python match/kenner_pd.py

data/match/post_event_vivian_pd_2020.csv: match/vivian_pd.py data/clean/pprr_vivian_pd_2021.csv data/clean/pprr_post_2020_11_06.csv
	python match/vivian_pd.py

data/match/post_event_covington_pd_2020.csv: match/covington_pd.py data/clean/actions_history_covington_pd_2021.csv data/clean/pprr_post_2020_11_06.csv
	python match/covington_pd.py

data/match/post_event_slidell_pd_2020.csv: match/slidell_pd.py data/clean/pprr_slidell_pd_2019.csv
	python match/slidell_pd.py

data/match/post_event_scott_pd_2021.csv: match/scott_pd.py data/clean/cprr_scott_pd_2020.csv data/clean/pprr_scott_pd_2021.csv data/clean/pprr_post_2020_11_06.csv
	python match/scott_pd.py

data/match/cprr_tangipahoa_so_2015_2021.csv: match/tangipahoa_so.py data/clean/cprr_tangipahoa_so_2015_2021.csv data/clean/pprr_post_2020_11_06.csv
	python match/tangipahoa_so.py
	
data/match/cprr_new_orleans_so_2019.csv: match/new_orleans_so.py data/clean/cprr_new_orleans_so_2019.csv data/clean/pprr_post_2020_11_06.csv
	python match/new_orleans_so.py

data/match/cprr_shreveport_pd_2018_2019.csv: match/shreveport_pd.py data/clean/cprr_shreveport_pd_2018_2019.csv data/clean/pprr_post_2020_11_06.csv data/clean/cprr_codebook_shreveport_pd.csv
	python match/shreveport_pd.py

data/match/cprr_lafayette_so_2015_2020.csv: match/lafayette_so.py data/clean/cprr_lafayette_so_2015_2020.csv data/clean/pprr_post_2020_11_06.csv
	python match/lafayette_so.py

data/match/cprr_lafayette_pd_2015_2020.csv data/match/post_event_lafayette_pd_2020.csv: match/lafayette_pd.py data/clean/cprr_lafayette_pd_2015_2020.csv data/clean/pprr_lafayette_pd_2010_2021.csv data/clean/pprr_post_2020_11_06.csv
	python match/lafayette_pd.py



data/clean/pprr_new_orleans_harbor_pd_2020.csv data/clean/pprr_new_orleans_harbor_pd_1991_2008.csv: clean/new_orleans_harbor_pd_pprr.py data/new_orleans_harbor_pd/new_orleans_harbor_pd_pprr_2020.csv
	python clean/new_orleans_harbor_pd_pprr.py

data/clean/pprr_baton_rouge_csd_2017.csv data/clean/pprr_baton_rouge_csd_2019.csv: clean/baton_rouge_csd_pprr.py data/baton_rouge_csd/*.csv
	python clean/baton_rouge_csd_pprr.py

data/clean/cprr_baton_rouge_pd_2018.csv: clean/baton_rouge_pd_cprr.py data/baton_rouge_pd/baton_rouge_pd_cprr_2018.csv
	python clean/baton_rouge_pd_cprr.py

data/clean/cprr_baton_rouge_so_2018.csv: clean/baton_rouge_so_cprr.py data/baton_rouge_so/baton_rouge_so_cprr_2018.csv
	python clean/baton_rouge_so_cprr.py

data/clean/cprr_new_orleans_harbor_pd_2020.csv: clean/new_orleans_harbor_pd_cprr.py data/new_orleans_harbor_pd/new_orleans_harbor_pd_cprr_2014-2020.csv
	python clean/new_orleans_harbor_pd_cprr.py

data/clean/lprr_louisiana_state_csc_1991_2020.csv: clean/louisiana_state_csc_lprr.py data/louisiana_state_csc/louisianastate_csc_lprr_1991-2020.csv data/louisiana_state_csc/la_lprr_appellants.csv
	python clean/louisiana_state_csc_lprr.py

data/clean/lprr_baton_rouge_fpcsb_1992_2012.csv: clean/baton_rouge_fpcsb_lprr.py data/baton_rouge_fpcsb/baton_rouge_fpcsb_logs_1992-2012.csv
	python clean/baton_rouge_fpcsb_lprr.py

data/clean/pprr_brusly_pd_2020.csv data/clean/cprr_brusly_pd_2020.csv data/clean/award_brusly_pd_2021.csv: clean/brusly_pd.py data/brusly_pd/brusly_pd_pprr_2020.csv data/brusly_pd/brusly_pd_cprr_2020.csv
	python clean/brusly_pd.py

data/clean/cprr_port_allen_pd_2019.csv data/clean/cprr_port_allen_pd_2017_2018.csv data/clean/cprr_port_allen_pd_2015_2016.csv: clean/port_allen_pd_cprr.py data/port_allen_pd/port_allen_cprr_2019.csv data/port_allen_pd/port_allen_cprr_2017-2018_byhand.csv data/port_allen_pd/port_allen_cprr_2015-2016_byhand.csv
	python clean/port_allen_pd_cprr.py

data/clean/cprr_madisonville_pd_2010_2020.csv: clean/madisonville_pd_cprr.py data/madisonville_pd/madisonville_pd_cprr_2010-2020_byhand.csv
	python clean/madisonville_pd_cprr.py

data/clean/pprr_madisonville_csd_2019.csv: clean/madisonville_csd_pprr.py data/madisonville_pd/madisonville_csd_pprr_2019.csv
	python clean/madisonville_csd_pprr.py

data/clean/pprr_post_2020_11_06.csv: clean/post_pprr.py data/post_council/post_pprr_11-6-2020.csv
	python clean/post_pprr.py

data/clean/cprr_greenwood_pd_2015_2020.csv: clean/greenwood_pd_cprr.py data/greenwood_pd/greenwood_pd_cprr_2015-2020_byhand.csv
	python clean/greenwood_pd_cprr.py

data/clean/pprr_port_allen_csd_2020.csv: clean/port_allen_csd_pprr.py data/port_allen_csd/port_allen_csd_pprr_2020.csv
	python clean/port_allen_csd_pprr.py

data/clean/cprr_baton_rouge_da_2021.csv: clean/baton_rouge_da_cprr_2021.py data/baton_rouge_da/baton_rouge_da_cprr_2021.csv
	python clean/baton_rouge_da_cprr_2021.py

data/clean/cprr_new_orleans_pd_1931_2020.csv: clean/ipm_new_orleans_pd_cprr_allegations.py data/ipm/new_orleans_pd_cprr_allegations_1931-2020.csv
	python clean/ipm_new_orleans_pd_cprr_allegations.py

data/clean/pprr_new_orleans_pd_1946_2018.csv: clean/ipm_new_orleans_iapro_pprr.py data/ipm/new_orleans_pd_pprr_1946-2018.csv
	python clean/ipm_new_orleans_iapro_pprr.py

data/clean/cprr_actions_new_orleans_pd_1931_2020.csv: clean/ipm_new_orleans_pd_cprr_actions_taken.py data/ipm/new_orleans_pd_cprr_actions_taken_1931-2020.csv
	python clean/ipm_new_orleans_pd_cprr_actions_taken.py

data/clean/uof_new_orleans_pd_2012_2019.csv: clean/ipm_new_orleans_pd_use_of_force.py data/ipm/new_orleans_pd_use_of_force_2012-2019.csv
	python clean/ipm_new_orleans_pd_use_of_force.py

data/clean/cprr_new_orleans_da_2021.csv: clean/new_orleans_da_cprr_2021_brady.py data/new_orleans_da/new_orleans_da_cprr_2021_brady.csv
	python clean/new_orleans_da_cprr_2021_brady.py

data/clean/cprr_st_tammany_so_2011_2021.csv: clean/st_tammany_so_cprr.py data/st_tammany_so/st_tammany_so_cprr_2011-2020_tabula.csv data/st_tammany_so/st_tammany_so_cprr_2020-2021_tabula.csv data/st_tammany_so/st_tammany_department_codes_tabula.csv
	python clean/st_tammany_so_cprr.py

data/clean/pprr_st_tammany_so_2020.csv: clean/st_tammany_so_pprr.py data/st_tammany_so/st._tammany_so_pprr_2020.csv
	python clean/st_tammany_so_pprr.py

data/clean/cprr_plaquemines_so_2019.csv: clean/plaquemines_so_cprr.py data/plaquemines_so/plaquemines_so_cprr_2019.csv
	python clean/plaquemines_so_cprr.py

data/clean/pprr_mandeville_csd_2020.csv data/clean/cprr_mandeville_pd_2019.csv: clean/mandeville_pd.py data/mandeville_pd/mandeville_csd_pprr_2020.csv data/mandeville_pd/mandeville_pd_cprr_2019_byhand.csv
	python clean/mandeville_pd.py

data/clean/pprr_caddo_parish_so_2020.csv: clean/caddo_parish_so_pprr.py data/caddo_parish_so/caddo_parish_so_pprr_2020.csv
	python clean/caddo_parish_so_pprr.py

data/clean/pprr_louisiana_csd_2021.csv: clean/louisiana_csd_pprr_2021.py data/louisiana_csd/louisiana_csd_pprr_2021.csv
	python clean/louisiana_csd_pprr_2021.py

data/clean/cprr_levee_pd.csv: clean/levee_pd.py data/levee_pd/levee_pd_cprr_2020.csv data/levee_pd/levee_pd_cprr_2019.csv
	python clean/levee_pd.py

data/clean/pprr_grand_isle_pd_2021.csv: clean/grand_isle_pd.py data/grand_isle/grand_isle_pd_pprr_2021_byhand.csv
	python clean/grand_isle_pd.py

data/clean/pprr_harahan_pd_2020.csv: clean/harahan_pd.py data/harahan_pd/harahan_pd_pprr_2020.csv
	python clean/harahan_pd.py

data/clean/pprr_harahan_csd_2020.csv: clean/harahan_csd.py data/harahan_csd/harahan_csd_pprr_roster_by_employment_status_2020.csv data/harahan_csd/harahan_csd_prrr_roster_by_employment_date_2020.csv
	python clean/harahan_csd.py

data/clean/pprr_gretna_pd_2018.csv: clean/gretna_pd.py data/gretna_pd/gretna_pd_pprr_2018.csv
	python clean/gretna_pd.py

data/clean/pprr_kenner_pd_2020.csv: clean/kenner_pd.py data/kenner_pd/kenner_pd_pprr_2020.csv data/kenner_pd/kenner_pd_pprr_formeremployees_long.csv data/kenner_pd/kenner_pd_pprr_formeremployees_short.csv
	python clean/kenner_pd.py

data/clean/pprr_vivian_pd_2021.csv: clean/vivian_csd.py data/vivian_csd/vivian_csd_pprr_2021.csv
	python clean/vivian_csd.py

data/clean/actions_history_covington_pd_2021.csv data/clean/pprr_covington_pd_2021.csv: clean/covington_pd.py data/covington_pd/covington_pd_actions_history.csv data/covington_pd/covington_pd_pprr_2010.csv data/covington_pd/covington_pd_pprr_2011.csv data/covington_pd/covington_pd_pprr_2012.csv data/covington_pd/covington_pd_pprr_2013.csv data/covington_pd/covington_pd_pprr_2014.csv data/covington_pd/covington_pd_pprr_2015.csv data/covington_pd/covington_pd_pprr_2016.csv data/covington_pd/covington_pd_pprr_2017.csv data/covington_pd/covington_pd_pprr_2018.csv data/covington_pd/covington_pd_pprr_2019.csv data/covington_pd/covington_pd_pprr_2020.csv
	python clean/covington_pd.py

data/clean/pprr_slidell_pd_2019.csv: clean/slidell_pd.py data/slidell_pd/slidell_pd_pprr_2009.csv data/slidell_pd/slidell_pd_pprr_2019.csv
	python clean/slidell_pd.py

data/clean/cprr_scott_pd_2020.csv: clean/scott_pd_cprr.py data/scott_pd/scott_pd_cprr_2020.csv
	python clean/scott_pd_cprr.py

data/clean/pprr_scott_pd_2021.csv: clean/scott_pd_pprr.py data/scott_pd/scott_pd_pprr_2021.csv
	python clean/scott_pd_pprr.py

data/clean/cprr_tangipahoa_so_2015_2021.csv: clean/tangipahoa_so_cprr.py data/tangipahoa_so/tangipahoa_so_cprr_2015_2021.csv
	python clean/tangipahoa_so_cprr.py

data/clean/cprr_new_orleans_so_2019.csv: clean/new_orleans_so_cprr.py data/new_orleans_so/new_orleans_so_cprr_2019_tabula.csv
	python clean/new_orleans_so_cprr.py

data/clean/cprr_shreveport_pd_2018_2019.csv data/clean/cprr_codebook_shreveport_pd.csv: clean/shreveport_pd_cprr.py data/shreveport_pd/shreveport_pd_cprr_dispositions_2018.csv data/shreveport_pd/shreveport_pd_cprr_names_2018.csv data/shreveport_pd/shreveport_pd_cprr_dispositions_2019.csv data/shreveport_pd/shreveport_pd_cprr_names_2019.csv data/shreveport_pd/shreveport_codebook.csv
	python clean/shreveport_pd_cprr.py

data/clean/cprr_lafayette_so_2015_2020.csv: clean/lafayette_so.py data/lafayette_so/lafayette_so_cprr_2015_2020.csv
	python clean/lafayette_so.py

data/clean/cprr_lafayette_pd_2015_2020.csv data/clean/pprr_lafayette_pd_2010_2021.csv: clean/lafayette_pd.py data/lafayette_pd/lafayette_pd_pprr_2010_2021.csv data/lafayette_pd/lafayette_pd_cprr_2015_2020.csv
	python clean/lafayette_pd.py
