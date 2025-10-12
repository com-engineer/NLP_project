import plotly.express as px
import plotly.graph_objects as go

class ResumeVisualizations:
    @staticmethod
    def create_ranking_chart(results):
        fig = px.bar(
            x=[r['file_name'] for r in results[:10]],
            y=[r['similarity_score'] for r in results[:10]],
            title="Top 10 Candidates"
        )
        return fig
    
    @staticmethod
    def create_match_level_pie(results):
        match_counts = {}
        for result in results:
            level = result['match_level']
            match_counts[level] = match_counts.get(level, 0) + 1
        
        fig = px.pie(
            values=list(match_counts.values()),
            names=list(match_counts.keys()),
            title="Match Level Distribution"
        )
        return fig
