import json
from datetime import timedelta, datetime
from dateutil import easter

#for every developer calculate how many days are available in each period.

with open('data.json', 'r') as f:
    data = json.load(f)
developers = data['developers']
periods = data['periods']
localholidays = data['local_holidays']
availabilities = []

holidaysItaly = ['01-01', '01-06', '04-25', '05-01', '06-02', '08-15', '11-01', '12-08', '12-25', '12-26']
for localholiday in localholidays:
    holiday_date = datetime.strptime(localholiday['day'], "%Y-%m-%d").date()
    holidaysItaly.append(holiday_date.strftime("%m-%d"))

def daysAvailable(start_date, end_date, birthday):
    totaldays = end_date - start_date 
    workdays = 0
    weekend = 0
    holidays = 0

    easter_dates = [easter.easter(year) for year in range(start_date.year, end_date.year + 1)]
    
    easter_monday_dates = [easter_date + timedelta(days=1) for easter_date in easter_dates]

    years = [x for x in range (start_date.year, end_date.year + 1)]    

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

    for i in years:
        birthday = birthday.replace(year=i)
        if start_date <= birthday <= end_date and birthday.weekday() != 5 and birthday.weekday() != 6:
            workdays -= 1
            holidays +=1

    return totaldays, workdays, weekend, holidays   

def main():
    for period in periods:
        start_date = datetime.strptime(period['since'], "%Y-%m-%d").date()
        end_date = datetime.strptime(period['until'], "%Y-%m-%d").date() 
        if end_date < start_date:
            raise ValueError("End date of the period can't be prior to the start date of the period")
        for developer in developers:
            availability = {}
            birthday = datetime.strptime(developer['birthday'], "%Y-%m-%d").date()
            totaldays, workdays, weekend, holidays = daysAvailable(start_date, end_date, birthday)
            availability["developer_id"] = developer["id"]
            availability["period_id"] = period["id"]  
            availability["total_days"] = totaldays.days +1
            availability["workdays"] = workdays
            availability["weekend_days"] = weekend
            availability["holidays"] = holidays
            availabilities.append(availability)


    with open("output.json", "w") as json_file:
        json.dump({"availabilities": availabilities}, json_file, indent=4)
    #output datas are not exactly as the original output.json file 

if __name__ == "__main__":
    main()