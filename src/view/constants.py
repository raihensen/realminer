
WINDOW_TITLE = "RealMiner"

PREFERENCES_FILE = "preferences.json"

DEFAULT_PREFERENCES = {
    "theme": "darkly",
    "recent_files": [],
    "show_demo_popups": True,
    "maximized": False
}

WELCOME_SCREEN_THEME = "litera"

HEAT_MAP_EXPLENATION = """Below, you can select between different types of heatmaps. Those Heatmaps can help you detect pottential bottle necks in your process! 
Please read carifully the meaning behind each of the heatmaps
"""

POOLING_TIME_DESCRIPTION = """The term "Pooling time" refers to the duration it takes to gather all objects of a specific type for a particular activity in a process flow.
It is calculated as the time difference between the first readiness of an object of that type and the last object of the same type which is ready for that activity.
Higher pooling time indicates a longer waiting period to gather the required objects, suggesting areas for process flow improvement. 
Analyzing and minimizing pooling time can enhance overall performance.
"""

LAGGING_TIME_DESCRIPTION = """The term "Lagging time" refers to the duration it takes to from the moment *any* object is readt to perform the Activity,
untill the *last* object from the specified object type is ready as well to perform a particular activity in a process flow.
Higher Lagging time indicates a longer waiting period due to the specific object type which delays an earlier execution of the activity, suggesting areas for process flow improvement. 
Analyzing and minimizing Lagging time can enhance overall performance.
"""

OBJECT_INTERACTIONS_DESCRIPTION = """This view can give you a quick overview of the relatiotionships between the different object in your process.
It shows for every pair of object types the number of shared events.
Higher activity counts means that those object intersect with each other much more during the process, and focusing on improving those interaction will result in the best performance increase overall.
Quick Tip: If you hover over the map, you can also see a list of the corresponding activities and the count.
"""

