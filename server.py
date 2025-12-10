from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import ChartModule
from mesa.visualization.UserParam import UserSettableParameter
from misinformation_model import MisinformationModel

def agent_portrayal(agent):
    portrayal = {
        "Shape": "circle",
        "Filled": True,
        "r": 0.8,
        "Layer": 0,
        "text": "",
        "text_color": "white"
    }
    
    # Set color and shape based on agent type and belief
    if agent.agent_type == "fact_checker":
        portrayal["Shape"] = "rect"
        portrayal["Color"] = "blue"
        portrayal["text"] = "FC"
    elif agent.agent_type == "influencer":
        portrayal["Shape"] = "triangle"
        portrayal["Color"] = "purple"
        portrayal["text"] = "INF"
        # Make size proportional to influence count
        portrayal["r"] = 0.8 + (agent.influence_count * 0.1)
    elif agent.agent_type == "echo_chamber":
        portrayal["Shape"] = "circle"
        # Color intensity based on belief strength
        if agent.believes_misinformation:
            intensity = int(255 * agent.belief_strength)
            portrayal["Color"] = f"rgb({intensity}, 0, 0)"  # Red intensity
        else:
            intensity = int(255 * agent.belief_strength)
            portrayal["Color"] = f"rgb(0, {intensity}, 0)"  # Green intensity
        portrayal["text"] = "EC"
        # Make size proportional to belief strength
        portrayal["r"] = 0.8 + (agent.belief_strength * 0.4)
    elif agent.agent_type == "political":
        portrayal["Shape"] = "diamond"
        if agent.political_side == "left":
            portrayal["Color"] = "blue"
            portrayal["text"] = "L"
        elif agent.political_side == "right":
            portrayal["Color"] = "red"
            portrayal["text"] = "R"
        else:  # neutral
            portrayal["Color"] = "purple"
            portrayal["text"] = "N"
        # Make size proportional to influence strength
        portrayal["r"] = 0.8 + (agent.influence_strength * 0.4)
    else:
        portrayal["Shape"] = "circle"
        portrayal["Color"] = "red" if agent.believes_misinformation else "green"
        portrayal["text"] = "M" if agent.believes_misinformation else "I"
    return portrayal

# Create grid visualization with larger size
grid = CanvasGrid(agent_portrayal, 10, 10, 600, 600)

# Create charts for tracking different metrics
belief_chart = ChartModule(
    [
        {"Label": "Informed", "Color": "green"},
        {"Label": "Misinformed", "Color": "red"},
    ]
)

agent_type_chart = ChartModule(
    [
        {"Label": "Fact_Checkers", "Color": "blue"},
        {"Label": "Influencers", "Color": "purple"},
        {"Label": "Echo_Chambers", "Color": "orange"},
        {"Label": "Normal_Agents", "Color": "gray"},
        {"Label": "Political_Total", "Color": "red"},
        {"Label": "Left_Leaning", "Color": "blue"},
        {"Label": "Right_Leaning", "Color": "red"},
        {"Label": "Neutral", "Color": "purple"},
    ]
)

influence_chart = ChartModule(
    [
        {"Label": "Total_Influence", "Color": "purple"},
        {"Label": "Average_Critical_Thinking", "Color": "blue"},
    ]
)

# Model parameters
model_params = {
    "width": 10,
    "height": 10,
    "num_agents": UserSettableParameter("slider", "Number of Agents", 100, 10, 200, 10),
    "num_influencers": UserSettableParameter("slider", "Number of Influencers", 10, 1, 50, 1),
    "scenario": UserSettableParameter(
        "choice",
        "Scenario",
        value="natural",
        choices=["natural", "influencers", "echo_chamber"]
    ),
}

# Create and launch server
server = ModularServer(
    MisinformationModel,
    [grid, belief_chart, agent_type_chart, influence_chart],
    "Social Media Misinformation Model",
    model_params
)

server.port = 8521
server.launch()
