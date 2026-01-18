from dataclasses import dataclass
from typing import Optional, List
from pydantic import BaseModel, Field


class WaterBreakdown(BaseModel):
    green_water_pct: float = Field(ge=0, le=100)
    blue_water_pct: float = Field(ge=0, le=100)
    grey_water_pct: float = Field(ge=0, le=100)


class RegionalImpact(BaseModel):
    high_stress_regions: List[str] = Field(default_factory=list)
    scarcity_multiplier: float = Field(ge=1.0, le=5.0, default=1.0)
    context: str = ""


class SustainableSwap(BaseModel):
    product_name: str
    water_liters: float = Field(ge=0)
    carbon_kg: float = Field(ge=0, default=0)
    savings_liters: float = Field(ge=0)
    savings_percentage: float = Field(ge=0, le=100)
    reasoning: str


class WaterFootprintAnalysis(BaseModel):
    product_name: str
    product_category: str
    total_liters: float = Field(ge=0)
    carbon_kg: float = Field(ge=0, default=0)
    breakdown: WaterBreakdown
    sustainable_swap: SustainableSwap
    regional_impact: Optional[RegionalImpact] = None
    actionable_steps: List[str] = Field(default_factory=list)
    collective_impact: Optional[str] = None
    confidence_score: float = Field(ge=0, le=1)
    data_source: str = "WFN 2024 + IPCC"
    fun_fact: Optional[str] = None
    
    @property
    def green_water_liters(self):
        return self.total_liters * (self.breakdown.green_water_pct / 100)
    
    @property
    def blue_water_liters(self):
        return self.total_liters * (self.breakdown.blue_water_pct / 100)
    
    @property
    def grey_water_liters(self):
        return self.total_liters * (self.breakdown.grey_water_pct / 100)


@dataclass
class WaterImpactMetrics:
    total_liters: float
    daily_drinking_equivalent: float
    shower_minutes_equivalent: float
    toilet_flushes_equivalent: float
    dishwasher_cycles_equivalent: float
    washing_machine_cycles_equivalent: float
    
    @classmethod
    def from_liters(cls, total_liters, drinking_water_daily=3.0, shower_per_minute=9.5,
                    toilet_flush=6.0, dishwasher_cycle=15.0, washing_machine_cycle=50.0):
        return cls(
            total_liters=total_liters,
            daily_drinking_equivalent=total_liters / drinking_water_daily,
            shower_minutes_equivalent=total_liters / shower_per_minute,
            toilet_flushes_equivalent=total_liters / toilet_flush,
            dishwasher_cycles_equivalent=total_liters / dishwasher_cycle,
            washing_machine_cycles_equivalent=total_liters / washing_machine_cycle
        )
    
    def get_best_comparison(self):
        if self.daily_drinking_equivalent < 30:
            return f"{self.daily_drinking_equivalent:.0f} days", self.daily_drinking_equivalent, "of drinking water"
        elif self.shower_minutes_equivalent < 120:
            return f"{self.shower_minutes_equivalent:.0f} minutes", self.shower_minutes_equivalent, "of shower time"
        elif self.shower_minutes_equivalent < 480:
            hours = self.shower_minutes_equivalent / 60
            return f"{hours:.1f} hours", hours, "of continuous shower"
        else:
            days = self.daily_drinking_equivalent
            if days >= 365:
                years = days / 365
                return f"{years:.1f} years", years, "of drinking water"
            return f"{days:.0f} days", days, "of drinking water"


class AnalysisError(BaseModel):
    error_type: str
    message: str
    user_friendly_message: str
    retry_suggested: bool = True
