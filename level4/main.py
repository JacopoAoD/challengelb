import json
from datetime import timedelta, datetime
from dateutil import easter
import math

with open('data.json', 'r') as f:
    data = json.load(f)
developers = data['developers']
projects = data['projects']
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

    workdays_with_bd = 0

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
                        workdays_with_bd += 1
                else:
                    #if it isn't either holiday or weekend, it's a work day
                    workdays += 1  
                    workdays_with_bd += 1

    for i in years:
        birthday = birthday.replace(year=i)
        if start_date <= birthday <= end_date and birthday.weekday() != 5 and birthday.weekday() != 6:
            workdays_with_bd -= 1
            #holidays +=1 commented because we don't have to save the holidays for every developer in the output file
            #just need the "common" ones

    return totaldays, workdays, workdays_with_bd, weekend, holidays   

def distribute_effort(effort_dev, effort_required):
    #I know the effort days available for the devs and how much it is required.
    effort_for_day = round(effort_required / effort_dev, 2) #effort_for_day is useful to know how much every day the developer should work to the project.
    hours_for_day = effort_for_day * 8 #8 as I suppose that every work day lasts 8 hours
    minutes = int((hours_for_day - int(hours_for_day)) * 60) 
    days = math.ceil(effort_dev / 3 * effort_for_day)
    return days, hours_for_day, minutes

def main():
    for project in projects:
        availability = {}
        total_effort_days = 0
        totaldays = 0
        workdays = 0
        weekend = 0
        holidays = 0        
        start_date = datetime.strptime(project['since'], "%Y-%m-%d").date()
        end_date = datetime.strptime(project['until'], "%Y-%m-%d").date()    
        if end_date < start_date:
            raise ValueError("End date of the period can't be prior to the start date of the period")  

        for developer in developers:
            
            birthday = datetime.strptime(developer['birthday'], "%Y-%m-%d").date()
            totaldays, workdays, workdays_with_bd, weekend, holidays = daysAvailable(start_date, end_date, birthday)
            #added workdays_with_bd --> in the output file i save the "general" workdays in the period,
            #but to calculate the feasibility I need to calculate the actual workdays of every single developer
            #Workdays_with_bd is needed just for calculations, not for output file
            total_effort_days += workdays_with_bd

        availability["period_id"] = project["id"]  
        availability["total_days"] = totaldays.days +1
        availability["workdays"] = workdays
        availability["weekend_days"] = weekend
        availability["holidays"] = holidays    
        availability["feasibility"] = total_effort_days >= project["effort_days"]  
        # ----- Everything prior to this point is part of level 3 -------
        # Now I know the feasibility of every single project. If a project is doable, I want to distribute the effort between developers.
        # With the "distribute_effort" function I calculate:
        #   - how many hour for day every developer should work to that project in order to distribute the effort.
        #   - in how many days is doable the project if every dev works all day to that project
        if availability["feasibility"] == True:         
            days, hours_for_day, minutes = distribute_effort(total_effort_days, project["effort_days"])
            availability["daily_work_for_dev"] = f"{int(hours_for_day):02d} hours: {minutes:02d} minutes"
            availability["doable_in"] = f"{days} days"    

        availabilities.append(availability)  

    with open("output.json", "w") as json_file:
        json.dump({"availabilities": availabilities}, json_file, indent=4)

if __name__ == "__main__":
    main()