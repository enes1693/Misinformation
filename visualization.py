import matplotlib.pyplot as plt

class Visualization:
    def __init__(self, model):
        self.model = model
        self.fig, self.ax = plt.subplots(figsize=(10, 8))
        self.scatter = None
        self.colors = {
            'normal': 'blue',
            'fact_checker': 'green',
            'influencer': 'red',
            'echo_chamber': 'purple',
            'political_left': 'darkred',
            'political_right': 'darkblue',
            'political_neutral': 'gray'
        }
        self.legend_elements = [
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='blue', markersize=10, label='Normal'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='green', markersize=10, label='Fact Checker'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='red', markersize=10, label='Influencer'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='purple', markersize=10, label='Echo Chamber'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='darkred', markersize=10, label='Political (Left)'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='darkblue', markersize=10, label='Political (Right)'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='gray', markersize=10, label='Political (Neutral)')
        ]

    def update(self, frame):
        self.model.step()
        
        # Update agent positions and colors
        positions = []
        colors = []
        sizes = []
        
        for agent in self.model.schedule.agents:
            positions.append(agent.pos)
            
            # Determine agent color based on type and state
            if agent.agent_type == "political":
                if agent.political_side == "left":
                    color = self.colors['political_left']
                elif agent.political_side == "right":
                    color = self.colors['political_right']
                else:
                    color = self.colors['political_neutral']
            else:
                color = self.colors[agent.agent_type]
            
            # Make misinformed agents darker
            if agent.believes_misinformation:
                color = self.darken_color(color)
            
            colors.append(color)
            
            # Set size based on agent type
            if agent.agent_type == "fact_checker":
                size = 100
            elif agent.agent_type == "influencer":
                size = 120
            elif agent.agent_type == "political":
                size = 110
            else:
                size = 80
            sizes.append(size)
        
        if self.scatter is None:
            self.scatter = self.ax.scatter(
                [p[0] for p in positions],
                [p[1] for p in positions],
                c=colors,
                s=sizes,
                alpha=0.6
            )
        else:
            self.scatter.set_offsets(positions)
            self.scatter.set_color(colors)
            self.scatter.set_sizes(sizes)
        
        # Update title with current statistics
        misinformed_count = sum(1 for agent in self.model.schedule.agents if agent.believes_misinformation)
        fact_checker_count = sum(1 for agent in self.model.schedule.agents if agent.agent_type == "fact_checker")
        influencer_count = sum(1 for agent in self.model.schedule.agents if agent.agent_type == "influencer")
        echo_chamber_count = sum(1 for agent in self.model.schedule.agents if agent.agent_type == "echo_chamber")
        political_count = sum(1 for agent in self.model.schedule.agents if agent.agent_type == "political")
        
        self.ax.set_title(
            f'Step: {self.model.schedule.steps}\n'
            f'Misinformed: {misinformed_count} | '
            f'Fact Checkers: {fact_checker_count} | '
            f'Influencers: {influencer_count} | '
            f'Echo Chambers: {echo_chamber_count} | '
            f'Political: {political_count}'
        )
        
        return self.scatter, 