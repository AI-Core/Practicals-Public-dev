from utils.client import Projects

name_to_weekly_duration = {}

for project in Projects():

    print(project.name)
    hourly_duration = sum([t.duration for t in project.tasks])
    weekly_duration = round(hourly_duration / 20, 1)
    print("Total Hourly Duration:", hourly_duration)
    print("Total Weekly Duration @ 20hrs per week:",
          )
    print()
    print()
    project.hourly_duration = hourly_duration
    project.weekly_duration = weekly_duration

    name_to_weekly_duration[project.name] = weekly_duration


def get_total_duration(project_names):
    return round(sum([name_to_weekly_duration[name] for name in project_names]), 1)


base_sequence = ["Hangman", "Computer-Vision", "Data-Collection-Pipeline"]

program_name_to_specialisation_scenario_name = {
    "Data Engineering": "Pinterest-Data-Processing-Pipeline",
    "Data Science": "Modelling-Airbnb-Property-Listings",
    "ML Engineering": "Facebook-Marketplace",
    "Data Analytics": "Data-Analytics-Migration-Tableau"
}

for program_name, scenario_name in program_name_to_specialisation_scenario_name.items():
    print(
        f"{program_name} program duration: {get_total_duration([*base_sequence, scenario_name])} weeks")
    print()
