// API types for the data profiling backend
export interface GetMetadataRequest {
    database: string;
    table: string;
    columns?: string[];
}

export interface GetMetadataResponse {
    database: string;
    table: string;
    columns?: string[] | null;
}

export interface FormField {
    name: string;
    type: string;
    label: string;
    required: boolean;
    placeholder?: string;
    description?: string;
    min?: number;
    max?: number;
    step?: number;
    options?: Array<{ value: string; label: string }>;
}

export interface FormSchema {
    title: string;
    description: string;
    fields: FormField[];
}

export interface APIEndpoint {
    method: string;
    title: string;
    description: string;
    icon: string;
    color: string;
    schema: FormSchema;
}

export interface WebSocketMessage {
    type: string;
    message?: string;
    client_id?: string;
    timestamp: string;
    active_connections?: number;
}

export interface ConnectionStats {
    total_connections: number;
    active_connections: number;
    messages_sent: number;
}
