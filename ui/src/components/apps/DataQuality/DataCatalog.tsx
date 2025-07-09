import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Database,
  Search,
  Tag,
  Clock,
  Shield,
  FileText,
  GitBranch,
  Users,
  Calendar,
  TrendingUp,
  Info,
  ExternalLink,
  Star,
  StarOff
} from 'lucide-react';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';

interface DataCatalogProps {
  catalogData: any;
  dataSource: any;
}

export const DataCatalog: React.FC<DataCatalogProps> = ({ catalogData, dataSource }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTag, setSelectedTag] = useState<string | null>(null);
  const [favorites, setFavorites] = useState<Set<string>>(new Set());
  const [catalogEntries, setCatalogEntries] = useState<any[]>([]);
  
  useEffect(() => {
    // Load catalog entries
    loadCatalogEntries();
  }, [dataSource]);
  
  const loadCatalogEntries = () => {
    // Mock catalog entries - in real app, this would fetch from API
    const mockEntries = [
      {
        id: 'customers',
        name: 'customers',
        type: 'table',
        database: 'retail_analytics',
        description: 'Customer master data with demographics and preferences',
        owner: 'data-team',
        tags: ['pii', 'master-data', 'critical'],
        sensitivity: 'high',
        quality_score: 92,
        usage_count: 1523,
        last_updated: '2024-02-15T10:30:00Z',
        last_profiled: '2024-02-15T14:45:00Z',
        row_count: 10000,
        column_count: 20,
        size_bytes: 2457600,
        lineage: {
          upstream: ['raw.customer_data'],
          downstream: ['analytics.customer_segments', 'reports.customer_dashboard']
        },
        schema: [
          { name: 'customer_id', type: 'string', description: 'Unique customer identifier' },
          { name: 'email', type: 'string', description: 'Customer email address', tags: ['pii'] },
          { name: 'created_at', type: 'timestamp', description: 'Account creation timestamp' }
        ]
      },
      {
        id: 'transactions',
        name: 'transactions',
        type: 'table',
        database: 'retail_analytics',
        description: 'Sales transaction records with line items',
        owner: 'data-team',
        tags: ['transactional', 'financial'],
        sensitivity: 'medium',
        quality_score: 88,
        usage_count: 3421,
        last_updated: '2024-02-15T12:00:00Z',
        last_profiled: '2024-02-15T14:45:00Z',
        row_count: 274855,
        column_count: 15,
        size_bytes: 54971000,
        lineage: {
          upstream: ['pos.sales_data', 'online.order_data'],
          downstream: ['analytics.revenue_metrics', 'ml.recommendation_model']
        }
      },
      {
        id: 'products',
        name: 'products',
        type: 'table',
        database: 'retail_analytics',
        description: 'Product catalog with categories and pricing',
        owner: 'product-team',
        tags: ['master-data', 'reference'],
        sensitivity: 'low',
        quality_score: 95,
        usage_count: 892,
        last_updated: '2024-02-14T08:00:00Z',
        last_profiled: '2024-02-15T14:45:00Z',
        row_count: 5000,
        column_count: 18,
        size_bytes: 1843200
      }
    ];
    
    setCatalogEntries(mockEntries);
  };
  
  const toggleFavorite = (id: string) => {
    const newFavorites = new Set(favorites);
    if (newFavorites.has(id)) {
      newFavorites.delete(id);
    } else {
      newFavorites.add(id);
    }
    setFavorites(newFavorites);
  };
  
  const filteredEntries = catalogEntries.filter(entry => {
    const matchesSearch = searchTerm === '' || 
      entry.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      entry.description.toLowerCase().includes(searchTerm.toLowerCase());
      
    const matchesTag = !selectedTag || entry.tags.includes(selectedTag);
    
    return matchesSearch && matchesTag;
  });
  
  const allTags = Array.from(new Set(catalogEntries.flatMap(e => e.tags)));
  
  const getSensitivityColor = (sensitivity: string) => {
    switch (sensitivity) {
      case 'high': return 'text-red-600';
      case 'medium': return 'text-yellow-600';
      case 'low': return 'text-green-600';
      default: return 'text-gray-600';
    }
  };
  
  return (
    <div className="space-y-6">
      {/* Search and Filters */}
      <Card>
        <CardContent className="py-4">
          <div className="flex items-center space-x-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <Input
                placeholder="Search catalog..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <div className="flex items-center space-x-2">
              <Tag className="w-4 h-4 text-muted-foreground" />
              {allTags.map(tag => (
                <Badge
                  key={tag}
                  variant={selectedTag === tag ? 'default' : 'outline'}
                  className="cursor-pointer"
                  onClick={() => setSelectedTag(selectedTag === tag ? null : tag)}
                >
                  {tag}
                </Badge>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>
      
      {/* Catalog Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatCard
          icon={Database}
          label="Total Assets"
          value={catalogEntries.length.toString()}
        />
        <StatCard
          icon={Users}
          label="Data Owners"
          value={new Set(catalogEntries.map(e => e.owner)).size.toString()}
        />
        <StatCard
          icon={TrendingUp}
          label="Avg Quality Score"
          value={`${Math.round(catalogEntries.reduce((acc, e) => acc + e.quality_score, 0) / catalogEntries.length)}%`}
        />
        <StatCard
          icon={Clock}
          label="Last Updated"
          value="2 hours ago"
        />
      </div>
      
      {/* Catalog Entries */}
      <Tabs defaultValue="grid" className="space-y-4">
        <TabsList>
          <TabsTrigger value="grid">Grid View</TabsTrigger>
          <TabsTrigger value="table">Table View</TabsTrigger>
          <TabsTrigger value="lineage">Lineage</TabsTrigger>
        </TabsList>
        
        <TabsContent value="grid">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredEntries.map(entry => (
              <CatalogCard
                key={entry.id}
                entry={entry}
                isFavorite={favorites.has(entry.id)}
                onToggleFavorite={() => toggleFavorite(entry.id)}
              />
            ))}
          </div>
        </TabsContent>
        
        <TabsContent value="table">
          <Card>
            <CardContent className="p-0">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead></TableHead>
                    <TableHead>Name</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>Owner</TableHead>
                    <TableHead>Quality</TableHead>
                    <TableHead>Usage</TableHead>
                    <TableHead>Last Updated</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredEntries.map(entry => (
                    <TableRow key={entry.id}>
                      <TableCell>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => toggleFavorite(entry.id)}
                        >
                          {favorites.has(entry.id) ? (
                            <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                          ) : (
                            <StarOff className="w-4 h-4" />
                          )}
                        </Button>
                      </TableCell>
                      <TableCell className="font-medium">{entry.name}</TableCell>
                      <TableCell>
                        <Badge variant="outline">{entry.type}</Badge>
                      </TableCell>
                      <TableCell>{entry.owner}</TableCell>
                      <TableCell>
                        <div className="flex items-center space-x-2">
                          <Progress value={entry.quality_score} className="w-12 h-2" />
                          <span className="text-sm">{entry.quality_score}%</span>
                        </div>
                      </TableCell>
                      <TableCell>{entry.usage_count.toLocaleString()}</TableCell>
                      <TableCell>
                        {new Date(entry.last_updated).toLocaleDateString()}
                      </TableCell>
                      <TableCell>
                        <Button variant="ghost" size="sm">
                          <ExternalLink className="w-4 h-4" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>
        
        <TabsContent value="lineage">
          <DataLineageView entries={filteredEntries} />
        </TabsContent>
      </Tabs>
    </div>
  );
};

// Stat Card Component
const StatCard: React.FC<{
  icon: React.ElementType;
  label: string;
  value: string;
}> = ({ icon: Icon, label, value }) => (
  <Card>
    <CardContent className="p-6">
      <div className="flex items-center justify-between mb-2">
        <Icon className="w-5 h-5 text-muted-foreground" />
      </div>
      <div className="text-2xl font-bold">{value}</div>
      <p className="text-sm text-muted-foreground">{label}</p>
    </CardContent>
  </Card>
);

// Catalog Card Component
const CatalogCard: React.FC<{
  entry: any;
  isFavorite: boolean;
  onToggleFavorite: () => void;
}> = ({ entry, isFavorite, onToggleFavorite }) => {
  const getSensitivityColor = (sensitivity: string) => {
    switch (sensitivity) {
      case 'high': return 'bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300';
      case 'medium': return 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300';
      case 'low': return 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300';
      default: return 'bg-gray-100 text-gray-700';
    }
  };
  
  return (
    <Card className="hover:shadow-lg transition-shadow">
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <CardTitle className="text-lg flex items-center space-x-2">
              <Database className="w-4 h-4" />
              <span>{entry.name}</span>
            </CardTitle>
            <p className="text-sm text-muted-foreground mt-1">
              {entry.description}
            </p>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={onToggleFavorite}
          >
            {isFavorite ? (
              <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
            ) : (
              <StarOff className="w-4 h-4" />
            )}
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {/* Tags */}
          <div className="flex flex-wrap gap-1">
            {entry.tags.map((tag: string) => (
              <Badge key={tag} variant="secondary" className="text-xs">
                {tag}
              </Badge>
            ))}
            <Badge className={`text-xs ${getSensitivityColor(entry.sensitivity)}`}>
              {entry.sensitivity} sensitivity
            </Badge>
          </div>
          
          {/* Metrics */}
          <div className="grid grid-cols-2 gap-2 text-sm">
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground">Quality</span>
              <span className="font-medium">{entry.quality_score}%</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground">Usage</span>
              <span className="font-medium">{entry.usage_count}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground">Rows</span>
              <span className="font-medium">{entry.row_count.toLocaleString()}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground">Cols</span>
              <span className="font-medium">{entry.column_count}</span>
            </div>
          </div>
          
          {/* Footer */}
          <div className="flex items-center justify-between pt-2 border-t">
            <div className="flex items-center space-x-2 text-xs text-muted-foreground">
              <Users className="w-3 h-3" />
              <span>{entry.owner}</span>
            </div>
            <div className="flex items-center space-x-2 text-xs text-muted-foreground">
              <Calendar className="w-3 h-3" />
              <span>{new Date(entry.last_updated).toLocaleDateString()}</span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

// Data Lineage View Component
const DataLineageView: React.FC<{ entries: any[] }> = ({ entries }) => {
  const [selectedEntry, setSelectedEntry] = useState<any>(entries[0]);
  
  if (!selectedEntry) {
    return (
      <Card>
        <CardContent className="py-8 text-center text-muted-foreground">
          No data available for lineage view
        </CardContent>
      </Card>
    );
  }
  
  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Data Lineage Explorer</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="mb-4">
            <select
              className="w-full border rounded-md px-3 py-2"
              value={selectedEntry.id}
              onChange={(e) => setSelectedEntry(entries.find(entry => entry.id === e.target.value))}
            >
              {entries.map(entry => (
                <option key={entry.id} value={entry.id}>
                  {entry.database}.{entry.name}
                </option>
              ))}
            </select>
          </div>
          
          <div className="space-y-6">
            {/* Upstream Dependencies */}
            {selectedEntry.lineage?.upstream && (
              <div>
                <h4 className="text-sm font-semibold mb-2 flex items-center space-x-2">
                  <GitBranch className="w-4 h-4 rotate-180" />
                  <span>Upstream Dependencies</span>
                </h4>
                <div className="space-y-2">
                  {selectedEntry.lineage.upstream.map((dep: string) => (
                    <div key={dep} className="flex items-center space-x-2 p-2 bg-gray-50 dark:bg-gray-900 rounded">
                      <Database className="w-4 h-4 text-muted-foreground" />
                      <span className="text-sm">{dep}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            {/* Current Table */}
            <div className="relative">
              <div className="absolute left-1/2 top-0 bottom-0 w-px bg-gray-300 dark:bg-gray-700 -translate-x-1/2" />
              <div className="relative bg-blue-50 dark:bg-blue-950 p-4 rounded-lg border-2 border-blue-500">
                <h4 className="font-semibold flex items-center space-x-2">
                  <Database className="w-5 h-5" />
                  <span>{selectedEntry.database}.{selectedEntry.name}</span>
                </h4>
                <p className="text-sm text-muted-foreground mt-1">
                  {selectedEntry.description}
                </p>
              </div>
            </div>
            
            {/* Downstream Dependencies */}
            {selectedEntry.lineage?.downstream && (
              <div>
                <h4 className="text-sm font-semibold mb-2 flex items-center space-x-2">
                  <GitBranch className="w-4 h-4" />
                  <span>Downstream Dependencies</span>
                </h4>
                <div className="space-y-2">
                  {selectedEntry.lineage.downstream.map((dep: string) => (
                    <div key={dep} className="flex items-center space-x-2 p-2 bg-gray-50 dark:bg-gray-900 rounded">
                      <Database className="w-4 h-4 text-muted-foreground" />
                      <span className="text-sm">{dep}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

// Progress component import fix
const Progress: React.FC<{ value: number; className?: string }> = ({ value, className }) => (
  <div className={`relative h-2 w-full overflow-hidden rounded-full bg-gray-200 dark:bg-gray-800 ${className}`}>
    <div
      className="h-full bg-blue-600 transition-all"
      style={{ width: `${Math.min(100, Math.max(0, value))}%` }}
    />
  </div>
);