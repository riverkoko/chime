# page_number_total_main.py

from lxml import objectify
from reportlab.lib.validators import isNumber
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Flowable, ActionFlowable
from reportlab.platypus import Paragraph, Spacer, PageBreak, Image
from reportlab.platypus import ListFlowable, ListItem, Table, TableStyle

from reportlab.lib.validators import isNumber, isString
from reportlab.lib.pagesizes import TABLOID
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors

from pdfgenerator.ScenarioHeader import ScenarioHeader, ScenarioInflectedHeader
from pdfgenerator.ScenarioGraph import ScenarioGraph, ScenarioInflectedGraph
# from pdfgenerator.ScenarioParameterTable import ScenarioParameterTable
from pdfgenerator.ScenarioMitigationTable import ScenarioMitigationTable
from reportlab.lib.colors import HexColor

from penn_chime.constants import VERSION

import os

import numpy as np
from scipy.interpolate import UnivariateSpline

from pandas import DataFrame
import pandas

from datetime import datetime, timedelta

from pdfgenerator.custom_canvas import PageNumCanvas
from pdfgenerator.header import header, cover_header

PDF_ASSETS = './src/pdfgenerator/assets/'
PDF_ANNOTATIONS = './parameters/notes/'
PDF_ACTUALS = './parameters/actuals/'
# PDF_ASSETS = './assets/'

SHOW_COMPUTED = False

def format_parameter(pv):

    t = str(type(pv))
    v = "Not Supported"

    if 'int' in t:
        v = "{:,.0f}".format(pv)
    elif 'float' in t:
        v = "{:,.4f}".format(pv)
    elif 'str' in t:
        v = pv
    elif 'datetime' in t:
        v = pv.strftime("%d-%b")
    elif 'NoneType' in t:
        v = "None"

    return v

def max_peak( p, n_days ) :
    if p >= n_days or p <= 0 : return None
    return p
def excel_date(date1):
    temp = datetime(1899, 12, 30)    # Note, not 31st Dec but 30th!
    delta = date1 - temp
    # return float(delta.days) + (float(delta.seconds) / 86400)
    return int(delta.days)
def excel_to_normaldate( d ):
    return datetime(1899, 12, 30) + timedelta(days=d)
def smoothed_line(x, y):

    w = np.isnan(y)
    y[w] = 0.

    spl = UnivariateSpline(x, y)
    spl.set_smoothing_factor(15.0)

    return spl(x)

class CurrentScenario(ActionFlowable):
    """
    A Custom Line Flowable
    """
    def __init__(self, current_scenario=0 ):
        ActionFlowable.__init__(self)
        self.current_scenario = current_scenario

    def __repr__(self):
        return "current scenario: " % self.current_scenario_id

    def apply(self, doc):
        doc.current_scenario = self.current_scenario

    def __call__(self):
        return self

    def identity(self, maxLen=None):
        return "current_scenario: %s%s" % (str(self.current_scenario),self._frameName())

def get_header_parameters(current_scenario, model_name, cd, sp) :

    param = {
        # 'dbltime'  : sp['Doubling Time (' + model_name + ')'][current_scenario] ,
        'sd0'      : sp['Social Distancing Reduction Rate: 0.0 - 1.0'][current_scenario] ,
        'sd0_R0'   : cd['r0 dt-' + model_name + ' sd-norm'][current_scenario] ,
        'sd0_Rt'   : cd['rt dt-' + model_name + ' sd-norm'][current_scenario] ,
        'sd0_edbl' : cd['db dt-' + model_name + ' sd-norm'][current_scenario] ,
        'sd1'      : sp['Social Distancing Reduction Rate (0): 0.0 - 1.0'][current_scenario] ,
        'sd1_R0'   : cd['r0 dt-' + model_name + ' sd-0'][current_scenario] ,
        'sd1_Rt'   : cd['rt dt-' + model_name + ' sd-0'][current_scenario] ,
        'sd1_edbl' : cd['db dt-' + model_name + ' sd-0'][current_scenario] ,
        'sd2'      : sp['Social Distancing Reduction Rate (1): 0.0 - 1.0'][current_scenario] ,
        'sd2_R0'   : cd['r0 dt-' + model_name + ' sd-1'][current_scenario] ,
        'sd2_Rt'   : cd['rt dt-' + model_name + ' sd-1'][current_scenario] ,
        'sd2_edbl' : cd['db dt-' + model_name + ' sd-1'][current_scenario] }

    if model_name == "observed":
        param.update( {
            'scenario' : 'Observed Rate' ,
            'dbltime'  : sp['Doubling Time (' + model_name + ')'][current_scenario] ,
            } )
    elif model_name == "low":
        param.update( {
            'scenario' : 'Low Hypothetical Rate' ,
            'dbltime'  : sp['Doubling Time (' + model_name + ')'][current_scenario] ,
            } )
    elif model_name == "high":
        param.update( {
            'scenario' : 'High Hypothetical Rate' ,
            'dbltime'  : sp['Doubling Time (' + model_name + ')'][current_scenario] ,
            } )
    elif model_name == "computed":
        param.update( { 'scenario' : 'Computed Rate' } )
        param.update( { 'dbltime'  : cd['db dt-computed sd-norm'][current_scenario] })

    else:
        param.update( { 'scenario' : 'Not supported' } )


    return param
def get_graph_parameters(current_scenario, model_name, cd, sp, data) :
    scenario_location = sp.loc[current_scenario]["Scenario ID"]

    rf = data[data['Location'] == scenario_location]

    rf = rf[["date"
        , "census-hosp dt-{m} sd-norm".format(m=model_name)
        , "census-hosp dt-{m} sd-0".format(m=model_name)
        , "census-hosp dt-{m} sd-1".format(m=model_name)
        , "census-icu dt-{m} sd-norm".format(m=model_name)
        , "census-icu dt-{m} sd-0".format(m=model_name)
        , "census-icu dt-{m} sd-1".format(m=model_name)
        , "census-vent dt-{m} sd-norm".format(m=model_name)
        , "census-vent dt-{m} sd-0".format(m=model_name)
        , "census-vent dt-{m} sd-1".format(m=model_name)
        , "MedSurg Capacity"
        , "ICU Capacity"
        , "Ventilators"
        , "Non-COVID19 MedSurg Occupancy"
        , "Non-COVID19 ICU Occupancy"
        , "Non-COVID19 Ventilators in Use"
        , 'day'
        ]]

    rf.rename (
        columns = {
        "census-hosp dt-{m} sd-norm".format(m=model_name)    : 'census-hosp-sd-norm'
        , "census-hosp dt-{m} sd-0".format(m=model_name)     : 'census-hosp-sd-0'
        , "census-hosp dt-{m} sd-1".format(m=model_name)     : 'census-hosp-sd-1'
        , "census-icu dt-{m} sd-norm".format(m=model_name)   : 'census-icu-sd-norm'
        , "census-icu dt-{m} sd-0".format(m=model_name)      : 'census-icu-sd-0'
        , "census-icu dt-{m} sd-1".format(m=model_name)      : 'census-icu-sd-1'
        , "census-vent dt-{m} sd-norm".format(m=model_name)  : 'census-vent-sd-norm'
        , "census-vent dt-{m} sd-0".format(m=model_name)     : 'census-vent-sd-0'
        , "census-vent dt-{m} sd-1".format(m=model_name)     : 'census-vent-sd-1'
        , "MedSurg Capacity"                                 : "hosp-beds"
        , "ICU Capacity"                                     : "icu-beds"
        , "Ventilators"                                      : "vent-beds"
        , "Non-COVID19 MedSurg Occupancy"                    : "hosp-occ"
        , "Non-COVID19 ICU Occupancy"                        : "icu-occ"
        , "Non-COVID19 Ventilators in Use"                   : "vent-occ"
        }, inplace = True
    )

    rf['date'] = rf['date'].apply( lambda a : excel_date(a))

    x = rf["date"].values
    y = rf["census-vent-sd-norm"].values

    cf = DataFrame()

    cf["date"] = x
    cf["day"] = rf["day"]
    for col in [
        "census-hosp-sd-norm",
        "census-icu-sd-norm",
        "census-vent-sd-norm",
        "census-hosp-sd-0",
        "census-icu-sd-0",
        "census-vent-sd-0",
        "census-hosp-sd-1",
        "census-icu-sd-1",
        "census-vent-sd-1",
        ]:
        cf[col] = smoothed_line(x, rf[col].values)

    cf['date'] = cf['date'].apply( lambda a : excel_to_normaldate(a).strftime("%Y%m%d"))

    for col in ( 'hosp-beds', 'icu-beds', 'vent-beds', 'hosp-occ', 'icu-occ', 'vent-occ'):
        cf[col] = rf[col]

    param = {
        'labeled-dates': cf[["date"]].iloc[::7, :].values.tolist(),
        'hosp-sd-norm' : cf[["date", "census-hosp-sd-norm"]].values.tolist(),
        'hosp-sd-0'    : cf[["date", "census-hosp-sd-0"]].values.tolist(),
        'hosp-sd-1'    : cf[["date", "census-hosp-sd-1"]].values.tolist(),
        'icu-sd-norm'  : cf[["date", "census-icu-sd-norm"]].values.tolist(),
        'icu-sd-0'     : cf[["date", "census-icu-sd-0"]].values.tolist(),
        'icu-sd-1'     : cf[["date", "census-icu-sd-1"]].values.tolist(),
        'vent-sd-norm' : cf[["date", "census-vent-sd-norm"]].values.tolist(),
        'vent-sd-0'    : cf[["date", "census-vent-sd-0"]].values.tolist(),
        'vent-sd-1'    : cf[["date", "census-vent-sd-1"]].values.tolist(),
        'hosp-beds'    : cf[["date", "hosp-beds"]].values.tolist(),
        'icu-beds'     : cf[["date", "icu-beds"]].values.tolist(),
        'vent-beds'    : cf[["date", "vent-beds"]].values.tolist(),
        'hosp-occ'     : cf[["date", "hosp-occ"]].values.tolist(),
        'icu-occ'      : cf[["date", "icu-occ"]].values.tolist(),
        'vent-occ'     : cf[["date", "vent-occ"]].values.tolist(),
    }

    param.update( { 'current-inpatient' : (
        sp['Currently Hospitalized COVID-19 Patients (>= 0)'][current_scenario],
        sp['Currently Precautionary Hospitalized Patients (>= 0)'][current_scenario],
        )  } )

    param.update( { 'peaks' : (
        cf[["date", "census-hosp-sd-norm", "day"]][cf[["date", "census-hosp-sd-norm", "day"]]["census-hosp-sd-norm"] == cf[["date", "census-hosp-sd-norm", "day"]]["census-hosp-sd-norm"].max()].values.tolist(),
        cf[["date", "census-icu-sd-norm" , "day"]][cf[["date", "census-icu-sd-norm" , "day"]]["census-icu-sd-norm"]  == cf[["date", "census-icu-sd-norm" , "day"]]["census-icu-sd-norm"].max()].values.tolist(),
        cf[["date", "census-vent-sd-norm", "day"]][cf[["date", "census-vent-sd-norm", "day"]]["census-vent-sd-norm"] == cf[["date", "census-vent-sd-norm", "day"]]["census-vent-sd-norm"].max()].values.tolist(),

        cf[["date", "census-hosp-sd-0", "day"]][cf[["date", "census-hosp-sd-0", "day"]]["census-hosp-sd-0"] == cf[["date", "census-hosp-sd-0", "day"]]["census-hosp-sd-0"].max()].values.tolist(),
        cf[["date", "census-icu-sd-0" , "day"]][cf[["date", "census-icu-sd-0" , "day"]]["census-icu-sd-0"]  == cf[["date", "census-icu-sd-0" , "day"]]["census-icu-sd-0"].max()].values.tolist(),
        cf[["date", "census-vent-sd-0", "day"]][cf[["date", "census-vent-sd-0", "day"]]["census-vent-sd-0"] == cf[["date", "census-vent-sd-0", "day"]]["census-vent-sd-0"].max()].values.tolist(),

        cf[["date", "census-hosp-sd-1", "day"]][cf[["date", "census-hosp-sd-1", "day"]]["census-hosp-sd-1"] == cf[["date", "census-hosp-sd-1", "day"]]["census-hosp-sd-1"].max()].values.tolist(),
        cf[["date", "census-icu-sd-1" , "day"]][cf[["date", "census-icu-sd-1" , "day"]]["census-icu-sd-1"]  == cf[["date", "census-icu-sd-1" , "day"]]["census-icu-sd-1"].max()].values.tolist(),
        cf[["date", "census-vent-sd-1", "day"]][cf[["date", "census-vent-sd-1", "day"]]["census-vent-sd-1"] == cf[["date", "census-vent-sd-1", "day"]]["census-vent-sd-1"].max()].values.tolist(),

        ) } )

    n_days = sp['Days to Project'][current_scenario]

    pk = [
        max_peak( param['peaks'][0][0][2], n_days),
        max_peak( param['peaks'][3][0][2], n_days),
        max_peak( param['peaks'][6][0][2], n_days),
    ]

    param.update( { 'sd' : (
        ( sp['Social Distancing Reduction Rate: 0.0 - 1.0'][current_scenario]    , pk[0] ),
        ( sp['Social Distancing Reduction Rate (0): 0.0 - 1.0'][current_scenario], pk[1] ),
        ( sp['Social Distancing Reduction Rate (1): 0.0 - 1.0'][current_scenario], pk[2] ),
        ) } )

    pk = [
        cf[["census-hosp-sd-norm"]]["census-hosp-sd-norm"].max(),
        cf[["census-hosp-sd-0"]]["census-hosp-sd-0"].max(),
        cf[["census-hosp-sd-1"]]["census-hosp-sd-1"].max(),

        cf[["census-icu-sd-norm"]]["census-icu-sd-norm"].max(),
        cf[["census-icu-sd-0"]]["census-icu-sd-0"].max(),
        cf[["census-icu-sd-1"]]["census-icu-sd-1"].max(),

        cf[["census-vent-sd-norm"]]["census-vent-sd-norm"].max(),
        cf[["census-vent-sd-0"]]["census-vent-sd-0"].max(),
        cf[["census-vent-sd-1"]]["census-vent-sd-1"].max(),

        sp.loc[current_scenario]["MedSurg Capacity"],
        sp.loc[current_scenario]["ICU Capacity"],
        sp.loc[current_scenario]["Ventilator Capacity"],

    ]

    param.update( { 'ymax' : np.max( pk ) })

    param.update( { 'capacity' : (
        next(iter(cf[["date", "day"]][cf[["date", "census-hosp-sd-norm", "day"]]["census-hosp-sd-norm"] >= cf['hosp-beds']].values.tolist()), None),
        next(iter(cf[["date", "day"]][cf[["date", "census-icu-sd-norm" , "day"]]["census-icu-sd-norm"]  >= cf["icu-beds"]].values.tolist()), None),
        next(iter(cf[["date", "day"]][cf[["date", "census-vent-sd-norm", "day"]]["census-vent-sd-norm"] >= cf["vent-beds"]].values.tolist()), None),

        next(iter(cf[["date", "day"]][cf[["date", "census-hosp-sd-0", "day"]]["census-hosp-sd-0"] >= cf["hosp-beds"]].values.tolist()), None),
        next(iter(cf[["date", "day"]][cf[["date", "census-icu-sd-0" , "day"]]["census-icu-sd-0"]  >= cf["icu-beds"]].values.tolist()), None),
        next(iter(cf[["date", "day"]][cf[["date", "census-vent-sd-0", "day"]]["census-vent-sd-0"] >= cf["vent-beds"]].values.tolist()), None),

        next(iter(cf[["date", "day"]][cf[["date", "census-hosp-sd-1", "day"]]["census-hosp-sd-1"] >= cf["hosp-beds"]].values.tolist()), None),
        next(iter(cf[["date", "day"]][cf[["date", "census-icu-sd-1" , "day"]]["census-icu-sd-1"]  >= cf["icu-beds"]].values.tolist()), None),
        next(iter(cf[["date", "day"]][cf[["date", "census-vent-sd-1", "day"]]["census-vent-sd-1"] >= cf["vent-beds"]].values.tolist()), None),

        ) } )

    param.update( { 'beds' : (
        sp['MedSurg Capacity'][current_scenario],
        sp['ICU Capacity'][current_scenario],
        sp['Ventilator Capacity'][current_scenario], ) })

    return param

def get_inflected_graph_parameters(current_scenario, model_name, sp, data, mitigations, sir=False ) :

    scenario_location = sp.loc[current_scenario]["Scenario ID"]

    rf = data[data['Location'] == scenario_location]

    model_cols = [col for col in rf.columns if 'dt-{m}'.format(m=model_name) in col and "inflected" in col and ("census" in col or "susceptible" in col or "recovered" in col or "infected" in col)]
    model_cols.append( "MedSurg Capacity" )
    model_cols.append( "ICU Capacity")
    model_cols.append( "Ventilators")
    model_cols.append( "Non-COVID19 MedSurg Occupancy")
    model_cols.append( "Non-COVID19 ICU Occupancy")
    model_cols.append( "Non-COVID19 Ventilators in Use")
    model_cols.append( 'day' )
    model_cols.insert( 0, 'date' )

    rf = rf[model_cols]

    rf.rename (
        columns = {
        "census-hosp dt-{m} sd-inflected".format(m=model_name)      : 'census-hosp-sd',
        "census-icu dt-{m} sd-inflected".format(m=model_name)       : 'census-icu-sd',
        "census-vent dt-{m} sd-inflected".format(m=model_name)      : 'census-vent-sd',
        "susceptible dt-{m} sd-inflected".format(m=model_name)      : 'susceptible',
        "infected dt-{m} sd-inflected".format(m=model_name)         : 'infected',
        "recovered dt-{m} sd-inflected".format(m=model_name)        : 'recovered',
        "MedSurg Capacity"                                          : "hosp-beds",
        "ICU Capacity"                                              : "icu-beds",
        "Ventilators"                                               : "vent-beds",
        "Non-COVID19 MedSurg Occupancy"                             : "hosp-occ",
        "Non-COVID19 ICU Occupancy"                                 : "icu-occ",
        "Non-COVID19 Ventilators in Use"                            : "vent-occ",
        }, inplace = True
    )

    rf['date'] = rf['date'].apply( lambda a : excel_date(a))

    x = rf["date"].values

    cf = DataFrame()

    cf["date"] = x
    cf["day"] = rf["day"]
    if sir :
        cols = ["susceptible", "infected", "recovered", ]
    else :
        cols = ["census-hosp-sd", "census-icu-sd", "census-vent-sd", ]

    for col in cols:
        cf[col] = smoothed_line(x, rf[col].values)

    cf['date'] = cf['date'].apply( lambda a : excel_to_normaldate(a).strftime("%Y%m%d"))

    for col in ( 'hosp-beds', 'icu-beds', 'vent-beds', 'hosp-occ', 'icu-occ', 'vent-occ'):
        cf[col] = rf[col]

    param = {
        'labeled-dates': cf[["date"]].iloc[::7, :].values.tolist(),
        'hosp-beds'    : cf[["date", "hosp-beds"]].values.tolist(),
        'icu-beds'     : cf[["date", "icu-beds"]].values.tolist(),
        'vent-beds'    : cf[["date", "vent-beds"]].values.tolist(),
        'hosp-occ'     : cf[["date", "hosp-occ"]].values.tolist(),
        'icu-occ'      : cf[["date", "icu-occ"]].values.tolist(),
        'vent-occ'     : cf[["date", "vent-occ"]].values.tolist(),
    }
    if sir:
        param.update( {
            'susceptible'  : cf[["date", "susceptible"]].values.tolist(),
            'infected'     : cf[["date", "infected"]].values.tolist(),
            'recovered'    : cf[["date", "recovered"]].values.tolist(), })
    else:
        param.update({
            'hosp-sd'      : cf[["date", "census-hosp-sd"]].values.tolist(),
            'icu-sd'       : cf[["date", "census-icu-sd"]].values.tolist(),
            'vent-sd'      : cf[["date", "census-vent-sd"]].values.tolist(),})

    param.update( { 'current-inpatient' : (
        sp['Currently Hospitalized COVID-19 Patients (>= 0)'][current_scenario],
        sp['Currently Precautionary Hospitalized Patients (>= 0)'][current_scenario],
        )
    } )

    if not sir:
        param.update( { 'peaks' : (
            cf[["date", "census-hosp-sd", "day"]][cf[["date", "census-hosp-sd", "day"]]["census-hosp-sd"] == cf[["date", "census-hosp-sd", "day"]]["census-hosp-sd"].max()].values.tolist(),
            cf[["date", "census-icu-sd" , "day"]][cf[["date", "census-icu-sd" , "day"]]["census-icu-sd"]  == cf[["date", "census-icu-sd" , "day"]]["census-icu-sd"].max()].values.tolist(),
            cf[["date", "census-vent-sd", "day"]][cf[["date", "census-vent-sd", "day"]]["census-vent-sd"] == cf[["date", "census-vent-sd", "day"]]["census-vent-sd"].max()].values.tolist(),
            )
        } )

    if not sir:
        n_days = sp['Days to Project'][current_scenario]
        pk = [
            max_peak( param['peaks'][0][0][2], n_days),
            max_peak( param['peaks'][1][0][2], n_days),
            max_peak( param['peaks'][2][0][2], n_days),
        ]

        param.update( { 'peak-day' : pk } )

    if sir:
        pk = [
            cf[["infected"]]["infected"].max(),
            cf[["susceptible"]]["susceptible"].max(),
            cf[["recovered"]]["recovered"].max(),
        ]
    else :
        pk = [
            cf[["census-hosp-sd"]]["census-hosp-sd"].max(),
            cf[["census-icu-sd"]]["census-icu-sd"].max(),
            cf[["census-vent-sd"]]["census-vent-sd"].max(),

            sp.loc[current_scenario]["MedSurg Capacity"],
            sp.loc[current_scenario]["ICU Capacity"],
            sp.loc[current_scenario]["Ventilator Capacity"],
        ]

    param.update( { 'ymax' : np.max( pk ) })

    if not sir:
        param.update( { 'capacity' : (
            next(iter(cf[["date", "day"]][cf[["date", "census-hosp-sd", "day"]]["census-hosp-sd"] >= cf["hosp-beds"]].values.tolist()), None),
            next(iter(cf[["date", "day"]][cf[["date", "census-icu-sd" , "day"]]["census-icu-sd"]  >= cf["icu-beds"]].values.tolist()), None),
            next(iter(cf[["date", "day"]][cf[["date", "census-vent-sd", "day"]]["census-vent-sd"] >= cf["vent-beds"]].values.tolist()), None),
            )
        } )

    param.update( { 'beds' : (

        sp['MedSurg Capacity'][current_scenario],
        sp['ICU Capacity'][current_scenario],
        sp['Ventilator Capacity'][current_scenario],

            )
        })

    param.update( { 'mitigations' : mitigations })

    return param

def generate_pdf(pdf_file, projected_data, computed_data, scenario_parameters, mitigations, mitigation_data ):
    pdfmetrics.registerFont(TTFont('Calibri', 'Calibri.ttf'))
    pdfmetrics.registerFont(TTFont('CalibriBd', 'Calibri Bold.ttf'))
    pdfmetrics.registerFont(TTFont('CalibriIt', 'Calibri Italic.ttf'))
    pdfmetrics.registerFont(TTFont('CalibriBI', 'Calibri Bold Italic.ttf'))

    pdfmetrics.registerFontFamily('Calibri', normal='Calibri',bold='CalibriBd',italic='CalibriIt',boldItalic='CalibriBI')

    doc = SimpleDocTemplate(
        pdf_file,
        pagesize=TABLOID,
        rightMargin=0.42*inch, leftMargin=0.42*inch,
        topMargin=1.0*inch, bottomMargin=0.5*inch)

    doc.logo_path = PDF_ASSETS
    doc.logo = 'dha_logo.png'

    doc.author="COVID19 Scenario Projection Generator"
    doc.title="COVID19 Scenario Projections"
    doc.subject="COVID19"
    doc.scenario_parameters = scenario_parameters
    doc.data = projected_data
    doc.computed_data = computed_data
    doc.current_scenario = 0

    elements = []

    styles = getSampleStyleSheet()
    normal = styles["Normal"]

    txt='''<br/><br/><font size=18>Using UPenn COVID-19 Hospital Impact Model for Epidemics (C.H.I.M.E.)</font><br /><br />
        <font size=10 color="#aaaaaa">Source: <a color="blue" href="https://penn-chime.phl.io/">https://penn-chime.phl.io/</a></font><br /><br />

        <br /><br /><br /><br /><font size=14>UPenn C.H.I.M.E. MODEL</font> {version}<br /><br />
        '''.format(version=VERSION)

    elements.append(Paragraph(txt, normal))

    txt='''<br /><br /><font color="darkblue"><b>What is it?</b></font> Penn Medicine developed and released an open-source tool to help hospitals plan for patient increases and intake during the COVID-19 spread

        <br /><br /><font color="darkblue"><b>How does it work?</b></font> The tool, called CHIME, or COVID-19 Hospital Impact Model for Epidemics, uses S-I-R (Susceptible-Infected-Recovered) modeling, which computes the theoretical number of people infected with a contagious illness in a closed population over time to project outcomes. It’s currently set up to help Penn’s and other health systems’ operations leaders with projects of how many patients will need hospitalization, ICU beds and mechanical ventilation. The epidemic proceeds via a growth and decline process. This is the core model of infectious disease spread and has been in use in epidemiology for many years.

        <br /><br /><font color="darkblue"><b>Rationale for Use:</b></font> CHIME allows hospitals to enter information about their population and modify assumptions around the spread and behavior of COVID-19. It then runs a standard SIR model to project the number of new hospital admissions each day, along with the daily hospital census. These projections can then be used to create best- and worst-case scenarios to assist with capacity planning.

        <br /><br />Default parameters in the model can be customized not only for the at-risk population in question, but also can be adjusted for “real world vs. model” ranges including current hospitalized patients and assumptions around doubling time, social distancing mitigation, hospitalization %, ICU %, ventilation %. The tool may be used to help inform readiness responses and mitigation strategies.

        <br /><br /><font color="darkblue"><b>Updates are rolled out by Penn Medicine and community as U.S. spread progresses.</b></font>

        <br /><br /><font color="darkblue"><b>Key outputs for Capacity Planning</b></font>
        <br />
        '''

    paragraph = Paragraph(txt, normal)

    elements.append(paragraph)

    elements.append(ListFlowable(
            [Paragraph("Projected number of new admissions for COVID-19 per day, including new patients requiring hospitalization, new patients requiring intensive care, and new patients requiring ventilation", normal),
             ListItem(Paragraph("Census of COVID-19 Patients, including hospital census, ICU census, and Ventilator census accounting for length of stay and recovery time", normal))
             ],
            bulletType='bullet',
            start='bulletchar'
        ))

    elements.append(Paragraph("", normal))

    elements.append(Image( PDF_ASSETS + "chime.png", 400, 514 ))

    current_scenario_id = 0
    for scenario in ( scenario_parameters["Scenario ID"].unique() ):
        elements.append(CurrentScenario(current_scenario_id))
        elements.append(Spacer(0, 0.125*inch ))
        elements.append(PageBreak())

        for model in ( "low", 'observed' ):
            elements.append(ScenarioHeader(params=get_header_parameters(current_scenario_id, model, computed_data, scenario_parameters)))
            elements.append(ScenarioGraph(params=get_graph_parameters(current_scenario_id, model, computed_data, scenario_parameters, projected_data)))
            elements.append(Spacer(0, 0.125*inch ))

        p = scenario_parameters.loc[scenario_parameters['Scenario ID'] == scenario].transpose()
        pv = p.values.tolist()
        p = p.index.tolist()

        data = [
            ['Parameter', 'Value', '', 'Parameter', 'Value', '', 'Parameter', 'Value', ],
        ]

        for pi in range( 0, len(p), 3):
            r = [p[pi], format_parameter(pv[pi][0]), " ",]
            if pi + 1 < len(p):
                r.append(p[pi+1])
                # r.append(str(type(pv[pi+1][0])))
                r.append(format_parameter(pv[pi+1][0]))
                r.append("")
                if pi + 2 < len(p):
                    r.append(p[pi+2])
                    # r.append(str(pv[pi+2]))
                    # r.append(str(type(pv[pi+2][0])))
                    r.append(format_parameter(pv[pi+2][0]))

            data.append(r)

        t = Table(data)

        t.setStyle(TableStyle([
            ('LINEBELOW', (0,0), (1,0), 0.5, HexColor("#a2b7e0")),
            ('LINEBELOW', (3,0), (4,0), 0.5, HexColor("#a2b7e0")),
            ('LINEBELOW', (6,0), (-1,0), 0.5, HexColor("#a2b7e0")),

            ('LINEBELOW', (0,1), (1,-1), 0.25, HexColor("#dddddd")),
            ('LINEBELOW', (3,1), (4,-1), 0.25, HexColor("#dddddd")),
            ('LINEBELOW', (6,1), (-1,-1), 0.25, HexColor("#dddddd")),

            # ('BOX', (0,0), (-1,-1), 0.25, colors.black),

            ('FONT', (0,0), (-1,0), "CalibriBd", 6 ),
            ('FONT', (0,1), (-1,-1), "Calibri", 5 ),

            ('TOPPADDING', (0, 0), (-1,-1), 1),
            ('BOTTOMPADDING', (0, 0), (-1,-1), 1),
        ]))

        elements.append(t)

        if os.path.exists(PDF_ANNOTATIONS + scenario + ".txt"):
            elements.append(Spacer(0, 0.25*inch ))
            f = open(PDF_ANNOTATIONS + scenario + ".txt")
            p = Paragraph(f.read(), style=ParagraphStyle(name="notes",fontName="Calibri", fontSize=8, leading=9))
            f.close()
            data = [["Notes"], [p]]
            t = Table(data)

            t.setStyle(TableStyle([
                ('LINEBELOW', (0,0), (0,0), 0.5, HexColor("#a2b7e0")),

                ('FONT', (0,0), (0,0), "CalibriBd", 8 ),
                ('FONT', (1,0), (-1,-1), "Calibri", 6 ),

            ]))

            elements.append(t)

        if len(mitigations.columns) >0 :

            miti = mitigations.loc[(mitigations['init-model'] == 'dt-observed') & (mitigations['scenario_id'] == scenario)]
            # print ( "\n\n\n", scenario, "\n\n\n")
            # print ( "\n\n\n", mitigations, "\n\n\n")
            # print ( "\n\n\n", miti, "\n\n\n")
            if len(miti.index) > 0 :
                elements.append(PageBreak())
                elements.append(ScenarioInflectedHeader(params=get_header_parameters(current_scenario_id, "observed",  computed_data, scenario_parameters)))
                elements.append(ScenarioInflectedGraph(params=get_inflected_graph_parameters(current_scenario_id, "observed", scenario_parameters, mitigation_data, miti)))
                elements.append(Spacer(0, 0.5*inch ))
                elements.append(ScenarioInflectedGraph(params=get_inflected_graph_parameters(current_scenario_id, "observed", scenario_parameters, mitigation_data, miti, True),sir=True))
                elements.append(Spacer(0, 0.5*inch ))
                elements.append(ScenarioMitigationTable(mitigations=miti).getTable())

        current_scenario_id += 1


    doc.build(elements,
              onFirstPage=cover_header,
              onLaterPages=header,
              canvasmaker=PageNumCanvas)
