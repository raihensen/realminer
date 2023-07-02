
WINDOW_TITLE = "RealMiner"

PREFERENCES_FILE = "preferences.json"

DEFAULT_PREFERENCES = {
    "theme": "darkly",
    "recent_files": [],
    "show_demo_popups": True,
    "maximized": False
}

WELCOME_SCREEN_THEME = "litera"

TAB_EXPLANATION_FILTERS_SETTINGS = """By importing your event log, you have already done the first step. Let these notifications guide you through the discovery of your process.\n
If you do not need any instruction, you can disable them in the welcome screen.\n
You are currently in the 'Filter and Settings' tab. In this tab, you can filter your event log by object types and activities.
You can decide what is important for you. If you are not so sure about your log for now, you can also see it in this tab in the displayed table.
For a more graphical overview you can open the 'Variants' Tab next."""

TAB_EXPLANATION_VARIANTS = """In this tab, you can see different executions of your process. All variants of executions are listed on the left by their frequency.
By selecting them, you can see them in a graphical representation.
Once you have discovered different executions of your process, you might also be interested in the whole process.
Please click the 'Petri Net' tab to discover a model of your whole process."""

TAB_EXPLANATION_PETRI_NET = """In this tab, you can see the process model for your process. It consists of all activities of your process and is able to replay every trace.
With this, you should already have a good overview of your process. It is now time to dive deeper in the analysis of your process in the 'Heatmap' tab."""

TAB_EXPLANATION_HEATMAP = """In this tab, you can see several heatmaps visualising the relation between object types and between object types and activities.\n
On the left, you can select between three different heatmaps. The purpose of every heatmap is explained in the tab. Just select one heatmap to start with an explore all of them step by step."""

HEAT_MAP_EXPLANATION = """Below, you can select between different types of heatmaps. Those heatmaps can help you detect potential bottle necks in your process! 
Please read carefully the descriptions of each of the heatmaps."""

POOLING_TIME_DESCRIPTION = """The term "Pooling time" refers to the duration it takes to gather all objects of a specific type for a particular activity in a process flow.
It is calculated as the time difference between the first readiness of an object of that type and the last object of the same type which is ready for that activity.
Higher pooling time indicates a longer waiting period to gather the required objects, suggesting areas for process flow improvement. 
Analyzing and minimizing pooling time can enhance overall performance.
"""

LAGGING_TIME_DESCRIPTION = """The term "Lagging time" refers to the duration it takes from the moment *any* object is ready to perform the activity,
until the *last* object from the specified object type is ready as well to perform a particular activity in a process flow.
Higher lagging time indicates a longer waiting period due to the specific object type delaying an earlier execution of the activity, suggesting areas for process flow improvement. 
Analyzing and minimizing lagging time can enhance overall performance.
"""

OBJECT_INTERACTIONS_DESCRIPTION = """This view can give you a quick overview of the relationships between the different object in your process.
It shows for every pair of object types the number of shared events.
Higher activity counts means that those object intersect with each other much more during the process, and focusing on improving those interaction will result in the best performance increase overall.
Quick tip: If you hover over the map, you can also see a list of the corresponding activities and the count.
"""

