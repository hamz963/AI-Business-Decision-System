export interface Organization {
  id: string;
  name: string;
  slug: string;
}

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: 'admin' | 'executive' | 'analyst' | 'viewer';
  org_id: string;
  organization?: Organization;
}

export interface Dataset {
  id: string;
  org_id: string;
  name: string;
  description?: string;
  source_type: string;
  table_name: string;
  row_count: number;
  column_count: number;
  quality_score: number;
  quality_report?: {
    overall_score: number;
    status: string;
    columns: Array<{
      name: string;
      inferred_type: string;
      null_count: number;
      null_percentage: number;
      unique_count: number;
      sample_values: any[];
    }>;
    quality_metrics: Array<{
      dimension: string;
      score: number;
      details: string;
    }>;
    issues: string[];
    warnings: string[];
  };
  created_at: string;
}

export interface ExecutiveDashboardData {
  dataset_name: string;
  dataset_id?: string;
  metrics: {
    revenue: number;
    cogs: number;
    gross_profit: number;
    gross_margin_pct: number;
    operating_expenses: number;
    net_profit: number;
    net_margin_pct: number;
    orders: number;
    customers: number;
    average_order_value: number;
  };
  category_breakdown: Array<{
    category: string;
    revenue: number;
    volume: number;
    share_pct: number;
  }>;
  monthly_trend: Array<{
    month: string;
    revenue: number;
    cost: number;
    profit: number;
  }>;
  briefing: {
    generated_at: string;
    headline: string;
    summary: string;
    key_drivers: string[];
    forecast_outlook: string;
    critical_risks: string[];
    strategic_recommendations: Array<{
      initiative: string;
      impact: string;
      risk: string;
      timeframe: string;
    }>;
    confidence: string;
    evidence_citations: Array<{ metric: string; value: string }>;
  };
}

export interface ScenarioParams {
  price_change_pct: number;
  marketing_spend_pct: number;
  operating_cost_pct: number;
  headcount_change_pct: number;
  discount_rate_pct: number;
  assumed_elasticity: number;
}

export interface ScenarioResult {
  id?: string;
  name: string;
  parameters: ScenarioParams;
  baseline: {
    revenue: number;
    cogs: number;
    gross_profit: number;
    gross_margin_pct: number;
    operating_expenses: number;
    net_profit: number;
    net_margin_pct: number;
    projected_volume: number;
    break_even_point: number;
  };
  projected: {
    revenue: number;
    cogs: number;
    gross_profit: number;
    gross_margin_pct: number;
    operating_expenses: number;
    net_profit: number;
    net_margin_pct: number;
    projected_volume: number;
    break_even_point: number;
  };
  deltas: {
    revenue_delta: number;
    revenue_delta_pct: number;
    net_profit_delta: number;
    net_profit_delta_pct: number;
    margin_delta_basis_pts: number;
  };
  risk_score: number;
  risk_assessment: {
    level: string;
    factors: string[];
  };
  tradeoff_summary: string;
  recommendation: string;
}

export interface Decision {
  id: string;
  org_id: string;
  title: string;
  category: string;
  description: string;
  rationale: string;
  evidence: Array<{ metric: string; value: string }>;
  assumptions: string[];
  expected_impact: {
    revenue_impact_range: string;
    profit_impact_range: string;
    time_to_value: string;
    operational_effort: string;
  };
  options_matrix: Array<{
    name: string;
    description: string;
    expected_profit: number;
    risk_score: number;
    growth_potential: number;
    feasibility: number;
    net_score: number;
  }>;
  recommended_option: string;
  confidence_score: number;
  risk_level: string;
  status: 'proposed' | 'approved' | 'rejected' | 'implemented';
  review_notes?: string;
  reviewed_at?: string;
}

export interface ModelOption {
  id: string;
  name: string;
  provider: string;
  description: string;
  free_tier: boolean;
  is_active: boolean;
}

export interface AIAnalystResponse {
  query: string;
  intent: string;
  answer: string;
  facts: string[];
  inferences: string[];
  predictions: string[];
  assumptions: string[];
  recommendations: string[];
  evidence: Array<{ source?: string; metric: string; value: string }>;
  confidence: string;
  suggested_actions: string[];
  analyst_mode?: string;
}

export interface ForecastPoint {
  date: string;
  actual?: number;
  predicted: number;
  lower_bound: number;
  upper_bound: number;
}

export interface ForecastResult {
  metric: string;
  model_name: string;
  validation_mape: number;
  validation_rmse: number;
  history: ForecastPoint[];
  forecast: ForecastPoint[];
  summary_growth_pct: number;
  assumptions: string[];
}

export interface AnomalyItem {
  id: string;
  date: string;
  entity: string;
  field: string;
  observed_value: number;
  expected_value: number;
  deviation_z_score: number;
  severity: 'low' | 'medium' | 'high' | 'critical';
  details: string;
}
