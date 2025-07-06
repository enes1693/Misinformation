# misinformation_model.py

from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from agent import UserAgent

class MisinformationModel(Model):
    def __init__(self, width=10, height=10, num_agents=100, num_influencers=10, scenario="natural"):
        self.num_agents = num_agents
        self.num_influencers = num_influencers
        self.grid = MultiGrid(width, height, torus=True)
        self.schedule = RandomActivation(self)
        self.running = True
        self.scenario = scenario
        self.step_count = 0

        # Create agents based on scenario
        if scenario == "natural":
            self.create_natural_spread_agents()
        elif scenario == "fact_checkers":
            self.create_fact_checker_agents()
        elif scenario == "influencers":
            self.create_influencer_agents()
        elif scenario == "echo_chamber":
            self.create_echo_chamber_agents()
        elif scenario == "political":
            self.create_political_agents()

        # Set up data collection
        self.datacollector = DataCollector(
            model_reporters={
                "Informed": lambda m: sum(1 for a in m.schedule.agents if not a.believes_misinformation),
                "Misinformed": lambda m: sum(1 for a in m.schedule.agents if a.believes_misinformation),
                "Fact_Checkers": lambda m: sum(1 for a in m.schedule.agents if a.agent_type == "fact_checker"),
                "Influencers": lambda m: sum(1 for a in m.schedule.agents if a.agent_type == "influencer"),
                "Echo_Chambers": lambda m: sum(1 for a in m.schedule.agents if a.agent_type == "echo_chamber"),
                "Normal_Agents": lambda m: sum(1 for a in m.schedule.agents if a.agent_type == "normal"),
                "Total_Influence": lambda m: sum(a.influence_count for a in m.schedule.agents if a.agent_type == "influencer"),
                "Average_Critical_Thinking": lambda m: sum(a.critical_thinking for a in m.schedule.agents) / len(m.schedule.agents),
                "Left_Leaning": lambda m: sum(1 for a in m.schedule.agents if a.agent_type == "political" and a.political_side == "left"),
                "Right_Leaning": lambda m: sum(1 for a in m.schedule.agents if a.agent_type == "political" and a.political_side == "right"),
                "Neutral": lambda m: sum(1 for a in m.schedule.agents if a.agent_type == "political" and a.political_side == "neutral"),
                "Political_Total": lambda m: sum(1 for a in m.schedule.agents if a.agent_type == "political")
            }
        )

    def create_natural_spread_agents(self):
        """Create agents for natural spread scenario"""
        for i in range(self.num_agents):
            critical_thinking = self.random.random()
            misinformation = self.random.random() < 0.2  # 20% initial misinformation
            agent = UserAgent(i, self, "normal", critical_thinking, misinformation)
            self.schedule.add(agent)
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(agent, (x, y))

    def create_fact_checker_agents(self):
        """Create agents for fact checker scenario"""
        # Calculate number of fact checkers (20% of total agents)
        num_fact_checkers = max(1, int(self.num_agents * 0.20))
        num_normal_agents = self.num_agents - num_fact_checkers

        print(f"Creating {num_fact_checkers} fact checkers and {num_normal_agents} normal agents")  # Debug print

        # Create normal agents with higher initial misinformation
        for i in range(num_normal_agents):
            critical_thinking = self.random.random() * 0.4  # Lower critical thinking
            misinformation = self.random.random() < 0.5  # 50% initial misinformation
            agent = UserAgent(i, self, "normal", critical_thinking, misinformation)
            self.schedule.add(agent)
            # Place normal agents randomly
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(agent, (x, y))
        
        # Add fact checkers with strategic placement
        for i in range(num_normal_agents, self.num_agents):
            # Create fact checker agent
            agent = UserAgent(i, self, "fact_checker")
            self.schedule.add(agent)
            
            # Place fact checkers in a grid pattern
            fact_checker_index = i - num_normal_agents
            
            # Calculate position in a grid pattern
            if fact_checker_index < num_fact_checkers // 2:
                # First half of fact checkers in the center area
                center_x = self.grid.width // 2
                center_y = self.grid.height // 2
                offset = fact_checker_index % 3
                x = center_x + offset - 1
                y = center_y + (fact_checker_index // 3)
            else:
                # Second half of fact checkers in the corners
                corner = (fact_checker_index - (num_fact_checkers // 2)) % 4
                if corner == 0:  # Top-left
                    x, y = 1, 1
                elif corner == 1:  # Top-right
                    x, y = self.grid.width - 2, 1
                elif corner == 2:  # Bottom-left
                    x, y = 1, self.grid.height - 2
                else:  # Bottom-right
                    x, y = self.grid.width - 2, self.grid.height - 2
            
            # Ensure coordinates are within grid bounds
            x = max(0, min(self.grid.width - 1, x))
            y = max(0, min(self.grid.height - 1, y))
            
            # Place the agent
            self.grid.place_agent(agent, (x, y))
            print(f"Placed fact checker {i} at position ({x}, {y})")  # Debug print

    def create_influencer_agents(self):
        """Create agents for influencer scenario"""
        # Use the specified number of influencers
        num_influencers = min(self.num_influencers, self.num_agents - 1)  # Ensure at least one normal agent
        num_normal_agents = self.num_agents - num_influencers

        # Create normal agents
        for i in range(num_normal_agents):
            critical_thinking = self.random.random()
            misinformation = self.random.random() < 0.2
            agent = UserAgent(i, self, "normal", critical_thinking, misinformation)
            self.schedule.add(agent)
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(agent, (x, y))
        
        # Add influencers with strategic placement
        for i in range(num_normal_agents, self.num_agents):
            # Alternate between misinformed and informed influencers
            misinformation = (i % 2 == 0)
            agent = UserAgent(i, self, "influencer", misinformation=misinformation)
            self.schedule.add(agent)
            
            # Place influencers in a strategic pattern
            if i < num_normal_agents + num_influencers // 2:
                # First half of influencers in the center
                center_x = self.grid.width // 2
                center_y = self.grid.height // 2
                offset = (i - num_normal_agents) % 3
                x = max(0, min(self.grid.width - 1, center_x + offset - 1))
                y = max(0, min(self.grid.height - 1, center_y + (i - num_normal_agents) // 3))
            else:
                # Second half of influencers in the corners
                corner = (i - (num_normal_agents + num_influencers // 2)) % 4
                if corner == 0:  # Top-left
                    x, y = 1, 1
                elif corner == 1:  # Top-right
                    x, y = self.grid.width - 2, 1
                elif corner == 2:  # Bottom-left
                    x, y = 1, self.grid.height - 2
                else:  # Bottom-right
                    x, y = self.grid.width - 2, self.grid.height - 2
            
            # Ensure coordinates are within grid bounds
            x = max(0, min(self.grid.width - 1, x))
            y = max(0, min(self.grid.height - 1, y))
            
            self.grid.place_agent(agent, (x, y))

    def create_echo_chamber_agents(self):
        """Create agents for echo chamber scenario"""
        # Create 4 distinct clusters
        cluster_size = self.num_agents // 4
        
        for cluster in range(4):
            # Determine cluster center and belief
            if cluster < 2:  
                misinformation = True
            else:  
                misinformation = False
                
            # Calculate cluster center
            if cluster % 2 == 0:  # Left clusters
                center_x = self.grid.width // 4
            else:  # Right clusters
                center_x = 3 * self.grid.width // 4
                
            if cluster < 2:  # Top clusters
                center_y = self.grid.height // 4
            else:  # Bottom clusters
                center_y = 3 * self.grid.height // 4
            
            # Create agents for this cluster
            for i in range(cluster_size):
                agent_id = cluster * cluster_size + i
                if agent_id >= self.num_agents:
                    break
                    
                critical_thinking = self.random.random() * 0.3  # Lower critical thinking
                agent = UserAgent(agent_id, self, "echo_chamber", critical_thinking, misinformation)
                
                # Place agents near cluster center with some randomness
                x = max(0, min(self.grid.width - 1, center_x + self.random.randint(-2, 2)))
                y = max(0, min(self.grid.height - 1, center_y + self.random.randint(-2, 2)))
                
                # Add agent to schedule and grid
                self.schedule.add(agent)
                self.grid.place_agent(agent, (x, y))
                
                # Initialize cluster center after placement
                agent.cluster_center = (center_x, center_y)

   
    def step(self):
        """Execute one step of the simulation"""
        self.step_count += 1
        self.datacollector.collect(self)
        self.schedule.step()
        
        # Check if simulation should continue
        if self.scenario == "fact_checkers":
            # Count remaining misinformed agents
            misinformed_count = sum(1 for a in self.schedule.agents if a.believes_misinformation)
            fact_checker_count = sum(1 for a in self.schedule.agents if a.agent_type == "fact_checker")
            print(f"Step {self.step_count}: Misinformed agents: {misinformed_count}, Fact checkers: {fact_checker_count}")
            
            if misinformed_count == 0:
                self.running = False
            # Add debug print
            print(f"Step {self.step_count}: Misinformed agents: {misinformed_count}")
