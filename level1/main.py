import json
from datetime import timedelta, datetime
from dateutil import easter

with open('data.json', 'r') as f:
    data = json.load(f)
periods = data['periods']
availabilities = []

holidaysItaly = ['01-01', '01-06', '04-25', '05-01', '06-02', '08-15', '11-01', '12-08', '12-25', '12-26']

def daysAvailable(start_date, end_date):
    totaldays = end_date - start_date 
    workdays = 0
    weekend = 0
    holidays = 0

    easter_dates = [easter.easter(year) for year in range(start_date.year, end_date.year + 1)]
    
    easter_monday_dates = [easter_date + timedelta(days=1) for easter_date in easter_dates]

    for single_date in (start_date + timedelta(i) for i in range(totaldays.days + 1)):

        #check weekends
        if(single_date.weekday() == 5 or single_date.weekday() == 6):
            weekend += 1
        else:
            #check holidays
            if(single_date.strftime("%m-%d") in holidaysItaly):                
                holidays += 1
            else:
                #check easter monday (it changes every year)
                if (single_date.weekday() == 0 and single_date.strftime("%m-%d") != "04-25"):
                    if (single_date in easter_monday_dates):
                        holidays += 1
                    else:
                        workdays += 1
                else:
                    #if it isn't either holiday or weekend, it's a work day
                    workdays += 1  

    return totaldays, workdays, weekend, holidays                        
   
for period in periods:   
    availability = {}

    start_date = datetime.strptime(period['since'], "%Y-%m-%d").date()
    end_date = datetime.strptime(period['until'], "%Y-%m-%d").date()
    if end_date < start_date:
        raise ValueError("End date of the period can't be prior to the start date of the period")


    totaldays, workdays, weekend, holidays = daysAvailable(start_date, end_date)

    availability["total_days"] = totaldays.days +1 #+1 in order to considerate also the end date
    availability["period_id"] = period["id"]  
    availability["workdays"] = workdays
    availability["weekend_days"] = weekend
    availability["holidays"] = holidays
    availabilities.append(availability)
    

with open("output.json", "w") as json_file:
    json.dump({"availabilities": availabilities}, json_file, indent=4)

