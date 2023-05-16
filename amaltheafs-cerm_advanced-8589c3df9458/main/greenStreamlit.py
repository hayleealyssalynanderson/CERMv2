# Package Imports 
import streamlit as st
st.set_page_config(layout="wide")
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from parameters import *
from ScenarioGenerator import ScenarioGenerator
from utils import correlation_from_covariance
import matplotlib.ticker as mtick
from utils import correlation_from_covariance
from LargeCERMEngine import LargeCERMEngine
import datetime
from PIL import Image
import matplotlib.ticker as mtick
import os

Image.MAX_IMAGE_PIXELS = 1000000000 

## Styling 
button_style = """
        <style>
        .stButton > button {
            margin-left: 60px;
            width: 150px;
            height: 50px;
        }
        </style>
        """
theme = """ 
    base="light"
    primaryColor="#4cb744"
"""

## Logo
image = 'amaltheafs-cerm_advanced-8589c3df9458/main/logos/fin_rwa.png'
myCwd = os.getcwd();
logo_path = os.path.join(myCwd, image)
st.sidebar.image(logo_path,width=130)
st.sidebar.markdown('**Macro Parameters:**')


# App Heading 
def heading():

    st.markdown("""
        <h1 style='text-align: center; margin-bottom: -35px;'>
        CERM
        </h1>
    """, unsafe_allow_html=True
    )
    st.markdown("""
        <h6 style='text-align: center; margin-bottom: -35px;'>
        Climate-Extended Risk Model 
        </h6>
        <br>
        <br>

    """, unsafe_allow_html=True
    )
    st.write("")
    st.write("")
heading()

def params():
    horizon = st.sidebar.number_input( 'Horizon', 1, 50, value=50)
    st.sidebar.markdown( """ 
                            <p style= font-size:12px;color:#898A8B;margin-top:-85px;margin-left:65px;'>
                             time horizon of the study
                            </p>
                        """, unsafe_allow_html=True
                        )
    p = st.sidebar.slider( 'Climate Risk ', min_value=0.01, step=0.01, max_value=0.3, value=0.18, format="%f")
    st.sidebar.markdown( """ 
                            <p style= font-size:12px;color:#898A8B;margin-top:-100px;margin-left:90px;'>
                             of the economic risk per year
                            </p>
                        """, unsafe_allow_html=True
                        )
    Efficiency = st.sidebar.slider( 'Efficiency ', min_value=1, step=1, max_value=20, value=7, format="%d%%")
    st.sidebar.markdown( """ 
                            <p style= font-size:12px;color:#898A8B;margin-top:-100px;margin-left:65px;'>
                            transition efficiency yield
                            </p>
                        """, unsafe_allow_html=True
                        )
    Reactivity = st.sidebar.slider( 'Reactivity ', min_value=.001, step=.001, max_value=2.000, value=0.5, format="%f")
    st.sidebar.markdown( """ 
                            <p style= font-size:12px;color:#898A8B;margin-top:-100px;margin-left:65px;'>
                             transition effort reactivity coefficient
                            </p>
                        """, unsafe_allow_html=True
                        )
    st.sidebar.markdown("***")
    st.sidebar.markdown('**Parametric Portfolio:**')
    duration = st.sidebar.number_input( 'Duration ', min_value=1, step=1, value=10)
    st.sidebar.markdown( """
                            <p style= font-size:12px;color:#898A8B;margin-top:-85px;margin-left:65px;'>
                            average duration in years
                            </p>
                        """, unsafe_allow_html=True
                        )
    ## Target Net Zero
    st.sidebar.write('***Target net-zero portfolio:***')
    #Green Portfolio
    green_option = st.sidebar.selectbox('Average Target Rating:',('AAA', 'AA','A','BBB','BB','B+','B','D'),key="7")

    micro01 = st.sidebar.slider( 'Average Physical Risk Exposure ', min_value=0.0, step=.01, max_value=4.0, value=0.5, format="%f",key="3")
    st.sidebar.markdown( """
                                <p style= font-size:12px;color:#898A8B;margin-top:-85px;margin-left:65px;'>
                                
                                </p>
                            """, unsafe_allow_html=True
                            )
    micro02 = st.sidebar.slider( 'Average Transition Risk Exposure ', min_value=0.0, step=.01, max_value=4.0, value=0.0, format="%f",key="4")
    st.sidebar.markdown( """
                                <p style= font-size:12px;color:#898A8B;margin-top:-85px;margin-left:65px;'>
                                
                                </p>
                            """, unsafe_allow_html=True
                            )
    transition_target_date = st.sidebar.number_input( 'Transition Target Date ', min_value=2023, step=1, value=2050)
    #Portfolio A
    st.sidebar.write('***Initial portfolio:***')
    #Target rating
    a_option = st.sidebar.selectbox('Average Rating:',('AAA', 'AA','A','BBB','BB','B+','B','D'),key="8")
    
    micro11 = st.sidebar.slider( 'Average Physical Risk Exposure ', min_value=0.0, step=.01, max_value=4.0, value=1.0, format="%f", key="5")
    micro12 = st.sidebar.slider( 'Average Transition Exposure ', min_value=0.0, step=.01, max_value=4.0, value=2.0, format="%f", key="6")

    # number of iterations for Monte-Carlo simulation
    st.sidebar.markdown("***")
    st.sidebar.markdown('**Simulation:**')
    N = st.sidebar.number_input('N', 1, value=5000)  
    st.sidebar.markdown( """ 
            <p style= font-size:12px;color:#898A8B;margin-top:-87px;margin-left:20px;'>
             number of iterations for Monte-Carlo simulaton
            </p>
        """, unsafe_allow_html=True
        )
        


    if st.sidebar.button(' Run Simulation'):
        sideBar(horizon, p, Efficiency,Reactivity,duration,green_option,micro01,micro02,micro11,micro12,transition_target_date,a_option, N)

        
    st.sidebar.write("")
    st.markdown(button_style, unsafe_allow_html=True)

def percent(x, pos):
    return '{:3.3f}%'.format(x * 100)
    #'%.3f%%'
# SideBar Parameters
#@st.cache(suppress_st_warning=True)
def sideBar(horizon, p, Efficiency,Reactivity,duration,green_option,micro01,micro02,micro11,micro12,transition_target_date,a_option, N):

    # Preset Parameters    
    #transition efficiency coefficient (reduced)
    alpha = 0.001

    #transition effort reactivity coefficient
    beta = 0.001

    #climate change intensity of the economic activity (idiosyncratic)
    gamma = 0

    #hypothetical climate-free average growth rate of log GDP
    R = 2

    #independent transition coefficient
    theta = 0.001

    #idiosyncratic economic risk
    e = 1

    #time horizon of the study
    #horizon = 50
    #Number field
   
    

    # slider from 0% to 30% "of the economic risk per year" 
    #idiosyncratic physical risk
    #p = 0.18
    #Slider from 0 to 0.3
   
    
    scenario = ScenarioGenerator(horizon, alpha, beta, gamma, R, e, p, theta)
    scenario.compute()

    #logging of all macro-correlations evolutions

    macros = scenario.macro_correlation.T
    #plotting

    plt.figure(figsize=(16,12))
    plt.plot(range(1,horizon), macros[1:,:], label=["economic","physical","transition"])
    plt.title("Physical risk against economical risk in the absence of transition effort over "+str(horizon)+" years",fontsize=21)
    plt.ylabel("Normalized risk factor",fontsize=21)
    plt.xlabel("year",fontsize=21)
    plt.legend(fontsize=18,loc='lower right')
    #plt.show()
    
    st.write("### Unexpected Loss: ")   
    col9, inter_cols_pace = st.columns(2)
    st.write("### Global Climate-Related Risk: ")        
    col1, col2 = st.columns(2)
    st.write("### Target Net Zero Portfolio: ")
    col3, col4 = st.columns(2)
    st.write("### Initial Portfolio: ")
    col5, col6 = st.columns(2)
    st.write("### Transition Portfolio: ")
    col7, col8 = st.columns(2)
    #col1, inter_cols_pace, col2 = st.columns((2, 8, 2))




    #st.pyplot(plt.gcf()) # instead of plt.show()


    # we compute the climate scenario until 2 * horizon to get auto- and cross- correlations as delayed as the horizon

    scenario_extended = ScenarioGenerator(2 * horizon, alpha, beta, gamma, R, e, p, theta)
    scenario_extended.compute()

    # generation of the incremental matrix

    A = np.array(
        [[0, 0, 0], [-scenario.gamma, 1, -scenario.alpha], [0, scenario.beta, 0]])

    # initialization of autocorrelations

    autocorrelation = np.zeros(
        (horizon, horizon-1, scenario.nb_rf, scenario.nb_rf))
    autocorrelation_phy = np.zeros((horizon-1, horizon-1))
    autocorrelation_tra = np.zeros((horizon-1, horizon-1))
    autocorrelation_phy_tra = np.zeros((horizon-1, horizon))
    autocorrelation_tra_phy = np.zeros((horizon-1, horizon))

    # initialization of times and delays for which is drawn the graph

    times = range(1, horizon)
    taus = range(1, horizon)

    # execution

    for t in times:

        # logging of variance matrix at time t

        var_t = scenario_extended.var_at(t)
        corr = correlation_from_covariance(var_t)

        # logging of simultaneous cross-correlations, i.e. for delay tau=0

        autocorrelation_phy_tra[t-1, 0] = corr[2, 1]
        autocorrelation_tra_phy[t-1, 0] = corr[1, 2]

        # execution for each possible delay

        for tau in taus:

            # logging of variance matrix at time t+tau

            var_delay = scenario_extended.var_at(t+tau)
            # logging of inverse [standard deviations (macro-correlations)] at times t and t+tau

            at_time = np.reshape(1/np.sqrt(np.diag(var_t)), (3, 1))
            at_delay = np.reshape(1/np.sqrt(np.diag(var_delay)), (3, 1))

            # following the formula from the paper

            invsd = (at_delay@at_time.T)
            autocorrelation = invsd*(np.linalg.matrix_power(A, tau)@var_t)

            # logging all auto- and cross-correlations

            autocorrelation_phy[t-1, tau-1] = autocorrelation[1, 1]
            autocorrelation_tra[t-1, tau-1] = autocorrelation[2, 2]
            autocorrelation_phy_tra[t-1, tau] = autocorrelation[2, 1]
            autocorrelation_tra_phy[t-1, tau] = autocorrelation[1, 2]
        
        
    #plotting auto-correlation


    plt.figure(figsize=(16,12))
    plt.plot(np.flipud(autocorrelation_phy).diagonal())
    #plt.plot(autocorrelation_phy[0,:])



    plt.gca().yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1))

    plt.ylim([0, 1])

    plt.xlabel("delay",fontsize=18)
    plt.ylabel("correlation",fontsize=18)
    plt.title("Physical risk auto-correlation time amortization",fontsize=20)

    plt.legend()
    plt.show()
   # st.pyplot(plt.gcf()) # instead of plt.show()
   
    #transition efficiency coefficient (reduced)
    #Efficiency=7
    #Slider from 1 to 20


    alpha=Efficiency/100

    #transition effort reactivity coefficient
    #Reactivity=0.5
    #Slider from 0.001 to 2

 


    beta = Reactivity

    scenario = ScenarioGenerator(horizon, alpha, beta, gamma, R, e, p, theta)
    scenario.compute()

    #logging of all macro-correlations evolutions

    macros = scenario.macro_correlation.T

    #plotting

    plt.figure(figsize=(6, 4.5))
    plt.plot(range(1,horizon), macros[1:,:], label=["economic","physical","transition"])
    plt.title("Physical, Transition and Economic macro correlation over "+str(horizon)+" years",fontsize=10)
    plt.ylabel("Normalized risk factor",fontsize=10)
    plt.xlabel("year",fontsize=10)
    plt.legend(fontsize=5,loc='lower right')
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)
    plt.show()
   ## Graph 1
    

    with col1:
        fig1 = plt.figure(figsize=(16,12))
        plt.plot(range(1,horizon), macros[1:,:], label=["economic","physical","transition"])
        plt.title("Physical, Transition and Economic macro correlation over "+str(horizon)+" years",fontsize=20)        
        plt.ylabel("Normalized risk factor",fontsize=25)
        plt.xlabel("year",fontsize=25)
        plt.legend(fontsize=19,loc='lower right')
        plt.xticks(fontsize=20)
        plt.yticks(fontsize=20)
        plt.gca().yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1))
        st.pyplot(fig1)
        #st.write('Comparing Physical and Economic Risks Without Transition')
       
              
    
    # we compute the climate scenario until 2 * horizon to get auto- and cross- correlations as delayed as the horizon

    scenario_extended = ScenarioGenerator(2 * horizon, alpha, beta, gamma, R, e, p, theta)
    scenario_extended.compute()

    # generation of the incremental matrix

    A = np.array(
        [[0, 0, 0], [-scenario.gamma, 1, -scenario.alpha], [0, scenario.beta, 0]])

    # initialization of autocorrelations

    autocorrelation = np.zeros(
        (horizon, horizon-1, scenario.nb_rf, scenario.nb_rf))
    autocorrelation_phy = np.zeros((horizon-1, horizon-1))
    autocorrelation_tra = np.zeros((horizon-1, horizon-1))
    autocorrelation_phy_tra = np.zeros((horizon-1, horizon))
    autocorrelation_tra_phy = np.zeros((horizon-1, horizon))

    # initialization of times and delays for which is drawn the graph

    times = range(1, horizon)
    taus = range(1, horizon)
    # execution

    for t in times:

        # logging of variance matrix at time t

        var_t = scenario_extended.var_at(t)
        corr = correlation_from_covariance(var_t)

        # logging of simultaneous cross-correlations, i.e. for delay tau=0

        autocorrelation_phy_tra[t-1, 0] = corr[2, 1]
        autocorrelation_tra_phy[t-1, 0] = corr[1, 2]

        # execution for each possible delay

        for tau in taus:

            # logging of variance matrix at time t+tau

            var_delay = scenario_extended.var_at(t+tau)

            # logging of inverse [standard deviations (macro-correlations)] at times t and t+tau

            at_time = np.reshape(1/np.sqrt(np.diag(var_t)), (3, 1))
            at_delay = np.reshape(1/np.sqrt(np.diag(var_delay)), (3, 1))

            # following the formula from the paper

            invsd = (at_delay@at_time.T)
            autocorrelation = invsd*(np.linalg.matrix_power(A, tau)@var_t)

            # logging all auto- and cross-correlations

            autocorrelation_phy[t-1, tau-1] = autocorrelation[1, 1]
            autocorrelation_tra[t-1, tau-1] = autocorrelation[2, 2]
            autocorrelation_phy_tra[t-1, tau] = autocorrelation[2, 1]
            autocorrelation_tra_phy[t-1, tau] = autocorrelation[1, 2]
    #plotting auto-correlation


    plt.figure(figsize=(6, 4.5))
    plt.plot(np.flipud(autocorrelation_phy).diagonal())
    #plt.plot(autocorrelation_phy[0,:])

    plt.gca().yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1))

    plt.ylim([0, 1])

    plt.xlabel("delay",fontsize=10)
    plt.ylabel("correlation",fontsize=10)
    plt.title("Physical risk auto-correlation time amortization",fontsize=10)

    plt.legend()
    plt.show()
    
    #st.pyplot(plt.gcf()) # instead of plt.show()
    ## Graph 2
    with col2:
        fig2 = plt.figure(figsize=(16,12))
        plt.plot(np.flipud(autocorrelation_phy).diagonal())
        plt.gca().yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1))
        plt.ylim([0, 1])
        plt.xlabel("delay",fontsize=25)
        plt.ylabel("correlation",fontsize=25)
        plt.title("Physical risk auto-correlation time amortization",fontsize=25)
        plt.legend()
        plt.xticks(fontsize=20)
        plt.yticks(fontsize=20)
        st.pyplot(fig2)
        #st.write("Amortizing Physical Risk Auto-Correlation Time")
       
            
            


        
    #Transition raing matrix

    from Ratings import TEST_8_RATINGS
    st.write("")
    st.write("")
    st.write("")



    from Portfolio import Portfolio, load_from_file, show
    nb_ratings = 8
    nb_groups = 3
    nb_rf=3

    from Loan import Loan
    from Portfolio import Portfolio
    import uuid

    world_portfolio = Portfolio("world_portfolio")

    #from Portfolio import dump_to_file
    portfolio = world_portfolio
    #dump_to_file(world_portfolio,"demo")

    micro_correlation = np.ones((nb_groups, nb_ratings, nb_rf))

    #duration
    #duration=10
    #Numerical field

   
    
    ## Target Net Zero
   

    #Target rating
    Green_Rating=green_option 

    #Should be drop down within this list
 


    #Average physical exposure (in comparaison with the global economy)
    #micro_correlation[0,:,1]=0.5
    micro_correlation[0,:,1] = micro01

    #Slider from 0 to 4

    

    #Average transition exposure (in comparaison with the global economy)
    #micro_correlation[0,:,2]=0
    micro_correlation[0,:,2] = micro02 

    #Slider from 0 to 4


    

    #Transition target date
    


    A_Rating = a_option 


    #Should be drop down within this list
    print (TEST_8_RATINGS.list())


    #Average physical exposure (in comparaison with the global economy)
    #micro_correlation[1,:,1]=1
    micro_correlation[1,:,1] = micro11

    #Slider from 0 to 4


    #Average transition exposure (in comparaison with the global economy)
    #micro_correlation[1,:,2]=2
    micro_correlation[1,:,2] = micro12

    #Slider from 0 to 4



    ## Transition Portfolio
    #Portfolio B

    #Target rating
    B_Rating=A_Rating

    #Average physical exposure (in comparaison with the global economy)
    micro_correlation[2,:,1]=micro_correlation[1,:,1]

    #Average transition exposure (in comparaison with the global economy)
    micro_correlation[2,:,2]=micro_correlation[1,:,2]



    world_portfolio.add_loan(Loan(uuid.uuid4(), 'gov', "Green", 'gov', 100, 1000000000, 0, Green_Rating))
    world_portfolio.add_loan(Loan(uuid.uuid4(), 'gov', "Portfolio A", 'gov', 100, 1000000000, 0, A_Rating))
    world_portfolio.add_loan(Loan(uuid.uuid4(), 'gov', "Portfolio B", 'gov', 100, 1000000000, 0, B_Rating))




    size=world_portfolio.EAD(1,TEST_8_RATINGS).sum()
    target=world_portfolio.EAD(1,TEST_8_RATINGS).sum(axis=0)[0]/size

    portfolio_dict = show(portfolio)
    all_loans = np.vstack(portfolio_dict.values())
    all_principals = all_loans[:,0]
    total_principal = sum(np.array(all_principals, dtype=np.int32))

    # number of iterations for Monte-Carlo simulation
   
   # N = 5000

    # risk values

    risk1 = .05
    risk2 = .01

    #computation of all losses through LCERM

    engine = LargeCERMEngine(portfolio, TEST_8_RATINGS,scenario,duration,target,micro_correlation,transition_target_date)
    engine.compute(N)

    #definition of risk indices matching risk1 and risk2

    ind1 = int(np.floor(N*(1-risk1)))
    ind2 = int(np.floor(N*(1-risk2)))

    #logging of all losses

    losses = engine.loss_results

    #logging of final physical and transition cumulative risks (the - sign is simply so that loss distribution in the physical/transition plane is well-oriented)

    cumulative_growth_factors = -engine.cumulative_growth_factors[1:, :]

    #logging of final losses for plane distribution

    scenario_losses = losses.sum(axis=(1,2))

    #sorting of all losses, to assess the losses at risk1 and risk2

    sorted_losses = np.sort(losses, axis=0)

    #logging of non-cumulative expected loss, unexpected loss at risk risk1, unexpected loss at risk risk2 at each time

    el, ul1, ul2 = sorted_losses.sum(axis=(0,1))/N, (sorted_losses.sum(axis=1))[ind1], (sorted_losses.sum(axis=1))[ind2]
    el_g, ul1_g, ul2_g = sorted_losses.sum(axis=(0))/N, sorted_losses[ind1], sorted_losses[ind2]

    #logging of all final losses or all iterations

    #draws = np.sort(losses.sum(axis=(1,2)))
    #draws = np.sort(losses[:,0][:,-1])


    #computation of cumulative expected loss, unexpected loss at risk risk1, unexpected loss at risk risk2 at each time

    #for t in range(1,horizon):
    #   el[t] += el[t-1]
    #  ul1[t] += ul1[t-1]
    # ul2[t] += ul2[t-1]

    #logging of final cumulative expected loss, unexpected loss at risk risk1, unexpected loss at risk risk2


    #expected_loss = el[-1]
    #unexpected_loss1 = ul1[-1]
    #unexpected_loss2 = ul2[-1]

    el_rate=  np.zeros(horizon)
    ul1_rate= np.zeros(horizon)
    ul2_rate= np.zeros(horizon)

    el_rate[0]=1+el[0]/size
    ul1_rate[0]=1+ul1[0]/size
    ul2_rate[0]=1+ul2[0]/size

    for t in range(1,horizon):
        el_rate[t]=el_rate[t-1]*(1+(el[t]-el[t-1])/(size-el[t-1]))
        ul1_rate[t]=ul1_rate[t-1]*(1+(ul1[t]-ul1[t-1])/(size-ul1[t-1]))
        ul2_rate[t]=ul2_rate[t-1]*(1+(ul2[t]-ul2[t-1])/(size-ul2[t-1]))

        
    for t in range(0,horizon):
        el_rate[t]=el_rate[t]**(1/(t+1))-1
        ul1_rate[t]=ul1_rate[t]**(1/(t+1))-1
        ul2_rate[t]=ul2_rate[t]**(1/(t+1))-1



    #plotting of final loss distribution, along with expected loss and unexpected losses at risks risk1 and risk2

    draws = np.sort(sorted_losses[:,0,-1])
    expected_loss= draws.sum()/N
    unexpected_loss1=draws[ind1]
    unexpected_loss2 = draws[ind2]

    plt.figure(figsize=(8, 6))
    #plt.hist(draws, bins=max(200, N//100), alpha=.7)
    plt.hist(draws, bins=int(N/50),alpha=.7, linewidth=0.1)

    plt.axvline(x = expected_loss, color='pink')
    plt.text(expected_loss+20, N/120,"expected loss",rotation=90,fontsize=10)
    plt.axvline(x = unexpected_loss1, color='orange')
    plt.text(unexpected_loss1+20, N/120,"loss at risk "+str(100-int(100*risk1))+"% confidence level",rotation=90,fontsize=10)
    plt.axvline(x = unexpected_loss2, color='red')
    plt.text(unexpected_loss2+20, N/120,"loss at "+str(100-int(100*risk2))+"% confidence level",rotation=90,fontsize=10)

    plt.xlabel("loss",fontsize=10)
    plt.ylabel("number of occurences",fontsize=10)
    plt.title("Cumilative loss distribution of the Target Net Zero portfolio over " +str(horizon)+ " years",fontsize=10)
    plt.xlim([0, 1000000000])
    plt.ylim([0, 250])
    plt.xticks(fontsize=8)
    plt.yticks(fontsize=8)
    plt.legend()
    plt.show()
    #st.pyplot(plt.gcf()) # instead of plt.show()
    # Graph 3
    with col3:
        st.pyplot(plt.gcf()) # instead of plt.show()
        #st.write('Target Net Zero Cumilative Loss Distribution')
        

    #plotting of evolution of expected loss and unexpected losses at risks risk1 and risk2
    fig, ax1 = plt.subplots(figsize=(8, 6))
    ax1.plot(el_g[0], label="expected loss")
    ax1.plot(ul1_g[0], label="unexpected loss at risk "+str(int(100*risk1))+"%")
    ax1.plot(ul2_g[0], label="unexpected loss at risk "+str(int(100*risk2))+"%")
    
    # Remove the existing y-axis on the left side
    ax1.spines['left'].set_color('none')
    ax1.yaxis.set_visible(False)
    plt.xlabel("time")

    # Create a new y-axis with a range of 0 to 1 on the left side
    ax2 = ax1.twinx()
    ax2.set_ylim(0, 1)
    ax2.spines['right'].set_color('none')
    ax2.yaxis.set_visible(True)
    ax2.yaxis.tick_left()
    ax2.yaxis.set_ticks_position('left')
    ax2.set_ylabel("loss", labelpad=10)
    ax2.yaxis.set_label_coords(-0.12, 0.5)  # Adjust the position of the y-label
    plt.xlabel("time")

    plt.xlabel("time",fontsize=10)
    plt.ylabel("loss",fontsize=10)
    plt.title("Cumulative expected and unexpected losses of the Target Net Zero portfolio",fontsize=10)
    plt.xticks(fontsize=8)
    ax1.legend()

   

    plt.show()
    #Graph 4
    with col4:
        st.pyplot(plt.gcf()) # instead of plt.show()
        #st.write('Target Net Zero Cumulative Expeted and Unexpected Losses')
        

        

    #st.pyplot(plt.gcf()) # instead of plt.show()

    #plotting of final loss distribution, along with expected loss and unexpected losses at risks risk1 and risk2

    draws = np.sort(sorted_losses[:,1,-1])
    expected_loss= draws.sum()/N
    unexpected_loss1=draws[ind1]
    unexpected_loss2 = draws[ind2]
##16,12
    plt.figure(figsize=(8, 6))
    #plt.hist(draws, bins=max(200, N//100), alpha=.7)
    plt.hist(draws, bins=int(N/50),alpha=.7)

    plt.axvline(x = expected_loss, color='pink')
    plt.text(expected_loss+20, N/120,"expected loss",rotation=90,fontsize=10)
    plt.axvline(x = unexpected_loss1, color='orange')
    plt.text(unexpected_loss1+20, N/120,"loss at risk "+str(100-int(100*risk1))+"% confidence level",rotation=90,fontsize=10)
    plt.axvline(x = unexpected_loss2, color='red')
    plt.text(unexpected_loss2+20, N/120,"loss at "+str(100-int(100*risk2))+"% confidence level",rotation=90,fontsize=10)

    plt.xlabel("loss",fontsize=10)
    plt.ylabel("number of occurences",fontsize=10)
    plt.title("Cumulative loss distribution of initial portfolio over " +str(horizon)+ " years",fontsize=10)
    plt.xlim([0, 1000000000])
    plt.ylim([0, 250])

    plt.legend()
    plt.show()
    ## Graph5
    with col5:
        st.pyplot(plt.gcf()) # instead of plt.show()
        #st.write('Initial Portfolio Cumulative Loss Distribution')
        

    #plotting of evolution of expected loss and unexpected losses at risks risk1 and risk2

    fig, ax1 = plt.subplots(figsize=(8, 6))
    ax1.plot(el_g[1], label="expected loss")
    ax1.plot(ul1_g[1], label="unexpected loss at risk "+str(int(100*risk1))+"%")
    ax1.plot(ul2_g[1], label="unexpected loss at risk "+str(int(100*risk2))+"%")

    # Remove the existing y-axis on the left side
    ax1.spines['left'].set_color('none')
    ax1.yaxis.set_visible(False)
    plt.xlabel("time")

    # Create a new y-axis with a range of 0 to 1 on the left side
    ax2 = ax1.twinx()
    ax2.set_ylim(0, 1)
    ax2.spines['right'].set_color('none')
    ax2.yaxis.set_visible(True)
    ax2.yaxis.tick_left()
    ax2.yaxis.set_ticks_position('left')
    ax2.set_ylabel("loss", labelpad=10)
    ax2.yaxis.set_label_coords(-0.12, 0.5)  # Adjust the position of the y-label
    plt.xlabel("time")

    plt.xlabel("time",fontsize=10)
    plt.ylabel("loss",fontsize=10)
    plt.title("Cumulative expected and unexpected losses of the initial portfolio",fontsize=10)
    plt.xticks(fontsize=8)
    ax1.legend()
    plt.show()
    #Graph 6
    with col6:
        st.pyplot(plt.gcf()) # instead of plt.show()
        #st.write('Initial Portfolio Cumulative Expeted and Unexpected Loss')
        
    #st.pyplot(plt.gcf()) # instead of plt.show()

    
    draws = np.sort(sorted_losses[:,2,-1])
    expected_loss= draws.sum()/N
    unexpected_loss1=draws[ind1]
    unexpected_loss2 = draws[ind2]

    plt.figure(figsize=(8, 6))
    #plt.hist(draws, bins=max(200, N//100), alpha=.7)
    plt.hist(draws, bins=int(N/50),alpha=.7)

    plt.axvline(x = expected_loss, color='pink')
    plt.text(expected_loss+20, N/120,"expected loss",rotation=90,fontsize=10)
    plt.axvline(x = unexpected_loss1, color='orange')
    plt.text(unexpected_loss1+20, N/120,"loss at risk "+str(100-int(100*risk1))+"% confidence level",rotation=90,fontsize=10)
    plt.axvline(x = unexpected_loss2, color='red')
    plt.text(unexpected_loss2+20, N/120,"loss at "+str(100-int(100*risk2))+"% confidence level",rotation=90,fontsize=10)

    plt.xlabel("loss",fontsize=10)
    plt.ylabel("number of occurences",fontsize=10)
    plt.title("Cumulative loss distribution of the transition portfolio over " +str(horizon)+ " years",fontsize=10)
    plt.xlim([0, 1000000000])
    plt.ylim([0, 250])
    plt.xticks(fontsize=8)
    plt.yticks(fontsize=8)
    plt.legend()
    plt.show()
    #Graph 7
    with col7:
        st.pyplot(plt.gcf()) # instead of plt.show()
        #st.write('Transition Portfolio of Cumulative Loss Distribution')
        

    #plotting of evolution of expected loss and unexpected losses at risks risk1 and risk2

    fig, ax1 = plt.subplots(figsize=(8, 6))
    ax1.plot(el_g[2], label="expected loss")
    ax1.plot(ul1_g[2], label="unexpected loss at risk "+str(int(100*risk1))+"%")
    ax1.plot(ul2_g[2], label="unexpected loss at risk "+str(int(100*risk2))+"%")

    # Remove the existing y-axis on the left side
    ax1.spines['left'].set_color('none')
    ax1.yaxis.set_visible(False)
    plt.xlabel("time")
    # Create a new y-axis with a range of 0 to 1 on the left side
    ax2 = ax1.twinx()
    ax2.set_ylim(0, 1)
    ax2.spines['right'].set_color('none')
    ax2.yaxis.set_visible(True)
    ax2.yaxis.tick_left()
    ax2.yaxis.set_ticks_position('left')
    ax2.set_ylabel("loss", labelpad=10)
    ax2.yaxis.set_label_coords(-0.12, 0.5)  # Adjust the position of the y-label
    plt.xlabel("time")

    plt.xlabel("time")
    plt.ylabel("loss")
    plt.title("Cumulative expected and unexpected losses of the transition portfolio" ,fontsize=10)
    plt.xticks(fontsize=8)
    plt.yticks(fontsize=8)
    ax1.legend()
    
    plt.show()
    #Graph 8
    with col8:
        st.pyplot(plt.gcf()) # instead of plt.show()
        #st.write('Transition Portfolio of Expected and Unexpected Losses')
        

    #plotting of evolution of unexpected loss


    plt.figure(figsize=(16,12))
    plt.plot((ul1_g[0]-el_g[0])/1000000000, label="Net Zero target",color ='green')
    plt.plot((ul1_g[1]-el_g[1])/1000000000, label="Initial Portfolio",color='red')
    plt.plot((ul1_g[2]-el_g[2])/1000000000, label="Transition Portfolio",color='blue')
    #plt.plot((ul1_AB-el_AB)/2000000000, label="Portfolio A+B",color='purple')
    #plt.plot((ul1_g[3]-el_g[3])/1000000000, label="Brown", color='brown')
    #plt.plot((ul1_g[4]-el_g[4])/1000000000, label="Net zero 2050",color='blue')

    plt.legend(fontsize=18,loc='upper left')

    plt.gca().yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1))

    plt.ylim([0, 0.7])



    plt.xlabel("year",fontsize=25)
    plt.ylabel("unexpected loss",fontsize=25)
    plt.title("Cumulative unexpected loss of each portfolio",fontsize=25)
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20) 

    plt.show()
    #Graph 9
    with col9:
        ##Plotting of evolution of unexpected loss.
        st.pyplot(plt.gcf()) # instead of plt.show()
        ##st.write('Portfolio Unexpected Cumulative Loss')
        #st.write('Portfolio of Unexpected Loss')

        

    



params()

#sideBar()

