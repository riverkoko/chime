
"""Command line interface."""
from argparse import (
    Action,
    ArgumentParser,
)
from datetime import datetime
from datetime import date

import pandas

from pandas import DataFrame

from penn_chime.constants import CHANGE_DATE
from penn_chime.model.parameters import Parameters, Disposition
from penn_chime.model.sir import Sir as Model

from clienv import ChimeCLIEnvironment

from sys import stdout
from logging import INFO, basicConfig, getLogger

import shlex
import unicodedata
import os

# from pdfgenerator.chime_pdf_generator import generate_pdf

basicConfig(
    level=INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=stdout,
)
logger = getLogger(__name__)

VERBOSE = False
# OPEN_PDF = True

class FromFile(Action):
    """From File."""

    def __call__(self, parser, namespace, values, option_string=None):
        with values as f:
            parser.parse_args(f.read().split(), namespace)

def cast_date(string):
    return datetime.strptime(string, '%Y-%m-%d').date()

def validator(arg, cast, min_value, max_value, required, default ):
    """Validator."""

    def validate(string):
        """Validate."""
        if string == '' and cast != str:
            if required:
                raise AssertionError('%s is required.')
            return None
        value = cast(string)
        if min_value is not None:
            assert value >= min_value
        if max_value is not None:
            assert value <= max_value
        return value

    return validate

def parse_args(args):
    """Parse args."""
    parser = ArgumentParser(description="penn_chime: {CHANGE_DATE}")

    parser.add_argument("--file", type=open, action=FromFile)

    parser.add_argument(
        "--location", type=str, default="no location"
    )

    parser.add_argument(
        "--scenario-id", type=str, default="no id",
    )

    parser.add_argument("--hosp-capacity", type=int, help="MedSurg Capacity", default=0)
    parser.add_argument("--icu-capacity", type=int, help="ICU Capacity", default=0)
    parser.add_argument("--vent-capacity", type=int, help="Ventilators", default=0)

    parser.add_argument("--hosp-occupied", type=int, help="Non-COVID19 MedSurg Occupancy", default=0)
    parser.add_argument("--icu-occupied", type=int, help="Non-COVID19 ICU Occupancy", default=0)
    parser.add_argument("--vent-occupied", type=int, help="Non-COVID19 Ventilators in Use", default=0)

    parser.add_argument("--current-precautionary", type=int, help="Currently Hospitalized Precautionary COVID-19 Patients (>= 0)", default=0 ),

        # generate_pdf: 0 = None, 1=PDF for each scenario, 2=One PDF for with all scenarios, 3=Both
    parser.add_argument("--generate-pdf", type=int, help="Generate PDF Report", default=1)
    parser.add_argument("--actuals-date", type=cast_date, help="Actuals Date", default=cast_date('1980-01-01') )
    parser.add_argument("--mitigation-date", type=cast_date, help="Mitigation Start Date", default=None)


    for arg, cast, min_value, max_value, help, required, default in (
        ("--current-hospitalized", int, 0, None, "Currently Hospitalized COVID-19 Patients (>= 0)", True, None ),
        ("--date-first-hospitalized", cast_date, None, None, "Date of First Hospitalization", False, None ),
        ("--doubling-time-low", float, 0.0, None, "Doubling time (lower) before social distancing (days)", True, None ),
        ("--doubling-time-observed", float, 0.0, None, "Doubling time (observed) before social distancing (days)", True, None ),
        ("--doubling-time-high", float, 0.0, None, "Doubling time (upper) before social distancing (days)", True, None ),
        ("--hospitalized-days", int, 0, None, "Average Hospital Length of Stay (days)", True, None ),
        ("--hospitalized-rate", float, 0.00001, 1.0, "Hospitalized Rate: 0.00001 - 1.0", True, None ),
        ("--icu-days", int, 0, None, "Average Days in ICU", True, None),
        ("--icu-rate", float, 0.0, 1.0, "ICU Rate: 0.0 - 1.0", True, None),
        ("--market-share", float, 0.00001, 1.0, "Hospital Market Share (0.00001 - 1.0)", True, None ),
        ("--infectious-days", float, 0.0, None, "Infectious days", True, None),
        ("--n-days", int, 0, None, "Number of days to project >= 0", True, 200 ),
        ("--relative-contact-rate", float, 0.0, 1.0, "Social Distancing Reduction Rate: 0.0 - 1.0", True, None ),
        ("--relative-contact-rate-0", float, 0.0, 1.0, "Social Distancing Reduction Rate (0): 0.0 - 1.0", True, None ),
        ("--relative-contact-rate-1", float, 0.0, 1.0, "Social Distancing Reduction Rate (1): 0.0 - 1.0", True, None ),
        ("--population", int, 1, None, "Regional Population >= 1", True, None),
        ("--ventilated-days", int, 0, None, "Average Days on Ventilator", True, None),
        ("--ventilated-rate", float, 0.0, 1.0, "Ventilated Rate: 0.0 - 1.0", True, None),
        ("--current-date", cast_date, None, None, "Current Date", True, date.today() ),
        ("--start-day", int, None, None, "Start day for model output", False, None),
        ("--data-key", str, None, None, "Key for linking for displays", False, None),
        ):
        parser.add_argument(
            arg,
            type=validator(arg, cast, min_value, max_value, required, default),
            help=help,
        )

    return parser.parse_args(shlex.split(args))


def main():
    """Main."""
    data = DataFrame()
    head = DataFrame()
    computed_data = DataFrame()

    cenv = ChimeCLIEnvironment()

    f = open(cenv.parameters_file, "r")
    for x in f:
        x = "".join(ch for ch in x if unicodedata.category(ch)[0]!="C")

        a = parse_args(x)

        logger.info("Processing %s", a.location)

# funky date issue
        # if a.current_date is None :
        #     a.current_date = date.today()

        p = Parameters(
            current_hospitalized=a.current_hospitalized,
            doubling_time=a.doubling_time_low,
            infectious_days=a.infectious_days,
            market_share=a.market_share,
            n_days=a.n_days,
            relative_contact_rate=a.relative_contact_rate,
            population=a.population,
            hospitalized=Disposition(a.hospitalized_days, a.hospitalized_rate),
            icu=Disposition(a.icu_days, a.icu_rate),
            ventilated=Disposition(a.ventilated_days, a.ventilated_rate),
            mitigation_date=a.mitigation_date,
            current_date = a.current_date,
            recovered=0, # this will need to be fixed when CHIME catches up
            )

        fndata  = cenv.output_dir + "/chime-projection-" + a.scenario_id + ".csv"
        fncdata = cenv.output_dir + "/chime-computed-data-" + a.scenario_id + ".csv"
        fnhead  = cenv.output_dir + "/chime-parameters-" + a.scenario_id + ".csv"

        doubling_rates = [ [a.doubling_time_low, "dt-low"], [a.doubling_time_high, "dt-high"], [a.doubling_time_observed, "dt-observed"]] #, [ None, "dt-computed"]]
        contact_rates = [ [a.relative_contact_rate, "sd-norm"], [a.relative_contact_rate_0, "sd-0"], [a.relative_contact_rate_1, "sd-1"] ]

        m = []
        zi = 0

        for d in ( doubling_rates ):
            mr = []
            for r in ( contact_rates ) :

                p.relative_contact_rate = r[0]
                # if d[0] is None :
                #     p.doubling_time = None
                #     p.date_first_hospitalized = a.date_first_hospitalized
                # else :
                p.doubling_time = d[0]
                p.date_first_hospitalized = None

                if p.doubling_time is None and p.date_first_hospitalized is None:
                    p.doubling_time = doubling_rates[2][0]

                zi = zi + 1

                ds = Model (p)

                suffix = ' ' + d[1] + ' ' + r[1]
                ds.dispositions_df.rename( columns = { 'ever_hospitalized':'disp-hosp' + suffix, 'ever_icu':'disp-icu' + suffix, 'ever_ventilated':'disp-vent' + suffix }, inplace = True)
                ds.census_df.rename(       columns = { 'census_hospitalized':'census-hosp' + suffix, 'census_icu':'census-icu' + suffix, 'census_ventilated':'census-vent' + suffix }, inplace = True)
                ds.admits_df.rename(       columns = { 'admits_hospitalized':'new-hosp' + suffix,   'admits_icu':'new-icu' + suffix, 'admits_ventilated':'new-vent' + suffix }, inplace = True)

                ds.raw_df = ds.raw_df[[ "day", "susceptible", "infected", "recovered" ]]
                ds.raw_df.rename(       columns = { 'susceptible':'susceptible' + suffix,   'infected':'infected' + suffix, 'recovered':'infected' + suffix }, inplace = True)

                mr.append( ds )

            m.append(mr)

        # # assemble and merge datasets for output
        # # the second day column is to assist with a lookup function in Excel

        rf = DataFrame( m[0][0].census_df[['day']] )
        df = DataFrame( m[0][0].census_df[['day']] )

        rf['Location'] = a.location

        rf["MedSurg Capacity"] = a.hosp_capacity
        rf["ICU Capacity"] = a.icu_capacity
        rf["Ventilators"] = a.vent_capacity

        rf["Non-COVID19 MedSurg Occupancy"] = a.hosp_occupied
        rf["Non-COVID19 ICU Occupancy"] = a.icu_occupied
        rf["Non-COVID19 Ventilators in Use"] = a.vent_occupied


        if a.data_key is not None:
            rf['data key'] = a.data_key

        df['day-r'] = rf['day']

        for mr in ( m ) :
            for ds in ( mr ) :
                rf = rf.merge(ds.census_df).merge(ds.admits_df).merge(ds.raw_df ).merge(ds.dispositions_df)

        rf = rf.merge( df )

        if a.start_day is not None :
            rf = rf[rf['day'] >= a.start_day]

        rf.to_csv(fndata, index=False)

        if len(data.columns) == 0 :
            data = rf.copy()
        else :
            data = pandas.concat([data, rf])


        # Report out the parameters used to run the model for reference

        param = {
            'Scenario ID'                                          : [ a.scenario_id ],
            'Currently Hospitalized COVID-19 Patients (>= 0)'      : [ a.current_hospitalized ],
            'Currently Precautionary Hospitalized Patients (>= 0)' : [ a.current_precautionary ],
            'Doubling Time (low)'                                  : [ a.doubling_time_low ],
            'Doubling Time (observed)'                             : [ a.doubling_time_observed ],
            'Doubling Time (high)'                                 : [ a.doubling_time_high ],
            'Infectious days'                                      : [ a.infectious_days ],
            'Market Share'                                         : [ a.market_share ],
            'Social Distancing Reduction Rate: 0.0 - 1.0'          : [ a.relative_contact_rate ],
            'Social Distancing Reduction Rate (0): 0.0 - 1.0'      : [ a.relative_contact_rate_0 ],
            'Social Distancing Reduction Rate (1): 0.0 - 1.0'      : [ a.relative_contact_rate_1 ],
            'Population'                                           : [ a.population ],
            'Hospitalized Rate: 0.00001 - 1.0'                     : [ a.hospitalized_rate ],
            'Average Hospital Length of Stay (days)'               : [ a.hospitalized_days ],
            'ICU Rate: 0.0 - 1.0'                                  : [ a.icu_rate ],
            'Average Days in ICU'                                  : [ a.icu_days ],
            'Ventilated Rate: 0.0 - 1.0'                           : [ a.ventilated_rate ],
            'Average Days on Ventilator'                           : [ a.ventilated_days ],
            'Date of First Hospitalization'                        : [ a.date_first_hospitalized ],
            'Mitigation Start Date'                                : [ a.mitigation_date ],
            'Location Code'                                        : [ a.location ],
            'Start day for model output'                           : [ a.start_day ],
            'MedSurg Capacity'                                     : [ a.hosp_capacity ],
            'ICU Capacity'                                         : [ a.icu_capacity ],
            'Ventilator Capacity'                                  : [ a.vent_capacity ],
            # 'Non-COVID19 MedSurg Occupancy'                        : [ a.hosp_occupied ],
            # 'Non-COVID19 ICU Occupancy'                            : [ a.icu_occupied ],
            # 'Non-COVID19 Ventilators in Use'                       : [ a.vent_occupied ],
            'Days to Project'                                      : [ a.n_days ],

            'Report Generated'                                     : cenv.run_datetime.strftime("%m/%d/%Y %H:%M:%S"),
            'Actuals as of'                                        : [a.actuals_date.strftime("%m/%d/%Y")] }

        if a.data_key is not None:
            param.update({ 'Data Key': [ a.data_key ], })

        finfo = DataFrame( param )
        finfo.to_csv(fnhead, index=False)

        if len(head.columns) == 0 :
            head = finfo.copy()
        else :
            head = pandas.concat([head, finfo])

        cdata = {
                'scenario_id'            : [ a.scenario_id ],
                'r0 dt-low sd-norm'      : [ m[0][0].r_naught ],
                'r0 dt-low sd-0'         : [ m[0][1].r_naught ],
                'r0 dt-low sd-1'         : [ m[0][2].r_naught ],
                'rt dt-low sd-norm'      : [ m[0][0].r_t ],
                'rt dt-low sd-0'         : [ m[0][1].r_t ],
                'rt dt-low sd-1'         : [ m[0][2].r_t ],
                'db dt-low sd-norm'      : [ m[0][0].doubling_time_t ],
                'db dt-low sd-0'         : [ m[0][1].doubling_time_t ],
                'db dt-low sd-1'         : [ m[0][2].doubling_time_t ],

                'r0 dt-high sd-norm'     : [ m[1][0].r_naught ],
                'r0 dt-high sd-0'        : [ m[1][1].r_naught ],
                'r0 dt-high sd-1'        : [ m[1][2].r_naught ],
                'rt dt-high sd-norm'     : [ m[1][0].r_t ],
                'rt dt-high sd-0'        : [ m[1][1].r_t ],
                'rt dt-high sd-1'        : [ m[1][2].r_t ],
                'db dt-high sd-norm'     : [ m[1][0].doubling_time_t ],
                'db dt-high sd-0'        : [ m[1][1].doubling_time_t ],
                'db dt-high sd-1'        : [ m[1][2].doubling_time_t ],

                'r0 dt-observed sd-norm' : [ m[2][0].r_naught ],
                'r0 dt-observed sd-0'    : [ m[2][1].r_naught ],
                'r0 dt-observed sd-1'    : [ m[2][2].r_naught ],
                'rt dt-observed sd-norm' : [ m[2][0].r_t ],
                'rt dt-observed sd-0'    : [ m[2][1].r_t ],
                'rt dt-observed sd-1'    : [ m[2][2].r_t ],
                'db dt-observed sd-norm' : [ m[2][0].doubling_time_t ],
                'db dt-observed sd-0'    : [ m[2][1].doubling_time_t ],
                'db dt-observed sd-1'    : [ m[2][2].doubling_time_t ],

                # 'r0 dt-computed sd-norm' : [ m[3][0].r_naught ],
                # 'r0 dt-computed sd-0'    : [ m[3][1].r_naught ],
                # 'r0 dt-computed sd-1'    : [ m[3][2].r_naught ],
                # 'rt dt-computed sd-norm' : [ m[3][0].r_t ],
                # 'rt dt-computed sd-0'    : [ m[3][1].r_t ],
                # 'rt dt-computed sd-1'    : [ m[3][2].r_t ],
                # 'db dt-computed sd-norm' : [ m[3][0].doubling_time_t ],
                # 'db dt-computed sd-0'    : [ m[3][1].doubling_time_t ],
                # 'db dt-computed sd-1'    : [ m[3][2].doubling_time_t ]
                }

        if a.data_key is not None:
            cdata.update({ 'Data Key': [ a.data_key ], })

        cinfo = DataFrame( cdata )
        cinfo.to_csv(fncdata, index=False)

        if len(computed_data.columns) == 0 :
            computed_data = cinfo.copy()
        else :
            computed_data = pandas.concat([computed_data, cinfo])

        # if a.generate_pdf == 1 or a.generate_pdf == 3 :
        #
        #     pdf_file = cenv.output_dir + "/chime-" + a.scenario_id + ".pdf"
        #     generate_pdf( pdf_file, rf, cinfo, finfo )
        #     if OPEN_PDF: os.system( "open " + pdf_file)

        del cinfo
        del rf
        del m
        del finfo

        op = open(cenv.output_dir + "/chime-" + a.scenario_id + ".csv", "w")

        for f in ( [fnhead, fncdata, fndata ] ) :
            fo = open(f, "r")
            op.write( fo.read() )
            op.write("\n")
            fo.close()
            os.remove(f)

        op.close()

    fndata  = cenv.output_dir + "/chime-projection.csv"
    fncdata = cenv.output_dir + "/chime-computed-data.csv"
    fnhead  = cenv.output_dir + "/chime-parameters.csv"

    for df, name in (
        (data, fndata),
        (head, fnhead),
        (computed_data, fncdata)
    ):
        df.to_csv(name, index=False)

    # if a.generate_pdf >= 2 :
    #     head.reset_index(drop=True, inplace=True)
    #     computed_data.reset_index(drop=True, inplace=True)
    #     pdf_file = cenv.output_dir + "/chime-report.pdf"
    #     generate_pdf(pdf_file, data, computed_data, head )
    #     if OPEN_PDF: os.system("open " + pdf_file)

    logger.info("Output directory: %s", cenv.output_dir)

if __name__ == "__main__":
    main()
