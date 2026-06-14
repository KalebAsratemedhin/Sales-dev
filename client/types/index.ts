export interface OutreachConfig {
  linkedin_url: string;
  calendly_scheduling_url: string;
  product_docs_path: string;
  chroma_collection_name: string;
  default_timezone: string;
  default_meeting_duration_minutes: number;
  updated_at: string;
}

export interface GoogleCalendarStatus {
  connected: boolean;
  oauth_app_configured: boolean;
  google_email?: string;
  calendar_id?: string;
  timezone?: string;
  meeting_duration_minutes?: number;
  connected_at?: string | null;
}

export interface GoogleCalendarAuthUrl {
  url: string;
  state: string;
}

export interface GmailStatus {
  connected: boolean;
  oauth_app_configured: boolean;
  google_email?: string;
  n8n_configured?: boolean;
  n8n_synced?: boolean;
  n8n_credential_id?: string;
  n8n_workflow_id?: string;
  n8n_sync_error?: string;
  connected_at?: string | null;
  n8n_synced_at?: string | null;
}

export interface GmailAuthUrl {
  url: string;
  state: string;
}

export interface UserProfile {
  full_name: string;
  email: string;
  profile_pic_url?: string | null;
}

export interface UserSettings {
  calendly_scheduling_url: string;
}

export interface ProductDoc {
  id: number;
  filename: string;
  uploaded_at: string;
}

export interface ProductDocListResponse {
  items: ProductDoc[];
}

export interface Lead {
  id: number;
  email: string;
  name: string;
  company_name: string;
  company_website: string;
  source: string;
  profile_url: string;
  persona: number | null;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface Persona {
  id: number;
  name: string;
  title_keywords: string;
  industry_keywords: string;
  search_keywords: string;
  is_active: boolean;
}

export interface Research {
  id: number;
  lead_id: number;
  website_summary: string;
  pain_points: string[];
  use_cases: string[];
  raw_content_preview: string;
  created_at: string;
}

export interface ResearchListItem extends Research {
  lead_name: string;
  lead_email: string;
  company_name: string;
  lead_status: string;
}

export interface ResearchStats {
  total: number;
  today: number;
  recent_logs: MonitorLogLine[];
}

export interface EmailThreadSummary {
  id: number;
  lead_id: number;
  name: string;
  to_email: string;
  subject: string;
  company_name: string;
  last_message_at: string;
  preview: string;
  has_inbound: boolean;
  unread: boolean;
  message_count: number;
}

export interface SentEmail {
  id: number;
  thread_id: number;
  direction: "outbound" | "inbound";
  body: string;
  sent_at: string;
  message_id: string;
}

export interface EmailThreadDetail extends EmailThreadSummary {
  research_summary: string;
  pain_points: string[];
  use_cases: string[];
  gmail_thread_id: string;
  messages: SentEmail[];
}

export interface OutreachStats {
  threads_total: number;
  emails_outbound: number;
  emails_inbound: number;
  outbound_today: number;
  inbound_today: number;
  unread_threads: number;
  recent_logs: MonitorLogLine[];
}

export interface MonitorLogLine {
  time: string;
  level: string;
  msg: string;
}

