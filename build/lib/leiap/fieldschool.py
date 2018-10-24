"""
These functions take care of some admin for the field team
"""


import pandas as _pd
import numpy as _np
import datetime as _datetime


#######################################################################################################################


def assign_chores(csv_file, names, start_col, end_col, start_date, end_date, out_file='chore_schedule.xlsx'):
    """Create equitable schedule of chore duties
    
    Parameters
    ----------
    csv_file : str
        File path to CSV file where names and dates are stored
    names : str
        CSV column with crew member names
    start_col, end_col : str
        CSV columns with crew member start dates and end dates, respectively
    start_date, end_date : str
        First and last days, respectively, when chores are needed
    out_file : str
        File path or name for the output Excel
    
    Returns
    -------
    crew_dates : pandas DataFrame
        DataFrame containing some info about how jobs were assigned. Useful for deciding if the results are fair. 
        
    Example
    -------
    >> assign_chores('all_students.csv',
                     names='student',
                     start_col='arrive', end_col='depart',
                     start_date='2017-06-27', end_date='2017-07-25')
    """
    
    # read in CSV file
    crew_dates = _pd.read_csv(csv_file)

    # convert date columns to date type
    crew_dates[start_col] = _pd.to_datetime(crew_dates[start_col])
    crew_dates[end_col] = _pd.to_datetime(crew_dates[end_col])
    
    crew_dates['workdays'] = 0
    crew_dates.set_index(names, inplace=True)

    workdays = []  # list to store all the days when chores are required

    # function to loop through days
    def daterange(start, end):
        for n in range(int((end - start).days)+1):
            yield start + _datetime.timedelta(n)

    # make program start and end dates into pandas Timestamps
    start_date = _pd.Timestamp(start_date)    
    end_date = _pd.Timestamp(end_date)

    for single_day in daterange(start_date, end_date):  # loop through days
        if single_day.dayofweek in [6, 0, 1, 2, 3]:  # if it is a workday
            workdays.append(single_day)  # add it to the list
            # find all present on that day
            crew_present = crew_dates[(crew_dates[start_col] < single_day) & (crew_dates[end_col] > single_day)]
            for person in crew_present.index:
                crew_dates.loc[person, 'workdays'] = crew_dates.loc[person, 'workdays']+1  # +1 to their workday count

    total_person_days = crew_dates['workdays'].sum()
    total_workdays = len(workdays)
    total_jobs = total_workdays * 6  # total number of chore slots to be filled

    # calculate each person's fraction of person days
    #     multiply this fraction by total jobs and round up for max jobs
    #     calculate estimated breakfasts (max jobs x 0.33), lunches (max jobs x 0.33), and dinners (max jobs x 0.33)
    #     initialize counts for each type of job

    crew_dates['day_fraction'] = crew_dates['workdays'] / total_person_days
    crew_dates['max_jobs'] = _np.ceil(crew_dates['day_fraction'] * total_jobs)
    crew_dates['breakfast_ct'] = 0
    crew_dates['breakfast_max'] = crew_dates['max_jobs'] * (1/3)
    crew_dates['lunch_ct'] = 0
    crew_dates['lunch_max'] = crew_dates['max_jobs'] * (1/3)
    crew_dates['dinner_ct'] = 0
    crew_dates['dinner_max'] = crew_dates['max_jobs'] * (1/3)

    # create dataframe with jobs as index
    job_list = ['breakfast1', 'breakfast2', 
                'lunch1', 'lunch2',
                'dinner1', 'dinner2']
    chores = _pd.DataFrame(index=job_list)

    # go day by day
    # find subset of people who are present that day
    # for each meal
    #     1. find out who has not reached their quota for that job type yet
    #     2. while number of assigned people is less than 2, 
    #            find those with the lowest job counts among those people
    #     3. randomly select from those people
    #     4. assign them to meal that day
    #     5. remove them from the possible selections for that day
    #     6. [repeat]

    for day in workdays:
        present_df = crew_dates[(crew_dates[start_col] <= day) & (crew_dates[end_col] >= day)]
        if len(present_df.index) < len(job_list):
            print("Failed! Not enough people present on "+str(day))
        day_list = []

        bf_count = 0
        while bf_count < 2:
            bf_df = present_df[(present_df['breakfast_ct'] < present_df['breakfast_max'])]
            min_ct = bf_df['breakfast_ct'].min()
            pick_df = bf_df[bf_df['breakfast_ct'] == min_ct]
            row = pick_df.sample(n=1, replace=True)
            person = row.index[0]
            if person not in day_list:
                day_list.append(person)
                crew_dates.loc[person, 'breakfast_ct'] += 1
                present_df.drop(person, inplace=True)
                bf_count += 1

        lun_count = 0
        while lun_count < 2:
            lun_df = present_df[(present_df['lunch_ct'] < present_df['lunch_max'])]
            min_ct = lun_df['lunch_ct'].min()
            pick_df = lun_df[lun_df['lunch_ct'] == min_ct]
            row = pick_df.sample(n=1, replace=True)
            person = row.index[0]
            if person not in day_list:
                day_list.append(person)
                crew_dates.loc[person, 'lunch_ct'] += 1
                present_df.drop(person, inplace=True)
                lun_count += 1

        din_count = 0
        while din_count < 2:
            din_df = present_df[(present_df['dinner_ct'] < present_df['dinner_max'])]
            min_ct = din_df['dinner_ct'].min()
            pick_df = din_df[din_df['dinner_ct'] == min_ct]
            row = pick_df.sample(n=1, replace=True)
            person = row.index[0]
            if person not in day_list:
                day_list.append(person)
                crew_dates.loc[person, 'dinner_ct'] += 1
                present_df.drop(person, inplace=True)
                din_count += 1

        roster = _pd.Series(day_list)  # convert list to pandas Series
        chores[day.date()] = roster.values  # add column to chores dataframe

    chores = chores.T  # get dates as rows, jobs as columns
    
    # save to Excel
    chores_writer = _pd.ExcelWriter(out_file, engine='xlsxwriter')
    chores.to_excel(chores_writer, sheet_name='chores')            
    chores_writer.save()
    
    # calculate a couple quick stats to evaluate how even the chores are distributed
    # a negative 'max-assigned' value indicates the person has more jobs than expected
    # a positive 'max-assigned' value indicates the person has fewer jobs than expected
    crew_dates['assigned_jobs'] = crew_dates['breakfast_ct']+crew_dates['lunch_ct']+crew_dates['dinner_ct']
    crew_dates['max-assigned'] = crew_dates['max_jobs']-crew_dates['assigned_jobs']
    return crew_dates

#######################################################################################################################
