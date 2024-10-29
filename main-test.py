import pandas as pd
from graph import Graph
from flight import Flight
from airport import Airport
from pnr import PNR
from datetime import datetime
import numpy as np
from dimod import BinaryQuadraticModel
import dimod


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
target_flights_df = pd.read_csv("data_files/PRMI-DM_TARGET_FLIGHTS.csv")
pnr_df = pd.read_csv("data_files/PRMI_DM_ALL_PNRs.csv")

# Step 2: Filter PNRs with matching DEP_KEY in both datasets
# Extract the DEP_KEYs from the target flights
target_dep_keys = target_flights_df['DEP_KEY'].unique()

# Filter PNRs where DEP_KEY matches
matching_pnr_df = pnr_df[pnr_df['DEP_KEY'].isin(target_dep_keys)]

# Step 3: Create a list of PNR objects from the filtered PNR DataFrame
pnr_list = []
for _, row in matching_pnr_df.iterrows():
    trip_id = f"{row['RECLOC']}_{row['DEP_KEY']}"  # Create unique trip identifier
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
    pnr.trip_id = trip_id  # Assign the trip identifier
    pnr_list.append(pnr)

# Now `pnr_list` contains all the PNR objects matching the DEP_KEY
# You can print or further process the list
print(len(pnr_list))



#=======================================================================================================

# now list of pnr object is the list of passengers that are on the cancelled flights

#=======================================================================================================

# Step 4: Find the available flights in the graph
airport_code = "VUY"
airport = flight_graph.get_airport(airport_code)
available_flights_vuy = [flight for flight in airport.flights_out if flight.status == "available" and flight.dest_cd == "TPH"]

#=======================================================================================================
#=======================================================================================================
#QUBO formulation
#=======================================================================================================
#=======================================================================================================

# # Building the QUBO formulation for the problem 

# # Initialize a dictionary to store binary variables
# # The keys are tuples (passenger_id, flight_id), values will be 0 or 1 to represent the binary state


# # Step 1: Initiate binary variables for each passenger-flight pair
# binary_variables = {}

# # Populate binary variables for each passenger-flight pair
# for passenger in pnr_list:
#     for flight in available_flights_vuy:
#         # Create a binary variable key for this passenger-flight pair
#         binary_variables[(passenger.trip_id, flight.dep_key)] = 0  # Initial state, will later be optimized


# # Step 2 : Objective function

# # Initialize the QUBO dictionary to store penalties for each passenger-flight assignment
# qubo_objective = {}

# # Populate QUBO objective based on time difference
# for passenger in pnr_list:
#     for flight in available_flights_vuy:
#         # Calculate time difference in minutes
#         original_time = datetime.strptime(passenger.dep_dtmz, "%Y-%m-%dT%H:%M:%SZ")
#         new_time = datetime.strptime(flight.dep_dtmz, "%Y-%m-%dT%H:%M:%SZ")
#         time_difference = abs((new_time - original_time).total_seconds() / 60.0)  # in minutes

#         # Set up the QUBO penalty based on time difference
#         qubo_objective[(passenger.trip_id, flight.dep_key)] = time_difference


# #Step 3: Constraints

# # Penalty strength for constraints
# penalty_strength = 1000

# # Initialize QUBO dictionary for the constraints
# qubo_constraints = {}

# # Constraint 1: Each passenger is assigned to exactly one flight
# for passenger in pnr_list:
#     for flight1 in available_flights_vuy:
#         for flight2 in available_flights_vuy:
#             if flight1 != flight2:
#                 # Adding penalties if the same passenger is assigned to multiple flights
#                 key = ((passenger.trip_id, flight1.dep_key), (passenger.trip_id, flight2.dep_key))
#                 qubo_constraints[key] = penalty_strength

# # Constraint 2: Seat availability on each flight
# for flight in available_flights_vuy:
#     assigned_passengers = [passenger for passenger in pnr_list if passenger.dep_key == flight.dep_key]
#     if len(assigned_passengers) > int(flight.c_avail_cnt):
#         for passenger1 in assigned_passengers:
#             for passenger2 in assigned_passengers:
#                 if passenger1 != passenger2:
#                     key = ((passenger1.trip_id, flight.dep_key), (passenger2.trip_id, flight.dep_key))
#                     qubo_constraints[key] = penalty_strength


# #Step 4: Combine the objective and constraints to create the final QUBO dictionary

# # Combine objective and constraints into a QUBO
# bqm = BinaryQuadraticModel('BINARY')

# # Add the objective terms to the QUBO
# for (passenger_flight, time_penalty) in qubo_objective.items():
#     bqm.add_variable(passenger_flight, time_penalty)

# # Add the constraint penalties to the QUBO
# for (pair1, pair2), penalty in qubo_constraints.items():
#     bqm.add_interaction(pair1, pair2, penalty)

# # The QUBO is now ready to be solved



#=======================================================================================================



# Assume pnr_list and available_flights_vuy are already populated

#=======================================================================================================
# QUBO formulation using dimod
#=======================================================================================================

# Step 1: Initialize a binary quadratic model (BQM)
bqm = dimod.BinaryQuadraticModel({}, {}, 0.0, dimod.BINARY)

pnr_list = pnr_list[:2]  # Limit the number of passengers for testing 
available_flights_vuy = available_flights_vuy[:10]  # Limit the number of flights for testing
# Step 2: Initiate binary variables for each passenger-flight pair
# Objective function coefficients
for passenger in pnr_list:
    for flight in available_flights_vuy:
        # original_time = datetime.strptime(passenger.dep_dtmz, "%Y-%m-%dT%H:%M:%SZ")
        # new_time = datetime.strptime(flight.dep_dtmz, "%Y-%m-%dT%H:%M:%SZ")
        original_time = datetime.strptime(passenger.dep_dtmz, "%Y-%m-%d %H:%M")  # pnr does not include seconds
        new_time = datetime.strptime(flight.dep_dtmz, "%Y-%m-%d %H:%M:%S")  # flight time does include seconds
        # time_difference = abs((new_time - original_time).total_seconds() / 60.0)  # in minutes
        time_difference = ((new_time - original_time).total_seconds() / 60.0)  # in minutes
        
        # Add a variable for this passenger-flight pair in the BQM
        if time_difference < 0:
            bqm.add_variable((passenger.trip_id, flight.dep_key), 10000)
        else:
            bqm.add_variable((passenger.trip_id, flight.dep_key), -5000+time_difference)

# Step 3: Constraints

# Increase penalty strength for assignment constraint
penalty_strength = 100  # Adjust this based on the scale of time differences

# Constraint 1: Ensure each passenger is assigned to exactly one flight
for passenger in pnr_list:
    for flight1 in available_flights_vuy:
        for flight2 in available_flights_vuy:
            if flight1 != flight2:
                bqm.add_interaction((passenger.trip_id, flight1.dep_key), (passenger.trip_id, flight2.dep_key), penalty_strength)

penalty_strength = 100  # Penalty for constraints

# Constraint 2: Seat availability constraint for each available flight
for flight in available_flights_vuy:
    # List of binary variables for passengers who could be assigned to this flight
    passenger_vars_for_flight = [(passenger.trip_id, flight.dep_key) for passenger in pnr_list]

    # Apply penalty for any pair of passengers assigned to the same flight beyond seat availability
    for i in range(len(passenger_vars_for_flight)):
        for j in range(i + 1, len(passenger_vars_for_flight)):
            passenger_pair = (passenger_vars_for_flight[i], passenger_vars_for_flight[j])
            # Add penalty for exceeding capacity (only if capacity could be exceeded by assigning both passengers)
            if len(passenger_vars_for_flight) > int(flight.c_avail_cnt):
                bqm.add_interaction(passenger_pair[0], passenger_pair[1], penalty_strength)







#=======================================================================================================
# Solve the BQM using a sampler
#=======================================================================================================

# Option 1: Use Simulated Annealing
sampler = dimod.SimulatedAnnealingSampler()
samples = sampler.sample(bqm, num_reads=200)

# # Option 2: Use Exact Solver (for small BQMs)
# sampler = dimod.ExactSolver()
# samples = sampler.sample(bqm)

# Display the best sample
best_sample = samples.first.sample
best_energy = samples.first.energy

# Print the results
print("Best Sample:", best_sample)
print("Energy of Best Sample:", best_energy)

# Step 4: Process the results
# Extract the flight assignments from the best sample
assignments = {}
for key, value in best_sample.items():
    if value == 1:  # Only consider assigned flights
        passenger_id, flight_id = key
        assignments.setdefault(passenger_id, []).append(flight_id)

# Print the assignments
# for passenger_id, flight_ids in assignments.items():
#     print(f"Passenger {passenger_id} assigned to flights: {flight_ids}")
    
# in the output show the passenger details, its orginal time and teh allocated new fight time and the time diffrence 

for passenger_id, flight_ids in assignments.items():
    for i in pnr_list:
        if i.trip_id == passenger_id:
            print(f"Passenger {passenger_id} assigned to flights: {flight_ids}")
            print(f"Original Time: {i.dep_dtmz}")
            for j in available_flights_vuy:
                if j.dep_key == flight_ids[0]:
                    print(f"New Flight Time: {j.dep_dtmz}")
                    print(f"Time Difference: {best_sample[(passenger_id, flight_ids[0])]}")
            print("\n")
