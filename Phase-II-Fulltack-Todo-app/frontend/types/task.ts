export interface Task {
  id: string;
  title: string;
  description?: string;
  priority: 'low' | 'medium' | 'high';
  status: 'pending' | 'in-progress' | 'completed';
  created_at: string; // ISO date string
  updated_at: string; // ISO date string
  user_id: string;
}