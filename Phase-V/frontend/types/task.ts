export interface Task {
  id: string;
  title: string;
  description?: string;
  priority: 'low' | 'medium' | 'high';
  difficulty_level: 'beginner' | 'intermediate' | 'advanced'; // Added difficulty level
  status: 'pending' | 'in-progress' | 'completed';
  created_at: string; // ISO date string
  updated_at: string; // ISO date string
  user_id: string;
  due_date?: string; // Added due date
  tags?: string[]; // Added tags
  recurrence_rule?: {
    interval: 'daily' | 'weekly' | 'monthly' | 'yearly' | 'custom';
    frequency: number;
    end_date?: string;
  }; // Added recurrence rule
  reminders?: Array<{
    scheduled_time: string;
    method: 'email' | 'push' | 'sms' | 'in-app';
  }>; // Added reminders
}