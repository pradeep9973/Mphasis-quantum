import pandas as pd
from graph import Graph
from flight import Flight
from airport import Airport
from pnr import PNR


#=======================================================================================================
# Create the graph
flight_graph = Graph()

# Path to the CSV file
available_flights = 'data_files/PRMI-DM-AVAILABLE_FLIGHTS.csv'  
cancelled_flights = 'data_files/PRMI-DM_TARGET_FLIGHTS_test.csv' 

# Build the graph using the CSV file
flight_graph.add_flights_from_csv(available_flights)
flight_graph.add_cancelled_flights_from_csv(cancelled_flights)

# # Draw the graph
# flight_graph.draw_graph()

#=======================================================================================================

# Step 1: Load both CSV files
target_flights_df = pd.read_csv("data_files/PRMI-DM_TARGET_FLIGHTS_test.csv")
pnr_df = pd.read_csv("data_files/PRMI_DM_ALL_PNRs.csv")

# Step 2: Filter PNRs with matching DEP_KEY in both datasets
# Extract the DEP_KEYs from the target flights
target_dep_keys = target_flights_df['DEP_KEY'].unique()

# Filter PNRs where DEP_KEY matches
matching_pnr_df = pnr_df[pnr_df['DEP_KEY'].isin(target_dep_keys)]

# Step 3: Create a list of PNR objects from the filtered PNR DataFrame
pnr_list = []
for _, row in matching_pnr_df.iterrows():
    pnr = PNR(
        recloc=row['RECLOC'],
        creation_dtz=row['CREATION_DTZ'],
        cabin_cd=row['CABIN_CD'],
        cos_cd=row['COS_CD'],
        oper_od_orig_cd=row['OPER_OD_ORIG_CD'],
        oper_od_dest_cd=row['OPER_OD_DEST_CD'],
        dep_key=row['DEP_KEY'],
        dep_dt=row['DEP_DT'],
        orig_cd=row['ORIG_CD'],
        dest_cd=row['DEST_CD'],
        flt_num=row['FLT_NUM'],
        dep_dtml=row['DEP_DTML'],
        arr_dtml=row['ARR_DTML'],
        dep_dtmz=row['DEP_DTMZ'],
        arr_dtmz=row['ARR_DTMZ'],
        od_broken_ind=row['OD_BROKEN_IND'],
        pax_cnt=row['PAX_CNT'],
        cvm=row['CVM'],
        conn_time_mins=row['CONN_TIME_MINS']
    )
    pnr_list.append(pnr)

# Now `pnr_list` contains all the PNR objects matching the DEP_KEY
# You can print or further process the list
print(len(pnr_list))

# for i in pnr_list:
#     print(i)    
#     print("\n")


# Step 4: Create a list of cancelled PNRs
cancelled_pnr_list = []
for pnr in pnr_list:
    if pnr.dep_key in flight_graph.cancelled_flights:
        cancelled_pnr_list.append(pnr)

# Now `cancelled_pnr_list` contains all the PNR objects with cancelled flights
