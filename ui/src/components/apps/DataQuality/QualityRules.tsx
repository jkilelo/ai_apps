import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../ui/card';
import { Button } from '../../ui/button';
import { Badge } from '../../ui/badge';
import { Switch } from '../../ui/switch';
import { Input } from '../../ui/input';
import { Label } from '../../ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../ui/tabs';
import { Alert, AlertDescription } from '../../ui/alert';
import {
  Shield,
  Play,
  Pause,
  Settings,
  Code,
  AlertTriangle,
  CheckCircle,
  Info,
  Filter,
  Plus,
  Edit,
  Trash,
  Copy
} from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '../../ui/dialog';
import { Textarea } from '../../ui/textarea';

interface QualityRule {
  rule_id: string;
  rule_name: string;
  rule_type: string;
  dimension: string;
  column_name: string;
  description: string;
  sql_expression: string;
  pyspark_code: string;
  python_code: string;
  threshold?: number;
  severity: string;
  enabled: boolean;
  business_context?: string;
  error_message?: string;
  suggested_action?: string;
}

interface QualityRulesProps {
  rules: QualityRule[];
  onExecute: (rules: QualityRule[]) => Promise<any>;
  profileData?: any;
}

export const QualityRules: React.FC<QualityRulesProps> = ({ 
  rules: initialRules, 
  onExecute,
  profileData 
}) => {
  const [rules, setRules] = useState<QualityRule[]>(initialRules);
  const [isExecuting, setIsExecuting] = useState(false);
  const [executionResults, setExecutionResults] = useState<any>(null);
  const [selectedRule, setSelectedRule] = useState<QualityRule | null>(null);
  const [filterType, setFilterType] = useState<string>('all');
  const [filterSeverity, setFilterSeverity] = useState<string>('all');
  const [isAddRuleOpen, setIsAddRuleOpen] = useState(false);
  
  const ruleTypes = [
    'completeness', 'uniqueness', 'validity', 'consistency', 
    'range_check', 'format_check', 'pattern_match', 'custom'
  ];
  
  const severityLevels = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'];
  
  const handleToggleRule = (ruleId: string) => {
    setRules(rules.map(rule => 
      rule.rule_id === ruleId ? { ...rule, enabled: !rule.enabled } : rule
    ));
  };
  
  const handleExecuteRules = async () => {
    setIsExecuting(true);
    try {
      const enabledRules = rules.filter(r => r.enabled);
      const results = await onExecute(enabledRules);
      setExecutionResults(results);
    } catch (error) {
      console.error('Error executing rules:', error);
    } finally {
      setIsExecuting(false);
    }
  };
  
  const handleEditRule = (rule: QualityRule) => {
    setSelectedRule(rule);
  };
  
  const handleDeleteRule = (ruleId: string) => {
    setRules(rules.filter(r => r.rule_id !== ruleId));
  };
  
  const handleSaveRule = (updatedRule: QualityRule) => {
    if (selectedRule) {
      setRules(rules.map(r => 
        r.rule_id === selectedRule.rule_id ? updatedRule : r
      ));
    } else {
      // Add new rule
      setRules([...rules, { ...updatedRule, rule_id: `custom_${Date.now()}` }]);
    }
    setSelectedRule(null);
    setIsAddRuleOpen(false);
  };
  
  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'CRITICAL': return 'destructive';
      case 'HIGH': return 'destructive';
      case 'MEDIUM': return 'warning';
      case 'LOW': return 'secondary';
      default: return 'default';
    }
  };
  
  const getDimensionIcon = (dimension: string) => {
    switch (dimension) {
      case 'completeness': return CheckCircle;
      case 'validity': return Shield;
      case 'consistency': return Settings;
      default: return Info;
    }
  };
  
  // Filter rules
  const filteredRules = rules.filter(rule => {
    if (filterType !== 'all' && rule.rule_type !== filterType) return false;
    if (filterSeverity !== 'all' && rule.severity !== filterSeverity) return false;
    return true;
  });
  
  const enabledCount = rules.filter(r => r.enabled).length;
  
  return (
    <div className="dq-container">
      {/* Header */}
      <div className="dq-card dq-mb-lg">
        <div className="dq-card-header">
          <div className="dq-rules-header">
            <div className="dq-flex dq-items-center dq-gap-md">
              <h3 className="dq-card-title">Data Quality Rules</h3>
              <Badge variant="outline" className="dq-badge">
                {enabledCount} of {rules.length} enabled
              </Badge>
            </div>
            <div className="dq-flex dq-gap-sm">
              <button
                className="dq-btn dq-btn-secondary dq-btn-sm"
                onClick={() => setIsAddRuleOpen(true)}
              >
                <Plus className="w-4 h-4" />
                Add Rule
              </button>
              <button
                onClick={handleExecuteRules}
                disabled={isExecuting || enabledCount === 0}
                className="dq-btn dq-btn-primary"
                style={{
                  background: isExecuting || enabledCount === 0 ? 'var(--color-gray-400)' : 'linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%)'
                }}
              >
                {isExecuting ? (
                  <>
                    <Pause className="w-4 h-4 dq-spinner" />
                    Executing...
                  </>
                ) : (
                  <>
                    <Play className="w-4 h-4" />
                    Execute Rules
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
        <div className="dq-card-body">
          {/* Filters */}
          <div className="dq-rules-filters">
            <div className="dq-flex dq-items-center dq-gap-sm">
              <Filter className="w-4 h-4 dq-text-gray" />
              <label className="dq-label">Type:</label>
              <select
                className="dq-select dq-text-sm"
                style={{ minWidth: '150px' }}
                value={filterType}
                onChange={(e) => setFilterType(e.target.value)}
              >
                <option value="all">All Types</option>
                {ruleTypes.map(type => (
                  <option key={type} value={type}>
                    {type.replace('_', ' ')}
                  </option>
                ))}
              </select>
            </div>
            <div className="dq-flex dq-items-center dq-gap-sm">
              <label className="dq-label">Severity:</label>
              <select
                className="dq-select dq-text-sm"
                style={{ minWidth: '120px' }}
                value={filterSeverity}
                onChange={(e) => setFilterSeverity(e.target.value)}
              >
                <option value="all">All</option>
                {severityLevels.map(level => (
                  <option key={level} value={level}>{level}</option>
                ))}
              </select>
            </div>
          </div>
        </div>
      </div>
      
      {/* Execution Results */}
      {executionResults && (
        <div className={`dq-alert ${executionResults.passed ? 'dq-alert-success' : 'dq-alert-danger'} dq-mb-lg`}>
          <div className="dq-w-full">
            <div className="dq-flex dq-justify-between dq-items-center dq-mb-sm">
              <span className="dq-font-semibold">
                {executionResults.passed ? 'All rules passed!' : 'Some rules failed'}
              </span>
              <Badge variant={executionResults.passed ? 'success' : 'destructive'} className="dq-badge">
                {executionResults.passedCount} / {executionResults.totalCount} passed
              </Badge>
            </div>
            {executionResults.failedRules && executionResults.failedRules.length > 0 && (
              <div className="dq-mt-sm">
                {executionResults.failedRules.map((failed: any) => (
                  <div key={failed.rule_id} className="dq-text-sm dq-mb-xs">
                    • {failed.rule_name}: {failed.error_message}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
      
      {/* Rules List */}
      <div className="dq-grid dq-gap-md">
        {filteredRules.map((rule) => (
          <RuleCard
            key={rule.rule_id}
            rule={rule}
            onToggle={() => handleToggleRule(rule.rule_id)}
            onEdit={() => handleEditRule(rule)}
            onDelete={() => handleDeleteRule(rule.rule_id)}
          />
        ))}
      </div>
      
      {/* Rule Editor Dialog */}
      <RuleEditorDialog
        rule={selectedRule}
        isOpen={!!selectedRule || isAddRuleOpen}
        onClose={() => {
          setSelectedRule(null);
          setIsAddRuleOpen(false);
        }}
        onSave={handleSaveRule}
        columns={profileData?.column_profiles?.map((p: any) => p.column_name) || []}
      />
    </div>
  );
};

// Rule Card Component
const RuleCard: React.FC<{
  rule: QualityRule;
  onToggle: () => void;
  onEdit: () => void;
  onDelete: () => void;
}> = ({ rule, onToggle, onEdit, onDelete }) => {
  const [showCode, setShowCode] = useState(false);
  const DimensionIcon = getDimensionIcon(rule.dimension);
  
  return (
    <div className={`dq-rule-card ${rule.severity.toLowerCase()}`}>
      <div className="dq-flex dq-justify-between dq-items-start dq-gap-md dq-mb-md dq-flex-wrap">
        <div className="dq-flex dq-gap-md dq-flex-1" style={{ minWidth: 0 }}>
          <div className="dq-p-sm" style={{
            background: 'var(--color-gray-100)',
            borderRadius: 'var(--radius-lg)',
            flexShrink: 0
          }}>
            <DimensionIcon className="w-5 h-5" />
          </div>
          <div className="dq-flex-1" style={{ minWidth: 0 }}>
            <div className="dq-flex dq-items-center dq-gap-sm dq-mb-sm dq-flex-wrap">
              <h4 className="dq-font-semibold dq-truncate">{rule.rule_name}</h4>
              <Badge variant={getSeverityColor(rule.severity)} className="dq-badge dq-text-xs">
                {rule.severity}
              </Badge>
              <Badge variant="outline" className="dq-badge dq-text-xs">
                {rule.rule_type}
              </Badge>
            </div>
            <p className="dq-text-sm dq-text-gray dq-mb-sm">
              {rule.description}
            </p>
            <div className="dq-flex dq-items-center dq-gap-md dq-text-xs dq-text-gray dq-flex-wrap">
              <span>Column: {rule.column_name}</span>
              {rule.threshold !== undefined && (
                <span>Threshold: {rule.threshold}</span>
              )}
            </div>
          </div>
        </div>
          
        <div className="dq-flex dq-items-center dq-gap-sm">
          <Switch
            checked={rule.enabled}
            onCheckedChange={onToggle}
          />
          <button className="dq-btn dq-btn-sm" onClick={() => setShowCode(!showCode)} style={{ padding: '0.5rem' }}>
            <Code className="w-4 h-4" />
          </button>
          <button className="dq-btn dq-btn-sm" onClick={onEdit} style={{ padding: '0.5rem' }}>
            <Edit className="w-4 h-4" />
          </button>
          <button className="dq-btn dq-btn-sm" onClick={onDelete} style={{ padding: '0.5rem' }}>
            <Trash className="w-4 h-4" />
          </button>
        </div>
      </div>
        
      {showCode && (
        <div className="dq-mt-lg">
          <div className="dq-tabs">
            <div className="dq-tab-list" style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)' }}>
              <button className="dq-tab active">SQL</button>
              <button className="dq-tab">PySpark</button>
              <button className="dq-tab">Python</button>
            </div>
            <div className="dq-tab-content">
              <CodeBlock code={rule.sql_expression} language="sql" />
            </div>
          </div>
        </div>
      )}
        
      {rule.business_context && (
        <div className="dq-alert dq-alert-info dq-mt-md">
          <Info className="w-4 h-4" />
          <span className="dq-text-sm">{rule.business_context}</span>
        </div>
      )}
    </div>
  );
};

// Code Block Component
const CodeBlock: React.FC<{ code: string; language: string }> = ({ code, language }) => {
  const [copied, setCopied] = useState(false);
  
  const handleCopy = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };
  
  return (
    <div style={{ position: 'relative' }}>
      <pre className="dq-overflow-container" style={{
        background: 'var(--color-gray-900)',
        color: 'var(--color-gray-100)',
        padding: 'var(--space-md)',
        borderRadius: 'var(--radius-lg)',
        fontSize: 'var(--text-sm)'
      }}>
        <code>{code}</code>
      </pre>
      <button
        className="dq-btn dq-btn-sm"
        style={{
          position: 'absolute',
          top: 'var(--space-sm)',
          right: 'var(--space-sm)',
          padding: '0.5rem'
        }}
        onClick={handleCopy}
      >
        {copied ? (
          <CheckCircle className="w-4 h-4 dq-text-success" />
        ) : (
          <Copy className="w-4 h-4" />
        )}
      </button>
    </div>
  );
};

// Rule Editor Dialog
const RuleEditorDialog: React.FC<{
  rule: QualityRule | null;
  isOpen: boolean;
  onClose: () => void;
  onSave: (rule: QualityRule) => void;
  columns: string[];
}> = ({ rule, isOpen, onClose, onSave, columns }) => {
  const [formData, setFormData] = useState<Partial<QualityRule>>(
    rule || {
      rule_name: '',
      rule_type: 'custom',
      dimension: 'validity',
      column_name: '',
      description: '',
      sql_expression: '',
      pyspark_code: '',
      python_code: '',
      threshold: 0,
      severity: 'MEDIUM',
      enabled: true,
      business_context: '',
      error_message: '',
      suggested_action: ''
    }
  );
  
  const handleSubmit = () => {
    onSave(formData as QualityRule);
  };
  
  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>
            {rule ? 'Edit Quality Rule' : 'Add New Quality Rule'}
          </DialogTitle>
          <DialogDescription>
            Define data quality validation rules for your dataset
          </DialogDescription>
        </DialogHeader>
        
        <div className="grid gap-4 py-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label>Rule Name</Label>
              <Input
                value={formData.rule_name}
                onChange={(e) => setFormData({...formData, rule_name: e.target.value})}
                placeholder="e.g., Email Format Validation"
              />
            </div>
            
            <div>
              <Label>Column</Label>
              <select
                className="w-full border rounded-md px-3 py-2"
                value={formData.column_name}
                onChange={(e) => setFormData({...formData, column_name: e.target.value})}
              >
                <option value="">Select column</option>
                {columns.map(col => (
                  <option key={col} value={col}>{col}</option>
                ))}
              </select>
            </div>
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label>Rule Type</Label>
              <select
                className="w-full border rounded-md px-3 py-2"
                value={formData.rule_type}
                onChange={(e) => setFormData({...formData, rule_type: e.target.value})}
              >
                <option value="completeness">Completeness</option>
                <option value="uniqueness">Uniqueness</option>
                <option value="validity">Validity</option>
                <option value="consistency">Consistency</option>
                <option value="range_check">Range Check</option>
                <option value="format_check">Format Check</option>
                <option value="pattern_match">Pattern Match</option>
                <option value="custom">Custom</option>
              </select>
            </div>
            
            <div>
              <Label>Severity</Label>
              <select
                className="w-full border rounded-md px-3 py-2"
                value={formData.severity}
                onChange={(e) => setFormData({...formData, severity: e.target.value})}
              >
                <option value="CRITICAL">Critical</option>
                <option value="HIGH">High</option>
                <option value="MEDIUM">Medium</option>
                <option value="LOW">Low</option>
              </select>
            </div>
          </div>
          
          <div>
            <Label>Description</Label>
            <Textarea
              value={formData.description}
              onChange={(e) => setFormData({...formData, description: e.target.value})}
              placeholder="Describe what this rule validates"
              rows={2}
            />
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label>Threshold (%)</Label>
              <Input
                type="number"
                value={formData.threshold}
                onChange={(e) => setFormData({...formData, threshold: parseFloat(e.target.value)})}
                placeholder="95"
              />
            </div>
            
            <div>
              <Label>Dimension</Label>
              <select
                className="w-full border rounded-md px-3 py-2"
                value={formData.dimension}
                onChange={(e) => setFormData({...formData, dimension: e.target.value})}
              >
                <option value="accuracy">Accuracy</option>
                <option value="completeness">Completeness</option>
                <option value="consistency">Consistency</option>
                <option value="timeliness">Timeliness</option>
                <option value="validity">Validity</option>
                <option value="uniqueness">Uniqueness</option>
              </select>
            </div>
          </div>
          
          <div>
            <Label>SQL Expression</Label>
            <Textarea
              value={formData.sql_expression}
              onChange={(e) => setFormData({...formData, sql_expression: e.target.value})}
              placeholder="SELECT COUNT(*) FROM table WHERE column IS NULL"
              rows={3}
              className="font-mono text-sm"
            />
          </div>
          
          <div>
            <Label>Business Context</Label>
            <Textarea
              value={formData.business_context}
              onChange={(e) => setFormData({...formData, business_context: e.target.value})}
              placeholder="Why is this rule important?"
              rows={2}
            />
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label>Error Message</Label>
              <Input
                value={formData.error_message}
                onChange={(e) => setFormData({...formData, error_message: e.target.value})}
                placeholder="Message shown when rule fails"
              />
            </div>
            
            <div>
              <Label>Suggested Action</Label>
              <Input
                value={formData.suggested_action}
                onChange={(e) => setFormData({...formData, suggested_action: e.target.value})}
                placeholder="How to fix the issue"
              />
            </div>
          </div>
        </div>
        
        <DialogFooter>
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button onClick={handleSubmit}>
            {rule ? 'Update Rule' : 'Create Rule'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

// Helper functions
const getSeverityColor = (severity: string) => {
  switch (severity) {
    case 'CRITICAL': return 'destructive';
    case 'HIGH': return 'destructive';
    case 'MEDIUM': return 'warning';
    case 'LOW': return 'secondary';
    default: return 'default';
  }
};

const getDimensionIcon = (dimension: string) => {
  switch (dimension) {
    case 'completeness': return CheckCircle;
    case 'validity': return Shield;
    case 'consistency': return Settings;
    default: return Info;
  }
};