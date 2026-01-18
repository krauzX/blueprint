from datetime import datetime, timedelta
from typing import List
from collections import defaultdict


class TrendAnalyzer:
    def __init__(self, history: List):
        self.history = history
    
    def get_weekly_summary(self):
        if not self.history:
            return None
        
        total_water = sum(a.total_liters for a in self.history)
        total_carbon = sum(getattr(a, 'carbon_kg', 0) for a in self.history)
        
        categories = defaultdict(int)
        for analysis in self.history:
            categories[analysis.product_category] += 1
        
        top_category = max(categories.items(), key=lambda x: x[1])[0] if categories else "None"
        
        avg_water = total_water / len(self.history)
        avg_carbon = total_carbon / len(self.history)
        
        potential_savings = sum(a.sustainable_swap.savings_liters for a in self.history)
        carbon_savings = sum(getattr(a.sustainable_swap, 'carbon_kg', 0) for a in self.history 
                           if getattr(a, 'carbon_kg', 0) > 0)
        
        return {
            'total_items': len(self.history),
            'total_water': total_water,
            'total_carbon': total_carbon,
            'avg_water_per_item': avg_water,
            'avg_carbon_per_item': avg_carbon,
            'top_category': top_category,
            'potential_savings_water': potential_savings,
            'potential_savings_carbon': carbon_savings,
            'category_breakdown': dict(categories)
        }
    
    def detect_patterns(self):
        if len(self.history) < 3:
            return []
        
        patterns = []
        
        categories = [a.product_category for a in self.history]
        if categories.count(categories[-1]) >= 3:
            patterns.append(f"You scan a lot of {categories[-1]} items - consider bulk alternatives to reduce impact")
        
        high_water_items = [a for a in self.history if a.total_liters > 5000]
        if len(high_water_items) >= 2:
            patterns.append(f"You've scanned {len(high_water_items)} high-water items - small swaps = huge impact")
        
        avg_confidence = sum(a.confidence_score for a in self.history) / len(self.history)
        if avg_confidence < 0.6:
            patterns.append("Tip: Better lighting & closer photos = more accurate analysis")
        
        return patterns
    
    def get_milestone_progress(self, total_water: float):
        milestones = [
            (10000, "🌱 Beginner", "First 10K liters tracked"),
            (50000, "💧 Conscious", "50K liters analyzed"),
            (100000, "🌊 Expert", "100K+ liters tracked"),
            (500000, "🌍 Champion", "Half million liters!")
        ]
        
        for threshold, title, desc in reversed(milestones):
            if total_water >= threshold:
                next_idx = milestones.index((threshold, title, desc)) + 1
                if next_idx < len(milestones):
                    next_milestone, next_title, next_desc = milestones[next_idx]
                    remaining = next_milestone - total_water
                    return {
                        'current': title,
                        'current_desc': desc,
                        'next': next_title,
                        'next_desc': next_desc,
                        'remaining': remaining,
                        'progress_pct': (total_water / next_milestone) * 100
                    }
                return {'current': title, 'current_desc': desc, 'next': None}
        
        return {
            'current': '🌱 Starter',
            'current_desc': 'Just getting started',
            'next': 'Beginner',
            'next_desc': 'First 10K liters tracked',
            'remaining': 10000 - total_water,
            'progress_pct': (total_water / 10000) * 100
        }


class ChallengeEngine:
    @staticmethod
    def generate_weekly_challenge(history):
        if not history:
            return {
                'title': '🎯 First Scan Challenge',
                'description': 'Scan 5 products this week to understand your impact',
                'target': 5,
                'current': 0,
                'reward': 'Unlock trend analysis'
            }
        
        stats = TrendAnalyzer(history).get_weekly_summary()
        
        if stats['top_category'] == 'Food':
            return {
                'title': '🥗 Plant-Based Week',
                'description': 'Try 3 plant-based alternatives this week',
                'target': 3,
                'current': 0,
                'reward': f"Save ~45,000L water",
                'tip': 'Beef → Chicken/Lentils saves 70% water'
            }
        elif stats['top_category'] == 'Textiles':
            return {
                'title': '♻️ Secondhand Hero',
                'description': 'Buy 2 secondhand items instead of new',
                'target': 2,
                'current': 0,
                'reward': 'Save ~16,000L water + 40kg CO2',
                'tip': 'Thrifting = 82% less water footprint'
            }
        else:
            savings_potential = stats['potential_savings_water']
            return {
                'title': '💚 Swap & Save',
                'description': 'Make 1 sustainable swap this week',
                'target': 1,
                'current': 0,
                'reward': f'Save {savings_potential:,.0f}L water potential',
                'tip': 'Check your History for easy wins'
            }
